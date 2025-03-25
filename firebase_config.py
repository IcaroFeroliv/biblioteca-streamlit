import firebase_admin
from firebase_admin import credentials, firestore

# Caminho correto para o JSON
cred_path = r"C:\Users\Usuario\PycharmProjects\Streamlit\bibliotecaprojeta-840dc-firebase-adminsdk-fbsvc-eef0722126.json"

# Verificar se o Firebase já está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

# Inicializar o Firestore
db = firestore.client()
