import os
import glob
import shutil
from flask import Flask, request, flash
from flask_restful import Resource, Api
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
from domain.table_analysis.table_analyser import TableAnalyser

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg",])
host = "192.168.1.7"
port = 5000
app = Flask(__name__, static_folder="temp", static_url_path='/assets')
app.config["UPLOAD_FOLDER"] = "./temp"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["SECRET_KEY"] = "pojzdoandoiaxuqpsokmqd"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
CORS(app)
api = Api(app)

# table_analyser: TableAnalyser = None

def prepare_server():
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    global table_analyser
    table_analyser = TableAnalyser("domain/config/cascade_mask_rcnn_hrnetv2p_w32_20e.py",
                                   "domain/table_analysis/model/epoch_36.pth",
                                   app.config["UPLOAD_FOLDER"])

def remove_content(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def is_file_extension_allowed(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file(request):
    # check if the post request has the file part
    if "file" not in request.files:
        flash("No file part")
        raise ValueError("No file selected")
    file = request.files["file"]
    # if user does not select file, browser also
    # submit an empty part without filename
    if not file or file.filename == "":
        flash("No selected file")
        raise ValueError("File name is not valid")
    if not is_file_extension_allowed(file.filename):
        flash("Invalid extension")
        raise ValueError("File name is not valid")
    filename = secure_filename(file.filename)
    return file, filename

@app.route('/detection/table', methods=['POST'])
def analyse_table():
    file, filename = None, None
    try:
        file, filename = validate_file(request)
    except ValueError as err:
        return {"error": str(err)}
    remove_content(app.config["UPLOAD_FOLDER"])
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    table_analyser.analyse(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    url = "http://" + host + ":" + str(port) + "/assets/"
    return {
        "original": url + filename,
        "detected tables": url + "detected_tables.png",
        "xml_result": url + "result.xml"
    }

if __name__ == "__main__":
    prepare_server()
    app.run(debug=True, host=host, port=port)


