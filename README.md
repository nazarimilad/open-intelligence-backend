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

In this proof of concept, the image is transformed in two steps:

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

### Installation

#### Prerequisites for table detection

* Nvidia GPU
* Cuda 10.0 or higher (for table detection)
* Linux or MacOS (please don't try it on Windows, it won't work, save yourself a few hours of vainless pain)

If you don't need the table detection, then you won't need a GPU and you will be able to use the software on Windows too. 

#### Installation instructions

1. Install MMdetection, based on the instructions provided in the README.md in [CascadeTabNet](https://github.com/DevashishPrasad/CascadeTabNet). Cuda 10.0 is mentioned in the installation section, but Cuda 11.0 works just as fine. 
Note: the machine learning model CascadeTabNet is using, was created using the old 1.2 version of MMdetection. I would appreciate it if someone could recreate the model with the current version 2 of MMdetection, which does not support models created with version 1.x. The nice thing about version 2 of MMdetection is that it supports inference without GPU!  

2. `git clone https://github.com/nazarimilad/open-intelligence-backend`

3. `cd open-intelligence-backend`

4. Create a new Python virtual environmnent and activate it

5. Install the requirements. I know, I need to make a `requirements.txt` but I don't have the time currently.

6. Start the server with `python3 main.py`

7. ???

8. Profit

### Extra information

* The code for the front end, as seen in [the demo gif](https://github.com/nazarimilad/open-intelligence-backend/blob/master/documentation/demo.gif), can be found [here](https://github.com/nazarimilad/open-intelligence-frontend)

* The server will listen on default port 5000. You can change the host and port in `main.py`

* You will notice that the structure analysis code of [CascadeTabNet](https://github.com/DevashishPrasad/CascadeTabNet) is still there, altough it's not used. This is because I'm keeping it for comparison purposes. I'll be cleaning the code later.

* I'm a complete beginner in the computer vision domain. I'm certain that [my code for horizontal and vertical line detection](https://github.com/nazarimilad/open-intelligence-backend/blob/master/domain/line_detection/line_detector.py) is crap, so I would really appreciate it if someone with good knowledge in computer vision could give some feedback on my work.


