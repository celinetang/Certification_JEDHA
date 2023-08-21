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
import webbrowser



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

    ## DATASET PROCESSINGS
    ###################################################################################################
    
    ### Load raw data
    df = pd.read_excel('get_around_delay_analysis.xlsx',sheet_name='rentals_data')

    ### Processing data
    #### modify 'state' column to add information on whether checkout is on time or late:
    df['detailed_state'] = df['delay_at_checkout_in_minutes'].apply(lambda x : 'on_time' if x <= 0
                                                                else '1h_late_checkout' if 0<x<60
                                                                else '2h_late_checkout' if 60<x<120
                                                                else 'very_late_checkout' if x>120
                                                                else np.nan
                                                                )
    # There are some rentals that are specified as ENDED but have a NaN value for delay in checkout in minutes. We presume those ended on time. 

    df['detailed_state'] = df['detailed_state'].fillna(df['state'])
    df['detailed_state'] = df['detailed_state'].replace('ended', 'unknown_checkout_time')
    lst = ["on_time", "1h_late_checkout", '2h_late_checkout', 'very_late_checkout','canceled', 'unknown_checkout_time']
    df_status = df['detailed_state'].value_counts(normalize=True).reset_index()
    df_status['detailed_state'] = pd.Categorical(df_status['detailed_state'], lst, ordered=True)
    df_status = df_status.sort_values('detailed_state')
    nb_rentals = len(df)

    # Link each rentals with the previous rental to see if it has influence on cancellation or not
    df1= df.copy()
    df_merged = df.merge(df1, how='left', left_on='previous_ended_rental_id', right_on='rental_id', suffixes=['_current', '_previous'] )

    #We're only going to consider the car rentals that have a previous rental ID
    df_merged = df_merged.dropna(subset=['previous_ended_rental_id_current'])
    nb_rentals_previous_data = df_merged.shape[0]

    #Reorder the columns with previous rental information followed by current rental information.
    df1 = df_merged[['rental_id_previous', 'checkin_type_previous', 'state_previous', 'detailed_state_previous', 'delay_at_checkout_in_minutes_previous', 'rental_id_current', 'checkin_type_current', 'state_current', 'time_delta_with_previous_rental_in_minutes_current', 'detailed_state_current' , 'delay_at_checkout_in_minutes_current' ]]
    df1.loc[:,'checkin_delay_in_minutes'] = df1['delay_at_checkout_in_minutes_previous'] - df1['time_delta_with_previous_rental_in_minutes_current']
    m1 = (df1['checkin_delay_in_minutes'] > 0) & (df1['state_current'] == 'canceled')
    m2 = (df1['checkin_delay_in_minutes'] > 0) & (df1['state_current'] == 'ended')
    m3 = (df1['checkin_delay_in_minutes'] < 0) & (df1['state_current'] == 'ended')

    df1.loc[:,'impact'] = np.select([m1, m2, m3], ['Cancellation due to late checkout', 'Late checkin', 'No impact'], 
                            default='No data')
    df_impact = df1['impact'].value_counts(normalize=True).reset_index()
    color_mapping = {'No impact' : 'green', 'No data' : 'grey',
       'Cancellation due to late checkout' : 'red',
       'Late checkin' : '#FF9900'}
    
    df1['detailed_state_previous'] = pd.Categorical(df1['detailed_state_previous'], lst, ordered=True)
    df1['impact'] = pd.Categorical(df1['impact'], ['No impact', 'Late checkin', 'Cancellation due to late checkout', 'No data'], ordered=True)
    df1 = df1.sort_values(['detailed_state_previous', 'impact'])
    timedelta_avg = df1['time_delta_with_previous_rental_in_minutes_current'].mean()

    # DATASET for pricing EDA
    df2 = pd.read_csv("get_around_pricing_project.csv")
    avg = round(df2['rental_price_per_day'].mean(), 2)

    ###################################################################################################
    ## PAGE and GRAPHICS CONFIGURATION
    ###################################################################################################
    
    ### Side Menu
    with st.sidebar:
        selected = option_menu("Menu", ["Project Presentation", 'Delays Analysis','Pricing Analysis', 'Price Prediction API'], 
            icons=['house', 'alarm','app-indicator'], menu_icon="car-front-fill", default_index=0)
        selected


   

    ###################################################################################################
    ## PROJECT PRESENTATION

    if selected == 'Project Presentation':
        st.image('get_around.png')
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
        - Second, you can find a price analysis for rental cars, and different factors that impact their rate
        - Finally you will find an price prediction API. """)




         ###################################################################################################
    ## DELAY ANALYSIS

    if selected == "Delays Analysis":
        st.markdown("<h1 style='text-align: center; color: white;'>Exploratory Data Analysis - DELAYS</h1>", unsafe_allow_html=True)
        st.markdown(" ")

        ### Main metrics
        st.header('Main metrics of dataset')
        main_metrics_cols = st.columns([20,50])
        with main_metrics_cols[0]:
            st.metric(label = "Number of rentals", value= nb_rentals)
            st.metric(label = "Number of cars", value= df['car_id'].nunique())
            st.metric(label = "Share of 'Connect' rentals", value= f"{round(len(df[df['checkin_type'] == 'connect']) /nb_rentals * 100)}%")
        with main_metrics_cols[1]:
            donut = go.Figure(
                            data=[go.Pie(
                            labels=df_status['detailed_state'],
                            values=df_status['proportion'],
                            sort=False, 
                            hole = .5), 
                                ])
            donut.update_layout(
                    title = go.layout.Title(text = "Percentages of checkout statuses"), height = 600, width = 800)
            donut.update_traces(marker=dict(colors=['#54A24B', 'RGB(253, 205, 172)', 'RGB(252, 141, 98)', 'RGB(217, 95, 2)',  '#DC3912','#7F7F7F']))
            st.plotly_chart(donut, use_container_width=True)

        ### Study of influence of previous rentals
        st.header('Study of influence of previous rentals')
        st.metric(label = "Number of rentals with given previous information", value= nb_rentals_previous_data)
        
        impact_cols = st.columns([45,50])
        with impact_cols[0]:
            previous_state_pie= px.pie(df1['detailed_state_previous'].value_counts(normalize=True).reset_index(), values='proportion', names='detailed_state_previous', 
            color = 'detailed_state_previous',
            title='Distribution of detailed state of previous rental',
            width = 600, height = 600)
            previous_state_pie.update_traces(marker=dict(colors=['#54A24B', 'RGB(253, 205, 172)', 'RGB(252, 141, 98)', 'RGB(217, 95, 2)',  '#DC3912','#7F7F7F']))
            st.plotly_chart(previous_state_pie, use_container_width=True)
        with impact_cols[1]:
            impact_previous_rental = px.pie(df_impact, values='proportion', names='impact', 
            color = 'impact', color_discrete_map=color_mapping, 
            title='Impact of previous rental checkout delay on current rental checkin', 
            width = 800, height = 600)
            st.plotly_chart(impact_previous_rental, use_container_width=True)

        impact_hist = px.histogram(df1, x="detailed_state_previous", 
             color='impact', color_discrete_map=color_mapping, 
             category_orders=dict(previous_rental_state=df1['detailed_state_previous'].unique()),
             barnorm = 'percent', text_auto=True, 
             facet_row='checkin_type_current',
             title='Impact of previous rental car delay on current rental status for mobile (uppper) and connect (lower) type rentals', 
             width = 900, height = 800)
        st.plotly_chart(impact_hist, use_container_width=True)

        st.write("""
It is obvious that when the previous rental car is returned more than 2 hours after due date, the rate of cancellation drastically increases from 2% to 14%.
It is therefore interesting to install a threshold of duration between two consecutive rentals in order to minimize these cancellations. 
""")
                 
        hist_time = px.histogram(df1, x = "time_delta_with_previous_rental_in_minutes_current", 
                   color = 'impact', color_discrete_map=color_mapping, 
                   width = 900, height = 800)
        hist_time.add_vline(x=timedelta_avg, line_color = 'grey', line_dash = 'dash', 
                    annotation_text ='Average time difference : 4h30min')
        hist_time.update_layout(title="Distribution of Time Difference planned between Consecutive Rentals",
                        xaxis_title="Time difference (minutes)",yaxis_title="Count",showlegend=True)
        st.plotly_chart(hist_time, use_container_width=True)
                        
        
        hist_impact = px.histogram(df1, x = "time_delta_with_previous_rental_in_minutes_current", 
                   facet_row='checkin_type_current',
                   color = 'impact', color_discrete_map=color_mapping,
                   barnorm='percent', text_auto=True ,
                   nbins=30, 
                   width = 1200, height = 1000)
        hist_impact.update_layout(title="Percentage of various impacts according to time difference between two consecutive rentals",xaxis_title="Time difference (minutes)",yaxis_title="Percentage",showlegend=True)
        st.plotly_chart(hist_impact, use_container_width=True)

        col1,col2 = st.columns([1,1])
        with col1:
            st.write("""
- There is a significantly higher rate of cancellation when the time difference is between two rentals is shorter than 40 min with 5.3%. In this case, 35% of next rentals have late checkin.
- As time difference increases, up until 5 hours time difference, the cancellation rate diminishes by half. """  )     
        with col2:
            st.write("""We can consider that above 90% of no impact in current car is sufficient for business, which would mean a threshold of 90-110 min.
The minimum time difference of 90 min between two car rentals would be enough to ensure >90% of car rentals happen as planned.
The very confortable time difference of 240 min (4 hours) ensures that abode 98% of car rentals happen without impact. 

Also, there is a much higher ratio (double) of ate checkin when it is a mobile rental, rather than using getaround connect. 
""")



     ###################################################################################################
    ## PRICING ANALYSIS

    if selected == 'Pricing Analysis':
        st.markdown("<h1 style='text-align: center; color: white;'>Pricing Analysis - How much does it cost ?</h1>", unsafe_allow_html=True)
        st.markdown(" ")

        ### Main metrics
        st.header('Average Pricing')
        st.metric(label = "Average price (Euro per day)", value= avg)
        
        distrib_price = ff.create_distplot([df2['rental_price_per_day']], group_labels=['distplot'])
        distrib_price.add_vline(x=df2['rental_price_per_day'].mean(), line_color = 'red', line_dash = 'dash', annotation_text ='Average rental price : 121 E/day')
        distrib_price.update_layout(title="Distribution of Rental Price per Day",xaxis_title="Rental price per day",yaxis_title="Density",showlegend=True)
        st.plotly_chart(distrib_price, use_container_width=True)

        ### Main metrics
        st.header('Different Features and their impact on pricing')
        condition = ['private_parking_available', 'has_gps',
       'has_air_conditioning', 'automatic_car', 'has_getaround_connect',
       'has_speed_regulator', 'winter_tires']

        for i, cond in enumerate(condition) :
            fig = px.histogram(df2, x = "rental_price_per_day", 
                    color = cond, marginal = 'box')
            fig.update_layout(title="Distribution of rental price per day according to " + cond,xaxis_title="rental price per day",yaxis_title="Count",showlegend=True)
            st.plotly_chart(fig, use_container_width=True)

         ###################################################################################################
    ## PRICE PREDICTION API

    if selected == 'Price Prediction API':
        st.markdown("<h1 style='text-align: center; color: white;'>Pricing Analysis - How much does it cost ?</h1>", unsafe_allow_html=True)
        st.markdown(" ")
        
        
        st.write("An API was created in order to predict the rental price per day of a car depending on the parameters that the user choose (color, fuel etc)")    
          
        st.write("For more information on the API created in order to predict the rental price per day of a car :")    
        link = '[API Documentation](https://getaround-fastapi-8ff526a585fa.herokuapp.com/docs)'
        st.markdown(link, unsafe_allow_html=True)

        # --------------------------------     UPLOAD + BUTTONS     --------------------------------   
        st.markdown("---")
        st.write('')
        col1, col2, col3 = st.columns(3)
    
        with col1:
            st.write('Main features:')
            option = st.selectbox(
        'What car model do you own ?',
        ('Citroën', 'Peugeot', 'PGO', 'Renault', 'Audi', 'BMW', 'Ford',
       'Mercedes', 'Opel', 'Porsche', 'Volkswagen', 'KIA Motors',
       'Alfa Romeo', 'Ferrari', 'Fiat', 'Lamborghini', 'Maserati',
       'Lexus', 'Honda', 'Mazda', 'Mini', 'Mitsubishi', 'Nissan', 'SEAT',
       'Subaru', 'Suzuki', 'Toyota', 'Yamaha'))
            
            option2 = st.selectbox(
        'What fuel ?',
        ('diesel', 'petrol', 'hybrid_petrol', 'electro'))
            
            option3 = st.selectbox(
        'What color ?',
        ('black', 'grey', 'white', 'red', 'silver', 'blue', 'orange',
       'beige', 'brown', 'green'))
            
            option4 = st.selectbox(
        'What car type ?',
        ('convertible','coupe','estate','hatchback','sedan','subcompact','suv','van'))
            
            number1 = st.number_input('Insert a mileage')

            number2 = st.number_input('Insert the engine power')

        with col2: 
            st.write('Additional options:')
            options5 = st.multiselect(
        'Private Parking Available:',
        ['true', 'false'])
            
            options6 = st.multiselect(
        'Has GPS:',
        ['true', 'false'])
            
            options7 = st.multiselect(
        'Has air conditioning:',
        ['true', 'false'])
            
            options8 = st.multiselect(
        'Automatic car:',
        ['true', 'false'])
            
        with col3:
            st.write('Additional options:')
            options9 = st.multiselect(
        'Has GetAround Connect:',
        ['true', 'false'])
            
            options10 = st.multiselect(
        'Has Speed Regulator',
        ['true', 'false'])
            
            options11 = st.multiselect(
        'Has Winter Tires',
        ['true', 'false'])
            
        
            st.write("")
            st.write("")
            api_call = st.button("Predict my rental price", key = "predict car price")
            st.write("")
            st.write("")
            if api_call:
                # Barre de progression:
                import time
                progress_text = "Predicting..."
                my_bar = st.progress(0, text=progress_text)
                for percent_complete in range(100):
                    time.sleep(0.05)
                    my_bar.progress(percent_complete + 1, text=progress_text)

                st.success('This is a success message!', icon="✅")
        
        # --------------------------------   API  PREDICTION    ---------------
        st.markdown("---")
        if api_call : 
            api_endpoint = "https://getaround-fastapi-8ff526a585fa.herokuapp.com/predict"

            headers = {'Content-Type': 'application/json'}  # Adding the headers
    
            file = {
                "car_features": [
                                    {
                                    "model_key": option,
                                    "mileage": number1,
                                    "engine_power": number2,
                                    "fuel": option2,
                                    "paint_color": option3,
                                    "car_type": option4,
                                    "private_parking_available": options5[0],
                                    "has_gps": options6[0],
                                    "has_air_conditioning": options7[0],
                                    "automatic_car": options8[0],
                                    "has_getaround_connect": options9[0],
                                    "has_speed_regulator": options10[0],
                                    "winter_tires": options11[0]
                                    }]}

            response = requests.post(api_endpoint, json=file)
    
            # Process the API response
            if response.status_code == 200:
                result = response.json()
                prediction = result["predictions"][0]
                st.write("")
                
                st.header(f"Renting this car out will cost {prediction} E/day!")
                

                st.markdown("---")
              



        