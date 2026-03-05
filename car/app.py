import streamlit as st
import pandas as pd
import numpy as np
import joblib
import pymongo
import hashlib
import time
import base64
from datetime import datetime

# =========================================================
# 1. CONFIGURATION & VIDÉO LOCALE
# =========================================================
st.set_page_config(
    page_title="PRESTIGE MOTORS | L'Excellence Automobile",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Fonction pour lire la vidéo locale ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

# Chargement de la vidéo
LOCAL_VIDEO_NAME = "vide.mp4"
video_str = get_base64_of_bin_file(LOCAL_VIDEO_NAME)

# Construction du HTML Vidéo + Overlay
if video_str:
    video_tag = f'''
    <video autoplay muted loop id="myVideo">
        <source src="data:video/mp4;base64,{video_str}" type="video/mp4">
    </video>
    <div id="videoOverlay"></div>
    <script>
    document.addEventListener("scroll", function() {{
        const video = document.getElementById("myVideo");
        if (video) {{
            let offset = window.pageYOffset;
            video.style.transform = "translateY(" + offset * 0.15 + "px)";
        }}
    }});
    </script>
    '''
else:
    video_tag = ""
    st.toast("⚠️ Note: Fichier 'vide.mp4' introuvable.", icon="📹")

# --- CSS GLOBAL ---
st.markdown(f"""
    <style>
    /* VIDEO CINÉMATIQUE */
    #myVideo {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -2;
        object-fit: cover;
        object-position: center 45%; /* Centrage optimal desktop */
        transition: transform 0.3s ease;
    }}
    @media (max-width: 768px) {{
        #myVideo {{
            object-position: center 30%; /* Centrage mobile */
        }}
    }}

    /* VOILE SOMBRE */
    #videoOverlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(to bottom, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.5) 50%, rgba(0,0,0,0.9) 100%);
        backdrop-filter: blur(2px);
        -webkit-backdrop-filter: blur(2px);
        z-index: -1;
    }}

    /* SUPPRESSION DES MARGES STREAMLIT */
    .stApp {{ background: transparent; }}
    .stAppHeader {{ background-color: rgba(0,0,0,0) !important; }}
    .block-container {{ padding-top: 4rem; }}

    /* TYPOGRAPHIE LUXE */
    h1, h2, h3 {{ 
        color: white !important; 
        font-family: 'Helvetica Neue', sans-serif; 
        text-transform: uppercase; 
        letter-spacing: 2px;
        text-shadow: 0 4px 10px rgba(0,0,0,1);
    }}
    p, label, span {{ color: #e2e8f0 !important; font-weight: 400; }}

    /* EFFET GLASSMORPHISM */
    .glass-card {{
        background: rgba(10, 10, 10, 0.75);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.6);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }}
    .glass-card:hover {{
        border-color: #d4af37;
        transform: translateY(-5px);
    }}

    /* BOUTONS STYLE OR */
    .stButton>button {{
        background: linear-gradient(45deg, rgba(20,20,20,0.8), rgba(50,50,50,0.8));
        border: 1px solid rgba(212, 175, 55, 0.4);
        color: #d4af37;
        height: 50px;
        font-weight: bold;
        letter-spacing: 2px;
        transition: 0.4s;
    }}
    .stButton>button:hover {{
        background: #d4af37;
        color: black;
        border-color: #d4af37;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.6);
    }}

    /* INPUTS SOMBRES */
    .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input, .stTextInput input {{
        background-color: rgba(0, 0, 0, 0.7) !important;
        color: white !important;
        border: 1px solid #555 !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.95);
        border-right: 1px solid #333;
    }}
    </style>
    {video_tag}
""", unsafe_allow_html=True)

# =========================================================
# 2. SYSTÈME (MONGODB + IA)
# =========================================================
@st.cache_resource
def init_system():
    # Mongo
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        db = client["garage_db"]
    except:
        db = None
    
    # IA
    try:
        model = joblib.load("modele_voiture.pkl")
        scaler = joblib.load("scaler.pkl")
    except:
        model, scaler = None, None
    return db, model, scaler

db, model, scaler = init_system()

# Création admin si absent
if db is not None:
    if db.users.count_documents({"username": "admin"}) == 0:
        db.users.insert_one({"username": "admin", "password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "CEO"})

# Mappings
BRANDS = {0: "Audi", 1: "BMW", 2: "Ford", 3: "Honda", 4: "Hyundai", 5: "Mercedes", 6: "Toyota", 7: "Volkswagen", 8: "Renault", 9: "Peugeot"}
def get_id(val, dic): return list(dic.keys())[list(dic.values()).index(val)]

# =========================================================
# 3. NAVIGATION (PUBLIC vs ADMIN)
# =========================================================
if 'view' not in st.session_state: st.session_state['view'] = 'public'
if 'user' not in st.session_state: st.session_state['user'] = None

def toggle_view():
    st.session_state['view'] = 'admin_login' if st.session_state['view'] == 'public' else 'public'

# =========================================================
# VUE 1 : PUBLIC
# =========================================================
if st.session_state['view'] == 'public':
    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown("##  PRESTIGE MOTORS")
    with c2:
        if st.button("ACCÈS STAFF 🔒"):
            toggle_view()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding: 60px 0;">
        <h1 style="font-size: 70px; margin-bottom:10px;">L'ART DE L'AUTOMOBILE</h1>
        <p style="font-size: 20px; color: #d4af37 !important; text-transform:uppercase; letter-spacing:4px;">
            Achat • Vente • Expertise IA
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_a, c_b, c_c = st.columns(3)
    with c_a:
        st.markdown('<div class="glass-card" style="text-align:center;"><h3>🏎️ Stock</h3><p>Véhicules d\'exception disponibles.</p></div>', unsafe_allow_html=True)
    with c_b:
        st.markdown('<div class="glass-card" style="text-align:center;"><h3>🤖 Technologie</h3><p>Estimation IA précise.</p></div>', unsafe_allow_html=True)
    with c_c:
        st.markdown('<div class="glass-card" style="text-align:center;"><h3>🌍 International</h3><p>Livraison partout dans le monde.</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>ESTIMEZ VOTRE VÉHICULE</h2>", unsafe_allow_html=True)
    
    _, col_form, _ = st.columns([1, 2, 1])
    with col_form:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            pb_b = st.selectbox("Marque", list(BRANDS.values()), key="pb")
            pb_km = st.number_input("Kilométrage", 0, 500000, 50000, key="pkm")
            pb_age = st.slider("Âge (Années)", 0, 20, 3, key="page")
            
            if st.button("OBTENIR UNE FOURCHETTE DE PRIX"):
                if model:
                    feat = np.array([[pb_km, get_id(pb_b, BRANDS), 0, 0, 0, pb_age]])
                    feat_scaled = scaler.transform(feat)
                    prix = model.predict(feat_scaled)[0]
                    st.success(f"✨ Estimation indicative : {prix*0.9:,.0f} € - {prix*1.1:,.0f} €")
                    st.info("Pour une offre ferme, connectez-vous ou visitez notre showroom.")
                else:
                    st.error("Service indisponible.")
            st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# VUE 2 : ADMIN
# =========================================================
else:
    if st.sidebar.button("⬅️ RETOUR SITE PUBLIC"):
        st.session_state['view'] = 'public'
        st.rerun()

    if st.session_state['user'] is None:
        _, c_log, _ = st.columns([1,1,1])
        with c_log:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align:center;'>PORTAIL SÉCURISÉ</h2>", unsafe_allow_html=True)
            with st.form("login"):
                u = st.text_input("Identifiant")
                p = st.text_input("Mot de passe", type="password")
                if st.form_submit_button("CONNEXION"):
                    if db is not None:
                        h = hashlib.sha256(p.encode()).hexdigest()
                        usr = db.users.find_one({"username": u, "password": h})
                        if usr:
                            st.session_state['user'] = usr['username']
                            st.rerun()
                        else:
                            st.error("Accès refusé.")
                    else:
                        st.error("BDD Offline.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        with st.sidebar:
            st.title("MANAGER V4")
            st.success(f"👤 {st.session_state['user']}")
            menu = st.radio("MENU", ["🏠 SHOWROOM", "💎 EXPERTISE IA", "📜 LOGS"])
            if st.button("DÉCONNEXION"):
                st.session_state['user'] = None
                st.rerun()

        # SHOWROOM
        if menu == "🏠 SHOWROOM":
            st.title("GESTION DU PARC")
            if db is not None:
                cars = list(db.showroom.find())
                c1, c2 = st.columns(2)
                for i, car in enumerate(cars):
                    with (c1 if i%2==0 else c2):
                        st.markdown(f"""
                        <div class="glass-card" style="text-align:left; padding:20px;">
                            <img src="{car.get('image_url')}" style="width:100%; border-radius:10px;">
                            <h3>{car['brand']} {car['model']}</h3>
                            <h2 style="color:#d4af37;">{car['price']:,.0f} €</h2>
                            <p>{car['specs']} | {car.get('status', 'En stock')}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Connectez la BDD pour voir le stock.")

        # EXPERTISE IA
        elif menu == "💎 EXPERTISE IA":
            st.title("COTATION PROFESSIONNELLE")
            with st.container():
                st.markdown('<div class="glass-card" style="text-align:left;">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1:
                    b = st.selectbox("Marque", list(BRANDS.values()))
                    km = st.number_input("Kilométrage Réel", 0, 500000, 45000)
                with c2:
                    age = st.slider("Âge", 0, 30, 3)
                    fuel = st.selectbox("Carburant", ["Diesel", "Essence"])
                with c3:
                    trans = st.selectbox("Boite", ["Automatique", "Manuelle"])
                    typ = st.selectbox("Type", ["SUV", "Berline", "Coupe"])

                if st.button("LANCER L'ANALYSE COMPLÈTE"):
                    if model:
                        bar = st.progress(0)
                        for x in range(50):
                            time.sleep(0.01)
                            bar.progress(x*2)
                        bar.empty()

                        feat = np.array([[km, get_id(b, BRANDS), 0, 0, 0, age]])
                        feat_scaled = scaler.transform(feat)
                        prix = model.predict(feat_scaled)[0]
                        marge = 0.18
                        rachat = prix * (1 - marge)

                        st.markdown("---")
                        k1, k2, k3 = st.columns(3)
                        k1.metric("PRIX RACHAT (NET)", f"{rachat:,.0f} €")
                        k2.metric("COTE MARCHÉ", f"{prix:,.0f} €")
                        k3.metric("MARGE PRÉVISIONNELLE", f"{prix - rachat:,.0f} €")

                        if db is not None:
                            db.history.insert_one({"user": st.session_state['user'], "desc": f"{b} {typ}", "price": prix, "date": datetime.now()})
                            st.toast("Dossier archivé en BDD", icon="✅")
                st.markdown('</div>', unsafe_allow_html=True)

        # LOGS
        elif menu == "📜 LOGS":
            st.title("HISTORIQUE DES ESTIMATIONS")
            if db is not None:
                logs = list(db.history.find().sort("date", -1).limit(10))
                for l in logs:
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:5px; margin-bottom:5px; display:flex; justify-content:space-between;">
                        <span>{l.get('desc')} ({l.get('user')})</span>
                        <strong style="color:#d4af37;">{l.get('price'):,.0f} €</strong>
                    </div>
                    """, unsafe_allow_html=True)
