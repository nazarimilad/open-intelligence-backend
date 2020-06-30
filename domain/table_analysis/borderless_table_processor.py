import cv2
import pytesseract
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import fclusterdata 
from domain.table_analysis.table_processor import TableProcessor
from domain.line_detection.line_detector import LineDetector


class BorderlessTableProcessor(TableProcessor):

    def get_table_from_image(self, image_path):
        original_image = cv2.imread(image_path)
        preprocessed_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        text_boxes = self.get_text_boxes(preprocessed_image)
        text_boxes = self._assign_rows(text_boxes)
        text_boxes = self._assign_columns(text_boxes)
        text_boxes = self._split_columns_on_vert_lines(preprocessed_image, text_boxes)
        table = self.text_boxes_to_table(text_boxes)
        return table

    def _assign_rows(self, text_boxes):
        max_dist_rows = 10
        row_indexes = self.get_clustering_indexes(
            text_boxes[["y_middle"]].values, 
            max_dist_rows
        )
        text_boxes["row"] = row_indexes
        return text_boxes

    def _assign_columns(self, text_boxes):
        max_dist_columns = 60
        columns_indexes = self.get_clustering_indexes(
            text_boxes[["x_middle"]].values, 
            max_dist_columns
        )
        text_boxes["column"] = columns_indexes
        return text_boxes

    def get_clustering_indexes(self, list_data, max_distance):
        clusters = fclusterdata(list_data, t=max_distance, criterion='distance')
        clusters_with_list_data = dict()
        for index, cluster_number in enumerate(clusters):
            if not clusters_with_list_data.get(cluster_number):
                clusters_with_list_data[cluster_number] = list()
            clusters_with_list_data[cluster_number].append(list_data[index])
        clusters_to_indexes = dict()
        for index, (key, value) in enumerate(clusters_with_list_data.items()):
            clusters_to_indexes[key] = index
        indexes = [
            clusters_to_indexes[cluster_number] for cluster_number in clusters
        ]
        return indexes

    def _split_columns_on_vert_lines(self, image, text_boxes):
        line_detector = LineDetector()
        _, vert_lines = line_detector.detect_lines(image, text_boxes, "vertical")
        text_boxes_columns = [x for _, x in text_boxes.groupby("column")]
        for no, (x1, y1, x2, y2) in enumerate(vert_lines):
            for df_index, df in enumerate(text_boxes_columns):
                left = df["left"].min()
                right = df["x2"].max()
                if x1 > left and x1 <= right:
                    for row_index, row in df.iterrows():
                        # if textbox is on right side of this line, then
                        # this textbox should be placed one column further (left to right)
                        if row.x2 >= x1:
                            text_boxes["column"][row.name] = row["column"] + no + 1
        return text_boxes