import streamlit as st
import sqlite3
import numpy as np
import pandas as pd
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
import plotly.express as px
import os
import requests

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Rice Leaf Nutrient Deficiency Detection System",
    page_icon="🌾",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>

.stApp{
background-image:url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1600");
background-size:cover;
background-position:center;
background-attachment:fixed;
}

#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header{visibility:hidden;}

.stButton>button{
background:#2e8b57;
color:white;
border-radius:10px;
height:3em;
width:100%;
}

h1,h2,h3,p,label{
color:white !important;
}

.sidebar .sidebar-content{
background-color:#1e5631;
}

</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT PRIMARY KEY,
password TEXT
)
""")

conn.commit()

# ---------------- USER FUNCTIONS ----------------
def add_user(username,password):
    try:
        c.execute(
            "INSERT INTO users VALUES (?,?)",
            (username,password)
        )
        conn.commit()
        return True
    except:
        return False

def login_user(username,password):
    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username,password)
    )
    return c.fetchone()

---------------- MODEL LOADING ----------------

import os
import requests
from tensorflow.keras.models import load_model

@st.cache_resource
def load_ai_model():

model_path = "rice_model.keras"

url = "https://1drv.ms/download/c/9452a9ab72438e79/IQCH1QILdjRxRq7VKS0tmChjAXjPeAHUvs6tPXGTWsQWxAv"

try:

    if not os.path.exists(model_path):

        with st.spinner("Downloading AI Model... Please wait"):

            response = requests.get(url, stream=True)

            with open(model_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

    model = load_model(model_path)

    return model

except Exception as e:

    st.error(f"Model Loading Error: {e}")

    return None

model = load_ai_model()

---------------- CLASSES ----------------

class_names = [
"Nitrogen Deficiency",
"Phosphorus Deficiency",
"Potassium Deficiency"
]
# ---------------- RECOMMENDATIONS ----------------
fertilizers = {
    "Healthy":
        "No deficiency detected. Plant is healthy.",

    "Nitrogen Deficiency":
        "Apply Urea fertilizer.",

    "Phosphorus Deficiency":
        "Apply DAP fertilizer.",

    "Potassium Deficiency":
        "Apply Potash fertilizer.",
        
    "Not Rice Leaf":
        "The uploaded image does not appear to be a rice leaf."
}

# ---------------- PREDICTION ----------------
def predict_image(img):

    if model is None:
        return None,None,None

    img = img.resize((224,224))

    arr = np.array(img)/255.0

    arr = np.expand_dims(arr,axis=0)

    prediction = model.predict(arr,verbose=0)

    confidence = float(np.max(prediction))*100

    predicted_class = class_names[
        np.argmax(prediction)
    ]

    return predicted_class,confidence,prediction

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if "username" not in st.session_state:
    st.session_state.username=""

# ---------------- LOGIN / SIGNUP ----------------
if not st.session_state.logged_in:

    st.title("🌾 Rice Leaf Nutrient Deficiency Detection System")

    menu = st.selectbox(
        "Choose Option",
        ["Login","Sign Up"]
    )

    if menu=="Login":

        st.subheader("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            result = login_user(
                username,
                password
            )

            if result:
                st.session_state.logged_in=True
                st.session_state.username=username
                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid Username or Password")

    else:

        st.subheader("📝 Sign Up")

        new_user = st.text_input(
            "Create Username"
        )

        new_pass = st.text_input(
            "Create Password",
            type="password"
        )

        if st.button("Create Account"):

            if add_user(
                new_user,
                new_pass
            ):
                st.success(
                    "Account Created Successfully"
                )

            else:
                st.error(
                    "Username Already Exists"
                )

# ---------------- MAIN APP ----------------
else:

    st.sidebar.title("🌾 Navigation")

    st.sidebar.success(
        f"Welcome {st.session_state.username}"
    )

    page = st.sidebar.radio(
        "Select Page",
        [
            "🏠 Home",
            "📷 Detection",
            "ℹ️ About Project"
        ]
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout"):

        st.session_state.logged_in=False
        st.session_state.username=""
        st.rerun()

    # HOME
    if page=="🏠 Home":

        st.title(
            "🌾 Rice Leaf Nutrient Deficiency Detection System"
        )

        st.markdown("""
### Features

✅ Login & Sign Up

✅ Upload Image

✅ Camera Capture

✅ AI Prediction

✅ Confidence Percentage

✅ Confidence Graph

✅ Fertilizer Recommendation

✅ Not-a-Rice-Leaf Detection

✅ About Project

✅ Professional Sidebar
""")

    # ABOUT
    elif page=="ℹ️ About Project":

        st.title("ℹ️ About Project")

        st.markdown("""
### Rice Leaf Nutrient Deficiency Detection System

This project uses Deep Learning and Computer Vision
to detect nutrient deficiencies in rice leaves.

### Detects

• Healthy Leaf

• Nitrogen Deficiency

• Phosphorus Deficiency

• Potassium Deficiency

### Technologies

• Python

• TensorFlow

• Streamlit

• SQLite

• Plotly
""")

    # DETECTION
    elif page=="📷 Detection":

        st.title("📷 Rice Leaf Detection")

        uploaded_file = st.file_uploader(
            "Upload Rice Leaf Image",
            type=["jpg","jpeg","png"]
        )

        camera_image = st.camera_input(
            "Capture Image"
        )

        image_file = None

        if uploaded_file:
            image_file = uploaded_file

        elif camera_image:
            image_file = camera_image

        if image_file:

            image = Image.open(
                image_file
            ).convert("RGB")

            st.image(
                image,
                caption="Rice Leaf Image",
                use_container_width=True
            )

            if st.button("🔍 Predict"):

                if model is None:

                    st.error(
                        "Model not loaded correctly. Please verify the Google Drive ID and access permissions."
                    )

                else:

                    predicted_class,confidence,prediction = predict_image(
                        image
                    )

                    # Not Rice Leaf Threshold check
                    if confidence < 80:

                        st.error(
                            "Wrong Image! Please upload a rice leaf image only."
                        )
                        st.stop()

                    else:

                        st.success(
                            f"Prediction : {predicted_class}"
                        )

                        st.info(
                            f"Confidence : {confidence:.2f}%"
                        )

                        st.subheader(
                            "💊 Fertilizer Recommendation"
                        )

                        st.success(
                            fertilizers.get(predicted_class, "No recommendation details found.")
                        )

                        # Populating graph data for all 4 model classes dynamically
                        confidences_list = [float(p) * 100 for p in prediction[0]]
                        
                        chart_data = pd.DataFrame({
                            "Class": class_names[:len(confidences_list)],
                            "Confidence": confidences_list
                        })

                        fig = px.bar(
                            chart_data,
                            x="Class",
                            y="Confidence",
                            title="Prediction Confidence"
                        )

                        st.plotly_chart(
                            fig,
                            use_container_width=True
                        )
