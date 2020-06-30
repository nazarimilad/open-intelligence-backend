from flask import Flask, request, flash
from werkzeug.utils import secure_filename

class Validator:

    @staticmethod
    def _is_file_extension_allowed(filename):
        ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg",])
        return "." in filename and \
            filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def validate(request):
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
        if not Validator._is_file_extension_allowed(file.filename):
            flash("Invalid extension")
            raise ValueError("File name is not valid")
        filename = secure_filename(file.filename)
        return file, filename