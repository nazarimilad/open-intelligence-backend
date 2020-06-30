import cv2
import numpy
import pytesseract
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd
import random

def show_result(image):
    cv2.imshow("image", image)
    cv2.waitKey(5000)

def show_result_rectangle(image, x1, y1, x2, y2, color, weight):
    cv2.rectangle(image, (x1, y1), (x2, y2), color, weight)
    show_result(image)
    return image

def get_coordinates(image, cell):
    Coords = cell.find("Coords")
    coords = Coords.get("points").split(" ")
    coord_1, coord_2 = coords[0], coords[2]
    coords_1 = coords[0].split(",")
    coords_2 = coords[2].split(",")
    x1 = int(coords_1[0])
    y1 = int(coords_1[1])
    x2 = int(coords_2[0])
    y2 = int(coords_2[1])
    return x1, y1, x2, y2

def get_text(image, x1, y1, x2, y2, counter):
    roi = image[y1:y2, x1:x2]
    cv2.imwrite("roi.png", roi)
    cv2.imwrite("roi_" + str(counter) + ".png", roi)
    return pytesseract.image_to_string("roi.png", config="--psm 6 --oem 1")

def add_rectangle(image, x1, y1, x2, y2):
    component = lambda: random.randint(0,255)
    cv2.rectangle(
        image,
        (x1, y1), (x2, y2),
        (component(),component(),component()),
        2
    )
    return image
    
def process_xml(xml_path, image_path):
    image = cv2.imread(image_path)
    image_cells = image.copy()
    root = ET.parse(xml_path).getroot()
    tables = list()
    table_counter = 0
    for table in root:
        cell_counter = 0
        row_counter = 0
        matrix = dict()
        cell_c = 0
        for cell in table.iter("cell"):
            x1, y1, x2, y2 = get_coordinates(image, cell)
            text = get_text(image, x1, y1, x2, y2, cell_c)
            image_cells = add_rectangle(image_cells, x1, y1, x2, y2)
            row_number = str(cell.attrib["start-row"])
            if not matrix.get(row_number):
                matrix[row_number] = list()
            matrix[str(cell.attrib["start-row"])].append(text)
            cell_c += 1
        pd_data = list(matrix.values())
        print("matrix:")
        print(matrix)
        cv2.imwrite(str(table_counter) + "_xml_result_cells.png", image_cells)
        df = pd.DataFrame(pd_data[1:], columns=pd_data[0])
        print(df)
        tables.append(df.to_json(orient="split"))
    return tables