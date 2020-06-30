import cv2
import numpy as np
import math
from domain.line_detection.line_detection import line_detection

class LineDetector:

    def detect_lines(self, image, text_boxes, line_type=None):
        image_2 = image.copy()
        horiz_lines, vert_lines = self.find_lines(image, text_boxes, line_type)
        # horiz_lines, vert_lines = self.remove_lines_on_text(horiz_lines, vert_lines, text_boxes)
        horiz_lines, vert_lines = self.add_border_lines(horiz_lines, vert_lines, text_boxes)
        horiz_lines, vert_lines = self.extend_lines(horiz_lines, vert_lines)
        horiz_lines, vert_lines = self.merge_nearby_lines(horiz_lines, vert_lines)
        # self.show_lines(horiz_lines, vert_lines, image)
        # horiz_lines2, vert_lines2 = line_detection(image_2)
        # self.show_lines(horiz_lines2, vert_lines2, image_2)
        return horiz_lines, vert_lines

    def find_lines(self, image, text_boxes, line_type=None):
        image = self.remove_detected_text_from_image(image, text_boxes)
        # cv2.imshow("before:", image)
        # cv2.waitKey()
        # image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 1)
        kernel = np.ones((3,3),np.uint8)
        image = cv2.erode(image, kernel, iterations = 1)
        kernel = np.ones((3,3),np.uint8)
        image = cv2.dilate(image,kernel,iterations = 1)
        # cv2.imshow("after:", image)
        # cv2.waitKey()
        ## To visualize image after thresholding ##
        # cv2.imshow("bw",image)
        # cv2.waitKey(0)
        horiz_lines = list()
        vert_lines = list()
        if line_type is None:
            horiz_lines = self.find_lines_of_type(image, "horizontal", 20, 150)
            vert_lines = self.find_lines_of_type(image, "vertical", 20, 150)
        else:
            if line_type == "horizontal":
                horiz_lines = self.find_lines_of_type(image, "horizontal", 20, 150)
            elif line_type == "vertical":
                vert_lines = self.find_lines_of_type(image, "vertical", 20, 150)
        return horiz_lines, vert_lines

    def remove_detected_text_from_image(self, image, text_boxes):
        if text_boxes.empty:
            return image
        image_text_boxes_removed = image.copy()
        for index, row in text_boxes.iterrows():
            cv2.rectangle(
                image_text_boxes_removed, 
                (row["left"]-2, row["top"]-2), 
                (row["x2"]+2, row["y2"]+2), 
                (255, 255, 255), -1)
        return image_text_boxes_removed

    def find_lines_of_type(self, image, type, edges_low_threshold, threshold_hough_lines):
        kernel_size = 5
        blur_gray = cv2.GaussianBlur(image,(kernel_size, kernel_size),0)
        edges = cv2.Canny(blur_gray, edges_low_threshold, edges_low_threshold*3)

        rho = 1  # distance resolution in pixels of the Hough grid
        theta = np.pi / 180  # angular resolution in radians of the Hough grid
        min_line_length = 100  # minimum number of pixels making up a line
        max_line_gap = 20  # maximum gap in pixels between connectable line segments
        line_image = np.copy(image) * 0  # creating a blank to draw lines on

        # Run Hough on edge detected image
        # Output "lines" is an array containing endpoints of detected line segments
        lines = cv2.HoughLinesP(edges, 
                                rho, 
                                theta=theta, 
                                threshold=threshold_hough_lines, 
                                minLineLength=min_line_length,
                                maxLineGap=max_line_gap)

        if lines is None:
            return list()

        filtered_lines = list()

        t5 = math.tan(5*math.pi/180)
        t60 = math.sqrt(3)/2

        if type == "horizontal":
            for line in lines:
                x1, y1, x2, y2 = tuple(line[0])
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                if dx != 0 and abs(dy/dx) < t60:
                    filtered_lines.append((x1, y1, x2, y2))
            filtered_lines = sorted(filtered_lines, key=lambda tup: tup[1])
        elif type == "vertical":
            for line in lines:
                x1, y1, x2, y2 = tuple(line[0])
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                if not (dx != 0 and abs(dy/dx) < t60):
                    filtered_lines.append((x1, y1, x2, y2))
            filtered_lines = sorted(filtered_lines, key=lambda tup: tup[0])
        return filtered_lines

    def remove_lines_on_text(self, horiz_lines, vert_lines, text_boxes):
        if text_boxes.empty:
            return horiz_lines, vert_lines
        filtered_horiz_lines = list()
        horiz_lines_to_remove = list()
        for x1, y1, x2, y2 in horiz_lines:
            text_boxes_with_line_on = text_boxes.loc[(text_boxes["y_middle"] - 4 < y1) & (text_boxes["y_middle"] + 4 > y1)]
            if text_boxes_with_line_on.empty:
                filtered_horiz_lines.append((x1, y1, x2, y2))
        return filtered_horiz_lines, vert_lines

    def add_border_lines(self, horiz_lines, vert_lines, text_boxes):
        if text_boxes.empty:
            return horiz_lines, vert_lines
        padding_between_words_and_line = 2
        if len(horiz_lines) > 0:
            # first horizontal line
            first_horiz_line = horiz_lines[0]
            y1_first_horiz_line = first_horiz_line[1]
            first_row_text_boxes = text_boxes.loc[text_boxes["top"] < y1_first_horiz_line]
            if not first_row_text_boxes.empty:
                x1 = first_horiz_line[0]
                y1 = first_row_text_boxes["top"].min() - padding_between_words_and_line
                x2 = first_horiz_line[2]
                y2 = y1
                new_horiz_line = (x1, y1, x2, y2)
                horiz_lines.insert(0, new_horiz_line)

            # last horizontal line
            last_horiz_line = horiz_lines[-1]
            y1_last_horiz_line = last_horiz_line[1]
            last_row_text_boxes = text_boxes.loc[text_boxes["top"] > y1_last_horiz_line]
            if not last_row_text_boxes.empty:
                x1 = last_horiz_line[0]
                y1 = last_row_text_boxes["y2"].max() + padding_between_words_and_line
                x2 = last_horiz_line[2]
                y2 = y1
                new_horiz_line = (x1, y1, x2, y2)
                horiz_lines.append(new_horiz_line)

        if len(vert_lines) > 0:
            # first vertical line
            first_vert_line = vert_lines[0]
            x1_first_vert_line = first_vert_line[0]
            first_column_text_boxes = text_boxes.loc[text_boxes["x2"] < x1_first_vert_line]
            if not first_column_text_boxes.empty:
                x1 = first_column_text_boxes["left"].min() - padding_between_words_and_line
                y1 = first_vert_line[1]
                x2 = x1
                y2 = first_vert_line[3]
                new_vert_line = (x1, y1, x2, y2)
                vert_lines.insert(0, new_vert_line)

            # last horizontal line
            last_vert_line = vert_lines[-1]
            x1_last_vert_line = last_vert_line[0]
            last_column_text_boxes = text_boxes.loc[text_boxes["left"] > x1_last_vert_line]
            if not last_column_text_boxes.empty:
                x1 = last_column_text_boxes["x2"].max() + padding_between_words_and_line
                y1 = last_vert_line[1]
                x2 = x1
                y2 = last_vert_line[3]
                new_vert_line = (x1, y1, x2, y2)
                vert_lines.append(new_vert_line)
        return horiz_lines, vert_lines

    def extend_lines(self, horiz_lines, vert_lines):
        all_lines = [*horiz_lines, *vert_lines]
        if len(all_lines) > 0:
            lowest_x1 = all_lines[0][0]
            highest_x2 = all_lines[0][2]
            lowest_y1 = all_lines[0][1]
            highest_y2 = all_lines[0][3]
            for x1, y1, x2, y2 in all_lines[1:]:
                if x1 < lowest_x1:
                    lowest_x1 = x1
                if x2 > highest_x2:
                    highest_x2 = x2
                if y1 < lowest_y1:
                    lowest_y1 = y1
                if y2 > highest_y2:
                    highest_y2 = y2

        for index, (x1, y1, x2, y2) in enumerate(horiz_lines):
            horiz_lines[index] = (lowest_x1, y1, highest_x2, y1)
        for index, (x1, y1, x2, y2) in enumerate(vert_lines):
            vert_lines[index] = (x1, lowest_y1, x1, highest_y2)

        return horiz_lines, vert_lines
    
    def merge_nearby_lines(self, horiz_lines, vert_lines, line_fusion_threshold_px=10):
        horiz_lines_merged = horiz_lines
        if len(horiz_lines_merged) > 0:
            for i in range(10):
                horiz_lines_merged_iteration = list()
                horiz_line_index = 0
                while horiz_line_index < (len(horiz_lines_merged) - 1):
                    x1, y1, x2, y2 = horiz_lines_merged[horiz_line_index]
                    x1_next, y1_next, x2_next, y2_next = horiz_lines_merged[horiz_line_index + 1]
                    height_diff = y1_next - y1
                    if height_diff < line_fusion_threshold_px:
                        new_y = y1 + int(height_diff/2)
                        horiz_lines_merged_iteration.append((x1, new_y, x2, new_y))
                        horiz_line_index += 1
                    else:
                        horiz_lines_merged_iteration.append((x1, y1, x2, y2))
                    horiz_line_index += 1
                horiz_lines_merged_iteration.append(horiz_lines_merged[-1])
                horiz_lines_merged = horiz_lines_merged_iteration

        vert_lines_merged = vert_lines
        if len(vert_lines_merged) > 0:
            for i in range(10):
                vert_lines_merged_iteration = list()
                vert_line_index = 0
                while vert_line_index < (len(vert_lines_merged) - 1):
                    x1, y1, x2, y2 = vert_lines_merged[vert_line_index]
                    x1_next, y1_next, x2_next, y2_next = vert_lines_merged[vert_line_index + 1]
                    width_diff = x1_next - x1
                    if width_diff < line_fusion_threshold_px:
                        new_x = x1 + int(width_diff/2)
                        vert_lines_merged_iteration.append((new_x, y1, new_x, y2))
                        vert_line_index += 1
                    else:
                        vert_lines_merged_iteration.append((x1, y1, x2, y2))
                    vert_line_index += 1
                vert_lines_merged_iteration.append(vert_lines_merged[-1])
                vert_lines_merged = vert_lines_merged_iteration

        return horiz_lines_merged, vert_lines_merged

    def show_lines(self, horiz_lines, vert_lines, image):
        cv2.imshow("image", image)
        cv2.waitKey()
        if horiz_lines:
            for x1, y1, x2, y2 in horiz_lines:
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        if vert_lines:
            for x1, y1, x2, y2 in vert_lines:
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.imshow("image", image)
        cv2.waitKey()