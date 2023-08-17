import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.subplots as sp
from plotly.subplots import make_subplots
import json



###########################
# MAIN CODE ###############
###########################
### Page style
st.set_page_config(
        page_title="GetAround Late Checkouts Analysis",
        page_icon="🚘⏱",
        layout="wide"
    )

if __name__ == '__main__':

    ###################################################################################################
    ## PAGE and GRAPHICS CONFIGURATION
    ###################################################################################################
    
    ### Side Menu
    with st.sidebar:
        selected = option_menu("Menu", ["Project Presentation", 'Delays Analysis','Pricing Analysis and Prediction'], 
            icons=['house', 'alarm','app-indicator'], menu_icon="car-front-fill", default_index=0)
        selected


   

    ###################################################################################################
    ## PROJECT PRESENTATION

    if selected == 'Project Presentation':
        st.image('getaround_logo.jpg')
        st.write(
        """
        GetAround is the Airbnb for cars. You can rent cars from any person for a few hours to a few days!

Founded in 2009, this company has known rapid growth. 
In 2019, they count over 5 million users and about 20K available cars worldwide. 
        """,
        unsafe_allow_html=True,
    )

        st.markdown("---")
        st.write("")
        st.subheader("Project ")
        st.write("")
        st.write("""

When using Getaround, drivers book cars for a specific time period, from an hour to a few days long. They are supposed to bring back the car on time, but it happens from time to time that drivers are late for the checkout.

Late returns at checkout can generate high friction for the next driver if the car was supposed to be rented again on the same day : Customer service often reports users unsatisfied because they had to wait for the car to come back from the previous rental or users that even had to cancel their rental because the car wasnt returned on time.""")
        
        st.markdown("---")
        st.write("")
        st.subheader("Objectives ")
        st.write("")
    
        st.markdown(" ")
    
        st.write("""
        In order to mitigate those issues we’ve decided to implement a minimum delay between two rentals. A car won’t be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental.

        It solves the late checkout issue but also potentially hurts Getaround/owners revenues: we need to find the right trade off.
        
        - First, a delay analysis is conducted on the dataset that is provided, in order to determine a threshold duration between checkout and checkin of next rental.
        - Second, you can find a price predictor for rental cars. """)

            