import firebase_admin
import streamlit as st
from firebase_admin import credentials, firestore



# Verificar se o Firebase já está inicializado
cred = credentials.Certificate(st.secrets["firebase"])
firebase_admin.initialize_app(cred)

# Inicializar o Firestore
db = firestore.client()
