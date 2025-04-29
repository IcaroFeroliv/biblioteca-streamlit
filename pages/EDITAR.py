import time
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage


st.set_page_config(page_title="Grupo Projeta", layout="wide")

st.markdown("""
    <style>
        /* Esconde a barra de ferramentas do Streamlit */
        .stAppHeader.st-emotion-cache-h4xjwg.e4hpqof0,
        ._terminalButton_rix23_138 
         {

            visibility: hidden;
        }

    </style>
""", unsafe_allow_html=True)

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

col1, col2 = st.columns([2,1])
with col1:
    st.title("Editar Atestados")
with col2:
    st.image("logoprojeta.png", width=350)

# Buscar todos os documentos para montar os filtros dinamicamente
todos_docs = db.collection("atestados").stream()
empresas_cadastradas = set()
servicos_cadastrados = set()
documentos = {}

for doc in todos_docs:
    data = doc.to_dict()
    documentos[doc.id] = data
    if "Empresa" in data:
        empresas_cadastradas.add(data["Empresa"])
    if "Servico" in data:
        servicos_cadastrados.add(data["Servico"])

# Transformar em listas ordenadas
empresas_opcoes = ["Todos"] + sorted(list(empresas_cadastradas))
servicos_opcoes = ["Todos"] + sorted(list(servicos_cadastrados))

# Criando estado para armazenar os dados da pesquisa
if "atestados_encontrados" not in st.session_state:
    st.session_state.atestados_encontrados = {}

if "atestado_selecionado" not in st.session_state:
    st.session_state.atestado_selecionado = None

# Filtros dinâmicos
colf1, colf2, colf3, colf4 = st.columns(4)
with colf1:
    empresas_grupo = st.selectbox("Filtrar por Empresa", empresas_opcoes)
with colf2:
    servico = st.selectbox("Filtrar por Tipo de Serviço", servicos_opcoes)
with colf3:
    filtro_CAT = st.text_input("Número CAT (parcial ou completo)")
with colf4:
    filtro_objeto = st.text_input("Objeto (parcial ou completo)")

# Botão para pesquisar atestados
if st.button("Pesquisar"):
    encontrados = {}

    for doc_id, data in documentos.items():
        cond_empresa = (empresas_grupo == "Todos") or (data.get("Empresa") == empresas_grupo)
        cond_servico = (servico == "Todos") or (data.get("Servico") == servico)
        cond_num_interno = (
                filtro_CAT.strip() == "" or
                filtro_CAT.lower() in str(data.get("CAT", "")).lower()
        )
        cond_objeto = (
                filtro_objeto.strip() == "" or
                filtro_objeto.lower() in str(data.get("Objeto", "")).lower()
        )

        if cond_empresa and cond_servico and cond_num_interno and cond_objeto:
            encontrados[doc_id] = data

    if not encontrados:
        st.warning("Nenhum atestado encontrado com os filtros aplicados.")
    else:
        st.session_state.atestados_encontrados = encontrados
        st.session_state.atestado_selecionado = None

# Verifica se há atestados filtrados e exibe a lista
if st.session_state.atestados_encontrados:
    atestado_id = st.selectbox("Selecione um atestado para editar",
                               list(st.session_state.atestados_encontrados.keys()))

    if atestado_id:
        st.session_state.atestado_selecionado = atestado_id

# Se um atestado foi selecionado, exibe os campos editáveis
if st.session_state.atestado_selecionado:
    atestado_id = st.session_state.atestado_selecionado
    dados = st.session_state.atestados_encontrados[atestado_id]

    st.subheader("Editar Atestado")
    novos_dados = {}

    for chave, valor in dados.items():
        if isinstance(valor, str):
            novos_dados[chave] = st.text_input(f"{chave}", valor, key=f"text_input_{chave}")
        elif isinstance(valor, (int, float)):
            novos_dados[chave] = st.number_input(f"{chave}", value=valor, key=f"text_input_{chave}")
        elif isinstance(valor, bool):
            novos_dados[chave] = st.checkbox(f"{chave}", value=valor, key=f"text_input_{chave}")
        elif isinstance(valor, list):
            novos_dados[chave] = st.multiselect(f"{chave}", valor, default=valor, key=f"text_input_{chave}")

    if st.button("Salvar Alterações"):
        db.collection("atestados").document(atestado_id).update(novos_dados)
        st.success("Atestado atualizado com sucesso!")
        time.sleep(1)
        st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)
