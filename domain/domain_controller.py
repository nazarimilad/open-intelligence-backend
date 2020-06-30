import os
from domain.table_detection.table_detector import TableDetector
from domain.preprocessing import preprocessor
from domain.ocr import ocr


class DomainController:

    def __init__(self, work_path, detector_config_path, detector_model_path):
        self.work_path = work_path
        self.table_detector = TableDetector(
            detector_config_path,
            detector_config_path,
            self.work_path
        )
    
    def get_tables(self):
        preprocessor.preprocess(
            os.path.join(self.work_path, "original.png"),
            self.work_path
        )
        self.table_detector.analyse(os.path.join(self.work_path, "preprocessed.png"))
        tables = ocr.process_xml(
            os.path.join(app.config["UPLOAD_FOLDER"], "result.xml"),
            os.path.join(app.config["UPLOAD_FOLDER"], "preprocessed.png")
        )
        return tables