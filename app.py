import os
import streamlit as st
import tensorflow as tf
import numpy as np
import pandas as pd
from datetime import datetime
from PIL import Image
from utils import register_user, authenticate_user, save_scan, get_user_history
import base64

def get_base64_img(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="GreenScan AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check for secrets
REQUIRED_SECRETS = ["firebase_web", "firebase_service_account"]
missing_secrets = [s for s in REQUIRED_SECRETS if s not in st.secrets]

if missing_secrets:
    st.error(f"Missing required secrets in `.streamlit/secrets.toml`: {', '.join(missing_secrets)}")
    st.info("Please provide the necessary secrets to enable Firebase and Firestore functionality.")
    st.stop()


# ================= THEME CONSTANTS =================
PRIMARY_COLOR = "#064e3b"  # Deep Forest Green
ACCENT_COLOR = "#fbbf24"   # Amber Gold
BG_COLOR = "#fdfdfb"       # Warm Off-white
TEXT_COLOR = "#0f172a"     # Slate Dark

# ================= CSS STYLING =================
def load_css():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        * {{
            font-family: 'Outfit', sans-serif;
        }}

        .stApp {{
            background-color: {BG_COLOR};
        }}
        
        /* --- ANIMATIONS --- */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes pulseGlow {{
            0% {{ box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.4); }}
            70% {{ box-shadow: 0 0 0 10px rgba(251, 191, 36, 0.1); }}
            100% {{ box-shadow: 0 0 0 0 rgba(251, 191, 36, 0); }}
        }}

        .fade-in {{
            animation: fadeInUp 0.6s ease-out forwards;
        }}

        .block-container {{
            padding-top: 2rem;
        }}

        /* --- CUSTOM SIDEBAR --- */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #064e3b 0%, #022c22 100%);
            border-right: 1px solid rgba(255,255,255,0.05);
        }}
        
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}

        [data-testid="stSidebarNav"] {{
            background-color: transparent !important;
            padding-top: 2rem;
        }}

        [data-testid="stSidebarNav"] ul li div {{
            background-color: transparent !important;
            border-radius: 12px;
            margin: 4px 0;
            transition: all 0.3s;
        }}

        [data-testid="stSidebarNav"] ul li div:hover {{
            background-color: rgba(255,255,255,0.1) !important;
        }}

        /* --- DASHBOARD GALLERY CARDS --- */
        .selection-card {{
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(6, 78, 59, 0.1);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 10px 30px -5px rgba(0,0,0,0.03);
            cursor: pointer;
            animation: fadeInUp 0.8s ease-out;
        }}
        
        .selection-card:hover {{
            transform: translateY(-10px);
            border-color: {PRIMARY_COLOR}40;
            box-shadow: 0 20px 40px -10px rgba(6, 78, 59, 0.1);
        }}
        
        .card-img-wrapper {{
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 1.2rem;
            height: 180px;
        }}
        .card-img-wrapper img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        /* --- DASHBOARD STYLES --- */
        .hero-banner {{
            position: relative;
            background: linear-gradient(135deg, #064e3b 0%, #115e59 100%);
            padding: 2.5rem 2rem; 
            border-radius: 20px;
            color: white;
            margin-bottom: 2rem; 
            box-shadow: 0 20px 40px -10px rgba(6, 78, 59, 0.3);
            overflow: hidden;
            animation: fadeInUp 0.5s ease-out;
        }}

        .hero-banner::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: radial-gradient(circle at 2px 2px, rgba(255,255,255,0.05) 1px, transparent 0);
            background-size: 24px 24px;
        }}
        
        .hero-banner::after {{
            content: "";
            position: absolute;
            top: -50%;
            right: -10%;
            width: 300px;
            height: 300px;
            background: {ACCENT_COLOR};
            opacity: 0.1;
            border-radius: 50%;
            filter: blur(60px);
        }}
        
        .stButton > button {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 14px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s;
            letter-spacing: 0.3px;
        }}
        
        .stButton > button:hover {{
            background-color: #042f24;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(6, 78, 59, 0.4);
        }}

        /* Highlighting the Analysis button */
        div[data-testid="column"] button:has(div:contains("Analyze Leaf")) {{
            background-color: {ACCENT_COLOR} !important;
            color: #064e3b !important;
            animation: pulseGlow 2s infinite;
        }}

        /* Transparent overlays for crop selection */
        .stButton > button[key^="btn_"] {{
            height: 300px;
            margin-top: -330px;
            background-color: transparent !important;
            border: none !important;
            color: transparent !important;
            z-index: 10;
        }}

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px;
            background-color: transparent;
        }}

        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            background-color: transparent !important;
            border-radius: 0px;
            padding: 0px 10px;
            font-weight: 600;
            color: #64748b;
        }}

        .stTabs [aria-selected="true"] {{
            color: {PRIMARY_COLOR} !important;
            border-bottom: 3px solid {PRIMARY_COLOR} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

load_css()

# ================= MODEL LOADER =================
@st.cache_resource
def load_models():
    models = {"Rice": None, "Pulses": None}

    model_paths = {
        "Rice": "models/rice_model1.keras",
        "Pulses": "models/pulses_model1.keras"
    }

    for name, path in model_paths.items():
        if os.path.exists(path):
            try:
                models[name] = tf.keras.models.load_model(
                    path,
                    compile=False,
                    safe_mode=False
                )

                # Force build to avoid Keras graph bugs
                models[name].build((None, 224, 224, 3))

            except Exception as e:
                st.error(f"{name} model failed to load: {e}")

        else:
            st.warning(f"{name} model file not found at {path}")

    return models


loaded_models = load_models()

# ================= HELPERS =================
def get_class_names(choice):
    filename = "static/rice_classes.txt" if choice == "Rice" else "static/pulses_classes.txt"
    try:
        with open(filename, "r") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def preprocess_image(image):
    image = image.convert("RGB")
    image = image.resize((224, 224))
    img = np.array(image, dtype=np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# ================= SESSION MANAGEMENT =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "crop_choice" not in st.session_state:
    st.session_state.crop_choice = None

def login_user(username):
    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.page = "dashboard"

def logout_user():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.crop_choice = None
    st.session_state.page = "dashboard"

# ================= NAVIGATION & SIDEBAR =================
def render_sidebar():
    with st.sidebar:
        st.markdown("""<style>.stApp { overflow: auto !important; }</style>""", unsafe_allow_html=True)
        st.title("GreenScan AI")
        st.write(f"Logged in as: **{st.session_state.username}**")
        st.markdown("---")
        
        if st.button("Dashboard", use_container_width=True, type="primary" if st.session_state.page == "dashboard" else "secondary"):
            st.session_state.page = "dashboard"
            st.rerun()
            
        if st.button("History", use_container_width=True, type="primary" if st.session_state.page == "history" else "secondary"):
            st.session_state.page = "history"
            st.rerun()

        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
        if st.button("Log Out", use_container_width=True):
            logout_user()
            st.rerun()

        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                <p style="margin: 0; font-size: 0.8rem; color: rgba(255,255,255,0.6) !important;">Developed by</p>
                <p style="margin: 0; font-size: 1rem; font-weight: 600; color: {ACCENT_COLOR} !important;">Bougi Swarna</p>
            </div>
        """, unsafe_allow_html=True)

# ================= PAGE 1: LOGIN =================
def login_page():
    st.markdown("""<style>::-webkit-scrollbar { display: none; } .stApp { overflow: hidden !important; } .block-container { padding-top: 5rem !important; }</style>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col_hero, col_form, col4 = st.columns([0.2, 1, 1, 0.2], gap="large")

    with col_hero:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(6, 78, 59, 0.9) 0%, rgba(17, 94, 89, 0.95) 100%), url('https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?q=80&w=2826&auto=format&fit=crop'); background-size: cover; background-position: center; border-radius: 20px; padding: 3rem; height: 100%; min-height: 500px; display: flex; flex-direction: column; justify-content: space-between; color: white;">
            <div>
                <div style="background: rgba(255,255,255,0.2); width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(5px);"><span style="font-size: 30px;">🌲</span></div>
                <h1 style="color: white !important; margin-top: 20px; font-size: 2.5rem; font-weight: 700; letter-spacing: -1px;">GreenScan AI</h1>
                <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem; margin-top: 10px; line-height: 1.6;">Next-generation agriculture diagnostics powering the future of sustainable farming.</p>
            </div>
            <div style="padding: 1.5rem; background: rgba(255,255,255,0.1); border-radius: 16px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1);">
                <span style="font-weight: 600; color: {ACCENT_COLOR};">NEW UPDATE:</span> Support for 44+ plant categories coming soon.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_form:
        st.markdown("""<h2 style="color: #1e293b; margin-bottom: 10px;">Welcome Back</h2><p style="color: #64748b; margin-bottom: 30px;">Enter your credentials to access the dashboard.</p>""", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["Log In", "Create Account"])
        with tab_login:
            u_email = st.text_input("Email", key="login_user")
            u_pass = st.text_input("Password", type="password", key="login_pass")
            if st.button("Sign In →", use_container_width=True):
                status, response = authenticate_user(u_email, u_pass)
                if status: login_user(u_email); st.rerun()
                else: st.error(response)
        with tab_register:
            new_user = st.text_input("Email", key="reg_user")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Create Account", use_container_width=True):
                status, message = register_user(new_user, new_pass)
                if status: st.success(message)
                else: st.error(message)

# ================= PAGE 2: DASHBOARD VIEW =================
def dashboard_view():
    if st.session_state.page == "dashboard":
        rice_base64 = get_base64_img("static/rice_pic.jpg")
        pulses_base64 = get_base64_img("static/pulses_pic.jpeg")
        # Only show the Dashboard hero banner and Selection Cards if NO crop is selected
        if not st.session_state.crop_choice:
            # The Dashboard Banner
            st.markdown(f"""
            <div class="hero-banner">
                <h1 style='text-align: center;'>GreenScan AI</h1>
                        <h6 style='text-align: center;'>Select a crop to analyze its leaf health</h6>
            </div>
            """, unsafe_allow_html=True)

            col_rice, col_pulses = st.columns(2, gap="large")
            

            with col_rice:
                st.markdown(f"""
                    <div class="selection-card">
                        <div class="card-img-wrapper">
                            <img src="data:image/jpeg;base64,{rice_base64}">
                        </div>
                        <h4 style="margin: 0; color: #1e293b;">Rice Detection</h4>
                        <p style="color: #64748b; font-size: 0.9rem;">Analyze paddy leaf diseases</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Analyze Rice crops", key="btn_rice", use_container_width=True):
                    st.session_state.crop_choice = "Rice"
                    st.rerun()

            with col_pulses:
                st.markdown(f"""
                    <div class="selection-card">
                        <div class="card-img-wrapper">
                            <img src="data:image/jpeg;base64,{pulses_base64}">
                        </div>
                        <h4 style="margin: 0; color: #1e293b;">Pulses Detection</h4>
                        <p style="color: #64748b; font-size: 0.9rem;">Analyze bean and pea diseases</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Analyze Pulses crops", key="btn_pulses", use_container_width=True):
                    st.session_state.crop_choice = "Pulses"
                    st.rerun()
        # This part triggers ONLY after a crop is selected
        else:
            if st.button("← Back to Crop Selection", type="secondary"):
                st.session_state.crop_choice = None
                st.rerun()

            col1, col2 = st.columns([1, 1.4], gap="medium")
            current_model = loaded_models.get(st.session_state.crop_choice)
            class_names = get_class_names(st.session_state.crop_choice)

            with col1:
                st.markdown(f"<h3>Upload {st.session_state.crop_choice} Leaf</h3>", unsafe_allow_html=True)
                uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
                if uploaded_file:
                    image = Image.open(uploaded_file)
                    st.image(image, use_container_width=True, caption="Source Image")

            with col2:
                st.markdown("<h3>Analysis Results</h3>", unsafe_allow_html=True)
                if uploaded_file and st.button("Analyze Leaf", use_container_width=True):
                    if current_model:
                        with st.spinner(f"Analyzing {st.session_state.crop_choice} leaf using AI model..."):
                            img = preprocess_image(image)
                            preds = current_model.predict(img)
                            top_indices = np.argsort(preds[0])[-10:][::-1]
                            idx = top_indices[0]
                            accuracy = preds[0][idx] * 100
                            label = class_names[idx] if idx < len(class_names) else "Unknown"

                            if "___" in label:
                                plant, disease = label.split("___")
                            else:
                                plant, disease = st.session_state.crop_choice, label
                        
                            is_healthy = "healthy" in disease.lower()
                            color = PRIMARY_COLOR if is_healthy else "#ef4444"
                            save_scan(st.session_state.username, plant, disease.replace('_', ' '), float(accuracy), "Healthy" if is_healthy else "Infected")

                            st.markdown(f"""
                            <div class="fade-in" style="background: white; border-radius: 24px; padding: 2rem; box-shadow: 0 20px 50px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; margin-bottom: 2rem;">
                                <div style="display: flex; align-items: flex-start; gap: 1.5rem;">
                                    <div style="background: {color}15; width: 80px; height: 80px; border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; flex-shrink: 0;">
                                        {'✅' if is_healthy else '⚠️'}
                                    </div>
                                    <div style="flex-grow: 1;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                            <span style="background: {color}15; color: {color}; padding: 4px 12px; border-radius: 100px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                                                {st.session_state.crop_choice} Diagnostic
                                            </span>
                                            <span style="color: #64748b; font-size: 0.85rem; font-weight: 500;">{datetime.now().strftime('%b %d, %H:%M')}</span>
                                        </div>
                                        <h2 style="margin: 0; color: #1e293b; font-size: 1.8rem; line-height: 1.2;">{disease.replace('_', ' ')}</h2>
                                        <p style="color: #64748b; margin-top: 5px; font-size: 1rem;">The leaf shows signs of <b>{disease.replace('_', ' ')}</b> with a confidence score of <b>{accuracy:.1f}%</b>.</p>
                                    </div>
                                </div>
                                <div style="margin-top: 2rem; padding: 1.5rem; background: #f8fafc; border-radius: 16px;">
                                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                        <span style="font-weight: 600; color: #1e293b;">Confidence Gauge</span>
                                        <span style="font-weight: 700; color: {color};">{accuracy:.1f}%</span>
                                    </div>
                                    <div style="height: 12px; background: #e2e8f0; border-radius: 100px; overflow: hidden;">
                                        <div style="width: {accuracy}%; height: 100%; background: {color}; border-radius: 100px; transition: width 1s cubic-bezier(0.34, 1.56, 0.64, 1);"></div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            with st.expander("Show detailed probabilities"):
                                df_top = pd.DataFrame({
                                    "Condition": [class_names[i] if i < len(class_names) else f"Idx {i}" for i in top_indices],
                                    "Confidence": [preds[0][i] * 100 for i in top_indices]
                                })
                                st.dataframe(df_top, column_config={"Confidence": st.column_config.ProgressColumn("Probability", format="%.2f%%", min_value=0, max_value=100)}, use_container_width=True, hide_index=True)
                    else: st.error(f"{st.session_state.crop_choice} model not loaded.")
                elif not uploaded_file: st.info("Please upload an image to begin.")

# ================= PAGE 3: HISTORY VIEW =================
def history_page():
    if st.session_state.page == "history":
        st.markdown("<h2 style='text-align: center;'>Scan History</h2>", unsafe_allow_html=True)
        history_data = get_user_history(st.session_state.username)
        if not history_data:
            st.info("No scans found.")
        else:
            df = pd.DataFrame(history_data)
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Scans", len(df))
            m2.metric("Healthy", len(df[df['status'] == 'Healthy']))
            m3.metric("Infected", len(df[df['status'] == 'Infected']), delta_color="inverse")
            df = df.rename(columns={"date": "Date", "plant": "Crop", "disease": "Diagnosis", "confidence": "Confidence", "status": "Status"})
            st.dataframe(df, use_container_width=True, hide_index=True)

# ================= APP CONTROLLER =================
if st.session_state.logged_in:
    render_sidebar()
    if st.session_state.page == "dashboard": dashboard_view()
    elif st.session_state.page == "history": history_page()
else:
    login_page()

