from domain.table_analysis.border import border
from domain.table_analysis.Functions.blessFunc import borderless
from mmdet.apis import inference_detector, show_result, init_detector
import cv2
import lxml.etree as etree
import glob
import matplotlib.pyplot as plt
import mmcv

class TableAnalyser:

    def __init__(self, config_path, checkpoint_path, result_path):
        self.config_path = config_path
        self.checkpoint_path = checkpoint_path
        self.result_path = result_path
        self.model = init_detector(config_path, checkpoint_path)

    def analyse(self, img_path):
        # List of images in the image_path
        result = inference_detector(self.model, img_path)
        img = show_result(img_path, result, ('Bordered', 'cell', 'Borderless'), score_thr=0.7, show=False)
        plt.figure(figsize=(15, 10))
        plt.imshow(mmcv.bgr2rgb(img))
        plt.savefig("temp/detected_table.png", bbox_inches="tight", pad_inches=0)
        res_border = []
        res_bless = []
        res_cell = []
        root = etree.Element("document")
        ## for border
        for r in result[0][0]:
            if r[4]>.85:
                res_border.append(r[:4].astype(int))
        ## for cells
        for r in result[0][1]:
            if r[4]>.85:
                r[4] = r[4]*100
                res_cell.append(r.astype(int))
        ## for borderless
        for r in result[0][2]:
            if r[4]>.85:
                res_bless.append(r[:4].astype(int))
        ## if border tables detected 
        if len(res_border) != 0:
            ## call border script for each table in image
            for res in res_border:
                try:
                    root.append(border(res,cv2.imread(img_path)))  
                except:
                    pass
        if len(res_bless) != 0:
            if len(res_cell) != 0:
                for no,res in enumerate(res_bless):
                    root.append(borderless(res,cv2.imread(img_path),res_cell))

        myfile = open(self.result_path + "/" + "result.xml", "w")
        myfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        myfile.write(etree.tostring(root, pretty_print=True,encoding="unicode"))
        myfile.close()