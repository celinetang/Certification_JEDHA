# Block 5 - Deployment : GetAround

This project is submitted for the Jedha Data Fullstack program certification.

## Deliverables

Personal video presentation: 

Check out my final dashboard here : 👉 [go to app](https://getaround-final-dashboard-2c0c91f46e90.herokuapp.com/)

## Project Overview
[GetAround](https://www.getaround.com/?wpsrc=Google+Organic+Search) is the Airbnb for cars. You can rent cars from any person for a few hours to a few days! Founded in 2009, this company has known rapid growth. In 2019, they count over 5 million users and about 20K available cars worldwide. 

When using Getaround, drivers book cars for a specific time period, from an hour to a few days long. They are supposed to bring back the car on time, but it happens from time to time that drivers are late for the checkout.
Late returns at checkout can generate high friction for the next driver if the car was supposed to be rented again on the same day : Customer service often reports users unsatisfied because they had to wait for the car to come back from the previous rental or users that even had to cancel their rental because the car wasn’t returned on time.
In this project, we study the threshold between two rentals so as to find a trade-off between delays and earnings.

Also, we create a price prediction API so car owners can estimate the average price per day of their car if they rent it out. 
It is accessible via the final dashboard, with the inclusion of various features for their cars. 

## Objective
Different tools were used to create the system's interacting with each other

- Datasets can b found in foler 0_data
- EDA on rental delays : study of threshold between two rentals to minimize delays and cancellations
- EDA on pricing and various features that impact pricing per day
- Train various models in order to choose the best price predicting model
- Load the model on FastAPI deployed with Heroku : 
    - https://getaround-fastapi-8ff526a585fa.herokuapp.com/docs
    - Source code in: 3_API_Prediction/app.py
- Online app interface created with Stremlit deployed with Heroku : 
    - https://getaround-final-dashboard-2c0c91f46e90.herokuapp.com/
    - Source code in: 4_Web_Dashboard/app.py

## Prerequisites

- The source code is written in Python 3.
- To locally run app and API you need Docker and Heroku 


