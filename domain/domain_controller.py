import os
from domain.table_detection.table_detector import TableDetector
from domain.preprocessing import preprocessor
from domain.ocr import ocr
from domain.table_analysis.table_processor import TableProcessor
from domain.table_analysis.bordered_table_processor import BorderedTableProcessor
from domain.table_analysis.borderless_table_processor import BorderlessTableProcessor
import json
import numpy as np

class DomainController:

    def __init__(self, work_path, detector_config_path, detector_model_path):
        self.work_path = work_path
        self.table_detector = TableDetector(
            detector_config_path,
            detector_model_path,
            self.work_path
        )
        self.bordered_table_processor = BorderedTableProcessor()
        self.borderless_table_processor = BorderlessTableProcessor()

    def default(self, obj):
        if type(obj).__module__ == np.__name__:
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj.item()
        raise TypeError('Unknown type:', type(obj))
    
    def get_tables(self):
        preprocessor.preprocess(os.path.join(self.work_path, "original.png"), self.work_path)
        detection_result = self.table_detector.analyse(os.path.join(self.work_path, "preprocessed.png"))
        # tables = ocr.process_xml(
        #     os.path.join(self.work_path, "result.xml"),
        #     os.path.join(self.work_path, "preprocessed.png")
        # )
        tables = list()
        for detection in detection_result:
            table = None
            table_type = detection["table_type"]
            image_path = detection["image_path"]
            if table_type == "bordered":
                table = self.bordered_table_processor.get_table_from_image(image_path)
            elif table_type == "borderless":
                table = self.borderless_table_processor.get_table_from_image(image_path)
            else:
                raise ValueError(f"Table type {table_type} is not supported.")
            tables.append(table.to_json(orient="split"))
        return tables