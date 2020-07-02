# Open-Intelligence backend

## Introduction 
Open Intelligence, will be an open source machine learning middleware API.

It will be an alternative to the closed source machine learning API's of Google, Amazon, Microsoft, etc. that everyone will be able to setup on premise.

Open Intelligence could be used by a file sharing system such as [Nextcloud](https://nextcloud.com/) to analyse and transform document data (OCR for example), by [Jellyfin](https://jellyfin.org/) for video recommendations and more.

The first feature is a proof of concept for my bachelor thesis, table transformation from images. Since I still have to graduate this year, the focus currently is the proof of concept and not Open Intelligence. This is why the server is just a basic debugging Flask REST API.

But if you have suggestions and/or questions, you can make an issue of course.
Contributions are also welcome!

## Table detection and transformation

Wouldn't it be great if you could take a screenshot of a table on a website for example and automatically be able to paste the table data of the screenshot image into your spreadsheet software? 

![Demonstration](documentation/demo.gif)

This is what table detection and transformation is about.

In this proof of concept, the image is transformed in mainly two steps:

1. Table detection
2. Table structure analysis and transformation

### Table detection

It is possible that the image not only contains the table we need to transform, but
also a page title, paragraphs, drawings, etc. 

This is why we need to first extract the table from the image with table detection.

For table detection, I'm currently using [CascadeTabNet](https://github.com/DevashishPrasad/CascadeTabNet). With their algorithm, the authors of CascadeTabNet achieved 3rd rank in ICDAR 2019 post-competition results for table detection while attaining the best accuracy results for the ICDAR 2013 and TableBank dataset. Their paper can be found [here](https://arxiv.org/abs/2004.12629).

### Table structure analysis and transformation

Although [CascadeTabNet](https://github.com/DevashishPrasad/CascadeTabNet) provides an approach for table transformation, the results were not really convincing in my case. This is why I wrote my own algorithm for it.

For a bordered table (a table in which every cell has borders), we assign every text box a row and column index based on its own position compared to the position of the (vertical and horizontal) border lines. For example: if the y2 value of a text box is greater than the y value of the first horizontal line, but it's lower than the y value of the second horizontal line, then we can assume that this textbox belongs to the first row of the table.

In a borderless table, since there are no borders for every cell, the spacing between text boxes of different columns is significantly greater than the spacing between text boxes of the same column. Similarly, text boxes of different rows have significantly different y-values. Based on this observervations, we use hierarchical clustering to cluster the different text boxes, once for the column index and once again for the row index. I'm using hierarchical clustering because we can specify a maximum distance between the clusters. In other popular clustering algorithms, such as K-means clustering, you have to specify the amount of clusters. For this we would need to know the amount of columns and rows, which is information we don't have.

## Data processing flow

1. The `/detection/table` REST [API method](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/rest/api.py#L34) is called with the image as a file attachement, from the [front end](https://github.com/nazarimilad/open-intelligence-frontend/blob/0d4bcc26d9e9f1e53857e131137038cd7f37202e/open-intelligence-frontend/src/components/file-upload/file-upload.js#L12)
2. The file is validated by the [Validator](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/rest/validation/validator.py#L4) class. This is to prevent invalid or non-image files to be fed to the the rest of the pipeline
3. After this, the domain controller is called for further [handling](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/domain/domain_controller.py#L31):   

    4. The image is [preprocessed](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/domain/preprocessing/preprocessor.py#L18): extra padding is added to the image. This is necessary because, while the table detector works well on documents with table(s) in it, it has difficulties recognising the table in a cropped image of a specific table.
    5. The tables [get detected](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/domain/table_detection/table_detector.py#L20) by CascadeTabNet and an isolated image of every table is send to the table processor
    6. [The table processor](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/domain/table_analysis/bordered_table_processor.py#L11) finds all the text boxes with OCR ([Tesseract](https://github.com/tesseract-ocr/tesseract)), including the text value, position, width, height, etc of every text box in the image. All this information about the text boxes is held in a Pandas Dataframe
    7. The table image (and the text boxes in the case of borderless tables) is analysed to [assign](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/domain/table_analysis/bordered_table_processor.py#L25) a row and column index to every text box
    8. Text boxes with identical row and column values [are aggregated](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/domain/table_analysis/table_processor.py#L69)
    9. The text box dataframe [gets transformed into a new dataframe](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/domain/table_analysis/table_processor.py#L46) containing only the text information, since other values like the x, y, width, heigh, etc values of the text boxes are not needed anymore.
    10. This new dataframe is transformed [into JSON data](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/domain/domain_controller.py#L49) 
    11. Steps 6-10 are repeated for the image of every detected table. 
    12. The final result is send back to the REST API server, which [sends the analysis result](https://github.com/nazarimilad/open-intelligence-backend/blob/61847c5b0153bf431c2bc107a099eb3355d76ba6/rest/api.py#L44) to the client that made the API request in the first place

## Installation

### Prerequisites for table detection

* Nvidia GPU
* Cuda 10.0 or higher (for table detection)
* Linux or MacOS (please don't try it on Windows, it won't work, save yourself a few hours of vainless pain)

If you don't need the table detection, then you won't need a GPU and you will be able to use the software on Windows too. 

### Installation instructions

1. Install MMdetection, based on the instructions provided in the README.md in [CascadeTabNet](https://github.com/DevashishPrasad/CascadeTabNet). Cuda 10.0 is mentioned in the installation section, but Cuda 11.0 works just as fine. 
Note: the machine learning model CascadeTabNet is using, was created using the old 1.2 version of MMdetection. I would appreciate it if someone could recreate the model with the current version 2 of MMdetection, which does not support models created with version 1.x. The nice thing about version 2 of MMdetection is that it supports inference without GPU!  

2. `git clone https://github.com/nazarimilad/open-intelligence-backend`

3. `cd open-intelligence-backend`

4. Create a new Python virtual environmnent and activate it

5. Install the requirements. I know, I need to make a `requirements.txt` but I don't have the time currently.

6. Start the server with `python3 main.py`

7. ???

8. Profit

## Extra information

* The code for the front end, as seen in [the demo gif](https://github.com/nazarimilad/open-intelligence-backend/blob/master/documentation/demo.gif), can be found [here](https://github.com/nazarimilad/open-intelligence-frontend)

* The server will listen on default port 5000. You can change the host and port in `main.py`

* You will notice that the structure analysis code of [CascadeTabNet](https://github.com/DevashishPrasad/CascadeTabNet) is still there, altough it's not used. This is because I'm keeping it for comparison purposes. I'll be cleaning the code later.

* I'm a complete beginner in the computer vision domain. I'm certain that [my code for horizontal and vertical line detection](https://github.com/nazarimilad/open-intelligence-backend/blob/master/domain/line_detection/line_detector.py) is crap, so I would really appreciate it if someone with good knowledge in computer vision could give some feedback on my work.


