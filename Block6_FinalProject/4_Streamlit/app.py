import streamlit as st
import pandas as pd
import numpy as np
import requests
from PIL import Image
from PIL.ImageOps import exif_transpose
import time
import base64
import io
import os
from streamlit_lottie import st_lottie
from sqlalchemy import create_engine, text, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


### Config
st.set_page_config(page_title="Which bug ?", page_icon="", layout="wide")



# ---------------------------------------   HEADER      --------------------------------------   

col1, col2, col3 = st.columns([1,3,1])
with col1:
    st_lottie("https://assets8.lottiefiles.com/packages/lf20_c7duFwCJnt.json",key='worm')
with col2:
    st.markdown("<h1 style='text-align: center; color: white;'>Welcome to ButterflyR</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white;'>Snap, Flutter and Track Butterflies ! </h3>", unsafe_allow_html=True)
    st.markdown("---")
with col3:
    st_lottie("https://assets5.lottiefiles.com/packages/lf20_RRITfaLgba.json", key="pap2")

if __name__ == '__main__':   

# -------------------------------------    INTRO     ----------------------------------   
    
    st.markdown("---")
    st.write('')
    col1, col2, col3, col4 = st.columns([1,1.3,1,0.6])
   
    with col1:
        st.write("")
        st.subheader("Let's BUG it !")
        st.write("")
        st.write("Upload a picture or take a photo, upload it on the right and get which butterfly is it and more info.")




# --------------------------------     UPLOAD + BUTTONS     --------------------------------   
    with col2:
        img_file = st.file_uploader("Upload a photo of your butterfly:")

    with col3:
        if img_file is not None:
            # Display the preview of the uploaded photo
            img = Image.open(img_file)
            st.image(img, width=200)

    with col4:
        st.write("")
        st.write("")
        api_call = st.button("Analyze my butterfly", key = "predict butterfly")
        st.write("")
        st.write("")
        if api_call:
            # Barre de progression:
            import time
            progress_text = "Minute, papillon! :fly:"
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.05)
                my_bar.progress(percent_complete + 1, text=progress_text)
                


# --------------------------------   API  PREDICTION    --------------------------------   
        
    if api_call:

        api_endpoint = "https://butterfly-fastapi-d8196d1bfb5f.herokuapp.com/predict"
        
        files = {"file": img_file.getvalue()}
        response = requests.post(api_endpoint, files=files)
        # Process the API response
        if response.status_code == 200:
            result = response.json()
            prediction = result["prediction"]
            # Jump lines & predict
            st.write("")
            st.write("")
            st.markdown("---")
            st.write("### What a beautiful",prediction,"!")
            st.balloons()

# -----------------------------     AFFICHAGE PREDICTION    ----------------------------   

            folder_prediction = str(prediction).upper()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(f"valid/{folder_prediction}/1.jpg")
            with col2:
                st.image(f"valid/{folder_prediction}/2.jpg")
            with col3:
                st.image(f"valid/{folder_prediction}/3.jpg")

# -----------------------------     SCRAP WIKIPEDIA    ----------------------------------   

            st.write("")
            st.subheader("Wanna get more info ? :open_book:")
            # Import package
            import wikipedia

            try:
                wiki = wikipedia.page(f"{prediction}")
                # Extract the plain text content of the page
                text = wiki.content
                # Remove headers and formatting
                import re
                text = re.sub(r'==.*?==+', '', text)
                text = text.replace('\n', '')
                st.write(text)
            except wikipedia.exceptions.DisambiguationError as e:
                st.write(f"Apologies, we have a problem. The term '{prediction}' may refer to multiple pages. Please try to provide more specific information.")
            except wikipedia.exceptions.PageError as e:
                st.write(f"Apologies, we have a problem. The page '{prediction}' does not exist on Wikipedia.")
            except Exception as e:
                st.write(f"Apologies, we encountered an error: {str(e)}")


# --------------------------------     CLOSE LOOP   ---------- ----------------------------   

        else:
            st.error("Failed to send the image to the API.")


# ---------------------------------     GEOLOC    ----------------------------------------   
            
            
    st.markdown("---")
    st.subheader("Geolocate you ! :round_pushpin:")

    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter

    col1, col2 = st.columns(2)

    with col1:
        st.write('This will allow us to track all butterflies in the world')
        street = st.text_input("Street (optional)", "Charles de montesquieu")
        city = st.text_input("City", "Antony")
        country = st.text_input("Country", "France")
        geoloc = st.button("Fly !", key = "Geoloc")
        
    with col2:
        earth = st.image('earth.png', width=400)
        if geoloc:
            earth.empty()
            geolocator = Nominatim(user_agent="GTA Lookup")
            geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
            try:
                location = geolocator.geocode(street+", "+city+", "+country)
                lat = location.latitude
                lon = location.longitude
                map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                st.map(map_data)
            except Exception as e:
                st.write("Apologies, an error occurred:", e)


# ---------------------------------     COMMENTAIRES    -----------------------------------
    
    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:
        # Option pour saisir un commentaire
        commentaires = st.text_area("Comments",value="Any problem with the app ? Send us your comments!", height=100)
        # Afficher les commentaires saisis
        send_comments = st.button("Submit :envelope_with_arrow:", key = "Submit comment")
        if send_comments:           
            Session = sessionmaker(bind=engine)
            session = Session()
            new_comment = Commenting(comment=commentaires)
            session.add(new_comment)
            session.commit()
            session.close()
            st.success("Thanks for your comment ! !")
    
    with col2:
        st.image("pap-bleu.gif")

# -------------------------------------     END    ---------------------------------------

### Footer 
empty_space, footer = st.columns([1, 2])

with empty_space:
    st.write("")

with footer:
    st.write("")
    st.write("")
    st.markdown("""🦋 Thanks for your contribution, we hope to see you soon. 🦋""")

st.markdown("---")

# https://docs.streamlit.io/library/api-reference/widgets
# https://docs.streamlit.io/library/api-reference/control-flow/st.form

