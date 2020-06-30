import os
import glob
import shutil
from flask import Flask, request, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
from domain.domain_controller import DomainController
from rest.validation.validator import Validator

class Server:

    def __init__(self, host, port, work_path, domain_controller):
        self.host = host
        self.port = port
        self.work_path = work_path
        self.assets_url = "http://" + host + ":" + str(port) + "/assets/"
        Path(self.work_path).mkdir(parents=True, exist_ok=True)
        self.domain_controller = domain_controller
        self.app = self._init_app(self.host, self.port, self.work_path)
    
    def start(self):
        self.app.run(debug=True, host=self.host, port=self.port)

    def _init_app(self, host, port, work_path):
        app = Flask(__name__, static_folder=work_path, static_url_path='/assets')
        app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
        app.config["SECRET_KEY"] = "pojzdoandoiaxuqpsokmqd"
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        CORS(app)

        @app.route('/detection/table', methods=['POST'])
        def analyse_table():
            file, filename = None, None
            try:
                file, filename = Validator.validate(request)
            except ValueError as err:
                return {"error": str(err)}
            self._remove_content(self.work_path)
            file.save(os.path.join(self.work_path, "original.png"))
            table = domain_controller.get_tables()
            return {
                "original": self.assets_url + "original.png",
                "detected tables": self.assets_url + "detected_tables.png",
                "xml_result": self.assets_url + "result.xml",
                "tables": tables
            }
        return app
    
    def _remove_content(self, folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))