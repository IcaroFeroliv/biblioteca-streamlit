import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Pega as credenciais do secrets.toml
firebase_config = dict(st.secrets["firebase"])

# Corrigir quebra de linha da chave
firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")

# Criar objeto de credenciais do Firebase
cred = credentials.Certificate(firebase_config)

# Inicializar Firebase somente se ainda não foi iniciado
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred, {
        'storageBucket': firebase_config["storage_bucket"]
    })
db = firestore.client()

st.set_page_config(page_title="Grupo Projeta", layout="wide")

st.markdown("""
    <style>
        /* Esconde a barra de ferramentas do Streamlit */
        header
         {

            visibility: hidden;
        }

    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])
with col1:
    st.title("Deletar Atestado")
with col2:
    st.image("logoprojeta.png", width=350)

db = firestore.client()

# Buscar todos os documentos
todos_docs = db.collection("atestados").stream()
documentos = {}
empresas_cadastradas = set()
servicos_cadastrados = set()

for doc in todos_docs:
    data = doc.to_dict()
    documentos[doc.id] = data
    empresas_cadastradas.add(data.get("Empresa", ""))
    servicos_cadastrados.add(data.get("Servico", ""))

# Filtros
colf1, colf2, colf3, colf4 = st.columns(4)

with colf1:
    empresas_opcoes = ["Todos"] + sorted(empresas_cadastradas)
    filtro_empresa = st.selectbox("Filtrar por Empresa", empresas_opcoes)

with colf2:
    servicos_opcoes = ["Todos"] + sorted(servicos_cadastrados)
    filtro_servico = st.selectbox("Filtrar por Tipo de Serviço", servicos_opcoes)

with colf3:
    filtro_cat = st.text_input("Número CAT (parcial ou completo)")

with colf4:
    filtro_objeto = st.text_input("Objeto (parcial ou completo)")

# Botão de pesquisa
if st.button("Pesquisar"):
    resultados = {}

    for doc_id, data in documentos.items():
        cond1 = (filtro_empresa == "Todos") or (data.get("Empresa") == filtro_empresa)
        cond2 = (filtro_servico == "Todos") or (data.get("Servico") == filtro_servico)
        cond3 = (filtro_cat.lower() in str(data.get("CAT", "")).lower()) if filtro_cat else True
        cond4 = (filtro_objeto.lower() in str(data.get("Objeto", "")).lower()) if filtro_objeto else True

        if cond1 and cond2 and cond3 and cond4:
            resultados[doc_id] = data

    if not resultados:
        st.warning("Nenhum atestado encontrado.")
    else:
        st.session_state.atestados_encontrados = resultados
        st.session_state.atestado_selecionado = None

# Mostrar lista de atestados encontrados
if "atestados_encontrados" in st.session_state and st.session_state.atestados_encontrados:
    atestado_id = st.selectbox("Selecione o atestado para deletar",
                               options=list(st.session_state.atestados_encontrados.keys()),
                               format_func=lambda k: f"{st.session_state.atestados_encontrados[k].get('CAT', '')} - {st.session_state.atestados_encontrados[k].get('Objeto', '')}"
                               )

    if atestado_id:
        dados = st.session_state.atestados_encontrados[atestado_id]
        st.subheader("Informações do Atestado")

        for chave, valor in dados.items():
            if isinstance(valor, str):
                st.text_input(f"{chave}", value=valor, disabled=True, key=f"view_text_{chave}")
            elif isinstance(valor, (int, float)):
                st.number_input(f"{chave}", value=valor, disabled=True, key=f"view_number_{chave}")
            elif isinstance(valor, bool):
                st.checkbox(f"{chave}", value=valor, disabled=True, key=f"view_check_{chave}")
            elif isinstance(valor, list):
                st.multiselect(f"{chave}", options=valor, default=valor, disabled=True, key=f"view_list_{chave}")
            else:
                st.text_area(f"{chave}", value=str(valor), disabled=True, key=f"view_area_{chave}")

        st.warning(f"⚠️ Você está prestes a deletar o atestado: **{dados.get('Objeto', 'sem nome')}**.")

        if st.button("❌ Deletar este atestado"):
            confirmar = st.radio("Tem certeza?", ["Não", "Sim"], horizontal=True)

            if confirmar == "Sim":
                db.collection("atestados").document(atestado_id).delete()
                st.success("✅ Atestado deletado com sucesso!")
                time.sleep(1)
                st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)