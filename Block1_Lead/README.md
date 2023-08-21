# Block 1 - Build and Manage Data Infrastucture : Transaction Fraud Detection

This project is submitted for the Jedha Data Fullstack program certification.

## Deliverables

Personal video presentation : https://share.vidyard.com/watch/VHwkC7UeSKwCQxgfV6qngJ?

Powerpoint presentation : File Slides.pptx

## Project Overview

Fraud is a huge issue among financial institutions. In the EU in 2019, the European Central Bank estimated that fraudulent credit card transactions amounted more €1 billion! 😮

AI can really help solve this issue by detecting fraudulent payments in a very precise manner. This usecase is actually now one of the most famous one among Data Scientists.

However, eventhough we managed to build powerful algorithms, the hard thing is now to use them in production. This means predict fraudulent payment in real-time and respond appropriately. 

## Objective

Different tools were used to create the system's interacting with each other :
- Dataset provided [here](https://lead-program-assets.s3.eu-west-3.amazonaws.com/M05-Projects/fraudTest.csv)
    - contains a large amount of payments labelled as fraudulent or not
    - used to create a ML algorithm
- Set up monitoring various Machine Learning models via MLFlow
    - https://lead-mlflow-e5bf7ad8367e.herokuapp.com
    - linked to PostgreSQL on Heroku and S3 Bucket in AWS
    - MLFlow source code in 1_MLFlow/
- Train a model for fraudulent payment detector using scikit-learn : 
    - Model source code in: 2_ML/ML.ipynb
    - all trained models are saved in S3 on AWS
- Infrastructure that ingest real-time payment
    - via the [real-time API application](https://real-time-payments-api.herokuapp.com/)
    - using Kafka confluent, source code in 3_Kafka
    - Producer_real_time_data.py file requests the real time data API cited above and stores them in Kafka Confluent
    - Consumer_real_time_data.py file will take data loaded in Kafka Confluent, load the model and preprocessing pickle from S3 and give out a prediction of a transaction
    - the results are saved in a csv file in the 4_th folder
- Orchestrate all the actions using Airflow
    - creation of DAGs for prediction and notification

## Prerequisites

- The source code is written in Python 3.
- To locally run app and API you need Docker and Heroku 
- requirements.txt are included in each folder
- To run Kafka you need to create a confluent cluster account


## Team contributors
Ophélie Jouffroy<br/>
Céline Tang<br/>
Samba<br/>
