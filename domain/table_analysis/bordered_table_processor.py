import cv2
import pytesseract
import pandas as pd
import numpy as np
import math
from domain.table_analysis.table_processor import TableProcessor
from domain.line_detection.line_detector import LineDetector

class BorderedTableProcessor(TableProcessor):

    def get_table_from_image(self, image_path):
        original_image = cv2.imread(image_path)
        preprocessed_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        text_boxes = self.get_text_boxes(preprocessed_image)
        # processing for picture image:
        # cv2.imwrite(f"./temp/preprocessed_image_a_before_thresholding.png", preprocessed_image)
        # preprocessed_image = cv2.imread(table_file, cv2.IMREAD_GRAYSCALE)
        # (thresh, preprocessed_image) = cv2.threshold(preprocessed_image, 128, 255, cv2.THRESH_BINARY)
        # cv2.imwrite(f"./temp/preprocessed_image_b_after_thresholding.png", preprocessed_image)
        # rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)) 
        # preprocessed_image = cv2.erode(preprocessed_image, rect_kernel, iterations = 1)
        # cv2.imwrite(f"./temp/preprocssed_image_c_after_eroding.png", preprocessed_image)
        line_detector = LineDetector()
        horiz_lines, vert_lines = line_detector.detect_lines(preprocessed_image, text_boxes)
        text_boxes = self.assign_rows(horiz_lines, text_boxes)
        text_boxes = self.assign_columns(vert_lines, text_boxes)
        table = self.text_boxes_to_table(text_boxes)
        return table

    def assign_rows(self, horiz_lines, text_boxes):
        row_ranges = list()
        for index, horiz_line in enumerate(horiz_lines[:len(horiz_lines) - 1]):
            x1, y1, x2, y2 = tuple(horiz_line)
            row_ranges.append((y1, horiz_lines[index + 1][1]))
        top_values = text_boxes["y2"].values.tolist()
        row_indexes = list()
        for top in top_values:
            for index, (min, max) in enumerate(row_ranges):
                if top <= max:
                    row_indexes.append(index)
                    break
            else:
                row_indexes.append(index)
        text_boxes["row"] = row_indexes
        return text_boxes
        
    def assign_columns(self, vert_lines, text_boxes):
        column_ranges = list()
        for index, vert_line in enumerate(vert_lines[:len(vert_lines) - 1]):
            x1, y1, x2, y2 = tuple(vert_line)
            column_ranges.append((x1, vert_lines[index + 1][0]))
        left_values = text_boxes["x2"].values.tolist()
        column_indexes = list()
        for left in left_values:
            was_appended = False
            for index, (min, max) in enumerate(column_ranges):
                if left <= max:
                    column_indexes.append(index)
                    was_appended = True
                    break
            else:
                column_indexes.append(index)
        text_boxes["column"] = column_indexes
        return text_boxes
