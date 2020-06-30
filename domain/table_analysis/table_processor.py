from abc import ABC, abstractmethod
import cv2
import pytesseract
import pandas as pd
import numpy as np

class TableProcessor(ABC):

    def __init__(self):
        if type(self) is TableProcessor:
            raise Exception('TableProcessor is an abstract class and cannot be instantiated directly.')

    @abstractmethod
    def get_table_from_image(self, image_path):
        raise NotImplementedError("This method has to implemented in a sub class.")

    def get_text_boxes(self, image):
        # preprocessing
        ret3, thresholded_image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        tesseract_image = cv2.cvtColor(thresholded_image, cv2.COLOR_BGR2RGB)

        OCR_TEXT_CONFIDENCE_THRESHOLD = 0.4
        OCR_CONFIG_PSM_LEVEL = 3
        boxes = pytesseract.image_to_data(
            tesseract_image, 
            output_type=pytesseract.Output.DICT,
            config=f"--psm {OCR_CONFIG_PSM_LEVEL}"
        )
        boxes = pd.DataFrame.from_dict(boxes)
        boxes["conf"] = boxes["conf"].apply(lambda x: int(x))
        boxes = boxes[boxes.conf > OCR_TEXT_CONFIDENCE_THRESHOLD]
        boxes["text"] = boxes["text"].apply(lambda x: x.strip())
        boxes = boxes[boxes.text != ""]
        boxes.drop(["level", "page_num", "block_num", "par_num", "line_num", "word_num", "conf"], 
            axis=1, 
            inplace=True
        )
        boxes = boxes.reset_index(drop=True)
        if not boxes.empty:
            boxes["y_middle"] = boxes.apply(lambda row: row.top + int(row.height/2), axis=1)
            boxes["y2"] = boxes.apply(lambda row: row.top + row.height, axis=1)
            boxes["x_middle"] = boxes.apply(lambda row: row.left + int(row.width/2) , axis=1)
            boxes["x2"] = boxes.apply(lambda row: row.left + row.width, axis=1)
        return boxes

    def text_boxes_to_table(self, text_boxes):
        text_boxes = self.aggregate_text_boxes(text_boxes)
        amount_rows = text_boxes["row"].max() + 1
        amount_columns = text_boxes["column"].max() + 1
        data = list()
        for i in range(amount_rows):
            row = list()
            for j in range(amount_columns):
                result = text_boxes.loc[
                    (text_boxes["row"] == i) & 
                    (text_boxes["column"] == j)
                ]
                if result.empty:
                    row.append(None)
                else:
                    row.append(result["text"].iloc[0].strip())
            data.append(row)
        table = pd.DataFrame(data=data[1:], columns=data[0])
        table = table.dropna(axis=1, how='all')
        table = table.dropna(axis=0, how='all')
        print(table.head(50))
        return table

    def aggregate_text_boxes(self, text_boxes):
        grouped = [x for _, x in text_boxes.groupby(["column", "row"])]
        data = list()
        for df in grouped:
            df = df.reset_index(drop=True)
            left = df["left"][0]
            top = df["top"].min()
            width = df["width"].sum()
            height = df["height"].max()
            text = ""
            column = df["column"][0]
            row = df["row"][0]
            for index, element in df.iterrows():
                text += (" " + element["text"])
            data.append([left, top, width, height, text, row, column])
        columns = df.columns.values.tolist()
        text_boxes_aggregated = pd.DataFrame(
            data=data,
            columns=["left", "top", "width", "height", "text", "row", "column"]
        )
        return text_boxes_aggregated
