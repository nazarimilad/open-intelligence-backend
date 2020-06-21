import os
from flask import Flask, request, flash
from flask_restful import Resource, Api
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
from domain.table_analysis.table_analyser import TableAnalyser

UPLOAD_FOLDER = "./temp"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg",])

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["SECRET_KEY"] = "pojzdoandoiaxuqpsokmqd"
CORS(app)
api = Api(app)

table_analyser: TableAnalyser = None

def prepare_server():
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    global table_analyser
    table_analyser = TableAnalyser("domain/config/cascade_mask_rcnn_hrnetv2p_w32_20e.py",
                                   "domain/table_analysis/model/epoch_36.pth",
                                   app.config["UPLOAD_FOLDER"])

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
    filename = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filename)
    table_analyser.analyse(filename)
    return {"file": "saved"}

if __name__ == "__main__":
    prepare_server()
    app.run(debug=True, host="0.0.0.0")


