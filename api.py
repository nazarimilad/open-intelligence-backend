import os
from flask import Flask, request, flash
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg",])


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
api = Api(app)

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

class TableAnalyser(Resource):
    def post(self):
        if request.method == "POST":
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
        else:
            return {"file": "not saved 0"}

api.add_resource(TableAnalyser, "/detection/table")

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.run(debug=True)


