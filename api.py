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

@app.route('/detection/table', methods=['POST'])
def analyse_table():
    # check if the post request has the file part
    if "file" not in request.files:
        flash("No file part")
        return {"file": "not saved 1"}
    file = request.files["file"]
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == "":
        flash("No selected file")
        return {"file": "not saved 2"}
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return {"file": "saved"}

if __name__ == "__main__":
    prepare_server()
    app.run(debug=True)


