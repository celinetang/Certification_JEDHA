# Block 6 - Final Project : Mille et Une APP

This project is submitted for the Jedha Data Fullstack program certification.

## Deliverables

**Check out our app here : 👉 [go to app](https://papillon-streamlit-bfb375963555.herokuapp.com/)**

DemoDay video presentation (watch group 1 from 6'40 to 19'): [watch here](https://www.youtube.com/watch?v=5qngzP4DGGU )

Personal video presentation: 

Powerpoint presentation : [here](https://docs.google.com/presentation/d/1iaaTtyrFAPNk3UaQ-5sxpDKRRIIILs7gO6IsiAauOXQ/edit#slide=id.ga5178bf3d4_2_0)

## Project Overview

The Mille et Une App' is an online app that helps you identify the butterfly you see. Take a picture of the butterfly, upload it, and the app will try its best to recognize it and suggest it's name, and give out main information about the species.

An additional feature with geolocalisation is added to help entomologist track down the butterfly biosphere.


## Objective
Different tools were used to create the system's interacting with each other

- Dataset from Kaggle containing : 100 butterfly or moth species
    - 12594 images in train set, 500 test, 500 validation images 224 X 224 X 3 jpg format 
    - https://www.kaggle.com/datasets/gpiosenka/butterfly-images40-species
- Set up monitoring various Machine Learning models via MLFlow
    - https://butterfly-mlflow-8cf571945f28.herokuapp.com/
    - MLFlow source code in 1_MLFlow/
    - Note : muliple machine learning models have been done during project, however, the original MLFlow set up was deleted (for cost reasons). This is why this one seems quite empty, but is hown here to see its functioning
- Train a model via Kaggle notebook Inception V3 model : 
    - Model source code in: 2_ML/papillon-100cat-10epoch.ipynb
    - model.h5 files are not pushed on Github as too heavy -
- Load the model on FastAPI deployed with Heroku : 
    - https://papillon-api-1e396125389e.herokuapp.com/docs
    - Source code in: 3_FastAPI/app.py
- Online app interface created with Stremlit deployed with Heroku : 
    - https://papillon-streamlit-bfb375963555.herokuapp.com/
    - Source code in: 4_Streamlit/app.py

## Prerequisites

- The source code is written in Python 3.
- To locally run app and API you need Docker and Heroku 

## Team contributors
Elodie Sune<br/>
Céline Tang<br/>
Zouhair Khomsi<br/>
