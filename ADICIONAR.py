import time
import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage
import re

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
        .stAppHeader.st-emotion-cache-h4xjwg.e4hpqof0,
        ._terminalButton_rix23_138 
         {
        
            visibility: hidden;
        }

    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2,1])
with col1:
    st.title("Formulário de Cadastro")
with col2:
    st.image("logoprojeta.png", width=350)

# Lista de empresas do grupo
empresas = ["OBJETIVA", "PROJETA", "SONDA", "PLATOR", "MINAS PROJETOS Objetiva", "PITAGORAS Objetiva", "METAVERSO Compasso", "DIAMANTE Compasso", "VITORIA Objetiva"]

# Participações automáticas mapeadas por nome da empresa
participacoes_automaticas = {
    "DIAMANTE Compasso": 33,
    "METAVERSO Compasso": 51,
    "MINAS PROJETOS Objetiva": 60,
    "PITAGORAS Objetiva": 51,
    "VITORIA Objetiva": 30,
    "OBJETIVA": 100,
    "PROJETA": 100,
    "SONDA": 100,
    "PLATOR": 100,

}

empresas_grupo = st.selectbox("Empresa do Grupo", ["Selecione"] + empresas)


c1, c2, c3, c4 = st.columns(4)
with c1:
    cliente = st.text_input("Cliente")

with c2:
    servicos = [
        "Diversos",
        "Estudos e Projetos Ambientais – Edificação",
        "Estudos e Projetos Ambientais - Infraestrutura",
        "Plano Diretor",
        "Plano Saneamento Básico - PMSB",
        "Projeto Edificação",
        "Projeto Praças e Parques",
        "Projeto Rodovias",
        "Projeto Saneamento",
        "Projeto Vias Urbanas",
        "REURB Regularização Fundiária",
        "Sondagem / Controle Tecnológico",
        "Supervisão Gerenciamento Edificação",
        "Supervisão Gerenciamento Rodovias",
        "Supervisão Gerenciamento Saneamento",
        "Supervisão Gerenciamento Vias Urbanas",
        "Topografia"
    ]
    servico = st.selectbox("Tipo de serviço", ["Selecione"] + servicos)

with c3:
    cat_numero = st.text_input("Número da CAT")

with c4:
    # Verifica se há participação automática
    if empresas_grupo in participacoes_automaticas:
        participacao = participacoes_automaticas[empresas_grupo]
        st.metric("Participação:", int(participacao))
    else:
        participacao = st.number_input("Participação (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.2f")

co1, co2 = st.columns(2)
with co1:
    nome_profissionais_coor = ["Ana Carolina", "André", "Ayana Lemos","Bárbara Izabela","Bruno Andrelli", "Cláudio", "Christian Sorensen", "Daniel Pinheiro", "Danilo Vitor", "Debora", "Debora Dayane",
                               "Douglas Lins","Emanuel da Silva", "Emanuel Jose", "Érika", "Fabiane Ferreira", "Grazielle", "Isabela", "Juliana Goncalves", "Julio Cesar", "Lucas Bastos", "Luiz Felipe",
                               "Mariane de Paula", "Matheus Comanduci", "Mauricio Otavio", "Márcio", "Moises Coelho", "Pablo Otoni", "Patricia", "Sarah Malta", "Sayuri", "Sérgio Henrique", "Thiago Figueiredo",
                               "Tiago Guedes", "Vicente", "Vinicius Gama", "Welington de Avila"]
    nome_profissional_coor = st.selectbox("Nome do Profissional de Coordenação", ["Selecione"] + nome_profissionais_coor)

with co2:
    nome_profissionais = ["Ana Carolina", "André", "Ayana Lemos","Bárbara Izabela","Bruno Andrelli", "Cláudio", "Christian Sorensen", "Daniel Pinheiro", "Danilo Vitor", "Debora", "Debora Dayane",
                               "Douglas Lins","Emanuel da Silva", "Emanuel Jose", "Érika", "Fabiane Ferreira", "Grazielle", "Isabela", "Juliana Goncalves", "Julio Cesar", "Lucas Bastos", "Luiz Felipe",
                               "Mariane de Paula", "Matheus Comanduci", "Mauricio Otavio", "Márcio", "Moises Coelho", "Pablo Otoni", "Patricia", "Sarah Malta", "Sayuri", "Sérgio Henrique", "Thiago Figueiredo",
                               "Tiago Guedes", "Vicente", "Vinicius Gama", "Welington de Avila"]
    nome_profissional = st.multiselect("Nome dos Profissionais", nome_profissionais)

objeto = st.text_input("Objeto")

MAX_NOME_ARQUIVO = 100

# Dicionário para armazenar os arquivos PDF válidos de cada profissional
pdfs_profissionais = {}

# Gera dinamicamente os uploads de acordo com os profissionais selecionados
for profissional in nome_profissional:
    pdf = st.file_uploader(f"Anexe o PDF de {profissional}", type=["pdf"], key=f"pdf_{profissional}")

    if pdf:
        nome_original = pdf.name
        nome_limpo = re.sub(r"[^\w\-_\.]", "_", nome_original)

        if len(nome_limpo) > MAX_NOME_ARQUIVO:
            st.warning(f"O nome do arquivo enviado para `{profissional}` é muito longo "
                       f"(`{nome_original}`). Por favor, renomeie o arquivo com um nome mais curto e sem acentos ou símbolos especiais.")
        elif not nome_limpo.lower().endswith(".pdf"):
            st.warning(f"O arquivo enviado para `{profissional}` não é um PDF válido.")
        else:
            # Nome seguro e tamanho OK
            pdfs_profissionais[profissional] = pdf

# Período
st.subheader("Período")
col1, col2, col3 = st.columns(3)
with col1:
    data_inicial = st.date_input("Data de Início", min_value=datetime(1900, 1, 1))
with col2:
    data_final = st.date_input("Data Final", min_value=datetime(1900, 1, 1))

with col3:
    if data_inicial and data_final and data_inicial <= data_final:
        dias = (data_final - data_inicial).days
        meses = dias / 30
        st.success(f"O Prazo para o projeto é de {meses:.1f} meses.")
        meses_projeto = round(meses, 1)
    else:
        st.error("A data final não pode ser antes da data inicial!")


# Informações Gerais

st.subheader("Informações Gerais")
cola1, cola2, cola3, cola4 = st.columns(4)
with cola1:
    extensao = st.number_input("Extensão (km)", min_value=0.0, step=0.1)
with cola2:
    area = st.number_input("Área (m²)", min_value=0.0, step=1.0)
with cola3:
    bim = st.selectbox("BIM", ["Não", "Sim"])
with cola4:
    patrimonio = st.selectbox("Patrimônio Tombado", ["Não", "sim"])

#Projeto edificação exibir sub

prancha_pmbs = prancha_reur = cadastral_topografia = drone_topografia = area_topografia = prancha_topografia = prancha_diversos = prancha_pdi = prancha_ifpminf = prancha_ddlinf = prancha_ddoinf = prancha_rdoinf = prancha_piainf = prancha_pmgirsinf = prancha_pradainf = prancha_rcainf = prancha_lacinf = prancha_rasinf = prancha_pcainf = prancha_eiainf = prancha_ifpmedi = prancha_ddledi = prancha_ddoedi = prancha_rdoedi = prancha_piaedi = prancha_pmgirsedi = prancha_pradaedi = prancha_rcaedi = prancha_lacedi = prancha_rasedi = prancha_eiaedi = prancha_pcaedi = prancha_rededisps = prancha_etaps = prancha_adutoraps = prancha_eteps = prancha_elevatoriopsfdp = prancha_interceptorps = prancha_redecoleps = prancha_orcsaps = prancha_elesaps = prancha_topps = fundacao_ps_info = aco_info = concreto_info = asfalto_info = solo_info = sondagem_info = prancha_infracomppr = prancha_iluppr = area_iluppr = prancha_extpr = area_extpr = prancha_elepr = kva_pr = area_elepr = prancha_orcpr = prancha_toppr = prancha_sinalpr = prancha_drepr = prancha_terpr = prancha_geopr = prancha_antipr = prancha_paisapr = prancha_urpr = meioambientepr_info = fundacaopr_info = oaepr_info = contencaopr_info = pavimentacaopr_info = estruturalpr_info = prancha_sinal = prancha_infracomp = rancha_sinal = prancha_dre = prancha_ter = prancha_geo = prancha_anti = prancha_paisavi = prancha_urvi = vu_meioambiente_info = vu_fundacao_info = vu_oae_info = vu_contencao_info = vu_topografia_info = vu_pavimentacao_info = vu_estrutural_info = prancha_reurb = prancha_acus = prancha_comp = prancha_hvac = prancha_glp = prancha_venex = prancha_arcond = prancha_ilupu = prancha_extr = prancha_cftv = prancha_spda = prancha_cets = prancha_ele = prancha_orc = prancha_top = area_ab = prancha_spci = area_urb = tipo_ab =  area_paisag = prancha_tps =prancha_irri = prancha_hds = pranchas_ab = pranchas_paisag = pranchas_cv = pranchas_are = pranchas_urb = pranchas_aa = pranchas_ar = pranchas_ac = fundacao_info = contencao_info = mobiliario_info = maqelet_info = tipo_estedi = estrutural_info = area_infraorcpr = tipo_contpr = area_est = tipo_estpep = m_cont = m_pav = cadastral_top = m2 = m3 = cadastral = drone = kva = uni_aco = kva_vu = tipo_aco = uni_Concreto = tipo_concreto = uni_asfalto = tipo_asfalto = uni_solos = tipo_solo = m_geo = furos_geo = tipo_sonda = tipo_fundps = area_fusaps = Tipo_topps = cadastral_ps = drone_os = area_topsaps = area_elesaps = kva_ps = area_orcsaps = m_redecoleps = m_interceptorps = m_elevatoriops = vazao_eteps = m_adutoraps = m_elevatoriaps = vazao_etaps = vol_etaps = m_rededisps =  area_urpr = area_paisapr = km_antipr = km_geopr = km_terpr = km_drepr = km_pavpr = m_pavpr = tipo_pavpr = tipo_subasepr = km_sinalpr = tipo_toppr = cadastral_toppr = km_toppr = area_toppr = km_orcpr = area_infraorcprtipo_contpr = m_contpr = m2_contpr = m3_contpr = tipo_oaevupr = area_oaepr = vao_oaepr = tipo_funduvpr = m2_fundpr = tipo_meivupr = uni_meipr = area_infracomppr = reur_habitantes = pdi_habitantes = un_eiainf = area_eiainf = un_pcainf = area_pcainf = un_rasinf = area_rasinf = un_lacinf = area_lacinf = un_rcainf = area_rcainf = un_pradainf = area_pradainf = un_pmgirsinf = area_pmgirsinf = un_piainf = area_piainf = un_rdoinf = area_rdoinf = un_ddoinf = area_ddoinf = un_ddlinf = area_ddlinf = un_ifpminf = area_ifpminf = un_ifpmedi = area_ifpmedi = un_ddledi = area_ddledi = un_ddoedi = area_ddoedi = un_rdoedi = area_rdoedi = un_piaedi = area_piaedi = un_pmgirsedi = area_pmgirsedi = un_pradaedi = area_pradaedi = un_rcaedi = area_rcaedi = area_lacedi = un_lacedi = area_rasedi = un_rasedi = un_pcaedi = area_pcaedi = area_eiaedi = un_eiaedi = area_aa = area_ac = area_ar = area_are = area_cv = edi_mobpep = area_mo = area_ue = area_paisa = tipo_abupep = area_abu = tipo_me3dpep = area_me3d = area_mt = tipo_fupep = area_fu = tipo_conpep = area_con = area_hds = area_irri = area_spci = area_tps = tipo_toppep = area_top = area_orc = area_ele = area_cets = area_spda = area_cftv = area_extr = area_ilupu = area_arcond = area_venex = area_glp = area_hvac = area_comp = area_acus = area_reurb = area_urvi = area_paisavi = km_anti = km_geo = km_ter = km_dre = km_pav = tipo_pavvu = tipo_subasevu = km_sinal = tipo_topvu = km_top = km_orc = area_infraorc = tipo_contvu = m2_cont = m3_cont = tipo_oaevu = area_oae = vao_oae = tipo_funduv = m2_fund = tipo_meivu = uni_mei = area_infracomp = pmbs_habitantes = None

if "Projeto Edificação" in servico or "Projeto Praças e Parques" in servico:
    tipo_servicos = ["ARQUITETÔNICO ANTEPROJETO", "ARQUITETÔNICO CONSTRUÇÃO", "ARQUITETÔNICO REFORMA", "ARQUITETÔNICO RESTAURO", "COMUNICAÇÃO VISUAL", "MOBILIÁRIO", "URBANISTICO", "AS BUILT", "MAQ ELET / 3D", "ESTRUTURAL", "FUNDAÇÃO", "CONTENÇÃO", "HIDROSANITÁRIO", "IRRIGAÇÃO", "SPCI", "TERRAPLENAGEM (PLANTA/SEÇÕES)","TOPOGRAFIA", "ORÇAMENTO", "ELÉTRICO", "CAB. ESTRUTURADO", "SPDA", "ALARME/CFTV", "EXTENSÃO DE REDE", "ILUMINAÇÃO PUBLICA", "AR CONDICIONADO", "VENTILAÇÃO/EXAUSTÃO", "GLP", "GASES MEDICINAIS", "COMPAT. PROJETOS", "ACÚSTICA", "REURB", "PAISAGISTICO"]
    tipo_servico =  st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

    tp_serv = tipo_servico

    if "ARQUITETÔNICO ANTEPROJETO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nArquitetônico Anteprojeto")
        with d2:
            area_aa = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_aa")
        with d3:
            pranchas_aa = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_aa")

        st.divider()

    if "ARQUITETÔNICO CONSTRUÇÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nArquitetônico Construção")
        with d2:
            area_ac = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ac")
        with d3:
            pranchas_ac = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ac")
        st.divider()

    if "ARQUITETÔNICO REFORMA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nArquitetônico Reforma")
        with d2:
            area_ar = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ar")
        with d3:
            pranchas_ar = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ar")
        st.divider()

    if "ARQUITETÔNICO RESTAURO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nArquitetônico Restauro")
        with d2:
            area_are = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_are")
        with d3:
            pranchas_are = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_are")
        st.divider()

    if "COMUNICAÇÃO VISUAL" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nComunicação Visual")
        with d2:
            area_cv = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cv")
        with d3:
            pranchas_cv = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_cv")
        st.divider()

    if "MOBILIÁRIO" in tipo_servico:
        mobiliario_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Mobiliário")
        with d2:
            tipo_mob = st.multiselect("Tipo", ["Edificação", "Urbano"], key="tipo_mob")

        if tipo_mob:
            colunas = st.columns(min(len(tipo_mob), 3))
            for i, tipo in enumerate(tipo_mob):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área", min_value=0.0, step=1.0, key=f"area_mob_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, format="%0.f",
                                              key=f"prancha_mob_{tipo}")
                    if area > 0 or prancha > 0:
                        mobiliario_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "URBANISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nUrbanístico")
        with d2:
            area_urb = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urb")
        with d3:
            pranchas_urb = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_urb")
        st.divider()

    if "PAISAGISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nPaisagístico")
        with d2:
            area_paisag = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisag")
        with d3:
            pranchas_paisag = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_paisag")
        st.divider()

    if "AS BUILT" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nAs Built")
        with d2:
            tipo_ab = st.selectbox("Tipo", ["C/ Matteport", "S/ Matteport"], key="tipo_ab")
        with d3:
            area_ab = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ab")
        with d4:
            pranchas_ab = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ab")
        st.divider()

    if "MAQ ELET / 3D" in tipo_servico:
        maqelet_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("MAQ ELET / 3D")
        with d2:
            tipo_me3d = st.multiselect("Tipo MAQ ELET / 3D", ["Modelagem 3D", "Maquete Eletrônica"], key="tipo_me3d")

        if tipo_me3d:
            colunas = st.columns(min(len(tipo_me3d), 3))
            for i, tipo in enumerate(tipo_me3d):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área", min_value=0.0, step=1.0, key=f"area_maq_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, format="%0.f",
                                              key=f"prancha_maq_{tipo}")
                    if area > 0 or prancha > 0:
                        maqelet_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "ESTRUTURAL" in tipo_servico:
        estrutural_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Estrutural")
        with d2:
            tipo_estedi = st.multiselect("Tipos Estruturais", ["Concreto", "Madeira", "Metálica"], key="tipo_estedi")

        if tipo_estedi:
            colunas = st.columns(min(len(tipo_estedi), 3))
            for i, tipo in enumerate(tipo_estedi):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área", min_value=0.0, step=1.0, key=f"area_est_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_est_{tipo}",
                                              format="%0.f")
                    if area > 0 or prancha > 0:
                        estrutural_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "FUNDAÇÃO" in tipo_servico:
        fundacao_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Fundação")
        with d2:
            tipo_funedi = st.multiselect("Tipo", ["Rasa(sapata, blocos e radier", "Profunda(estaca, tubulão e caixões",
                                                  "Rasa e Profunda"], key="tipo_funedi")

        if tipo_funedi:
            colunas = st.columns(min(len(tipo_funedi), 3))
            for i, tipo in enumerate(tipo_funedi):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área", min_value=0.0, step=1.0, key=f"area_fun_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, format="%0.f",
                                              key=f"prancha_fun_{tipo}")
                    if area > 0 or prancha > 0:
                        fundacao_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "CONTENÇÃO" in tipo_servico:
        contencao_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Contenção")
        with d2:
            tipo_conpep = st.multiselect("Tipo",
                                         ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"],
                                         key="tipo_conpep")

        if tipo_conpep:
            colunas = st.columns(min(len(tipo_conpep), 5))
            for i, tipo in enumerate(tipo_conpep):
                with colunas[i % 5]:
                    st.markdown(f"**{tipo}**")
                    area_m = st.number_input("Área (m)", min_value=0.0, step=1.0, key=f"area_m_con_{tipo}")
                    area_m2 = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_m2_con_{tipo}")
                    area_m3 = st.number_input("Área (m³)", min_value=0.0, step=1.0, key=f"area_m3_con_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_con_{tipo}",
                                              format="%0.f")
                    if area_m > 0 or area_m2 > 0 or area_m3 > 0 or prancha > 0:
                        contencao_info[tipo] = {
                            "m": area_m,
                            "m²": area_m2,
                            "m³": area_m3,
                            "prancha": prancha
                        }
        st.divider()

    if "HIDROSANITÁRIO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nHidrossanitário")
        with d2:
            area_hds = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_hds")
        with d3:
            prancha_hds = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_hds", format="%0.f")
        st.divider()

    if "IRRIGAÇÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nIrrigação")
        with d2:
            area_irri = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_irri")
        with d3:
            prancha_irri = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_irri", format="%0.f")
        st.divider()

    if "SPCI" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nSPCI")
        with d2:
            area_spci = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_spci")
        with d3:
            prancha_spci = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_spci", format="%0.f")
        st.divider()

    if "TERRAPLENAGEM (PLANTA/SEÇÕES)" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nTerraplenagem (Planta/Seções)")
        with d2:
            area_tps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_tps")
        with d3:
            prancha_tps = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_tps", format="%0.f")
        st.divider()

    if "TOPOGRAFIA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        d4, d5, d6 = st.columns(3)
        with d1:
            st.write("###### \nTopografia")
        with d2:
            tipo_toppep = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria",
                                                "Planialtimétrico georreferenciado",
                                                "Planialtimétrico georreferenciado e aerofotogrametrico",
                                                "Planialtimétrico aerofotogrametrico"], key="tipo_toppep")
        with d3:
            prancha_top = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_top", format="%0.f")
        with d4:
            cadastral = st.selectbox("Cadastral", ["Não", "Sim"])
        with d5:
            drone = st.selectbox("Drone", ["Não", "Sim"])
        with d6:
            area_top = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_top")
        st.divider()

    if "ORÇAMENTO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nOrçamento")
        with d2:
            area_orc = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_orc")
        with d3:
            prancha_orc = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_orc", format="%0.f")
        st.divider()

    if "ELÉTRICO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nElétrico")
        with d2:
            area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
        with d3:
            kva = st.number_input("KVA", min_value=0.0, step=0.1, key="kva")
        with d4:
            prancha_ele = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_ele", format="%0.f")
        st.divider()

    if "CAB. ESTRUTURADO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nCAB. Estruturado")
        with d2:
            area_cets = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cest")
        with d3:
            prancha_cets = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_cest", format="%0.f")
        st.divider()

    if "SPDA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nSPDA")
        with d2:
            area_spda = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_spda")
        with d3:
            prancha_spda = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_spda", format="%0.f")
        st.divider()

    if "ALARME/CFTV" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nAlarme/CFTV")
        with d2:
            area_cftv = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cftv")
        with d3:
            prancha_cftv = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_cftv", format="%0.f")
        st.divider()

    if "EXTENSÃO DE REDE" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nExtensão de Rede")
        with d2:
            area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")
        with d3:
            prancha_extr = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_extr", format="%0.f")
        st.divider()

    if "ILUMINAÇÃO PUBLICA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nIluminação Pública")
        with d2:
            area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")
        with d3:
            prancha_ilupu = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_ilupu", format="%0.f")
        st.divider()

    if "AR CONDICIONADO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nAr Condicionado")
        with d2:
            area_arcond = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_arcond")
        with d3:
            prancha_arcond = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_arcond", format="%0.f")
        st.divider()

    if "VENTILAÇÃO/EXAUSTÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nVentilação/Exaustão")
        with d2:
            area_venex = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_venex")
        with d3:
            prancha_venex = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_venex", format="%0.f")
        st.divider()

    if "GLP" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nGLP")
        with d2:
            area_glp = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_glp")
        with d3:
            prancha_glp = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_glp", format="%0.f")
        st.divider()

    if "GASES MEDICINAIS" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nGases Medicinais")
        with d2:
            area_hvac = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_hvac")
        with d3:
            prancha_hvac = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_hvac", format="%0.f")
        st.divider()

    if "COMPAT. PROJETOS" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nCompat. Projetos")
        with d2:
            area_comp = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_comp")
        with d3:
            prancha_comp = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_comp", format="%0.f")
        st.divider()

    if "ACÚSTICA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nAcústica")
        with d2:
            area_acus = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_acus")
        with d3:
            prancha_acus = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_acus", format="%0.f")
        st.divider()

    if "REURB" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nREURB")
        with d2:
            area_reurb = st.number_input("Un. Habitacionais", min_value=0.0, step=1.0, key="area_reurb", format="%0.f")
        with d3:
            prancha_reurb = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_reurb", format="%0.f")
        st.divider()

if "Supervisão Gerenciamento Edificação" in servico:

    tipo_servicos = ["ARQUITETÔNICO ANTEPROJETO", "ARQUITETÔNICO CONSTRUÇÃO", "ARQUITETÔNICO REFORMA",
                     "ARQUITETÔNICO RESTAURO", "COMUNICAÇÃO VISUAL", "MOBILIÁRIO", "URBANISTICO", "AS BUILT",
                     "MAQ ELET / 3D", "ESTRUTURAL", "FUNDAÇÃO", "CONTENÇÃO", "HIDROSANITÁRIO", "IRRIGAÇÃO", "SPCI",
                     "TERRAPLENAGEM (PLANTA/SEÇÕES)", "TOPOGRAFIA", "ORÇAMENTO", "ELÉTRICO", "CAB. ESTRUTURADO",
                     "SPDA", "ALARME/CFTV", "EXTENSÃO DE REDE", "ILUMINAÇÃO PUBLICA", "AR CONDICIONADO",
                     "VENTILAÇÃO/EXAUSTÃO", "GLP", "GASES MEDICINAIS", "COMPAT. PROJETOS", "ACÚSTICA", "REURB",
                     "PAISAGISTICO"]
    tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

    tp_serv = tipo_servico

    if "ARQUITETÔNICO ANTEPROJETO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nArquitetônico Anteprojeto")
        with d2:
            area_aa = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_aa")
        with d3:
            pranchas_aa = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_aa")

        st.divider()

    if "ARQUITETÔNICO CONSTRUÇÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nArquitetônico Construção")
        with d2:
            area_ac = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ac")
        with d3:
            pranchas_ac = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ac")
        st.divider()

    if "ARQUITETÔNICO REFORMA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nArquitetônico Reforma")
        with d2:
            area_ar = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ar")
        with d3:
            pranchas_ar = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ar")
        st.divider()

    if "ARQUITETÔNICO RESTAURO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nArquitetônico Restauro")
        with d2:
            area_are = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_are")
        with d3:
            pranchas_are = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_are")
        st.divider()

    if "COMUNICAÇÃO VISUAL" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nComunicação Visual")
        with d2:
            area_cv = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cv")
        with d3:
            pranchas_cv = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_cv")
        st.divider()

    if "MOBILIÁRIO" in tipo_servico:
        mobiliario_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Mobiliário")
        with d2:
            tipo_mob = st.multiselect("Tipo", ["Edificação", "Urbano"], key="tipo_mob")

        if tipo_mob:
            colunas = st.columns(min(len(tipo_mob), 3))
            for i, tipo in enumerate(tipo_mob):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área", min_value=0.0, step=1.0, key=f"area_mob_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, format="%0.f",
                                              key=f"prancha_mob_{tipo}")
                    if area > 0 or prancha > 0:
                        mobiliario_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "URBANISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nUrbanístico")
        with d2:
            area_urb = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urb")
        with d3:
            pranchas_urb = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_urb")
        st.divider()

    if "PAISAGISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nPaisagístico")
        with d2:
            area_paisag = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisag")
        with d3:
            pranchas_paisag = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_paisag")
        st.divider()

    if "AS BUILT" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nAs Built")
        with d2:
            tipo_ab = st.selectbox("Tipo", ["C/ Matteport", "S/ Matteport"], key="tipo_ab")
        with d3:
            area_ab = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ab")
        with d4:
            pranchas_ab = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ab")
        st.divider()

    if "MAQ ELET / 3D" in tipo_servico:
        maqelet_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("MAQ ELET / 3D")
        with d2:
            tipo_me3d = st.multiselect("Tipo MAQ ELET / 3D", ["Modelagem 3D", "Maquete Eletrônica"], key="tipo_me3d")

        if tipo_me3d:
            colunas = st.columns(min(len(tipo_me3d), 3))
            for i, tipo in enumerate(tipo_me3d):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área", min_value=0.0, step=1.0, key=f"area_maq_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, format="%0.f",
                                              key=f"prancha_maq_{tipo}")
                    if area > 0 or prancha > 0:
                        maqelet_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "ESTRUTURAL" in tipo_servico:
        estrutural_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Estrutural")
        with d2:
            tipo_estedi = st.multiselect("Tipos Estruturais", ["Concreto", "Madeira", "Metálica"], key="tipo_estedi")

        if tipo_estedi:
            colunas = st.columns(min(len(tipo_estedi), 3))
            for i, tipo in enumerate(tipo_estedi):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área", min_value=0.0, step=1.0, key=f"area_est_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_est_{tipo}",
                                              format="%0.f")
                    if area > 0 or prancha > 0:
                        estrutural_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "FUNDAÇÃO" in tipo_servico:
        fundacao_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Fundação")
        with d2:
            tipo_funedi = st.multiselect("Tipo", ["Rasa(sapata, blocos e radier", "Profunda(estaca, tubulão e caixões",
                                                  "Rasa e Profunda"], key="tipo_funedi")

        if tipo_funedi:
            colunas = st.columns(min(len(tipo_funedi), 3))
            for i, tipo in enumerate(tipo_funedi):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área", min_value=0.0, step=1.0, key=f"area_fun_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, format="%0.f",
                                              key=f"prancha_fun_{tipo}")
                    if area > 0 or prancha > 0:
                        fundacao_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "CONTENÇÃO" in tipo_servico:
        contencao_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Contenção")
        with d2:
            tipo_conpep = st.multiselect("Tipo",
                                         ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"],
                                         key="tipo_conpep")

        if tipo_conpep:
            colunas = st.columns(min(len(tipo_conpep), 5))
            for i, tipo in enumerate(tipo_conpep):
                with colunas[i % 5]:
                    st.markdown(f"**{tipo}**")
                    area_m = st.number_input("Área (m)", min_value=0.0, step=1.0, key=f"area_m_con_{tipo}")
                    area_m2 = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_m2_con_{tipo}")
                    area_m3 = st.number_input("Área (m³)", min_value=0.0, step=1.0, key=f"area_m3_con_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_con_{tipo}",
                                              format="%0.f")
                    if area_m > 0 or area_m2 > 0 or area_m3 > 0 or prancha > 0:
                        contencao_info[tipo] = {
                            "m": area_m,
                            "m²": area_m2,
                            "m³": area_m3,
                            "prancha": prancha
                        }
        st.divider()

    if "HIDROSANITÁRIO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nHidrossanitário")
        with d2:
            area_hds = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_hds")
        with d3:
            prancha_hds = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_hds", format="%0.f")
        st.divider()

    if "IRRIGAÇÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nIrrigação")
        with d2:
            area_irri = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_irri")
        with d3:
            prancha_irri = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_irri", format="%0.f")
        st.divider()

    if "SPCI" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nSPCI")
        with d2:
            area_spci = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_spci")
        with d3:
            prancha_spci = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_spci", format="%0.f")
        st.divider()

    if "TERRAPLENAGEM (PLANTA/SEÇÕES)" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nTerraplenagem (Planta/Seções)")
        with d2:
            area_tps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_tps")
        with d3:
            prancha_tps = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_tps", format="%0.f")
        st.divider()

    if "TOPOGRAFIA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        d4, d5, d6 = st.columns(3)
        with d1:
            st.write("###### \nTopografia")
        with d2:
            tipo_toppep = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria",
                                                "Planialtimétrico georreferenciado",
                                                "Planialtimétrico georreferenciado e aerofotogrametrico",
                                                "Planialtimétrico aerofotogrametrico"], key="tipo_toppep")
        with d3:
            prancha_top = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_top", format="%0.f")
        with d4:
            cadastral = st.selectbox("Cadastral", ["Não", "Sim"])
        with d5:
            drone = st.selectbox("Drone", ["Não", "Sim"])
        with d6:
            area_top = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_top")
        st.divider()

    if "ORÇAMENTO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nOrçamento")
        with d2:
            area_orc = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_orc")
        with d3:
            prancha_orc = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_orc", format="%0.f")
        st.divider()

    if "ELÉTRICO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nElétrico")
        with d2:
            area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
        with d3:
            kva = st.number_input("KVA", min_value=0.0, step=0.1, key="kva")
        with d4:
            prancha_ele = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_ele", format="%0.f")
        st.divider()

    if "CAB. ESTRUTURADO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nCAB. Estruturado")
        with d2:
            area_cets = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cest")
        with d3:
            prancha_cets = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_cest", format="%0.f")
        st.divider()

    if "SPDA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nSPDA")
        with d2:
            area_spda = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_spda")
        with d3:
            prancha_spda = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_spda", format="%0.f")
        st.divider()

    if "ALARME/CFTV" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nAlarme/CFTV")
        with d2:
            area_cftv = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cftv")
        with d3:
            prancha_cftv = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_cftv", format="%0.f")
        st.divider()

    if "EXTENSÃO DE REDE" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nExtensão de Rede")
        with d2:
            area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")
        with d3:
            prancha_extr = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_extr", format="%0.f")
        st.divider()

    if "ILUMINAÇÃO PUBLICA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nIluminação Pública")
        with d2:
            area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")
        with d3:
            prancha_ilupu = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_ilupu", format="%0.f")
        st.divider()

    if "AR CONDICIONADO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nAr Condicionado")
        with d2:
            area_arcond = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_arcond")
        with d3:
            prancha_arcond = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_arcond", format="%0.f")
        st.divider()

    if "VENTILAÇÃO/EXAUSTÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nVentilação/Exaustão")
        with d2:
            area_venex = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_venex")
        with d3:
            prancha_venex = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_venex", format="%0.f")
        st.divider()

    if "GLP" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nGLP")
        with d2:
            area_glp = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_glp")
        with d3:
            prancha_glp = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_glp", format="%0.f")
        st.divider()

    if "GASES MEDICINAIS" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nGases Medicinais")
        with d2:
            area_hvac = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_hvac")
        with d3:
            prancha_hvac = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_hvac", format="%0.f")
        st.divider()

    if "COMPAT. PROJETOS" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nCompat. Projetos")
        with d2:
            area_comp = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_comp")
        with d3:
            prancha_comp = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_comp", format="%0.f")
        st.divider()

    if "ACÚSTICA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nAcústica")
        with d2:
            area_acus = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_acus")
        with d3:
            prancha_acus = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_acus", format="%0.f")
        st.divider()

    if "REURB" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nREURB")
        with d2:
            area_reurb = st.number_input("Un. Habitacionais", min_value=0.0, step=1.0, key="area_reurb", format="%0.f")
        with d3:
            prancha_reurb = st.number_input("Prancha", min_value=0.0, step=1.0, key="prancha_reurb", format="%0.f")
        st.divider()

if "Projeto Vias Urbanas" in servico:
    tipo_servicos = ["URBANISTICO", "PAISAGISTICO", "ANTEPROJETO DE INFRA", "GEOMÉTRICO", "TERRAPLENAGEM", "HIDROLOGIA", "DRENAGEM", "PAVIMENTAÇÃO", "ESTRUTURAL", "SINALIZAÇÃO", "TOPOGRAFIA", "ORÇAMENTO", "CONTENÇÃO", "OAE", "FUNDAÇÃO", "MEIO AMBIENTE", "COMPAT. PROJETOS", "ELÉTRICO", "EXTENSÃO DE REDE", "ILUMINAÇÃO PUBLICA"]
    tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

    if "URBANISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nUrbanístico""")
        with d2:
            area_urvi = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urvi")
        with d3:
            prancha_urvi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_urvi")
        st.divider()

    if "PAISAGISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nPaisagístico""")
        with d2:
            area_paisavi = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisavi")
        with d3:
            prancha_paisavi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_paisavi")
        st.divider()

    if "ANTEPROJETO DE INFRA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nAnteprojeto de Infra""")
        with d2:
            km_anti = st.number_input("KM", min_value=0.0, step=1.0, key="km_anti")
        with d3:
            prancha_anti = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_anti")
        st.divider()

    if "GEOMÉTRICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nGeométrico""")
        with d2:
            km_geo = st.number_input("KM", min_value=0.0, step=1.0, key="km_geo")
        with d3:
            prancha_geo = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_geo")
        st.divider()

    if "TERRAPLENAGEM" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nTerraplenagem""")
        with d2:
            km_ter = st.number_input("KM", min_value=0.0, step=1.0, key="km_ter")
        with d3:
            prancha_ter = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ter")
        st.divider()

    if "DRENAGEM" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nDrenagem""")
        with d2:
            km_dre = st.number_input("KM", min_value=0.0, step=1.0, key="km_dre")
        with d3:
            prancha_dre = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_dre")
        st.divider()

    if "ESTRUTURAL" in tipo_servico:
        vu_estrutural_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Estrutural")
        with d2:
            tipo_estpep = st.multiselect("Tipos Estruturais", ["Concreto", "Madeira", "Metálica"], key="tipo_estpep")

        if tipo_estpep:
            colunas = st.columns(min(len(tipo_estpep), 3))
            for i, tipo in enumerate(tipo_estpep):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_est_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_est_{tipo}", format="%0.f")
                    if area > 0 or prancha > 0:
                        vu_estrutural_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "PAVIMENTAÇÃO" in tipo_servico:
        vu_pavimentacao_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Pavimentação")
        with d2:
            tipo_pavvu = st.multiselect("Tipo", ["Não informa", "CBUQ", "CONCRETO", "TSD"], key="tipo_pavvu")

        if tipo_pavvu:
            colunas = st.columns(min(len(tipo_pavvu), 3))
            for i, tipo in enumerate(tipo_pavvu):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    km_pav = st.number_input("KM", min_value=0.0, step=1.0, key=f"km_pav_{tipo}")
                    m_pav = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"m_pav_{tipo}")
                    prancha_pav = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_pav_{tipo}",
                                                  format="%0.f")
                    if km_pav > 0 or m_pav > 0 or prancha_pav > 0:
                        vu_pavimentacao_info[tipo] = {"km": km_pav, "m²": m_pav, "prancha": prancha_pav}
        st.divider()

    if "SINALIZAÇÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nSinalização""")
        with d2:
            km_sinal = st.number_input("KM", min_value=0.0, step=1.0, key="km_sinal")
        with d3:
            prancha_sinal = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_sinal")
        st.divider()

    if "TOPOGRAFIA" in tipo_servico:
        vu_topografia_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Topografia")
        with d2:
            tipo_topvu = st.multiselect("Tipo", [
                "Planialtimétrico",
                "Georreferenciado",
                "Aerofotogrametria",
                "Planialtimétrico georreferenciado",
                "Planialtimétrico georreferenciado e aerofotogrametrico",
                "Planialtimétrico aerofotogrametrico"
            ], key="tipo_topvu")

        if tipo_topvu:
            colunas = st.columns(min(len(tipo_topvu), 3))
            for i, tipo in enumerate(tipo_topvu):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    cadastral_top = st.selectbox(f"Cadastral ({tipo})", ["Não", "Sim"], key=f"cadastral_top_{tipo}")
                    km_top = st.number_input("KM", min_value=0.0, step=1.0, key=f"km_top_{tipo}")
                    area_top = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_top_{tipo}")
                    prancha_top = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_top_{tipo}",
                                                  format="%0.f")
                    if km_top > 0 or area_top > 0 or prancha_top > 0:
                        vu_topografia_info[tipo] = {
                            "cadastral": cadastral_top,
                            "km": km_top,
                            "área": area_top,
                            "prancha": prancha_top
                        }
        st.divider()

    if "ORÇAMENTO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("""###### \nOrçamento""")
        with d2:
            km_orc = st.number_input("KM", min_value=0.0, step=1.0, key="km_orc")
        with d3:
            area_infraorc = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_infraorc")
        with d4:
            prancha_orc = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_orc")
        st.divider()

    if "CONTENÇÃO" in tipo_servico:
        vu_contencao_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Contenção")
        with d2:
            tipo_contvu = st.multiselect("Tipo",
                                         ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"],
                                         key="tipo_contvu")

        if tipo_contvu:
            colunas = st.columns(min(len(tipo_contvu), 5))
            for i, tipo in enumerate(tipo_contvu):
                with colunas[i % 5]:
                    st.markdown(f"**{tipo}**")
                    m_cont = st.number_input("M", min_value=0.0, step=1.0, key=f"m_cont_{tipo}")
                    m2_cont = st.number_input("M²", min_value=0.0, step=0.1, key=f"m2_cont_{tipo}")
                    m3_cont = st.number_input("M³", min_value=0.0, step=0.1, key=f"m3_cont_{tipo}")
                    prancha_cont = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_cont_{tipo}",
                                                   format="%0.f")
                    if m_cont > 0 or m2_cont > 0 or m3_cont > 0 or prancha_cont > 0:
                        vu_contencao_info[tipo] = {
                            "m": m_cont,
                            "m²": m2_cont,
                            "m³": m3_cont,
                            "prancha": prancha_cont
                        }
        st.divider()

    if "OAE" in tipo_servico:
        vu_oae_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("OAE")
        with d2:
            tipo_oaevu = st.multiselect("Tipo", ["Laudo", "Concreto armado", "Concreto protendido", "Balanço sucessivo",
                                                 "Ponte estaiada", "Ponte mista"], key="tipo_oaevu")

        if tipo_oaevu:
            colunas = st.columns(min(len(tipo_oaevu), 3))
            for i, tipo in enumerate(tipo_oaevu):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area_oae = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_oae_{tipo}")
                    vao_oae = st.number_input("Vão (m)", min_value=0.0, step=0.1, key=f"vao_oae_{tipo}")
                    prancha_oae = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_oae_{tipo}",
                                                  format="%0.f")
                    if area_oae > 0 or vao_oae > 0 or prancha_oae > 0:
                        vu_oae_info[tipo] = {"área": area_oae, "vão": vao_oae, "prancha": prancha_oae}
        st.divider()

    if "FUNDAÇÃO" in tipo_servico:
        vu_fundacao_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Fundação")
        with d2:
            tipo_fundvu = st.multiselect("Tipo", ["Rasa(sapata, blocos e radier)", "Profunda(estaca, tubulão, caixões)",
                                                  "Rasa e Profunda"], key="tipo_fundvu")

        if tipo_fundvu:
            colunas = st.columns(min(len(tipo_fundvu), 3))
            for i, tipo in enumerate(tipo_fundvu):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    m2_fund = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"m2_fund_{tipo}")
                    prancha_fund = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_fund_{tipo}",
                                                   format="%0.f")
                    if m2_fund > 0 or prancha_fund > 0:
                        vu_fundacao_info[tipo] = {"m²": m2_fund, "prancha": prancha_fund}
        st.divider()

    if "MEIO AMBIENTE" in tipo_servico:
        vu_meioambiente_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Meio Ambiente")
        with d2:
            tipo_meivu = st.multiselect(
                "Tipo",
                ["EIA/RIMA", "RCA/PCA", "RCA", "PCA", "RADA", "PRADA", "Inventário Florestal"],
                key="tipo_meivu"
            )

        if tipo_meivu:
            colunas = st.columns(min(len(tipo_meivu), 3))
            for i, tipo in enumerate(tipo_meivu):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    unidade_mei = st.number_input(
                        "Unidade",
                        min_value=0,
                        step=1,
                        key=f"unidade_mei_{tipo}"
                    )
                    prancha_mei = st.number_input(
                        "Prancha",
                        min_value=0,
                        step=1,
                        key=f"prancha_mei_{tipo}"
                    )
                    if unidade_mei > 0 or prancha_mei > 0:
                        vu_meioambiente_info[tipo] = {
                            "unidade": unidade_mei,
                            "prancha": prancha_mei
                        }
        st.divider()

    if "COMPAT. PROJETOS" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nCompat. Projetos""")
        with d2:
            area_infracomp = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_infracomp")
        with d3:
            prancha_infracomp = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_infracomp")
        st.divider()

    if "ELÉTRICO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("""###### \nElétrico""")
        with d2:
            area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
        with d3:
            kva_vu = st.number_input("KVA", min_value=0.0, step=0.1, key="kva_vu")
        with d4:
            prancha_ele = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ele")
        st.divider()

    if "EXTENSÃO DE REDE" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nExtensão de Rede""")
        with d2:
            area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")
        with d3:
            prancha_extr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_extr")
        st.divider()

    if "ILUMINAÇÃO PUBLICA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nIluminação Pública""")
        with d2:
            area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu", format="%0.f")
        with d3:
            prancha_ilupu = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ilupu")
        st.divider()

if "Supervisão Gerenciamento Vias Urbanas" in servico:
    tipo_servicos = ["URBANISTICO", "PAISAGISTICO", "ANTEPROJETO DE INFRA", "GEOMÉTRICO", "TERRAPLENAGEM",
                     "HIDROLOGIA", "DRENAGEM", "ESTRUTURAL", "PAVIMENTAÇÃO", "SINALIZAÇÃO", "TOPOGRAFIA", "ORÇAMENTO",
                     "CONTENÇÃO", "OAE", "FUNDAÇÃO", "MEIO AMBIENTE", "COMPAT. PROJETOS", "ILUMINAÇÃO PUBLICA", "EXTENSÃO DE REDE", "ELÉTRICO"]
    tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

    if "URBANISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nUrbanístico""")
        with d2:
            area_urvi = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urvi")
        with d3:
            prancha_urvi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_urvi")
        st.divider()

    if "PAISAGISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nPaisagístico""")
        with d2:
            area_paisavi = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisavi")
        with d3:
            prancha_paisavi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_paisavi")
        st.divider()

    if "ANTEPROJETO DE INFRA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nAnteprojeto de Infra""")
        with d2:
            km_anti = st.number_input("KM", min_value=0.0, step=1.0, key="km_anti")
        with d3:
            prancha_anti = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_anti")
        st.divider()

    if "GEOMÉTRICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nGeométrico""")
        with d2:
            km_geo = st.number_input("KM", min_value=0.0, step=1.0, key="km_geo")
        with d3:
            prancha_geo = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_geo")
        st.divider()

    if "TERRAPLENAGEM" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nTerraplenagem""")
        with d2:
            km_ter = st.number_input("KM", min_value=0.0, step=1.0, key="km_ter")
        with d3:
            prancha_ter = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ter")
        st.divider()

    if "DRENAGEM" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nDrenagem""")
        with d2:
            km_dre = st.number_input("KM", min_value=0.0, step=1.0, key="km_dre")
        with d3:
            prancha_dre = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_dre")
        st.divider()

    if "ESTRUTURAL" in tipo_servico:
        vu_estrutural_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Estrutural")
        with d2:
            tipo_estpep = st.multiselect("Tipos Estruturais", ["Concreto", "Madeira", "Metálica"], key="tipo_estpep")

        if tipo_estpep:
            colunas = st.columns(min(len(tipo_estpep), 3))
            for i, tipo in enumerate(tipo_estpep):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_est_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_est_{tipo}",
                                              format="%0.f")
                    if area > 0 or prancha > 0:
                        vu_estrutural_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "PAVIMENTAÇÃO" in tipo_servico:
        vu_pavimentacao_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Pavimentação")
        with d2:
            tipo_pavvu = st.multiselect("Tipo", ["Não informa", "CBUQ", "CONCRETO", "TSD"], key="tipo_pavvu")

        if tipo_pavvu:
            colunas = st.columns(min(len(tipo_pavvu), 3))
            for i, tipo in enumerate(tipo_pavvu):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    km_pav = st.number_input("KM", min_value=0.0, step=1.0, key=f"km_pav_{tipo}")
                    m_pav = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"m_pav_{tipo}")
                    prancha_pav = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_pav_{tipo}",
                                                  format="%0.f")
                    if km_pav > 0 or m_pav > 0 or prancha_pav > 0:
                        vu_pavimentacao_info[tipo] = {"km": km_pav, "m²": m_pav, "prancha": prancha_pav}
        st.divider()

    if "SINALIZAÇÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nSinalização""")
        with d2:
            km_sinal = st.number_input("KM", min_value=0.0, step=1.0, key="km_sinal")
        with d3:
            prancha_sinal = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_sinal")
        st.divider()

    if "TOPOGRAFIA" in tipo_servico:
        vu_topografia_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Topografia")
        with d2:
            tipo_topvu = st.multiselect("Tipo", [
                "Planialtimétrico",
                "Georreferenciado",
                "Aerofotogrametria",
                "Planialtimétrico georreferenciado",
                "Planialtimétrico georreferenciado e aerofotogrametrico",
                "Planialtimétrico aerofotogrametrico"
            ], key="tipo_topvu")

        if tipo_topvu:
            colunas = st.columns(min(len(tipo_topvu), 3))
            for i, tipo in enumerate(tipo_topvu):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    cadastral_top = st.selectbox(f"Cadastral ({tipo})", ["Não", "Sim"], key=f"cadastral_top_{tipo}")
                    km_top = st.number_input("KM", min_value=0.0, step=1.0, key=f"km_top_{tipo}")
                    area_top = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_top_{tipo}")
                    prancha_top = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_top_{tipo}",
                                                  format="%0.f")
                    if km_top > 0 or area_top > 0 or prancha_top > 0:
                        vu_topografia_info[tipo] = {
                            "cadastral": cadastral_top,
                            "km": km_top,
                            "área": area_top,
                            "prancha": prancha_top
                        }
        st.divider()

    if "ORÇAMENTO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("""###### \nOrçamento""")
        with d2:
            km_orc = st.number_input("KM", min_value=0.0, step=1.0, key="km_orc")
        with d3:
            area_infraorc = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_infraorc")
        with d4:
            prancha_orc = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_orc")
        st.divider()

    if "CONTENÇÃO" in tipo_servico:
        vu_contencao_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Contenção")
        with d2:
            tipo_contvu = st.multiselect("Tipo",
                                         ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"],
                                         key="tipo_contvu")

        if tipo_contvu:
            colunas = st.columns(min(len(tipo_contvu), 5))
            for i, tipo in enumerate(tipo_contvu):
                with colunas[i % 5]:
                    st.markdown(f"**{tipo}**")
                    m_cont = st.number_input("M", min_value=0.0, step=1.0, key=f"m_cont_{tipo}")
                    m2_cont = st.number_input("M²", min_value=0.0, step=0.1, key=f"m2_cont_{tipo}")
                    m3_cont = st.number_input("M³", min_value=0.0, step=0.1, key=f"m3_cont_{tipo}")
                    prancha_cont = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_cont_{tipo}",
                                                   format="%0.f")
                    if m_cont > 0 or m2_cont > 0 or m3_cont > 0 or prancha_cont > 0:
                        vu_contencao_info[tipo] = {
                            "m": m_cont,
                            "m²": m2_cont,
                            "m³": m3_cont,
                            "prancha": prancha_cont
                        }
        st.divider()

    if "OAE" in tipo_servico:
        vu_oae_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("OAE")
        with d2:
            tipo_oaevu = st.multiselect("Tipo", ["Laudo", "Concreto armado", "Concreto protendido", "Balanço sucessivo",
                                                 "Ponte estaiada", "Ponte mista"], key="tipo_oaevu")

        if tipo_oaevu:
            colunas = st.columns(min(len(tipo_oaevu), 3))
            for i, tipo in enumerate(tipo_oaevu):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area_oae = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_oae_{tipo}")
                    vao_oae = st.number_input("Vão (m)", min_value=0.0, step=0.1, key=f"vao_oae_{tipo}")
                    prancha_oae = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_oae_{tipo}",
                                                  format="%0.f")
                    if area_oae > 0 or vao_oae > 0 or prancha_oae > 0:
                        vu_oae_info[tipo] = {"área": area_oae, "vão": vao_oae, "prancha": prancha_oae}
        st.divider()

    if "FUNDAÇÃO" in tipo_servico:
        vu_fundacao_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Fundação")
        with d2:
            tipo_fundvu = st.multiselect("Tipo", ["Rasa(sapata, blocos e radier)", "Profunda(estaca, tubulão, caixões)",
                                                  "Rasa e Profunda"], key="tipo_fundvu")

        if tipo_fundvu:
            colunas = st.columns(min(len(tipo_fundvu), 3))
            for i, tipo in enumerate(tipo_fundvu):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    m2_fund = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"m2_fund_{tipo}")
                    prancha_fund = st.number_input("Prancha", min_value=0.0, step=1.0, key=f"prancha_fund_{tipo}",
                                                   format="%0.f")
                    if m2_fund > 0 or prancha_fund > 0:
                        vu_fundacao_info[tipo] = {"m²": m2_fund, "prancha": prancha_fund}
        st.divider()

    if "MEIO AMBIENTE" in tipo_servico:
        vu_meioambiente_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Meio Ambiente")
        with d2:
            tipo_meivu = st.multiselect(
                "Tipo",
                ["EIA/RIMA", "RCA/PCA", "RCA", "PCA", "RADA", "PRADA", "Inventário Florestal"],
                key="tipo_meivu"
            )

        if tipo_meivu:
            colunas = st.columns(min(len(tipo_meivu), 3))
            for i, tipo in enumerate(tipo_meivu):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    unidade_mei = st.number_input(
                        "Unidade",
                        min_value=0,
                        step=1,
                        key=f"unidade_mei_{tipo}"
                    )
                    prancha_mei = st.number_input(
                        "Prancha",
                        min_value=0,
                        step=1,
                        key=f"prancha_mei_{tipo}"
                    )
                    if unidade_mei > 0 or prancha_mei > 0:
                        vu_meioambiente_info[tipo] = {
                            "unidade": unidade_mei,
                            "prancha": prancha_mei
                        }
        st.divider()

    if "COMPAT. PROJETOS" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nCompat. Projetos""")
        with d2:
            area_infracomp = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_infracomp")
        with d3:
            prancha_infracomp = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_infracomp")
        st.divider()

    if "ELÉTRICO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("""###### \nElétrico""")
        with d2:
            area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
        with d3:
            kva_vu = st.number_input("KVA", min_value=0.0, step=0.1, key="kva_vu")
        with d4:
            prancha_ele = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ele")
        st.divider()

    if "EXTENSÃO DE REDE" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nExtensão de Rede""")
        with d2:
            area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")
        with d3:
            prancha_extr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_extr")
        st.divider()

    if "ILUMINAÇÃO PUBLICA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("""###### \nIluminação Pública""")
        with d2:
            area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu", format="%0.f")
        with d3:
            prancha_ilupu = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ilupu")
        st.divider()

if "Projeto Rodovias" in servico:
    tipo_servicos = ["URBANISTICO", "PAISAGISTICO", "ANTEPROJETO DE INFRA", "GEOMÉTRICO", "TERRAPLENAGEM", "HIDROLOGIA", "DRENAGEM", "ESTRUTURAL", "PAVIMENTAÇÃO", "SINALIZAÇÃO", "TOPOGRAFIA", "ORÇAMENTO", "CONTENÇÃO", "OAE", "FUNDAÇÃO", "MEIO AMBIENTE", "COMPAT. PROJETOS", "ELÉTRICO", "ILUMINAÇÃO PUBLICA", "EXTENSÃO DE REDE"]
    tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

    if "URBANISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nUrbanístico")
        with d2:
            area_urpr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urpr")
        with d3:
            prancha_urpr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_urpr")
        st.divider()

    if "PAISAGISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nPaisagístico")
        with d2:
            area_paisapr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisapr")
        with d3:
            prancha_paisapr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_paisapr")
        st.divider()

    if "ANTEPROJETO DE INFRA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nAnteprojeto de Infra")
        with d2:
            km_antipr = st.number_input("KM", min_value=0.0, step=1.0, key="km_antipr")
        with d3:
            prancha_antipr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_antipr")
        st.divider()

    if "GEOMÉTRICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nGeométrico")
        with d2:
            km_geopr = st.number_input("KM", min_value=0.0, step=1.0, key="km_geopr")
        with d3:
            prancha_geopr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_geopr")
        st.divider()

    if "TERRAPLENAGEM" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nTerraplenagem")
        with d2:
            km_terpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_terpr")
        with d3:
            prancha_terpr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_terpr")
        st.divider()

    if "DRENAGEM" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nDrenagem")
        with d2:
            km_drepr = st.number_input("KM", min_value=0.0, step=1.0, key="km_drepr")
        with d3:
            prancha_drepr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_drepr")
        st.divider()

    if "ESTRUTURAL" in tipo_servico:
        estruturalpr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Estrutural")
        with d2:
            tipo_estpep = st.multiselect("Tipos Estruturais", ["Concreto", "Madeira", "Metálica"], key="tipo_estpep")

        if tipo_estpep:
            colunas = st.columns(min(len(tipo_estpep), 3))
            for i, tipo in enumerate(tipo_estpep):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area_est = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_est_{tipo}")
                    prancha_est = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_est_{tipo}")
                    if area_est > 0 or prancha_est > 0:
                        estruturalpr_info[tipo] = {
                            "área": area_est,
                            "prancha": prancha_est
                        }
        st.divider()

    if "PAVIMENTAÇÃO" in tipo_servico:
        pavimentacaopr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Pavimentação")
        with d2:
            tipo_pavpr = st.multiselect("Tipo de Pavimentação", ["CBUQ", "CONCRETO", "TSD"], key="tipo_pavpr")

        if tipo_pavpr:
            colunas = st.columns(min(len(tipo_pavpr), 3))
            for i, tipo in enumerate(tipo_pavpr):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    km_pavpr = st.number_input("KM", min_value=0.0, step=1.0, key=f"km_pavpr_{tipo}")
                    m_pavpr = st.number_input("M²", min_value=0.0, step=0.1, key=f"m2_pavpr_{tipo}")
                    prancha_pavpr = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_pavpr_{tipo}")
                    if km_pavpr > 0 or m_pavpr > 0 or prancha_pavpr > 0:
                        pavimentacaopr_info[tipo] = {
                            "km": km_pavpr,
                            "m²": m_pavpr,
                            "prancha": prancha_pavpr
                        }
        st.divider()

    if "SINALIZAÇÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nSinalização")
        with d2:
            km_sinalpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_sinalpr")
        with d3:
            prancha_sinalpr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_sinalpr")
        st.divider()

    if "TOPOGRAFIA" in tipo_servico:
        d1, d2, d3, d4, d5, d6 = st.columns(6)
        with d1:
            st.write("###### \nTopografia")
        with d2:
            tipo_toppr = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerofotogrametria",
                                               "Planialtimétrico georreferenciado",
                                               "Planialtimétrico georreferenciado e aerofotogrametrico",
                                               "Planialtimétrico aerofotogrametrico"], key="tipo_toppr")
        with d3:
            cadastral_toppr = st.selectbox("Cadastral", ["Não", "Sim"], key="cadastral_toppr")
        with d4:
            km_toppr = st.number_input("KM", min_value=0.0, step=1.0, key="km_toppr")
        with d5:
            area_toppr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_toppr")
        with d6:
            prancha_toppr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_toppr")
        st.divider()

    if "ORÇAMENTO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nOrçamento")
        with d2:
            km_orcpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_orcpr")
        with d3:
            area_infraorcpr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_infraorcpr")
        with d4:
            prancha_orcpr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_orcpr")
        st.divider()

    if "CONTENÇÃO" in tipo_servico:
        contencaopr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Contenção")
        with d2:
            tipo_contpr = st.multiselect("Tipo de Contenção",
                                         ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"],
                                         key="tipo_contpr")

        if tipo_contpr:
            colunas = st.columns(min(len(tipo_contpr), 5))
            for i, tipo in enumerate(tipo_contpr):
                with colunas[i % 5]:
                    st.markdown(f"**{tipo}**")
                    m_contpr = st.number_input("M", min_value=0.0, step=1.0, key=f"m_contpr_{tipo}")
                    m2_contpr = st.number_input("M²", min_value=0.0, step=0.1, key=f"m2_contpr_{tipo}")
                    m3_contpr = st.number_input("M³", min_value=0.0, step=0.1, key=f"m3_contpr_{tipo}")
                    prancha_contpr = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_contpr_{tipo}")
                    if m_contpr > 0 or m2_contpr > 0 or m3_contpr > 0 or prancha_contpr > 0:
                        contencaopr_info[tipo] = {
                            "m": m_contpr,
                            "m²": m2_contpr,
                            "m³": m3_contpr,
                            "prancha": prancha_contpr
                        }
        st.divider()

    if "OAE" in tipo_servico:
        oaepr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("OAE")
        with d2:
            tipo_oaevupr = st.multiselect("Tipo de OAE",
                                          ["Laudo", "Concreto armado", "Concreto protendido", "Balanço sucessivo",
                                           "Ponte estaiada", "Ponte mista"], key="tipo_oaevupr")

        if tipo_oaevupr:
            colunas = st.columns(min(len(tipo_oaevupr), 3))
            for i, tipo in enumerate(tipo_oaevupr):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area_oaepr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_oaepr_{tipo}")
                    vao_oaepr = st.number_input("VÃO (m)", min_value=0.0, step=0.1, key=f"vao_oaepr_{tipo}")
                    prancha_oaepr = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_oaepr_{tipo}")
                    if area_oaepr > 0 or vao_oaepr > 0 or prancha_oaepr > 0:
                        oaepr_info[tipo] = {
                            "área": area_oaepr,
                            "vão": vao_oaepr,
                            "prancha": prancha_oaepr
                        }
        st.divider()

    if "FUNDAÇÃO" in tipo_servico:
        fundacaopr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Fundação")
        with d2:
            tipo_funduvpr = st.multiselect("Tipo Fundação",
                                           ["Rasa(sapata, blocos e radier)", "Profunda(estaca, tubulão, caixões)",
                                            "Rasa e Profunda"], key="tipo_funduvpr")

        if tipo_funduvpr:
            colunas = st.columns(min(len(tipo_funduvpr), 3))
            for i, tipo in enumerate(tipo_funduvpr):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    m2_fundpr = st.number_input("M²", min_value=0.0, step=1.0, key=f"m2_fundpr_{tipo}")
                    prancha_fundpr = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_fundpr_{tipo}")
                    if m2_fundpr > 0 or prancha_fundpr > 0:
                        fundacaopr_info[tipo] = {
                            "m²": m2_fundpr,
                            "prancha": prancha_fundpr
                        }
        st.divider()

    if "MEIO AMBIENTE" in tipo_servico:
        meioambientepr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Meio Ambiente")
        with d2:
            tipo_meivupr = st.multiselect("Tipo Meio Ambiente", ["EIA/RIMA", "RCA/PCA", "RCA", "PCA", "RADA", "PRADA",
                                                                 "Inventário Florestal"], key="tipo_meivupr")

        if tipo_meivupr:
            colunas = st.columns(min(len(tipo_meivupr), 3))
            for i, tipo in enumerate(tipo_meivupr):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    unidade_meipr = st.number_input("Unidade", min_value=0.0, step=1.0, key=f"unidade_meipr_{tipo}")
                    prancha_meipr = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_meipr_{tipo}")
                    if unidade_meipr > 0 or prancha_meipr > 0:
                        meioambientepr_info[tipo] = {
                            "unidade": unidade_meipr,
                            "prancha": prancha_meipr
                        }
        st.divider()

    if "COMPAT. PROJETOS" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nCompat. Projetos")
        with d2:
            area_infracomppr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_infracomppr")
        with d3:
            prancha_infracomppr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_infracomppr")
        st.divider()

    if "ELÉTRICO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nElétrico")
        with d2:
            area_elepr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_elepr")
        with d3:
            kva_pr = st.number_input("KVA", min_value=0.0, step=0.1, key="kva_pr")
        with d4:
            prancha_elepr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_elepr")
        st.divider()

    if "EXTENSÃO DE REDE" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nExtensão de Rede")
        with d2:
            area_extpr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extpr")
        with d3:
            prancha_extpr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_extpr")
        st.divider()

    if "ILUMINAÇÃO PUBLICA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nIluminação Pública")
        with d2:
            area_iluppr = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_iluppr")
        with d3:
            prancha_iluppr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_iluppr")
        st.divider()

if "Supervisão Gerenciamento Rodovias" in servico:
    tipo_servicos = ["URBANISTICO", "PAISAGISTICO", "ANTEPROJETO DE INFRA", "GEOMÉTRICO", "TERRAPLENAGEM",
                     "HIDROLOGIA", "DRENAGEM", "ESTRUTURAL", "PAVIMENTAÇÃO", "SINALIZAÇÃO", "TOPOGRAFIA", "ORÇAMENTO",
                     "CONTENÇÃO", "OAE", "FUNDAÇÃO", "MEIO AMBIENTE", "COMPAT. PROJETOS", "ILUMINAÇÃO PUBLICA", "EXTENSÃO DE REDE", "ELÉTRICO"]
    tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

    if "URBANISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nUrbanístico")
        with d2:
            area_urpr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urpr")
        with d3:
            prancha_urpr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_urpr")
        st.divider()

    if "PAISAGISTICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nPaisagístico")
        with d2:
            area_paisapr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisapr")
        with d3:
            prancha_paisapr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_paisapr")
        st.divider()

    if "ANTEPROJETO DE INFRA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nAnteprojeto de Infra")
        with d2:
            km_antipr = st.number_input("KM", min_value=0.0, step=1.0, key="km_antipr")
        with d3:
            prancha_antipr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_antipr")
        st.divider()

    if "GEOMÉTRICO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nGeométrico")
        with d2:
            km_geopr = st.number_input("KM", min_value=0.0, step=1.0, key="km_geopr")
        with d3:
            prancha_geopr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_geopr")
        st.divider()

    if "TERRAPLENAGEM" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nTerraplenagem")
        with d2:
            km_terpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_terpr")
        with d3:
            prancha_terpr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_terpr")
        st.divider()

    if "DRENAGEM" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nDrenagem")
        with d2:
            km_drepr = st.number_input("KM", min_value=0.0, step=1.0, key="km_drepr")
        with d3:
            prancha_drepr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_drepr")
        st.divider()

    if "ESTRUTURAL" in tipo_servico:
        estruturalpr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Estrutural")
        with d2:
            tipo_estpep = st.multiselect("Tipos Estruturais", ["Concreto", "Madeira", "Metálica"], key="tipo_estpep")

        if tipo_estpep:
            colunas = st.columns(min(len(tipo_estpep), 3))
            for i, tipo in enumerate(tipo_estpep):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area_est = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_est_{tipo}")
                    prancha_est = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_est_{tipo}")
                    if area_est > 0 or prancha_est > 0:
                        estruturalpr_info[tipo] = {
                            "área": area_est,
                            "prancha": prancha_est
                        }
        st.divider()

    if "PAVIMENTAÇÃO" in tipo_servico:
        pavimentacaopr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Pavimentação")
        with d2:
            tipo_pavpr = st.multiselect("Tipo de Pavimentação", ["CBUQ", "CONCRETO", "TSD"], key="tipo_pavpr")

        if tipo_pavpr:
            colunas = st.columns(min(len(tipo_pavpr), 3))
            for i, tipo in enumerate(tipo_pavpr):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    km_pavpr = st.number_input("KM", min_value=0.0, step=1.0, key=f"km_pavpr_{tipo}")
                    m_pavpr = st.number_input("M²", min_value=0.0, step=0.1, key=f"m2_pavpr_{tipo}")
                    prancha_pavpr = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_pavpr_{tipo}")
                    if km_pavpr > 0 or m_pavpr > 0 or prancha_pavpr > 0:
                        pavimentacaopr_info[tipo] = {
                            "km": km_pavpr,
                            "m²": m_pavpr,
                            "prancha": prancha_pavpr
                        }
        st.divider()

    if "SINALIZAÇÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nSinalização")
        with d2:
            km_sinalpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_sinalpr")
        with d3:
            prancha_sinalpr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_sinalpr")
        st.divider()

    if "TOPOGRAFIA" in tipo_servico:
        d1, d2, d3, d4, d5, d6 = st.columns(6)
        with d1:
            st.write("###### \nTopografia")
        with d2:
            tipo_toppr = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerofotogrametria",
                                               "Planialtimétrico georreferenciado",
                                               "Planialtimétrico georreferenciado e aerofotogrametrico",
                                               "Planialtimétrico aerofotogrametrico"], key="tipo_toppr")
        with d3:
            cadastral_toppr = st.selectbox("Cadastral", ["Não", "Sim"], key="cadastral_toppr")
        with d4:
            km_toppr = st.number_input("KM", min_value=0.0, step=1.0, key="km_toppr")
        with d5:
            area_toppr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_toppr")
        with d6:
            prancha_toppr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_toppr")
        st.divider()

    if "ORÇAMENTO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nOrçamento")
        with d2:
            km_orcpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_orcpr")
        with d3:
            area_infraorcpr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_infraorcpr")
        with d4:
            prancha_orcpr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_orcpr")
        st.divider()

    if "CONTENÇÃO" in tipo_servico:
        contencaopr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Contenção")
        with d2:
            tipo_contpr = st.multiselect("Tipo de Contenção",
                                         ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"],
                                         key="tipo_contpr")

        if tipo_contpr:
            colunas = st.columns(min(len(tipo_contpr), 5))
            for i, tipo in enumerate(tipo_contpr):
                with colunas[i % 5]:
                    st.markdown(f"**{tipo}**")
                    m_contpr = st.number_input("M", min_value=0.0, step=1.0, key=f"m_contpr_{tipo}")
                    m2_contpr = st.number_input("M²", min_value=0.0, step=0.1, key=f"m2_contpr_{tipo}")
                    m3_contpr = st.number_input("M³", min_value=0.0, step=0.1, key=f"m3_contpr_{tipo}")
                    prancha_contpr = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_contpr_{tipo}")
                    if m_contpr > 0 or m2_contpr > 0 or m3_contpr > 0 or prancha_contpr > 0:
                        contencaopr_info[tipo] = {
                            "m": m_contpr,
                            "m²": m2_contpr,
                            "m³": m3_contpr,
                            "prancha": prancha_contpr
                        }
        st.divider()

    if "OAE" in tipo_servico:
        oaepr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("OAE")
        with d2:
            tipo_oaevupr = st.multiselect("Tipo de OAE",
                                          ["Laudo", "Concreto armado", "Concreto protendido", "Balanço sucessivo",
                                           "Ponte estaiada", "Ponte mista"], key="tipo_oaevupr")

        if tipo_oaevupr:
            colunas = st.columns(min(len(tipo_oaevupr), 3))
            for i, tipo in enumerate(tipo_oaevupr):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area_oaepr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_oaepr_{tipo}")
                    vao_oaepr = st.number_input("VÃO (m)", min_value=0.0, step=0.1, key=f"vao_oaepr_{tipo}")
                    prancha_oaepr = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_oaepr_{tipo}")
                    if area_oaepr > 0 or vao_oaepr > 0 or prancha_oaepr > 0:
                        oaepr_info[tipo] = {
                            "área": area_oaepr,
                            "vão": vao_oaepr,
                            "prancha": prancha_oaepr
                        }
        st.divider()

    if "FUNDAÇÃO" in tipo_servico:
        fundacaopr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Fundação")
        with d2:
            tipo_funduvpr = st.multiselect("Tipo Fundação",
                                           ["Rasa(sapata, blocos e radier)", "Profunda(estaca, tubulão, caixões)",
                                            "Rasa e Profunda"], key="tipo_funduvpr")

        if tipo_funduvpr:
            colunas = st.columns(min(len(tipo_funduvpr), 3))
            for i, tipo in enumerate(tipo_funduvpr):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    m2_fundpr = st.number_input("M²", min_value=0.0, step=1.0, key=f"m2_fundpr_{tipo}")
                    prancha_fundpr = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_fundpr_{tipo}")
                    if m2_fundpr > 0 or prancha_fundpr > 0:
                        fundacaopr_info[tipo] = {
                            "m²": m2_fundpr,
                            "prancha": prancha_fundpr
                        }
        st.divider()

    if "MEIO AMBIENTE" in tipo_servico:
        meioambientepr_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Meio Ambiente")
        with d2:
            tipo_meivupr = st.multiselect("Tipo Meio Ambiente", ["EIA/RIMA", "RCA/PCA", "RCA", "PCA", "RADA", "PRADA",
                                                                 "Inventário Florestal"], key="tipo_meivupr")

        if tipo_meivupr:
            colunas = st.columns(min(len(tipo_meivupr), 3))
            for i, tipo in enumerate(tipo_meivupr):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    unidade_meipr = st.number_input("Unidade", min_value=0.0, step=1.0, key=f"unidade_meipr_{tipo}")
                    prancha_meipr = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_meipr_{tipo}")
                    if unidade_meipr > 0 or prancha_meipr > 0:
                        meioambientepr_info[tipo] = {
                            "unidade": unidade_meipr,
                            "prancha": prancha_meipr
                        }
        st.divider()

    if "COMPAT. PROJETOS" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nCompat. Projetos")
        with d2:
            area_infracomppr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_infracomppr")
        with d3:
            prancha_infracomppr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_infracomppr")
        st.divider()

    if "ELÉTRICO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nElétrico")
        with d2:
            area_elepr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_elepr")
        with d3:
            kva_pr = st.number_input("KVA", min_value=0.0, step=0.1, key="kva_pr")
        with d4:
            prancha_elepr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_elepr")
        st.divider()

    if "EXTENSÃO DE REDE" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nExtensão de Rede")
        with d2:
            area_extpr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extpr")
        with d3:
            prancha_extpr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_extpr")
        st.divider()

    if "ILUMINAÇÃO PUBLICA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nIluminação Pública")
        with d2:
            area_iluppr = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_iluppr")
        with d3:
            prancha_iluppr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_iluppr")
        st.divider()

if "Plano Saneamento Básico - PMSB" in servico:
    tipo_servico = "Plano Saneamento Básico - PMSB"
    st.title("Plano Saneamento Básico - PMSB")
    d1, d2 = st.columns(2)
    with d1:
        pmbs_habitantes = st.number_input("Número de Habitantes", min_value=0.0, step=1.0, format="%.0f")
    with d2:
        prancha_pmbs = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_pmbs")
    st.divider()

if "Sondagem / Controle Tecnológico" in servico:
    tipo_servicos = ["SONDAGEM", "SOLO", "ASFALTO", "CONCRETO", "AÇO"]
    tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

    if "SONDAGEM" in tipo_servico:
        sondagem_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Sondagem")
        with d2:
            tipo_sonda = st.multiselect("Tipo", ["SPT", "Rotativa", "Trado", "Mista"], key="tipo_sonda")

        if tipo_sonda:
            colunas = st.columns(min(len(tipo_sonda), 4))
            for i, tipo in enumerate(tipo_sonda):
                with colunas[i % 4]:
                    st.markdown(f"**{tipo}**")
                    unidade_geo = st.number_input("Unidade", min_value=0.0, step=1.0, format="%.0f",
                                                  key=f"unidade_sondagem_{tipo}")
                    metros_geo = st.number_input("Metros (m)", min_value=0.0, step=0.1, key=f"metros_sondagem_{tipo}")
                    if unidade_geo > 0 or metros_geo > 0:
                        sondagem_info[tipo] = {
                            "unidade": unidade_geo,
                            "metros": metros_geo
                        }
        st.divider()

    if "SOLO" in tipo_servico:
        solo_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Solo")
        with d2:
            tipo_solo = st.multiselect("Tipo", [
                "LL – Limite de Liquidez", "LP – Limite de Plasticidade", "LC – Limite de Contração",
                "GPS - Granulometria por Peneiramento e Sedimentação", "ISC - Índice de Suporte Califórnia (CBR)",
                "CPN - Compactação Proctor Normal", "CPI – Compactação Proctor Internormal",
                "CPM – Compactação Proctor Modificado", "CIUSAT - Compressão Triaxial", "CIDSAT - Compressão Triaxial",
                "UUSAT - Compressão Triaxial", "MES – Peso/Massa específico dos Grãos", "W - Teor de Umidade Natural",
                "SCS – Dispersão Sedimentométrico Comparativo", "PCT - Permeabilidade em Câmara Triaxial",
                "Adensamento", "Cisalhamento", "Porosidade", "IN SITU (Frasco de Areia)",
                "IVmáx – Índice de Vazios Máximo", "IVmin – Índice de Vazios Mínimo",
                "BH – Balança Hidrostática", "ADN – Adensamento Oedométrico Unidimensional"
            ], key="tipo_solo")

        if tipo_solo:
            colunas = st.columns(min(len(tipo_solo), 4))
            for i, tipo in enumerate(tipo_solo):
                with colunas[i % 4]:
                    st.markdown(f"**{tipo}**")
                    unidade_solo = st.number_input("Unidade", min_value=0.0, step=1.0, format="%.0f",
                                                   key=f"unidade_solo_{tipo}")
                    metros_solo = st.number_input("Metros (m)", min_value=0.0, step=0.1, key=f"metros_solo_{tipo}")
                    if unidade_solo > 0 or metros_solo > 0:
                        solo_info[tipo] = {
                            "unidade": unidade_solo,
                            "metros": metros_solo
                        }
        st.divider()

    if "ASFALTO" in tipo_servico:
        asfalto_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Asfalto")
        with d2:
            tipo_asfalto = st.multiselect("Tipo", [
                "Viga Benkelman", "Teor de Betume", "Estabilidade Marshall",
                "Granulometria", "Densidade Aparente/Porosidade", "Compressão"
            ], key="tipo_asfalto")

        if tipo_asfalto:
            colunas = st.columns(min(len(tipo_asfalto), 3))
            for i, tipo in enumerate(tipo_asfalto):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    unidade_asfalto = st.number_input("Unidade", min_value=0.0, step=1.0, format="%.0f",
                                                      key=f"unidade_asfalto_{tipo}")
                    metros_asfalto = st.number_input("Metros (m)", min_value=0.0, step=0.1,
                                                     key=f"metros_asfalto_{tipo}")
                    if unidade_asfalto > 0 or metros_asfalto > 0:
                        asfalto_info[tipo] = {
                            "unidade": unidade_asfalto,
                            "metros": metros_asfalto
                        }
        st.divider()

    if "CONCRETO" in tipo_servico:
        concreto_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Concreto")
        with d2:
            tipo_concreto = st.multiselect("Tipo", [
                "Compressão axial (ruptura)", "Consistência (Slump)"
            ], key="tipo_concreto")

        if tipo_concreto:
            colunas = st.columns(min(len(tipo_concreto), 2))
            for i, tipo in enumerate(tipo_concreto):
                with colunas[i % 2]:
                    st.markdown(f"**{tipo}**")
                    unidade_concreto = st.number_input("Unidade", min_value=0.0, step=1.0, format="%.0f",
                                                       key=f"unidade_concreto_{tipo}")
                    metros_concreto = st.number_input("Metros (m)", min_value=0.0, step=0.1,
                                                      key=f"metros_concreto_{tipo}")
                    if unidade_concreto > 0 or metros_concreto > 0:
                        concreto_info[tipo] = {
                            "unidade": unidade_concreto,
                            "metros": metros_concreto
                        }
        st.divider()

    if "AÇO" in tipo_servico:
        aco_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Aço")
        with d2:
            tipo_aco = st.multiselect("Tipo", [
                "LE – Limite de Escoamento", "LR – Limite de Resistência",
                "A – Alongamento", "Dobramento"
            ], key="tipo_aco")

        if tipo_aco:
            colunas = st.columns(min(len(tipo_aco), 2))
            for i, tipo in enumerate(tipo_aco):
                with colunas[i % 2]:
                    st.markdown(f"**{tipo}**")
                    unidade_aco = st.number_input("Unidade", min_value=0.0, step=1.0, format="%.0f",
                                                  key=f"unidade_aco_{tipo}")
                    metros_aco = st.number_input("Metros (m)", min_value=0.0, step=0.1, key=f"metros_aco_{tipo}")
                    if unidade_aco > 0 or metros_aco > 0:
                        aco_info[tipo] = {
                            "unidade": unidade_aco,
                            "metros": metros_aco
                        }
        st.divider()

if "Projeto Saneamento" in servico:
    tipo_servicos = ["FUNDAÇÃO", "TOPOGRAFIA", "ELÉTRICO", "ORÇAMENTO", "REDE COLETORA", "INTERCEPTOR", "ELEVATÓRIO", "ETE", "ADUTORA", "ELEVATÓRIA", "ETA", "REDE DE DISTRIBUIÇÃO", "ILUMINAÇÃO PUBLICA", "EXTENSÃO DE REDE"]
    tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)


    if "FUNDAÇÃO" in tipo_servico:
        fundacao_ps_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Fundação")
        with d2:
            tipos_fundps = st.multiselect("Tipo",
                                          ["Rasa (sapata, blocos e radier)", "Profunda (estaca, tubulão e caixões)",
                                           "Rasa e Profunda"], key="tipos_fundps")

        if tipos_fundps:
            colunas = st.columns(min(len(tipos_fundps), 3))
            for i, tipo in enumerate(tipos_fundps):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_fundps_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_fundps_{tipo}")
                    if area > 0 or prancha > 0:
                        fundacao_ps_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "TOPOGRAFIA" in tipo_servico:
        d1, d2, d3, d4, d5, d6 = st.columns(6)
        with d1:
            st.write("""###### \nTopografia""")
        with d2:
            Tipo_topps = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria",
                                               "Planialtimétrico georreferenciado",
                                               "Planialtimétrico georreferenciado e aerofotogrametrico",
                                               "Planialtimétrico aerofotogrametrico"])
        with d3:
            cadastral_ps = st.selectbox("Cadastral", ["Não", "Sim"], key="cadastral_ps")
        with d4:
            drone_os = st.selectbox("Drone", ["Não", "Sim"], key="drone_os")
        with d5:
            area_topsaps = st.number_input("M²", min_value=0.0, step=1.0, key="area_topsaps")
        with d6:
            prancha_topps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_toppr")
        st.divider()

    if "ELÉTRICO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nElétrico")
        with d2:
            area_elesaps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_elesaps")
        with d3:
            kva_ps = st.number_input("KVA", min_value=0.0, step=0.1, key="kva_ps")
        with d4:
            prancha_elesaps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_elesaps")
        st.divider()

    if "ORÇAMENTO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nOrçamento")
        with d2:
            area_orcsaps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_orcsaps")
        with d3:
            prancha_orcsaps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_orcsaps")
        st.divider()

    if "REDE COLETORA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nRede Coletora")
        with d2:
            m_redecoleps = st.number_input("Metros (m)", min_value=0.0, step=1.0, key="m_redecoleps")
        with d3:
            prancha_redecoleps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_redecoleps")
        st.divider()

    if "INTERCEPTOR" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nInterceptor")
        with d2:
            m_interceptorps = st.number_input("Metros (m)", min_value=0.0, step=1.0, key="m_interceptorps")
        with d3:
            prancha_interceptorps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_interceptorps")
        st.divider()

    if "ELEVATÓRIO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nElevatório")
        with d2:
            m_elevatoriops = st.number_input("Metros (m)", min_value=0.0, step=1.0, key="m_elevatoriops")
        with d3:
            prancha_elevatoriopsfdp = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_elevatoriopsfdp")
        st.divider()

    if "ETE" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nETE")
        with d2:
            vazao_eteps = st.number_input("Vazão (l/s)", min_value=0.0, step=1.0, key="vazao_eteps")
        with d3:
            prancha_eteps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_elevatoriops")
        st.divider()

    if "ADUTORA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nAdutora")
        with d2:
            m_adutoraps = st.number_input("Metros (m)", min_value=0.0, step=1.0, key="m_adutoraps")
        with d3:
            prancha_adutoraps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_adutoraps")
        st.divider()

    if "ETA" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nETA")
        with d2:
            vazao_etaps = st.number_input("Vazão (l/s)", min_value=0.0, step=1.0, key="vazao_etaps")
        with d3:
            vol_etaps = st.number_input("Volume (m³)", min_value=0.0, step=1.0, key="vol_etaps")
        with d4:
            prancha_etaps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_etaps")
        st.divider()

    if "REDE DE DISTRIBUIÇÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nRede de Distribuição")
        with d2:
            m_rededisps = st.number_input("Metros (m)", min_value=0.0, step=1.0, key="m_rededisps")
        with d3:
            prancha_rededisps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_rededisps")
        st.divider()

    if "EXTENSÃO DE REDE" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nExtensão de Rede")
        with d2:
            area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")
        with d3:
            prancha_extr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_extr")
        st.divider()

    if "ILUMINAÇÃO PUBLICA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nIluminação Pública")
        with d2:
            area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")
        with d3:
            prancha_ilupu = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ilupu")
        st.divider()

if "Supervisão Gerenciamento Saneamento" in servico:
    tipo_servicos = ["FUNDAÇÃO", "TOPOGRAFIA", "ELÉTRICO", "ORÇAMENTO", "REDE COLETORA", "INTERCEPTOR",
                     "ELEVATÓRIO", "ETE", "ADUTORA", "ELEVATÓRIA", "ETA", "REDE DE DISTRIBUIÇÃO", "ILUMINAÇÃO PUBLICA", "EXTENSÃO DE REDE"]
    tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

    if "FUNDAÇÃO" in tipo_servico:
        fundacao_ps_info = {}
        d1, d2 = st.columns(2)
        with d1:
            st.title("Fundação")
        with d2:
            tipos_fundps = st.multiselect("Tipo",
                                          ["Rasa (sapata, blocos e radier)", "Profunda (estaca, tubulão e caixões)",
                                           "Rasa e Profunda"], key="tipos_fundps")

        if tipos_fundps:
            colunas = st.columns(min(len(tipos_fundps), 3))
            for i, tipo in enumerate(tipos_fundps):
                with colunas[i % 3]:
                    st.markdown(f"**{tipo}**")
                    area = st.number_input("Área (m²)", min_value=0.0, step=1.0, key=f"area_fundps_{tipo}")
                    prancha = st.number_input("Prancha", min_value=0, step=1, key=f"prancha_fundps_{tipo}")
                    if area > 0 or prancha > 0:
                        fundacao_ps_info[tipo] = {"área": area, "prancha": prancha}
        st.divider()

    if "TOPOGRAFIA" in tipo_servico:
        d1, d2, d3, d4, d5, d6 = st.columns(6)
        with d1:
            st.write("""###### \nTopografia""")
        with d2:
            Tipo_topps = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria",
                                               "Planialtimétrico georreferenciado",
                                               "Planialtimétrico georreferenciado e aerofotogrametrico",
                                               "Planialtimétrico aerofotogrametrico"])
        with d3:
            cadastral_ps = st.selectbox("Cadastral", ["Não", "Sim"], key="cadastral_ps")
        with d4:
            drone_os = st.selectbox("Drone", ["Não", "Sim"], key="drone_os")
        with d5:
            area_topsaps = st.number_input("M²", min_value=0.0, step=1.0, key="area_topsaps")
        with d6:
            prancha_topps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_toppr")
        st.divider()

    if "ELÉTRICO" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nElétrico")
        with d2:
            area_elesaps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_elesaps")
        with d3:
            kva_ps = st.number_input("KVA", min_value=0.0, step=0.1, key="kva_ps")
        with d4:
            prancha_elesaps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_elesaps")
        st.divider()

    if "ORÇAMENTO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nOrçamento")
        with d2:
            area_orcsaps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_orcsaps")
        with d3:
            prancha_orcsaps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_orcsaps")
        st.divider()

    if "REDE COLETORA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nRede Coletora")
        with d2:
            m_redecoleps = st.number_input("Metros (m)", min_value=0.0, step=1.0, key="m_redecoleps")
        with d3:
            prancha_redecoleps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_redecoleps")
        st.divider()

    if "INTERCEPTOR" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nInterceptor")
        with d2:
            m_interceptorps = st.number_input("Metros (m)", min_value=0.0, step=1.0, key="m_interceptorps")
        with d3:
            prancha_interceptorps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_interceptorps")
        st.divider()

    if "ELEVATÓRIO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nElevatório")
        with d2:
            m_elevatoriops = st.number_input("Metros (m)", min_value=0.0, step=1.0, key="m_elevatoriops")
        with d3:
            prancha_elevatoriopsfdp = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_elevatoriopsfdp")
        st.divider()

    if "ETE" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nETE")
        with d2:
            vazao_eteps = st.number_input("Vazão (l/s)", min_value=0.0, step=1.0, key="vazao_eteps")
        with d3:
            prancha_eteps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_elevatoriops")
        st.divider()

    if "ADUTORA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nAdutora")
        with d2:
            m_adutoraps = st.number_input("Metros (m)", min_value=0.0, step=1.0, key="m_adutoraps")
        with d3:
            prancha_adutoraps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_adutoraps")
        st.divider()

    if "ETA" in tipo_servico:
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.write("###### \nETA")
        with d2:
            vazao_etaps = st.number_input("Vazão (l/s)", min_value=0.0, step=1.0, key="vazao_etaps")
        with d3:
            vol_etaps = st.number_input("Volume (m³)", min_value=0.0, step=1.0, key="vol_etaps")
        with d4:
            prancha_etaps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_etaps")
        st.divider()

    if "REDE DE DISTRIBUIÇÃO" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nRede de Distribuição")
        with d2:
            m_rededisps = st.number_input("Metros (m)", min_value=0.0, step=1.0, key="m_rededisps")
        with d3:
            prancha_rededisps = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_rededisps")
        st.divider()

    if "EXTENSÃO DE REDE" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nExtensão de Rede")
        with d2:
            area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")
        with d3:
            prancha_extr = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_extr")
        st.divider()

    if "ILUMINAÇÃO PUBLICA" in tipo_servico:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.write("###### \nIluminação Pública")
        with d2:
            area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")
        with d3:
            prancha_ilupu = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ilupu")
        st.divider()

if "Estudos e Projetos Ambientais – Edificação" in servico:
    tipo_servicos = ["EIA/RIMA", "PCA – Plano de Controle Ambiental", "RAS – Relatório Ambiental Simplificado", "Licença Ambiental Concomitante", "RCA – Relatório de Controle Ambiental", "PRADA – Projeto de Recuperação de Águas Degradadas e Alteradas", "PMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos", "PIA – Plano de Intervenção Ambiental", "Relatório de Outorga", "Dispensa de outorga", "Dispensa de licenciamento", "Inventário florestal/Plano Manejo"]
    tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

    if "EIA/RIMA" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nEIA/RIMA""")
        with col2:
            un_eiaedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_eiaedi")
        with col3:
            area_eiaedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_eiaedi")
        with col4:
            prancha_eiaedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_eiaedi")
        st.divider()

    if "PCA – Plano de Controle Ambiental" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nPCA – Plano de Controle Ambiental""")
        with col2:
            un_pcaedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pcaedi")
        with col3:
            area_pcaedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_pcaedi")
        with col4:
            prancha_pcaedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_pcaedi")
        st.divider()

    if "RAS – Relatório Ambiental Simplificado" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nRAS – Relatório Ambiental Simplificado""")
        with col2:
            un_rasedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rasedi")
        with col3:
            area_rasedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_rasedi")
        with col4:
            prancha_rasedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_rasedi")
        st.divider()

    if "Licença Ambiental Concomitante" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nLicença Ambiental Concomitante""")
        with col2:
            un_lacedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_lacedi")
        with col3:
            area_lacedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_lacedi")
        with col4:
            prancha_lacedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_lacedi")
        st.divider()

    if "RCA – Relatório de Controle Ambiental" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nRCA – Relatório de Controle Ambiental""")
        with col2:
            un_rcaedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rcaedi")
        with col3:
            area_rcaedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_rcaedi")
        with col4:
            prancha_rcaedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_rcaedi")
        st.divider()

    if "PRADA – Projeto de Recuperação de Águas Degradadas e Alteradas" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nPRADA – Projeto de Recuperação de Águas Degradadas e Alteradas""")
        with col2:
            un_pradaedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pradaedi")
        with col3:
            area_pradaedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_pradaedi")
        with col4:
            prancha_pradaedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_pradaedi")
        st.divider()

    if "PMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nPMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos""")
        with col2:
            un_pmgirsedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pmgirsedi")
        with col3:
            area_pmgirsedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_pmgirsedi")
        with col4:
            prancha_pmgirsedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_pmgirsedi")
        st.divider()

    if "PIA – Plano de Intervenção Ambiental" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nPIA – Plano de Intervenção Ambiental""")
        with col2:
            un_piaedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_piaedi")
        with col3:
            area_piaedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_piaedi")
        with col4:
            prancha_piaedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_piaedi")
        st.divider()

    if "Relatório de Outorga" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nRelatório de Outorga""")
        with col2:
            un_rdoedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rdoedi")
        with col3:
            area_rdoedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_rdoedi")
        with col4:
            prancha_rdoedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_rdoedi")
        st.divider()

    if "Dispensa de outorga" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nDispensa de outorga""")
        with col2:
            un_ddoedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ddoedi")
        with col3:
            area_ddoedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_ddoedi")
        with col4:
            prancha_ddoedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ddoedi")
        st.divider()

    if "Dispensa de licenciamento" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nDispensa de licenciamento""")
        with col2:
            un_ddledi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ddledi")
        with col3:
            area_ddledi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_ddledi")
        with col4:
            prancha_ddledi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ddledi")
        st.divider()

    if "Inventário florestal/Plano Manejo" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nInventário florestal/Plano Manejo""")
        with col2:
            un_ifpmedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ifpmedi")
        with col3:
            area_ifpmedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_ifpmedi")
        with col4:
            prancha_ifpmedi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ifpmedi")
        st.divider()

if "Estudos e Projetos Ambientais - Infraestrutura" in servico:
    tipo_servicos = ["EIA/RIMA", "PCA – Plano de Controle Ambiental", "RAS – Relatório Ambiental Simplificado", "Licença Ambiental Concomitante", "RCA – Relatório de Controle Ambiental", "PRADA – Projeto de Recuperação de Águas Degradadas e Alteradas", "PMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos", "PIA – Plano de Intervenção Ambiental", "Relatório de Outorga", "Dispensa de outorga", "Dispensa de licenciamento", "Inventário florestal/Plano Manejo"]
    tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

    if "EIA/RIMA" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nEIA/RIMA""")
        with col2:
            un_eiainf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_eiainf")
        with col3:
            area_eiainf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_eiainf")
        with col4:
            prancha_eiainf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_eiainf")
        st.divider()

    if "PCA – Plano de Controle Ambiental" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nPCA – Plano de Controle Ambiental""")
        with col2:
            un_pcainf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pcainf")
        with col3:
            area_pcainf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_pcainf")
        with col4:
            prancha_pcainf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_pcainf")
        st.divider()

    if "RAS – Relatório Ambiental Simplificado" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nRAS – Relatório Ambiental Simplificado""")
        with col2:
            un_rasinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rasinf")
        with col3:
            area_rasinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_rasinf")
        with col4:
            prancha_rasinf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_rasinf")
        st.divider()

    if "Licença Ambiental Concomitante" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nLicença Ambiental Concomitante""")
        with col2:
            un_lacinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_lacinf")
        with col3:
            area_lacinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_lacinf")
        with col4:
            prancha_lacinf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_lacinf")
        st.divider()

    if "RCA – Relatório de Controle Ambiental" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nRCA – Relatório de Controle Ambiental""")
        with col2:
            un_rcainf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rcainf")
        with col3:
            area_rcainf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_rcainf")
        with col4:
            prancha_rcainf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_rcainf")
        st.divider()

    if "PRADA – Projeto de Recuperação de Águas Degradadas e Alteradas" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nPRADA – Projeto de Recuperação de Águas Degradadas e Alteradas""")
        with col2:
            un_pradainf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pradainf")
        with col3:
            area_pradainf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_pradainf")
        with col4:
            prancha_pradainf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_pradainf")
        st.divider()

    if "PMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nPMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos""")
        with col2:
            un_pmgirsinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pmgirsinf")
        with col3:
            area_pmgirsinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_pmgirsinf")
        with col4:
            prancha_pmgirsinf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_pmgirsinf")
        st.divider()

    if "PIA – Plano de Intervenção Ambiental" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nPIA – Plano de Intervenção Ambiental""")
        with col2:
            un_piainf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_piainf")
        with col3:
            area_piainf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_piainf")
        with col4:
            prancha_piainf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_piainf")
        st.divider()

    if "Relatório de Outorga" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nRelatório de Outorga""")
        with col2:
            un_rdoinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rdoinf")
        with col3:
            area_rdoinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_rdoinf")
        with col4:
            prancha_rdoinf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_rdoinf")
        st.divider()

    if "Dispensa de outorga" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nDispensa de outorga""")
        with col2:
            un_ddoinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ddoinf")
        with col3:
            area_ddoinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_ddoinf")
        with col4:
            prancha_ddoinf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ddoinf")
        st.divider()

    if "Dispensa de licenciamento" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nDispensa de licenciamento""")
        with col2:
            un_ddlinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ddlinf")
        with col3:
            area_ddlinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_ddlinf")
        with col4:
            prancha_ddlinf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ddlinf")
        st.divider()

    if "Inventário florestal/Plano Manejo" in tipo_servico:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("""###### \nInventário florestal/Plano Manejo""")
        with col2:
            un_ifpminf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ifpminf")
        with col3:
            area_ifpminf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2f", key="area_ifpminf")
        with col4:
            prancha_ifpminf = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_ifpminf")
        st.divider()

if "Plano Diretor" in servico:
    tipo_servico = "Plano Diretor"
    d1, d2 = st.columns(2)
    with d1:
        pdi_habitantes = st.number_input("Número de Habitantes", min_value=0.0, step=1.0, format="%.0f")
    with d2:
        prancha_pdi = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_eiainf")
        st.divider()

if "Diversos" in servico:
    tipo_servico = "Diversos"

    prancha_diversos = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_diversos")
    st.divider()

if "Topografia" in servico:
    d1, d2 = st.columns(2)
    with d1:
        st.title("Topografia")
    with d2:
        tipo_servico = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria",
                                             "Planialtimétrico georreferenciado",
                                             "Planialtimétrico georreferenciado e aerofotogrametrico",
                                             "Planialtimétrico aerofotogrametrico"])
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        cadastral_topografia = st.selectbox("Cadastral", ["Não", "Sim"])
    with a2:
        drone_topografia = st.selectbox("Drone", ["Não", "Sim"])
    with a3:
        area_topografia = st.number_input("M²", min_value=0.0, step=0.1, key="area_topp")
    with a4:
        prancha_topografia = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_eiainf")
        st.divider()

if "REURB Regularização Fundiária" in servico:
    tipo_servico = "REURB_Regularização Fundiária"
    st.title("REURB Regularização Fundiária")
    d1, d2 =st.columns(2)
    with d1:
        reur_habitantes = st.number_input("Unidade Habitacional", min_value=0.0, step=1.0, format="%.0f")
    with d2:
        prancha_reur = st.number_input("Nº Pranchas", min_value=0, step=1, key="prancha_eiainf")

    st.divider()

if st.button("Enviar"):
    # Verifica os campos obrigatórios
    campos_obrigatorios = {
        "Empresa do Grupo": empresas_grupo,
        "Cliente": cliente,
        "CAT": cat_numero,
        "Serviço": servico,
    }

    campos_faltando = [nome for nome, valor in campos_obrigatorios.items() if not valor]

    if campos_faltando:
        st.error(f"Por favor, preencha todos os campos obrigatórios: {', '.join(campos_faltando)}.")
    else:
        nome_atestado = f"{empresas_grupo}_{cliente}_{cat_numero}_{servico}"
        nome_atestado_formatado = nome_atestado.replace("/", "-")

        # Dicionário para armazenar as URLs no Firebase
        pdf_urls_profissionais = {}

        for nome, arquivo_pdf in pdfs_profissionais.items():
            nome_arquivo_pdf = f"atestados_pdfs/{nome_atestado}_{nome.replace(' ', '_')}.pdf"
            bucket = storage.bucket()
            blob = bucket.blob(nome_arquivo_pdf)
            blob.upload_from_file(arquivo_pdf, content_type="application/pdf")
            blob.make_public()
            pdf_urls_profissionais[nome] = blob.public_url

        # Criar dicionário com os dados
        dados_atestado = {
            "Empresa": empresas_grupo,
            "Cliente": cliente,
            "Servico": servico,
            "Profissional-Cordenação": nome_profissional_coor,
            "Profissional": nome_profissional,
            "Disciplina": tipo_servico,
            "Participação": participacao,
                "Tempo do projeto": meses_projeto,
            "CAT": cat_numero,
            "Data Início": str(data_inicial),
            "Data Final": str(data_final),
            "Objeto": objeto,
            "Extensão (km)": extensao,
            "Área (m²)": area,
            "BIM": bim,
            "Patrimônio Tombado": patrimonio,
            "ARQUITETÔNICO ANTEPROJETO(m²)": area_aa,
            "PRANCHA ARQUITETÔNICO ANTEPROJETO": pranchas_aa,
            "ARQUITETÔNICO CONSTRUÇÃO(m²)": area_ac,
            "PRANCHA ARQUITETÔNICO CONSTRUÇÃO": pranchas_ac,
            "ARQUITETÔNICO REFORMA(m²)": area_ar,
            "PRANCHA ARQUITETÔNICO REFORMA": pranchas_ar,
            "ARQUITETÔNICO RESTAURO(m²)": area_are,
            "PRANCHA ARQUITETÔNICO RESTAURO": pranchas_are,
            "COMUNICAÇÃO VISUAL(m²)": area_cv,
            "PRANCHA COMUNICAÇÃO VISUAL": pranchas_cv,
            "MOBILIÁRIO": mobiliario_info,
            "URBANISTICO(m²)": area_urb,
            "PRANCHA URBANISTICO": pranchas_urb,
            "PAISAGISTICO(m²)": area_paisag,
            "PRANCHA PAISAGISTICO": pranchas_paisag,
            "TIPO AS BUILT": tipo_ab,
            "AS BUILT(m²)": area_ab,
            "PRANCHA AS BUILT": pranchas_ab,
            "MAQ ELET/3D": maqelet_info,
            "ESTRUTURAL": estrutural_info,
            "FUNDAÇÃO": fundacao_info,
            "CONTENÇÃO": contencao_info,
            "HIDROSANITÁRIO(m²)": area_hds,
            "PRANCHA HIDROSANITÁRIO": prancha_hds,
            "IRRIGAÇÃO(m²)": area_irri,
            "PRANCHA IRRIGAÇÃO": prancha_irri,
            "SPCI(m²)": area_spci,
            "PRANCHA SPCI": prancha_spci,
            "TERRAPLENAGEM (PLANTA/SEÇÕES)(m²)": area_tps,
            "PRANCHA TERRAPLENAGEM (PLANTA/SEÇÕES)": prancha_tps,
            "TOPOGRAFIA(m²)": area_top,
            "PRANCHA TOPOGRAFIA": prancha_top,
            "TIPO TOPOGRAFIA": tipo_toppep,
            "CADASTRAL-TOP": cadastral,
            "DRONE-TOP": drone,
            "ORÇAMENTO(m²)": area_orc,
            "PRANCHA ORÇAMENTO": prancha_orc,
            "ELÉTRICO(m²)": area_ele,
            "KVA": kva,
            "PRANCHA ELÉTRICO": prancha_ele,
            "CAB. ESTRUTURADO(m²)": area_cets,
            "PRANCHA CAB. ESTRUTURADO": prancha_cets,
            "SPDA(m²)": area_spda,
            "PRANCHA SPDA": prancha_spda,
            "ALARME/CFTV(m²)": area_cftv,
            "PRANCHA ALARME/CFTV": prancha_cftv,
            "EXTENSÃO DE REDE(km)": area_extr,
            "PRANCHA EXTENSÃO DE REDE": prancha_extr,
            "ILUMINAÇÃO PUBLICA(pontos)": area_ilupu,
            "PRANCHA ILUMINAÇÃO PUBLICA": prancha_ilupu,
            "AR CONDICIONADO(m²)": area_arcond,
            "PRANCHA AR CONDICIONADO": prancha_arcond,
            "VENTILAÇÃO/EXAUSTÃO(m²)": area_venex,
            "PRANCHA VENTILAÇÃO/EXAUSTÃO": prancha_venex,
            "GLP(m²)": area_glp,
            "PRANCHA GLP": prancha_glp,
            "GASES MEDICINAIS(m²)": area_hvac,
            "PRANCHA GASES MEDICINAIS": prancha_hvac,
            "COMPAT. PROJETOS(m²)": area_comp,
            "PRANCHA COMPAT. PROJETOS": prancha_comp,
            "ACÚSTICA(m²)": area_acus,
            "PRANCHA ACÚSTICA": prancha_acus,
            "Un.Habitacionais": area_reurb,
            "PRANCHA REURB": prancha_reurb,
            "VU-URBANISTICO(m²)": area_urvi,
            "VU-PRANCHA URBANISTICO": prancha_urvi,
            "VU-PAISAGISTICO(m²)": area_paisavi,
            "VU-PRANCHA PAISAGISTICO": prancha_paisavi,
            "VU-ANTEPROJETO DE INFRA(KM)": km_anti,
            "VU-PRANCHA ANTEPROJETO DE INFRA": prancha_anti,
            "VU-GEOMÉTRICO(KM)": km_geo,
            "VU-PRANCHA GEOMÉTRICO": prancha_geo,
            "VU-TERRAPLENAGEM(KM)": km_ter,
            "VU-PRANCHA TERRAPLENAGEM": prancha_ter,
            "VU-DRENAGEM(KM)": km_dre,
            "VU-PRANCHA DRENAGEM": prancha_dre,
            "VU-ESTRUTURAL": vu_estrutural_info,
            "VU-PAVIMENTAÇÃO": vu_pavimentacao_info,
            "VU-SINALIZAÇÃO(KM)": km_sinal,
            "VU-PRANCHA SINALIZAÇÃO": prancha_sinal,
            "VU-TOPOGRAFIA": vu_topografia_info,
            "VU-ORÇAMENTO(KM)": km_orc,
            "VU-ORÇAMENTO(m²)": area_infraorc,
            "VU-PRANCHA ORÇAMENTO": prancha_orc,
            "VU-CONTENÇÃO": vu_contencao_info,
            "VU-OAE": vu_oae_info,
            "VU-FUNDAÇÃO": vu_fundacao_info,
            "VU-MEIO AMBIENTE": vu_meioambiente_info,
            "VU-COMPAT. PROJETOS(m²)": area_infracomp,
            "VU-PRANCHA COMPAT. PROJETOS": prancha_infracomp,
            "VU-ELÉTRICO(m²)": area_ele,
            "VU-KVA": kva_vu,
            "VU-PRANCHA ELÉTRICO": prancha_ele,
            "VU-EXTENSÃO DE REDE(KM)": area_extr,
            "VU-PRANCHA EXTENSÃO DE REDE": prancha_extr,
            "VU-ILUMINAÇÃO PUBLICA(Pontos)": area_ilupu,
            "VU-PRANCHA ILUMINAÇÃO PUBLICA": prancha_ilupu,
            "PMSB-NUMERO HABITANTES": pmbs_habitantes,
            "PMSB-PRANCHA":prancha_pmbs,
            "EDI-EIA/RIMA(UN)": un_eiaedi,
            "EDI-EIA/RIMA(Área)": area_eiaedi,
            "EDI-PRANCHA EIA/RIMA": prancha_eiaedi,
            "EDI-PCA(UN)": un_pcaedi,
            "EDI-PCA(Área)": area_pcaedi,
            "EDI-PRANCHA PCA": prancha_pcaedi,
            "EDI-RAS(UN)": un_rasedi,
            "EDI-RAS(Área)": area_rasedi,
            "EDI-PRANCHA RAS": prancha_rasedi,
            "EDI-LAC(UN)": un_lacedi,
            "EDI-LAC(Área)": area_lacedi,
            "EDI-PRANCHA LAC": prancha_lacedi,
            "EDI-RCA(UN)": un_rcaedi,
            "EDI-RCA(Área)": area_rcaedi,
            "EDI-PRANCHA RCA": prancha_rcaedi,
            "EDI-PRADA(UN)": un_pradaedi,
            "EDI-PRADA(Área)": area_pradaedi,
            "EDI-PRANCHA PRADA": prancha_pradaedi,
            "EDI-PMGIRS(UN)": un_pmgirsedi,
            "EDI-PMGIRS(Área)": area_pmgirsedi,
            "EDI-PRANCHA PMGIRS": prancha_pmgirsedi,
            "EDI-PIA(UN)": un_piaedi,
            "EDI-PIA(Área)": area_piaedi,
            "EDI-PRANCHA PIA": prancha_piaedi,
            "EDI-RdeO(UN)": un_rdoedi,
            "EDI-RdeO(Área)": area_rdoedi,
            "EDI-PRANCHA RdeO": prancha_rdoedi,
            "EDI-DDO(UN)": un_ddoedi,
            "EDI-DDO(Área)": area_ddoedi,
            "EDI-PRANCHA DDO": prancha_ddoedi,
            "EDI-DDL(UN)": un_ddledi,
            "EDI-DDL(Área)": area_ddledi,
            "EDI-PRANCHA DDL": prancha_ddledi,
            "EDI-IFPM(UN)": un_ifpmedi,
            "EDI-IFPM(Área)": area_ifpmedi,
            "EDI-PRANCHA If/PM": prancha_ifpmedi,
            "INF-EIA(UN)": un_eiainf,
            "INF-EIA(Área)": area_eiainf,
            "INF-PRANCHA EIA": prancha_eiainf,
            "INF-PCA(UN)": un_pcainf,
            "INF-PCA(Área)": area_pcainf,
            "INF-PRANCHA PCA": prancha_pcainf,
            "INF-RAS(UN)": un_rasinf,
            "INF-RAS(Área)": area_rasinf,
            "INF-PRANCHA RAS": prancha_rasinf,
            "INF-LAC(UN)": un_lacinf,
            "INF-LAC(Área)": area_lacinf,
            "INF-PRANCHA LAC": prancha_lacinf,
            "INF-RCA(UN)": un_rcainf,
            "INF-RCA(Área)": area_rcainf,
            "INF-PRANCHA RCA": prancha_rcainf,
            "INF-PRADA(UN)": un_pradainf,
            "INF-PRADA(Área)": area_pradainf,
            "INF-PRANCHA PRADA": prancha_pradainf,
            "INF-PMGIRS(UN)": un_pmgirsinf,
            "INF-PMGIRS(Área)": area_pmgirsinf,
            "INF-PRANCHA PMGIRS": prancha_pmgirsinf,
            "INF-PIA(UN)": un_piainf,
            "INF-PIA(Área)": area_piainf,
            "INF-PRANCHA PIA": prancha_piainf,
            "INF-RDO(UN)": un_rdoinf,
            "INF-RDO(Área)": area_rdoinf,
            "INF-PRANCHA RDO": prancha_rdoinf,
            "INF-DDO(UN)": un_ddoinf,
            "INF-DDO(Área)": area_ddoinf,
            "INF-PRANCHA DDO": prancha_ddoinf,
            "INF-DDL(UN)": un_ddlinf,
            "INF-DDL(Área)": area_ddlinf,
            "INF-PRANCHA DDL": prancha_ddlinf,
            "INF-IFPM(UN)": un_ifpminf,
            "INF-IFPM(Área)": area_ifpminf,
            "INF-PRANCHA IFPM": prancha_ifpminf,
            "PDI-NUMERO HABITANTE": pdi_habitantes,
            "PDI-PRANCHA": prancha_pdi,
            "DIVERSOS-PRANCHA":prancha_diversos,
            "REUR_HABITANTES": reur_habitantes,
            "REUR-PRANCHA":prancha_reur,
            "PR-URBANISTICO(m²)": area_urpr,
            "PR-PRANCHA URBANISTICO": prancha_urpr,
            "PR-PAISAGISTICO(m²)": area_paisapr,
            "PR-PRANCHA PAISAGISTICO": prancha_paisapr,
            "PR-ANTEPROJETO DE INFRA(KM)": km_antipr,
            "PR-PRANCHA ANTEPROJETO DE INFRA": prancha_antipr,
            "PR-GEOMÉTRICO(KM)": km_geopr,
            "PR-PRANCHA GEOMÉTRICO": prancha_geopr,
            "PR-TERRAPLENAGEM(KM)": km_terpr,
            "PR-PRANCHA TERRAPLENAGEM": prancha_terpr,
            "PR-DRENAGEM(KM)": km_drepr,
            "PR-PRANCHA DRENAGEM": prancha_drepr,
            "PR-ESTRUTURAL": estruturalpr_info,
            "PR-PAVIMENTAÇÃO": pavimentacaopr_info,
            "PR-SINALIZAÇÃO(KM)": km_sinalpr,
            "PR-PRANCHA SINALIZAÇÃO": prancha_sinalpr,
            "PR-TOPOGRAFIA(m²)": area_toppr,
            "PR-TOPOGRAFIA(KM)": km_toppr,
            "PR-PRANCHA TOPOGRAFIA": prancha_toppr,
            "PR-ORÇAMENTO(KM)": km_orcpr,
            "PR-ORÇAMENTO(m²)": area_infraorcpr,
            "PR-PRANCHA ORÇAMENTO": prancha_orcpr,
            "PR-CONTENÇÃO": contencaopr_info,
            "PR-OAE": oaepr_info,
            "PR-FUNDAÇÃO": fundacaopr_info,
            "PR-MEIO AMBIENTE": meioambientepr_info,
            "PR-COMPAT. PROJETOS(m²)": area_infracomppr,
            "PR-PRANCHA COMPAT. PROJETOS": prancha_infracomppr,
            "PR-ELÉTRICO(m²)": area_elepr,
            "PR-KVA": kva_pr,
            "PR-PRANCHA ELÉTRICO": prancha_elepr,
            "PR-EXTENSÃO DE REDE(KM)": area_extpr,
            "PR-PRANCHA EXTENSÃO DE REDE": prancha_extpr,
            "PR-ILUMINAÇÃO PUBLICA(Pontos)": area_iluppr,
            "PR-PRANCHA ILUMINAÇÃO PUBLICA": prancha_iluppr,
            "PS-FUNDAÇÃO": fundacao_ps_info,
            "PS-TOPOGRAFICO": Tipo_topps,
            "PS-CADASTRAL": cadastral_ps,
            "PS-DRONE": drone_os,
            "PS-AREATOP(m²)": area_topsaps,
            "PS-PRANCHA": prancha_topps,
            "PS-ELÉTRICO(m²)": area_elesaps,
            "PS-KVA": kva_ps,
            "PS-PRANCHA ELÉTRICO": prancha_elesaps,
            "PS-ORÇAMENTO(m²)": area_orcsaps,
            "PS-PRANCHA ORÇAMENTO": prancha_orcsaps,
            "PS-REDE COLETORA(m)": m_redecoleps,
            "PS-PRANCHA REDE COLETORA": prancha_redecoleps,
            "PS-INTERCEPTOR(m)": m_interceptorps,
            "PS-PRANCHA INTERCEPTOR": prancha_interceptorps,
            "PS-ELEVATÓRIO(m)": m_elevatoriops,
            "PS-PRANCHA ELEVATÓRIO": prancha_elevatoriopsfdp,
            "PS-ETE Vazão(l/s)": vazao_eteps,
            "PS-PRANCHA ETE": prancha_eteps,
            "PS-ADUTORA(m)": m_adutoraps,
            "PS-PRANCHA ADUTORA": prancha_adutoraps,
            "PS-ETA Vazão(l/s)": vazao_etaps,
            "PS-ETA VOL(m³)": vol_etaps,
            "PS-PRANCHA ETA": prancha_etaps,
            "PS-REDE DE DISTRIBUIÇÃO(m)": m_rededisps,
            "PS-PRANCHA REDE DE DISTRIBUIÇÃO": prancha_rededisps,
            "PS-EXTENSÃO DE REDE(KM)": area_extr,
            "PS-PRANCHA EXTENSÃO DE REDE": prancha_extr,
            "PS-ILUMINAÇÃO PUBLICA(Pontos)": area_ilupu,
            "PS-PRANCHA ILUMINAÇÃO PUBLICA": prancha_ilupu,
            "SONDAGEM": sondagem_info,
            "SOLO": solo_info,
            "ASFALTO": asfalto_info,
            "CONCRETO": concreto_info,
            "AÇO": aco_info,
            "TOPOGRAFIA-CADASTRAL":cadastral_topografia,
            "TOPOGRAFIA-AREA(m²)":area_topografia,
            "TOPOGRAFIA-DRONE":drone_topografia,
            "TOPOGRAFIA-PRANCHA":prancha_topografia
        }

        if pdf_urls_profissionais:
            dados_atestado["PDFS_PROFISSIONAIS"] = pdf_urls_profissionais

        # Filtrar os campos preenchidos antes de salvar no Firebase
        dados_filtrados = {
            chave: valor
            for chave, valor in dados_atestado.items()
            if valor not in [None, "", [], 0.0]
        }

        # Enviar para o Firebase com nome personalizado como ID
        db.collection("atestados").document(nome_atestado_formatado).set(dados_filtrados)

        st.success(f"Atestado `{nome_atestado_formatado}` salvo com sucesso!")
        time.sleep(1)
        st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)
