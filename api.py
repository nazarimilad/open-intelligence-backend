import os
from flask import Flask, request, flash
from flask_restful import Resource, Api
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg",])

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["SECRET_KEY"] = "pojzdoandoiaxuqpsokmqd"
CORS(app)
api = Api(app)

def prepare_server():
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file(request):
    # check if the post request has the file part
    print("request 2:")
    print(request)
    if "file" not in request.files:
        flash("No file part")
        raise ValueError("No file selected")
    file = request.files["file"]
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == "":
        flash("No selected file")
        raise ValueError("File name is not valid")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        return file, filename

@app.route('/detection/table', methods=['POST'])
def analyse_table():
    try:
        print("request 1:")
        print(request)
        file, filename = validate_file(request)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return {"file": "saved"}
    except ValueError as err:
        return {"error": str(err)}

if __name__ == "__main__":
    prepare_server()
    app.run(debug=True)


