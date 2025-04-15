import time
import streamlit as st
import pandas as pd
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage


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


abas = st.tabs(["Visualizar","Adicionar", "Editar"])

with abas[1]:
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
        servicos = ["Projeto Edificação", "Projeto Vias Urbanas", "Projeto Rodovias", "Plano Saneamento Básico - PMSB", "Projeto Saneamento", "Projeto Praças e Parques", "Estudos e Projetos Ambientais – Edificação", "Estudos e Projetos Ambientais - Infraestrutura",    "Plano Diretor", "Supervisão_Gerenciamento Edificação", "Supervisão_Gerenciamento Rodovias", "Supervisão_Gerenciamento Vias Urbanas", "Supervisão_Gerenciamento Saneamento", "Diversos", "Sondagem / Controle Tecnológico", "REURB_Regularização Fundiária", "Topografia"]
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
        nome_profissionais_coor = ["Juliana", "Matheus", "Danilo", "Isabela", "Tiago", "Ayana", "Moises", "Márcio", "Sayuri",
                              "Ana", "Christian", "Daniel", "Vicente", "André", "Debora", "Pablo", "Sérgio", "Érika",
                              "Bruno", "Cláudio", "Emanuel", "Grazielle", "Mauricio", "Patricia"]
        nome_profissional_coor = st.selectbox("Nome do Profissional de Coordenação", ["Selecione"] + nome_profissionais_coor)
    with co2:
        nome_profissionais = ["Juliana", "Matheus", "Danilo", "Isabela", "Tiago", "Ayana", "Moises", "Márcio", "Sayuri",
                              "Ana", "Christian", "Daniel", "Vicente", "André", "Debora", "Pablo", "Sérgio", "Érika",
                              "Bruno", "Cláudio", "Emanuel", "Grazielle", "Mauricio", "Patricia"]
        nome_profissional = st.multiselect("Nome dos Profissionais", nome_profissionais)


    objeto = st.text_input("Objeto")

    uploaded_pdf = st.file_uploader("Anexe o Atestado (PDF)", type=["pdf"])

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

    uni_aco = tipo_aco = uni_Concreto = tipo_concreto = uni_asfalto = tipo_asfalto = uni_solos = tipo_solo = m_geo = furos_geo = tipo_sonda = tipo_fundps = area_fusaps = Tipo_topps = cadastral_ps = drone_os = area_topsaps = area_elesaps = kva_ps = area_orcsaps = m_redecoleps = m_interceptorps = m_elevatoriops = vazao_eteps = m_adutoraps = m_elevatoriaps = vazao_etaps = vol_etaps = m_rededisps =  area_urpr = area_paisapr = km_antipr = km_geopr = km_terpr = km_drepr = km_pavpr = m_pavpr = tipo_pavpr = tipo_subasepr = km_sinalpr = tipo_toppr = cadastral_toppr = km_toppr = area_toppr = km_orcpr = area_infraorcprtipo_contpr = m_contpr = m2_contpr = m3_contpr = tipo_oaevupr = area_oaepr = vao_oaepr = tipo_funduvpr = m2_fundpr = tipo_meivupr = uni_meipr = area_infracomppr = reur_habitantes = pdi_habitantes = un_eiainf = area_eiainf = un_pcainf = area_pcainf = un_rasinf = area_rasinf = un_lacinf = area_lacinf = un_rcainf = area_rcainf = un_pradainf = area_pradainf = un_pmgirsinf = area_pmgirsinf = un_piainf = area_piainf = un_rdoinf = area_rdoinf = un_ddoinf = area_ddoinf = un_ddlinf = area_ddlinf = un_ifpminf = area_ifpminf = un_ifpmedi = area_ifpmedi = un_ddledi = area_ddledi = un_ddoedi = area_ddoedi = un_rdoedi = area_rdoedi = un_piaedi = area_piaedi = un_pmgirsedi = area_pmgirsedi = un_pradaedi = area_pradaedi = un_rcaedi = area_rcaedi = area_lacedi = un_lacedi = area_rasedi = un_rasedi = un_pcaedi = area_pcaedi = area_eiaedi = un_eiaedi = area_aa = area_ac = area_ar = area_are = area_cv = edi_mobpep = area_mo = area_ue = area_paisa = tipo_abupep = area_abu = tipo_me3dpep = area_me3d = tipo_estpep = area_est = area_mt = tipo_fupep = area_fu = tipo_conpep = area_con = area_hds = area_irri = area_spci = area_tps = tipo_toppep = area_top = area_orc = area_ele = area_cets = area_spda = area_cftv = area_extr = area_ilupu = area_arcond = area_venex = area_glp = area_hvac = area_comp = area_acus = area_reurb = area_urvi = area_paisavi = km_anti = km_geo = km_ter = km_dre = km_pav = tipo_pavvu = tipo_subasevu = km_sinal = tipo_topvu = km_top = km_orc = area_infraorc = tipo_contvu = m_cont = m2_cont = m3_cont = tipo_oaevu = area_oae = vao_oae = tipo_funduv = m2_fund = tipo_meivu = uni_mei = area_infracomp = pmbs_habitantes = None

    if "Projeto Edificação" in servico or "Projeto Praças e Parques" in servico:
        tipo_servicos = ["ARQUITETÔNICO ANTEPROJETO", "ARQUITETÔNICO CONSTRUÇÃO", "ARQUITETÔNICO REFORMA", "ARQUITETÔNICO RESTAURO", "COMUNICAÇÃO VISUAL", "MOBILIÁRIO", "URBANISTICO", "AS BUILT", "MAQ ELET / 3D", "ESTRUTURAL", "FUNDAÇÃO", "CONTENÇÃO", "HIDROSANITÁRIO", "IRRIGAÇÃO", "SPCI", "TERRAPLENAGEM (PLANTA/SEÇÕES)","TOPOGRAFIA", "ORÇAMENTO", "ELÉTRICO", "CAB. ESTRUTURADO", "SPDA", "ALARME/CFTV", "EXTENSÃO DE REDE", "ILUMINAÇÃO PUBLICA", "AR CONDICIONADO", "VENTILAÇÃO/EXAUSTÃO", "GLP", "GASES MEDICINAIS", "COMPAT. PROJETOS", "ACÚSTICA", "REURB", "PAISAGISTICO"]
        tipo_servico =  st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)


        tp_serv = tipo_servico


        if "ARQUITETÔNICO ANTEPROJETO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nArquitetonico Anteprojeto""")
            with d2:
                area_aa = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_aa")

        if "ARQUITETÔNICO CONSTRUÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nArquitetonico Construção""")
            with d2:
                area_ac = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ac")

        if "ARQUITETÔNICO REFORMA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nArquitetonico Reforma""")
            with d2:
                area_ar = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ar")

        if "ARQUITETÔNICO RESTAURO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nArquitetonico Restauro""")
            with d2:
                area_are = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_are")

        if "COMUNICAÇÃO VISUAL" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nComunicação Visual""")
            with d2:
                area_cv = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cv")

        if "MOBILIÁRIO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMobiliário""")
            with d2:
                edi_mobpep = st.selectbox("Tipo", ["Edificação", "Urbano"], key="edi_mobpep")
            with d3:
                area_mo = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_mo")

        if "URBANISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nUrbanistico""")
            with d2:
                area_ue = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ur")

        if "PAISAGISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nPaisagisco""")
            with d2:
                area_paisa = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisa")

        if "AS BUILT" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nAs Built""")
            with d2:
                tipo_abupep = st.selectbox("Tipo", ["C/ Matteport", "S/ Matteport"], key="tipo_abupep")
            with d3:
                area_abu = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_abu")

        if "MAQ ELET / 3D" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMAQ ELET / 3D""")
            with d2:
                tipo_me3dpep = st.selectbox("Tipo", ["Modelagem 3D", "Maquete Eletrônica"], key="tipo_me3dpep")
            with d3:
                area_me3d = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_me3d")

        if "ESTRUTURAL" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nEstrutural""")
            with d2:
                tipo_estpep = st.selectbox("Tipo", ["Concreto", "Madeira", "Metálica"], key="tipo_estpep")
            with d3:
                area_est = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_est")


        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                tipo_fupep = st.selectbox("Tipo", ["Rasa(sapata, blocos e radier", "Profunda(estaca, tubulaão e caixões", "Rasa e Profunda"], key="tipo_fupep")
            with d3:
                area_fu = st.number_input("M²", min_value=0.0, step=1.0, key="area_fu")

        if "CONTENÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nContenção""")
            with d2:
                tipo_conpep = st.selectbox("Tipo", ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"], key="tipo_conpep")
            with d3:
                area_con = st.number_input("M", min_value=0.0, step=1.0)
            with d4:
                m2 = st.number_input("M²", min_value=0.0, step=1.0, key="area_con")
            with d5:
                m3 = st.number_input("M³", min_value= 0.0, step=0.1)

        if "HIDROSANITÁRIO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nHidrossanitário""")
            with d2:
                area_hds = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_hds")

        if "IRRIGAÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nIrrigação""")
            with d2:
                area_irri = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_irri")

        if "SPCI" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSPCI""")
            with d2:
                area_spci = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_spci")

        if "TERRAPLENAGEM (PLANTA/SEÇÕES)" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nTeraplanagem (Planta/Seções)""")
            with d2:
                area_tps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_tps")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nTopografia""")
            with d2:
                tipo_toppep = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria", "Planialtimétrico georreferenciado", "Planialtimétrico georreferenciado e aerofotogrametrico", "Planialtimétrico aerofotogrametrico"], key="tipo_toppep")
            with d3:
                cadastral = st.selectbox("Cadastral", ["Não", "Sim"])
            with d4:
                drone = st.selectbox("Drone", ["Não", "Sim"])
            with d5:
                area_top = st.number_input("M²", min_value=0.0, step=1.0, key="area_top")

        if "ORÇAMENTO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nOrçamento""")
            with d2:
                area_orc = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_orc")

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
            with d3:
                kva = st.number_input("KVA", min_value=0.0, step=0.1)

        if "CAB. ESTRUTURADO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nCAB. Estruturado""")
            with d2:
                area_cets = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cest")

        if "SPDA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSPDA""")
            with d2:
                area_spda = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_spda")

        if "ALARME/CFTV" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAlarme/CFTV""")
            with d2:
                area_cftv = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cftv")

        if "EXTENSÃO DE REDE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nExtensão de Rede""")
            with d2:
                area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")

        if "ILUMINAÇÃO PUBLICA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nIluminação Publica""")
            with d2:
                area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")

        if "AR CONDICIONADO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAr Condicionado""")
            with d2:
                area_arcond = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_arcond")

        if "VENTILAÇÃO/EXAUSTÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nVentilação/Exaustão""")
            with d2:
                area_venex = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_venex")

        if "GLP" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nGLP""")
            with d2:
                area_glp = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_glp")

        if "GASES MEDICINAIS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nGases Medicinais""")
            with d2:
                area_hvac = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_hvac")

        if "COMPAT. PROJETOS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nCompat. Projetos""")
            with d2:
                area_comp = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_comp")

        if "ACÚSTICA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAcústica""")
            with d2:
                area_acus = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_acus")

        if "REURB" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nREURB""")
            with d2:
                area_reurb = st.number_input("Un. Habitacionais", min_value=0.0, step=1.0, key="area_reurn", format="%.0f")

    if "Supervisão_Gerenciamento Edificação" in servico:

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
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nArquitetonico Anteprojeto""")
            with d2:
                area_aa = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_aa")

        if "ARQUITETÔNICO CONSTRUÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nArquitetonico Construção""")
            with d2:
                area_ac = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ac")

        if "ARQUITETÔNICO REFORMA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nArquitetonico Reforma""")
            with d2:
                area_ar = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ar")

        if "ARQUITETÔNICO RESTAURO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nArquitetonico Restauro""")
            with d2:
                area_are = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_are")

        if "COMUNICAÇÃO VISUAL" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nComunicação Visual""")
            with d2:
                area_cv = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cv")

        if "MOBILIÁRIO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMobiliário""")
            with d2:
                edi_mobpep = st.selectbox("Tipo", ["Edificação", "Urbano"], key="edi_mobpep")
            with d3:
                area_mo = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_mo")

        if "URBANISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nUrbanistico""")
            with d2:
                area_ue = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ur")

        if "PAISAGISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nPaisagisco""")
            with d2:
                area_paisa = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisa")

        if "AS BUILT" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nAs Built""")
            with d2:
                tipo_abupep = st.selectbox("Tipo", ["C/ Matteport", "S/ Matteport"], key="tipo_abupep")
            with d3:
                area_abu = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_abu")

        if "MAQ ELET / 3D" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMAQ ELET / 3D""")
            with d2:
                tipo_me3dpep = st.selectbox("Tipo", ["Modelagem 3D", "Maquete Eletrônica"], key="tipo_me3dpep")
            with d3:
                area_me3d = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_me3d")

        if "ESTRUTURAL" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nEstrutural""")
            with d2:
                tipo_estpep = st.selectbox("Tipo", ["Concreto", "Madeira", "Metálica"], key="tipo_estpep")
            with d3:
                area_est = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_est")

        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                tipo_fupep = st.selectbox("Tipo",
                                          ["Rasa(sapata, blocos e radier", "Profunda(estaca, tubulaão e caixões",
                                           "Rasa e Profunda"], key="tipo_fupep")
            with d3:
                area_fu = st.number_input("M²", min_value=0.0, step=1.0, key="area_fu")

        if "CONTENÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nContenção""")
            with d2:
                tipo_conpep = st.selectbox("Tipo", ["Concreto", "Muro de arrimo", "Gabião", "Terra armada",
                                                    "Cortina atirantada"], key="tipo_conpep")
            with d3:
                area_con = st.number_input("M", min_value=0.0, step=1.0)
            with d4:
                m2 = st.number_input("M²", min_value=0.0, step=1.0, key="area_con")
            with d5:
                m3 = st.number_input("M³", min_value=0.0, step=0.1)

        if "HIDROSANITÁRIO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nHidrossanitário""")
            with d2:
                area_hds = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_hds")

        if "IRRIGAÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nIrrigação""")
            with d2:
                area_irri = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_irri")

        if "SPCI" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSPCI""")
            with d2:
                area_spci = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_spci")

        if "TERRAPLENAGEM (PLANTA/SEÇÕES)" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nTeraplanagem (Planta/Seções)""")
            with d2:
                area_tps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_tps")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nTopografia""")
            with d2:
                tipo_toppep = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria",
                                                    "Planialtimétrico georreferenciado",
                                                    "Planialtimétrico georreferenciado e aerofotogrametrico",
                                                    "Planialtimétrico aerofotogrametrico"], key="tipo_toppep")
            with d3:
                cadastral = st.selectbox("Cadastral", ["Não", "Sim"])
            with d4:
                drone = st.selectbox("Drone", ["Não", "Sim"])
            with d5:
                area_top = st.number_input("M²", min_value=0.0, step=1.0, key="area_top")

        if "ORÇAMENTO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nOrçamento""")
            with d2:
                area_orc = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_orc")

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
            with d3:
                kva = st.number_input("KVA", min_value=0.0, step=0.1)

        if "CAB. ESTRUTURADO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nCAB. Estruturado""")
            with d2:
                area_cets = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cest")

        if "SPDA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSPDA""")
            with d2:
                area_spda = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_spda")

        if "ALARME/CFTV" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAlarme/CFTV""")
            with d2:
                area_cftv = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_cftv")

        if "EXTENSÃO DE REDE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nExtensão de Rede""")
            with d2:
                area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")

        if "ILUMINAÇÃO PUBLICA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nIluminação Publica""")
            with d2:
                area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")

        if "AR CONDICIONADO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAr Condicionado""")
            with d2:
                area_arcond = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_arcond")

        if "VENTILAÇÃO/EXAUSTÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nVentilação/Exaustão""")
            with d2:
                area_venex = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_venex")

        if "GLP" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nGLP""")
            with d2:
                area_glp = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_glp")

        if "GASES MEDICINAIS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nGases Medicinais""")
            with d2:
                area_hvac = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_hvac")

        if "COMPAT. PROJETOS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nCompat. Projetos""")
            with d2:
                area_comp = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_comp")

        if "ACÚSTICA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAcústica""")
            with d2:
                area_acus = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_acus")

        if "REURB" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nREURB""")
            with d2:
                area_reurb = st.number_input("Un. Habitacionais", min_value=0.0, step=1.0, key="area_reurn", format="%.0f")

    if "Projeto Vias Urbanas" in servico:
        tipo_servicos = ["URBANISTICO", "PAISAGISTICO", "ANTEPROJETO DE INFRA", "GEOMÉTRICO", "TERRAPLENAGEM", "HIDROLOGIA", "DRENAGEM", "PAVIMENTAÇÃO", "ESTRUTURAL", "SINALIZAÇÃO", "TOPOGRAFIA", "ORÇAMENTO", "CONTENÇÃO", "OAE", "FUNDAÇÃO", "MEIO AMBIENTE", "COMPAT. PROJETOS", "ELÉTRICO", "EXTENSÃO DE REDE", "ILUMINAÇÃO PUBLICA"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)


        if "URBANISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nUrbanistico""")
            with d2:
                area_urvi = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urvi")

        if "PAISAGISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nPaisagisco""")
            with d2:
                area_paisavi = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisavi")


        if "ANTEPROJETO DE INFRA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAnteprojeto de Infra""")
            with d2:
                km_anti = st.number_input("KM", min_value=0.0, step=1.0, key="km_anti")

        if "GEOMÉTRICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nGeométrico""")
            with d2:
                km_geo = st.number_input("KM", min_value=0.0, step=1.0, key="km_geo")

        if "TERRAPLENAGEM" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nTerraplenagem""")
            with d2:
                km_ter = st.number_input("KM", min_value=0.0, step=1.0, key="km_ter")

        if "DRENAGEM" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nDrenagem""")
            with d2:
                km_dre = st.number_input("KM", min_value=0.0, step=1.0, key="km_dre")

        if "ESTRUTURAL" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nEstrutural""")
            with d2:
                tipo_estpep = st.selectbox("Tipo", ["Concreto", "Madeira", "Metálica"], key="tipo_estpep")
            with d3:
                area_est = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_est")

        if "PAVIMENTAÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nPavimentação""")
            with d2:
                km_pav = st.number_input("KM", min_value=0.0, step=1.0, key="km_pav")
            with d3:
                m_pav = st.number_input("M²", min_value=0.0, step=0.1, key="m_pav")
            with d4:
                tipo_pavvu = st.selectbox("Tipo", ["Não informa", "CBUQ", "CONCRETO", "TSD"], key="tipo_pavvu")
            with d5:
                tipo_subasevu = st.selectbox("Base sub base", ["Não informa", "Mistura na pista","Solo estabilizado granulometricamente"], key="tipo_subasevu")

        if "SINALIZAÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSinalização""")
            with d2:
                km_sinal = st.number_input("KM", min_value=0.0, step=1.0, key="km_sinal")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nTopografia""")
            with d2:
                tipo_topvu = st.selectbox("Tipo",["Planialtimétrico", "Georreferenciado", "Aerofotogrametria", "Planialtimétrico georreferenciado", "Planialtimétrico georreferenciado e aerofotogrametrico", "Planialtimétrico aerofotogrametrico"], key="tipo_topvu")

            with d3:
                cadastral_top = st.selectbox("Cadastral", ["Não", "Sim"])

            with d4:
                km_top = st.number_input("KM", min_value=0.0, step=1.0, key="km_top")

            with d5:
                area_top = st.number_input("M²", min_value=0.0, step=1.0, key="area_top")

        if "ORÇAMENTO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nOrçamento""")
            with d2:
                km_orc = st.number_input("KM", min_value=0.0, step=1.0, key="km_orc")
            with d3:
                area_infraorc = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_infraorc")

        if "CONTENÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nContenção""")
            with d2:
                tipo_contvu = st.selectbox("Tipo", ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"], key="tipo_contvu")
            with d3:
                m_cont = st.number_input("m", min_value=0.0, step=1.0, key="m_cont")
            with d4:
                m2_cont = st.number_input("M²", min_value=0.0, step=0.1, key="m2_cont")
            with d5:
                m3_cont = st.number_input("M³", min_value=0.0, step=0.1, key="m3_cont")

        if "OAE" in tipo_servico:
            d1, d2, d3, d4 = st.columns(4)
            with d1:
                st.write("""###### \nOAE""")
            with d2:
                tipo_oaevu = st.selectbox("Tipo", ["Laudo", "Concreto armado", "Concreto protendido", "Balanço sucessivo", "Ponte estaiada", "Ponte mista"], key="tipo_oaevu")
            with d3:
                area_oae = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_oae")
            with d4:
                vao_oae = st.number_input("VÃO(m)", min_value=0.0, step=0.1, key="vao_oae")

        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                tipo_funduv = st.selectbox("Tipo",["Rasa(sapata, blocos e radier)", "Profunda(estaca, tubulão, caixões)", "Rasa e Profunda"], key="tipo_fundvu")
            with d3:
                m2_fund = st.number_input("M²", min_value=0.0, step=1.0, key="m2_fund")

        if "MEIO AMBIENTE" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMeio Ambiente""")
            with d2:
                tipo_meivu = st.selectbox("Tipo",["EIA/RIMA", "RCA/PCA", "RCA", "PCA", "RADA", "PRADA", "Inventário Florestal"], key="tipo_meivu")
            with d3:
                uni_mei = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_mei", format="%.0f")

        if "COMPAT. PROJETOS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nCompat.Projeto""")
            with d2:
                area_infracomp = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_infracomp")

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
            with d3:
                kva = st.number_input("KVA", min_value=0.0, step=0.1)

        if "EXTENSÃO DE REDE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nExtensão de Rede""")
            with d2:
                area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")

        if "ILUMINAÇÃO PUBLICA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nIluminação Publica""")
            with d2:
                area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")

    if "Supervisão_Gerenciamento Vias Urbanas" in servico:
        tipo_servicos = ["URBANISTICO", "PAISAGISTICO", "ANTEPROJETO DE INFRA", "GEOMÉTRICO", "TERRAPLENAGEM",
                         "HIDROLOGIA", "DRENAGEM", "ESTRUTURAL", "PAVIMENTAÇÃO", "SINALIZAÇÃO", "TOPOGRAFIA", "ORÇAMENTO",
                         "CONTENÇÃO", "OAE", "FUNDAÇÃO", "MEIO AMBIENTE", "COMPAT. PROJETOS", "ILUMINAÇÃO PUBLICA", "EXTENSÃO DE REDE", "ELÉTRICO"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

        if "URBANISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nUrbanistico""")
            with d2:
                area_urvi = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urvi")

        if "PAISAGISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nPaisagisco""")
            with d2:
                area_paisavi = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisavi")

        if "ANTEPROJETO DE INFRA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAnteprojeto de Infra""")
            with d2:
                km_anti = st.number_input("KM", min_value=0.0, step=1.0, key="km_anti")

        if "GEOMÉTRICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nGeométrico""")
            with d2:
                km_geo = st.number_input("KM", min_value=0.0, step=1.0, key="km_geo")

        if "TERRAPLENAGEM" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nTerraplenagem""")
            with d2:
                km_ter = st.number_input("KM", min_value=0.0, step=1.0, key="km_ter")

        if "DRENAGEM" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nDrenagem""")
            with d2:
                km_dre = st.number_input("KM", min_value=0.0, step=1.0, key="km_dre")

        if "ESTRUTURAL" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nEstrutural""")
            with d2:
                tipo_estpep = st.selectbox("Tipo", ["Concreto", "Madeira", "Metálica"], key="tipo_estpep")
            with d3:
                area_est = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_est")

        if "PAVIMENTAÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nPavimentação""")
            with d2:
                km_pav = st.number_input("KM", min_value=0.0, step=1.0, key="km_pav")
            with d3:
                m_pav = st.number_input("M²", min_value=0.0, step=0.1, key="m_pav")
            with d4:
                tipo_pavvu = st.selectbox("Tipo", ["Não informa", "CBUQ", "CONCRETO", "TSD"], key="tipo_pavvu")
            with d5:
                tipo_subasevu = st.selectbox("Base sub base", ["Não informa", "Mistura na pista",
                                                               "Solo estabilizado granulometricamente"],
                                             key="tipo_subasevu")

        if "SINALIZAÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSinalização""")
            with d2:
                km_sinal = st.number_input("KM", min_value=0.0, step=1.0, key="km_sinal")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nTopografia""")
            with d2:
                tipo_topvu = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerofotogrametria",
                                                   "Planialtimétrico georreferenciado",
                                                   "Planialtimétrico georreferenciado e aerofotogrametrico",
                                                   "Planialtimétrico aerofotogrametrico"], key="tipo_topvu")

            with d3:
                cadastral_top = st.selectbox("Cadastral", ["Não", "Sim"])

            with d4:
                km_top = st.number_input("KM", min_value=0.0, step=1.0, key="km_top")

            with d5:
                area_top = st.number_input("M²", min_value=0.0, step=1.0, key="area_top")

        if "ORÇAMENTO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nOrçamento""")
            with d2:
                km_orc = st.number_input("KM", min_value=0.0, step=1.0, key="km_orc")
            with d3:
                area_infraorc = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_infraorc")

        if "CONTENÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nContenção""")
            with d2:
                tipo_contvu = st.selectbox("Tipo", ["Concreto", "Muro de arrimo", "Gabião", "Terra armada",
                                                    "Cortina atirantada"], key="tipo_contvu")
            with d3:
                m_cont = st.number_input("m", min_value=0.0, step=1.0, key="m_cont")
            with d4:
                m2_cont = st.number_input("M²", min_value=0.0, step=0.1, key="m2_cont")
            with d5:
                m3_cont = st.number_input("M³", min_value=0.0, step=0.1, key="m3_cont")

        if "OAE" in tipo_servico:
            d1, d2, d3, d4 = st.columns(4)
            with d1:
                st.write("""###### \nOAE""")
            with d2:
                tipo_oaevu = st.selectbox("Tipo", ["Laudo", "Concreto armado", "Concreto protendido",
                                                   "Balanço sucessivo", "Ponte estaiada", "Ponte mista"],
                                          key="tipo_oaevu")
            with d3:
                area_oae = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_oae")
            with d4:
                vao_oae = st.number_input("VÃO(m)", min_value=0.0, step=0.1, key="vao_oae")

        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                tipo_funduv = st.selectbox("Tipo",
                                           ["Rasa(sapata, blocos e radier)", "Profunda(estaca, tubulão, caixões)",
                                            "Rasa e Profunda"], key="tipo_fundvu")
            with d3:
                m2_fund = st.number_input("M²", min_value=0.0, step=1.0, key="m2_fund")

        if "MEIO AMBIENTE" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMeio Ambiente""")
            with d2:
                tipo_meivu = st.selectbox("Tipo", ["EIA/RIMA", "RCA/PCA", "RCA", "PCA", "RADA", "PRADA",
                                                   "Inventário Florestal"], key="tipo_meivu")
            with d3:
                uni_mei = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_mei", format="%.0f")

        if "COMPAT. PROJETOS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nCompat.Projeto""")
            with d2:
                area_infracomp = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_infracomp")

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
            with d3:
                kva = st.number_input("KVA", min_value=0.0, step=0.1)

        if "EXTENSÃO DE REDE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nExtensão de Rede""")
            with d2:
                area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")

        if "ILUMINAÇÃO PUBLICA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nIluminação Publica""")
            with d2:
                area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")

    if "Projeto Rodovias" in servico:
        tipo_servicos = ["URBANISTICO", "PAISAGISTICO", "ANTEPROJETO DE INFRA", "GEOMÉTRICO", "TERRAPLENAGEM", "HIDROLOGIA", "DRENAGEM", "ESTRUTURAL", "PAVIMENTAÇÃO", "SINALIZAÇÃO", "TOPOGRAFIA", "ORÇAMENTO", "CONTENÇÃO", "OAE", "FUNDAÇÃO", "MEIO AMBIENTE", "COMPAT. PROJETOS", "ELÉTRICO", "ILUMINAÇÃO PUBLICA", "EXTENSÃO DE REDE"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

        if "URBANISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nUrbanistico""")
            with d2:
                area_urpr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urpr")

        if "PAISAGISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nPaisagisco""")
            with d2:
                area_paisapr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisapr")

        if "ANTEPROJETO DE INFRA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAnteprojeto de Infra""")
            with d2:
                km_antipr = st.number_input("KM", min_value=0.0, step=1.0, key="km_antipr")

        if "GEOMÉTRICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nGeométrico""")
            with d2:
                km_geopr = st.number_input("KM", min_value=0.0, step=1.0, key="km_geopr")

        if "TERRAPLENAGEM" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nTerraplenagem""")
            with d2:
                km_terpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_terpr")

        if "DRENAGEM" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nDrenagem""")
            with d2:
                km_drepr = st.number_input("KM", min_value=0.0, step=1.0, key="km_drepr")

        if "ESTRUTURAL" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nEstrutural""")
            with d2:
                tipo_estpep = st.selectbox("Tipo", ["Concreto", "Madeira", "Metálica"], key="tipo_estpep")
            with d3:
                area_est = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_est")

        if "PAVIMENTAÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nPavimentação""")
            with d2:
                km_pavpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_pavpr")
            with d3:
                m_pavpr = st.number_input("M²", min_value=0.0, step=0.1, key="m_pavpr")
            with d4:
                tipo_pavpr = st.selectbox("Tipo", ["Não informa", "CBUQ", "CONCRETO", "TSD"], key="tipo_pavpr")
            with d5:
                tipo_subasepr = st.selectbox("Base sub base", ["Não informa", "Mistura na pista", "Solo estabilizado granulometricamente"], key="tipo_subasepr")

        if "SINALIZAÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSinalização""")
            with d2:
                km_sinalpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_sinalpr")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nTopografia""")
            with d2:
                tipo_toppr = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerofotogrametria", "Planialtimétrico georreferenciado", "Planialtimétrico georreferenciado e aerofotogrametrico", "Planialtimétrico aerofotogrametrico"], key="tipo_toppr")

            with d3:
                cadastral_toppr = st.selectbox("Cadastral", ["Não", "Sim"])

            with d4:
                km_toppr = st.number_input("KM", min_value=0.0, step=1.0, key="km_toppr")

            with d5:
                area_toppr = st.number_input("M²", min_value=0.0, step=1.0, key="area_toppr")

        if "ORÇAMENTO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nOrçamento""")
            with d2:
                km_orcpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_orcpr")
            with d3:
                area_infraorcpr = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_infraorcpr")

        if "CONTENÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nContenção""")
            with d2:
                tipo_contpr = st.selectbox("Tipo", ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"], key="tipo_contpr")
            with d3:
                m_contpr = st.number_input("m", min_value=0.0, step=1.0, key="m_contpr")
            with d4:
                m2_contpr = st.number_input("M²", min_value=0.0, step=0.1, key="m2_contpr")
            with d5:
                m3_contpr = st.number_input("M³", min_value=0.0, step=0.1, key="m3_contpr")

        if "OAE" in tipo_servico:
            d1, d2, d3, d4 = st.columns(4)
            with d1:
                st.write("""###### \nOAE""")
            with d2:
                tipo_oaevupr = st.selectbox("Tipo", ["Laudo", "Concreto armado", "Concreto protendido", "Balanço sucessivo", "Ponte estaiada", "Ponte mista"], key="tipo_oaevupr")
            with d3:
                area_oaepr = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_oaepr")
            with d4:
                vao_oaepr = st.number_input("VÃO(m)", min_value=0.0, step=0.1, key="vao_oaepr")

        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                tipo_funduvpr = st.selectbox("Tipo", ["Rasa(sapata, blocos e radier)", "Profunda(estaca, tubulão, caixões)", "Rasa e Profunda"], key="tipo_fundvupr")
            with d3:
                m2_fundpr = st.number_input("M²", min_value=0.0, step=1.0, key="m2_fundpr")

        if "MEIO AMBIENTE" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMeio Ambiente""")
            with d2:
                tipo_meivupr = st.selectbox("Tipo", ["EIA/RIMA", "RCA/PCA", "RCA", "PCA", "RADA", "PRADA",
                                                   "Inventário Florestal"], key="tipo_meivupr")
            with d3:
                uni_meipr = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_meipr", format="%.0f")

        if "COMPAT. PROJETOS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nCompat.Projeto""")
            with d2:
                area_infracomppr = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_infracomppr")

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
            with d3:
                kva = st.number_input("KVA", min_value=0.0, step=0.1)

        if "EXTENSÃO DE REDE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nExtensão de Rede""")
            with d2:
                area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")

        if "ILUMINAÇÃO PUBLICA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nIluminação Publica""")
            with d2:
                area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")

    if "Supervisão_Gerenciamento Rodovias" in servico:
        tipo_servicos = ["URBANISTICO", "PAISAGISTICO", "ANTEPROJETO DE INFRA", "GEOMÉTRICO", "TERRAPLENAGEM",
                         "HIDROLOGIA", "DRENAGEM", "ESTRUTURAL", "PAVIMENTAÇÃO", "SINALIZAÇÃO", "TOPOGRAFIA", "ORÇAMENTO",
                         "CONTENÇÃO", "OAE", "FUNDAÇÃO", "MEIO AMBIENTE", "COMPAT. PROJETOS", "ILUMINAÇÃO PUBLICA", "EXTENSÃO DE REDE", "ELÉTRICO"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

        if "URBANISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nUrbanistico""")
            with d2:
                area_urpr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urpr")

        if "PAISAGISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nPaisagisco""")
            with d2:
                area_paisapr = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisapr")

        if "ANTEPROJETO DE INFRA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAnteprojeto de Infra""")
            with d2:
                km_antipr = st.number_input("KM", min_value=0.0, step=1.0, key="km_antipr")

        if "GEOMÉTRICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nGeométrico""")
            with d2:
                km_geopr = st.number_input("KM", min_value=0.0, step=1.0, key="km_geopr")

        if "TERRAPLENAGEM" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nTerraplenagem""")
            with d2:
                km_terpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_terpr")

        if "DRENAGEM" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nDrenagem""")
            with d2:
                km_drepr = st.number_input("KM", min_value=0.0, step=1.0, key="km_drepr")

        if "ESTRUTURAL" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nEstrutural""")
            with d2:
                tipo_estpep = st.selectbox("Tipo", ["Concreto", "Madeira", "Metálica"], key="tipo_estpep")
            with d3:
                area_est = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_est")

        if "PAVIMENTAÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nPavimentação""")
            with d2:
                km_pavpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_pavpr")
            with d3:
                m_pavpr = st.number_input("M²", min_value=0.0, step=0.1, key="m_pavpr")
            with d4:
                tipo_pavpr = st.selectbox("Tipo", ["Não informa", "CBUQ", "CONCRETO", "TSD"], key="tipo_pavpr")
            with d5:
                tipo_subasepr = st.selectbox("Base sub base", ["Não informa", "Mistura na pista",
                                                               "Solo estabilizado granulometricamente"],
                                             key="tipo_subasepr")

        if "SINALIZAÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSinalização""")
            with d2:
                km_sinalpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_sinalpr")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nTopografia""")
            with d2:
                tipo_toppr = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerofotogrametria",
                                                   "Planialtimétrico georreferenciado",
                                                   "Planialtimétrico georreferenciado e aerofotogrametrico",
                                                   "Planialtimétrico aerofotogrametrico"], key="tipo_toppr")

            with d3:
                cadastral_toppr = st.selectbox("Cadastral", ["Não", "Sim"])

            with d4:
                km_toppr = st.number_input("KM", min_value=0.0, step=1.0, key="km_toppr")

            with d5:
                area_toppr = st.number_input("M²", min_value=0.0, step=1.0, key="area_toppr")

        if "ORÇAMENTO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nOrçamento""")
            with d2:
                km_orcpr = st.number_input("KM", min_value=0.0, step=1.0, key="km_orcpr")
            with d3:
                area_infraorcpr = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_infraorcpr")

        if "CONTENÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nContenção""")
            with d2:
                tipo_contpr = st.selectbox("Tipo", ["Concreto", "Muro de arrimo", "Gabião", "Terra armada",
                                                    "Cortina atirantada"], key="tipo_contpr")
            with d3:
                m_contpr = st.number_input("m", min_value=0.0, step=1.0, key="m_contpr")
            with d4:
                m2_contpr = st.number_input("M²", min_value=0.0, step=0.1, key="m2_contpr")
            with d5:
                m3_contpr = st.number_input("M³", min_value=0.0, step=0.1, key="m3_contpr")

        if "OAE" in tipo_servico:
            d1, d2, d3, d4 = st.columns(4)
            with d1:
                st.write("""###### \nOAE""")
            with d2:
                tipo_oaevupr = st.selectbox("Tipo", ["Laudo", "Concreto armado", "Concreto protendido",
                                                     "Balanço sucessivo", "Ponte estaiada", "Ponte mista"],
                                            key="tipo_oaevupr")
            with d3:
                area_oaepr = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_oaepr")
            with d4:
                vao_oaepr = st.number_input("VÃO(m)", min_value=0.0, step=0.1, key="vao_oaepr")

        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                tipo_funduvpr = st.selectbox("Tipo",
                                             ["Rasa(sapata, blocos e radier)", "Profunda(estaca, tubulão, caixões)",
                                              "Rasa e Profunda"], key="tipo_fundvupr")
            with d3:
                m2_fundpr = st.number_input("M²", min_value=0.0, step=1.0, key="m2_fundpr")

        if "MEIO AMBIENTE" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMeio Ambiente""")
            with d2:
                tipo_meivupr = st.selectbox("Tipo", ["EIA/RIMA", "RCA/PCA", "RCA", "PCA", "RADA", "PRADA",
                                                     "Inventário Florestal"], key="tipo_meivupr")
            with d3:
                uni_meipr = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_meipr", format="%.0f")

        if "COMPAT. PROJETOS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nCompat.Projeto""")
            with d2:
                area_infracomppr = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_infracomppr")

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
            with d3:
                kva = st.number_input("KVA", min_value=0.0, step=0.1)

        if "EXTENSÃO DE REDE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nExtensão de Rede""")
            with d2:
                area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")

        if "ILUMINAÇÃO PUBLICA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nIluminação Publica""")
            with d2:
                area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")

    if "Plano Saneamento Básico - PMSB" in servico:
        tipo_servico = "Plano Saneamento Básico - PMSB"
        pmbs_habitantes = st.number_input("Número de Habitantes", min_value=0.0, step=1.0, format="%.0f")

    if "Sondagem / Controle Tecnológico" in servico:
        tipo_servicos = ["SONDAGEM", "SOLO", "ASFALTO", "ENSAIOS", "CONCRETO", "AÇO"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

        if "SONDAGEM" in tipo_servico:
            d1, d2,d3, d4 = st.columns(4)
            with d1:
                st.write("""###### \nSondagem""")
            with d2:
                tipo_sonda = st.selectbox("Tipo", ["SPT", "Rotativa", "Trado", "Mista"])
            with d3:
                furos_geo = st.number_input("Furos", min_value=0.0, step=1.0, format="%.0f", key="furos_geo")
            with d4:
                m_geo = st.number_input("Metros", min_value=0.0, step=0.1, key="m_geo")

        if "SOLO" in tipo_servico:
            d1, d2,d3 = st.columns(3)
            with d1:
                st.write("""###### \nSolo""")
            with d2:
                tipo_solo = st.selectbox("Tipo", ["LL – Limite de Liquidez", "LP – Limite de Plasticidade", "LC – Limite de Contração", "GPS - Granulometria por Peneiramento e Sedimentação", "ISC - Indice de Suporte Califórnia (CBR)", "CPN - Compactação Proctor Normal", "CPI – Compactação Proctor Internormal", "CPM – Compactação Proctor Modificado", "CIUSAT - Compressão Triaxial", "CIDSAT - Compressão Triaxial", "UUSAT - Compressão Triaxial", "MES – Peso/Massa específico dos Grãos", "W- Teor de Umidade Natural", "SCS – Dispersão Sedimentométrico Comparativo", "PCT - Permeabilidade em Câmara Triaxial", "Adensamento", "Cisalhamento", "Porosidade", "IN SITU (Frasco de Areia)", "IVmáx – Ensaio de Determinação de Índice de Vazios Máximo", "IVmin – Ensaio de Determinação de Índice de Vazios Mínimo", "BH – Balança Hidrostática", "ADN – Adensamento Oedométrico Unidimensional"])
            with d3:
                uni_solos = st.number_input("Unidade", min_value=0.0, step=1.0, format="%.0f" ,key="uni_solos")

        if "ASFALTO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nAsfalto""")
            with d2:
                tipo_asfalto = st.selectbox("Tipo", ["Viga Benkelman", "Teor de Betume", "Estabilidade Marshall", "Granulometria", "Densidade Aparente/Porosidade", "Compressão"])
            with d3:
                uni_asfalto = st.number_input("Unidade", min_value=0.0, step=1.0,format="%.0f" ,key="uni_asfalto")

        if "CONCRETO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nConcreto""")
            with d2:
                tipo_concreto = st.selectbox("Tipo", ["Compressão axial (ruptura)", "Consistência (Slump)"])
            with d3:
                uni_Concreto = st.number_input("Unidade", min_value=0.0, step=1.0, format="%0.f", key="uni_concreto")

        if "AÇO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nAço""")
            with d2:
                tipo_aco = st.selectbox("Tipo", ["LE – Limite de Escoamento", "LR – Limite de Resistência", "A – Alongamento", "Dobramento"])
            with d3:
                uni_aco = st.number_input("Unidade", min_value=0.0, step=1.0, format="%0.f", key="uni_aco")

    if "Projeto Saneamento" in servico:
        tipo_servicos = ["FUNDAÇÃO", "TOPOGRAFIA", "ELÉTRICO", "ORÇAMENTO", "REDE COLETORA", "INTERCEPTOR", "ELEVATÓRIO", "ETE", "ADUTORA", "ELEVATÓRIA", "ETA", "REDE DE DISTRIBUIÇÃO", "ILUMINAÇÃO PUBLICA", "EXTENSÃO DE REDE", "ELÉTRICO"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)


        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                tipo_fundps = st.selectbox("Tipo", ["Rasa(sapata, blocos e radier", "Profunda(estaca, tubulaão e caixões", "Rasa e Profunda"])
            with d3:
                area_fusaps = st.number_input("M²", min_value=0.0, step=1.0, key="area_fusaps")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nTopografia""")
            with d2:
                Tipo_topps = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria", "Planialtimétrico georreferenciado", "Planialtimétrico georreferenciado e aerofotogrametrico", "Planialtimétrico aerofotogrametrico"])
            with d3:
                cadastral_ps = st.selectbox("Cadastral", ["Não", "Sim"], key="cadastral_ps")
            with d4:
                drone_os = st.selectbox("Drone", ["Não", "Sim"], key="drone_os")
            with d5:
                area_topsaps = st.number_input("M²", min_value=0.0, step=1.0, key="area_topsaps")

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_elesaps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_elesaps")
            with d3:
                kva_ps = st.number_input("KVA", min_value=0.0, step=0.1, key="kva_ps")

        if "ORÇAMENTO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nOrçamento""")
            with d2:
                area_orcsaps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_orcsaps")

        if "REDE COLETORA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nRede Coletora""")
            with d2:
                    m_redecoleps = st.number_input("M", min_value=0.0, step=1.0, key= "m_redecoleps")

        if "INTERCEPTOR" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nInterceptor""")
            with d2:
                m_interceptorps = st.number_input("M", min_value=0.0, step=1.0, key="m_interceptorps")

        if "ELEVATÓRIO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nElevatório""")
            with d2:
                m_elevatoriops = st.number_input("M", min_value=0.0, step=1.0, key="m_elevatoriops")

        if "ETE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nETE""")
            with d2:
                vazao_eteps = st.number_input("Vazão(l/s)", min_value=0.0, step=1.0, key="vazao_eteps")

        if "ADUTORA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAdutora""")
            with d2:
                m_adutoraps = st.number_input("M", min_value=0.0, step=1.0, key="m_adutoraps")

        if "ELEVATÓRIA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nElevatória""")
            with d2:
                m_elevatoriaps = st.number_input("M", min_value=0.0, step=1.0, key="m_elevatoriaps")

        if "ETA" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nETA""")
            with d2:
                vazao_etaps = st.number_input("Vazão(l/s)", min_value=0.0, step=1.0, key="vazao_etaps")
            with d3:
                vol_etaps = st.number_input("VOL(m³)", min_value=0.0, step=1.0, key="vol_etaps")

        if "REDE DE DISTRIBUIÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nRede de Distribuição""")
            with d2:
                m_rededisps = st.number_input("M", min_value=0.0, step=1.0, key="m_rededisps")

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
            with d3:
                kva = st.number_input("KVA", min_value=0.0, step=0.1)

        if "EXTENSÃO DE REDE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nExtensão de Rede""")
            with d2:
                area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")

        if "ILUMINAÇÃO PUBLICA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nIluminação Publica""")
            with d2:
                area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")

    if "Supervisão_Gerenciamento Saneamento" in servico:
        tipo_servicos = ["FUNDAÇÃO", "TOPOGRAFIA", "ELÉTRICO", "ORÇAMENTO", "REDE COLETORA", "INTERCEPTOR",
                         "ELEVATÓRIO", "ETE", "ADUTORA", "ELEVATÓRIA", "ETA", "REDE DE DISTRIBUIÇÃO", "ILUMINAÇÃO PUBLICA", "EXTENSÃO DE REDE", "ELÉTRICO"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                tipo_fundps = st.selectbox("Tipo",
                                           ["Rasa(sapata, blocos e radier", "Profunda(estaca, tubulaão e caixões",
                                            "Rasa e Profunda"])
            with d3:
                area_fusaps = st.number_input("M²", min_value=0.0, step=1.0, key="area_fusaps")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
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

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_elesaps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_elesaps")
            with d3:
                kva_ps = st.number_input("KVA", min_value=0.0, step=0.1, key="kva_ps")

        if "ORÇAMENTO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nOrçamento""")
            with d2:
                area_orcsaps = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_orcsaps")

        if "REDE COLETORA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nRede Coletora""")
            with d2:
                m_redecoleps = st.number_input("M", min_value=0.0, step=1.0, key="m_redecoleps")

        if "INTERCEPTOR" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nInterceptor""")
            with d2:
                m_interceptorps = st.number_input("M", min_value=0.0, step=1.0, key="m_interceptorps")

        if "ELEVATÓRIO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nElevatório""")
            with d2:
                m_elevatoriops = st.number_input("M", min_value=0.0, step=1.0, key="m_elevatoriops")

        if "ETE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nETE""")
            with d2:
                vazao_eteps = st.number_input("Vazão(l/s)", min_value=0.0, step=1.0, key="vazao_eteps")

        if "ADUTORA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAdutora""")
            with d2:
                m_adutoraps = st.number_input("M", min_value=0.0, step=1.0, key="m_adutoraps")

        if "ELEVATÓRIA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nElevatória""")
            with d2:
                m_elevatoriaps = st.number_input("M", min_value=0.0, step=1.0, key="m_elevatoriaps")

        if "ETA" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nETA""")
            with d2:
                vazao_etaps = st.number_input("Vazão(l/s)", min_value=0.0, step=1.0, key="vazao_etaps")
            with d3:
                vol_etaps = st.number_input("VOL(m³)", min_value=0.0, step=1.0, key="vol_etaps")

        if "REDE DE DISTRIBUIÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nRede de Distribuição""")
            with d2:
                m_rededisps = st.number_input("M", min_value=0.0, step=1.0, key="m_rededisps")

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_ele = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_ele")
            with d3:
                kva = st.number_input("KVA", min_value=0.0, step=0.1)

        if "EXTENSÃO DE REDE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nExtensão de Rede""")
            with d2:
                area_extr = st.number_input("KM", min_value=0.0, step=0.1, key="area_extr")

        if "ILUMINAÇÃO PUBLICA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nIluminação Publica""")
            with d2:
                area_ilupu = st.number_input("Pontos", min_value=0.0, step=1.0, key="area_ilupu")

    if "Estudos e Projetos Ambientais – Edificação" in servico:
        tipo_servicos = ["EIA/RIMA", "PCA – Plano de Controle Ambiental", "RAS – Relatório Ambiental Simplificado", "Licença Ambiental Concomitante", "RCA – Relatório de Controle Ambiental", "PRADA – Projeto de Recuperação de Águas Degradadas e Alteradas", "PMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos", "PIA – Plano de Intervenção Ambiental", "Relatório de Outorga", "Dispensa de outorga", "Dispensa de licenciamento", "Inventário florestal/Plano Manejo"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

        if "EIA/RIMA" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nEIA/RIMA""")
            with col2:
                un_eiaedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_eiaedi")
            with col3:
                area_eiaedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_eiaedi")

        if "PCA – Plano de Controle Ambiental" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nPCA – Plano de Controle Ambiental""")
            with col2:
                un_pcaedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pcaedi")
            with col3:
                area_pcaedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F",key="area_pcaedi")

        if "RAS – Relatório Ambiental Simplificado" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nRAS – Relatório Ambiental Simplificado""")
            with col2:
                un_rasedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rasedi")
            with col3:
                area_rasedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_rasedi")

        if "Licença Ambiental Concomitante" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nLicença Ambiental Concomitante""")
            with col2:
                un_lacedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_lacedi")
            with col3:
                area_lacedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_lacedi")

        if "RCA – Relatório de Controle Ambiental" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nRCA – Relatório de Controle Ambiental""")
            with col2:
                un_rcaedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rcaedi")
            with col3:
                area_rcaedi  = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_rcaedi")

        if "PRADA – Projeto de Recuperação de Águas Degradadas e Alteradas" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nPRADA – Projeto de Recuperação de Águas Degradadas e Alteradas""")
            with col2:
                un_pradaedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pradaedi")
            with col3:
                area_pradaedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_pradaedi")

        if "PMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nPMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos""")
            with col2:
                un_pmgirsedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pmgirsedi")
            with col3:
                area_pmgirsedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_pmgirsedi")

        if "PIA – Plano de Intervenção Ambiental" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nPIA – Plano de Intervenção Ambiental""")
            with col2:
                un_piaedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f",key="un_piaedi")
            with col3:
                area_piaedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_piaedi")

        if "Relatório de Outorga" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nRelatório de Outorga""")
            with col2:
                un_rdoedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rdoedi")
            with col3:
                area_rdoedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_rdoedi")

        if "Dispensa de outorga" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nDispensa de outorga""")
            with col2:
                un_ddoedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ddoedi")
            with col3:
                area_ddoedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_ddoedi")

        if "Dispensa de licenciamento" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nDispensa de licenciamento""")
            with col2:
                un_ddledi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ddledi")
            with col3:
                area_ddledi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_ddledi")

        if "Inventário florestal/Plano Manejo" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nInventário florestal/Plano Manejo""")
            with col2:
                un_ifpmedi = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ifpmedi")
            with col3:
                area_ifpmedi = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_ifpmedi")

    if "Estudos e Projetos Ambientais - Infraestrutura" in servico:
        tipo_servicos = ["EIA/RIMA", "PCA – Plano de Controle Ambiental", "RAS – Relatório Ambiental Simplificado", "Licença Ambiental Concomitante", "RCA – Relatório de Controle Ambiental", "PRADA – Projeto de Recuperação de Águas Degradadas e Alteradas", "PMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos", "PIA – Plano de Intervenção Ambiental", "Relatório de Outorga", "Dispensa de outorga", "Dispensa de licenciamento", "Inventário florestal/Plano Manejo"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

        if "EIA/RIMA" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nEIA/RIMA""")
            with col2:
                un_eiainf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_eiainf")
            with col3:
                area_eiainf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_eiainf")

        if "PCA – Plano de Controle Ambiental" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nPCA – Plano de Controle Ambiental""")
            with col2:
                un_pcainf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pcainf")
            with col3:
                area_pcainf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_pcainf")

        if "RAS – Relatório Ambiental Simplificado" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nRAS – Relatório Ambiental Simplificado""")
            with col2:
                un_rasinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rasinf")
            with col3:
                area_rasinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_rasinf")

        if "Licença Ambiental Concomitante" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nLicença Ambiental Concomitante""")
            with col2:
                un_lacinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_lacinf")
            with col3:
                area_lacinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_lacinf")

        if "RCA – Relatório de Controle Ambiental" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nRCA – Relatório de Controle Ambiental""")
            with col2:
                un_rcainf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rcainf")
            with col3:
                area_rcainf  = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_rcainf")

        if "PRADA – Projeto de Recuperação de Águas Degradadas e Alteradas" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nPRADA – Projeto de Recuperação de Águas Degradadas e Alteradas""")
            with col2:
                un_pradainf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pradainf")
            with col3:
                area_pradainf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_pradainf")

        if "PMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nPMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos""")
            with col2:
                un_pmgirsinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_pmgirsinf")
            with col3:
                area_pmgirsinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_pmgirsinf")

        if "PIA – Plano de Intervenção Ambiental" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nPIA – Plano de Intervenção Ambiental""")
            with col2:
                un_piainf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_piainf")
            with col3:
                area_piainf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_piainf")

        if "Relatório de Outorga" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nRelatório de Outorga""")
            with col2:
                un_rdoinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_rdoinf")
            with col3:
                area_rdoinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_rdoinf")

        if "Dispensa de outorga" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nDispensa de outorga""")
            with col2:
                un_ddoinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ddoinf")
            with col3:
                area_ddoinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_ddoinf")

        if "Dispensa de licenciamento" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nDispensa de licenciamento""")
            with col2:
                un_ddlinf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ddlinf")
            with col3:
                area_ddlinf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_ddlinf")

        if "Inventário florestal/Plano Manejo" in tipo_servico:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("""###### \nInventário florestal/Plano Manejo""")
            with col2:
                un_ifpminf = st.number_input("UN", min_value=0.0, step=1.0, format="%.0f", key="un_ifpminf")
            with col3:
                area_ifpminf = st.number_input("Área", min_value=0.0, step=1.0, format="%.2F", key="area_ifpminf")

    if "Plano Diretor" in servico:
        tipo_servico = "Plano Diretor"
        pdi_habitantes = st.number_input("Número de Habitantes", min_value=0.0, step=1.0, format="%.0f")

    if "Diversos" in servico:
        tipo_servico = "Diversos"

    if "Topografia" in servico:
        st.subheader("Topografia")
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            tipo_servico = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria", "Planialtimétrico georreferenciado", "Planialtimétrico georreferenciado e aerofotogrametrico", "Planialtimétrico aerofotogrametrico"])
        with d2:
            cadastral = st.selectbox("Cadastral", ["Não", "Sim"])
        with d3:
            drone = st.selectbox("Drone", ["Não", "Sim"])
        with d4:
            area_topp = st.number_input("M²", min_value=0.0, step=0.1, key="area_topp")

    if "REURB_Regularização Fundiária" in servico:
        tipo_servico = "REURB_Regularização Fundiária"
        reur_habitantes = st.number_input("Unidade Habitacional", min_value=0.0, step=1.0, format="%.0f")

    if cliente and data_inicial and servico:
        nome_atestado = f"{empresas_grupo}_{cliente}_{cat_numero}_{servico}"
        nome_atestado_formatado = nome_atestado.replace("/", "-")
    else:
        nome_atestado_formatado = None

    st.write(f"Nome do Atestado: `{nome_atestado_formatado}`")

    if st.button("Enviar"):
        if nome_atestado:
            pdf_url = None

            # Faz upload do PDF para o Firebase Storage, se houver
            if uploaded_pdf is not None:
                nome_arquivo_pdf = f"atestados_pdfs/{nome_atestado}.pdf"
                bucket = storage.bucket()
                blob = bucket.blob(nome_arquivo_pdf)
                blob.upload_from_file(uploaded_pdf, content_type="application/pdf")
                blob.make_public()
                pdf_url = blob.public_url

            # Criar dicionário com os dados
            dados_atestado = {
                "Empresa": empresas_grupo,
                "Cliente": cliente,
                "Servico": servico,
                "Profissional-Cordenação": nome_profissional_coor,
                "Profissional": nome_profissional,
                "Disciplina": tipo_servico,
                "Participação": participacao,
                "CAT": cat_numero,
                "Data Início": str(data_inicial),
                "Data Final": str(data_final),
                "Objeto": objeto,
                "Extensão (km)": extensao,
                "Área (m²)": area,
                "BIM": bim,
                "Patrimônio Tombado": patrimonio,
                "ARQUITETÔNICO ANTEPROJETO(m²)": area_aa,
                "ARQUITETÔNICO CONSTRUÇÃO(m²)": area_ac,
                "ARQUITETÔNICO REFORMA(m²)": area_ar,
                "ARQUITETÔNICO RESTAURO(m²)": area_are,
                "COMUNICAÇÃO VISUAL(m²)": area_cv,
                "TIPO MOBILIÁRIO": edi_mobpep,
                "MOBILIÁRIO(m²)": area_mo,
                "URBANISTICO(m²)": area_ue,
                "PAISAGISTICO(m²)": area_paisa,
                "TIPO AS BUILT": tipo_abupep,
                "AS BUILT(m²)": area_abu,
                "TIPO MAQ ELET/3D": tipo_me3dpep,
                "MAQ ELET / 3D(m²)": area_me3d,
                "TIPO ESTRUTURAL": tipo_estpep,
                "ESTRUTURAL(m²)": area_est,
                "METÁLICA(m²)": area_mt,
                "TIPO FUNDAÇÃO": tipo_fupep,
                "FUNDAÇÃO(m²)": area_fu,
                "TIPO CONTENÇÃO": tipo_conpep,
                "CONTENÇÃO(m²)": area_con,
                "HIDROSANITÁRIO(m²)": area_hds,
                "IRRIGAÇÃO(m²)": area_irri,
                "SPCI(m²)": area_spci,
                "TERRAPLENAGEM (PLANTA/SEÇÕES)(m²)": area_tps,
                "TIPO TOPOGRAFIA": tipo_toppep,
                "TOPOGRAFIA(m²)": area_top,
                "ORÇAMENTO(m²)": area_orc,
                "ELÉTRICO(m²)": area_ele,
                "CAB. ESTRUTURADO(m²)": area_cets,
                "SPDA(m²)": area_spda,
                "ALARME/CFTV(m²)": area_cftv,
                "EXTENSÃO DE REDE(km)": area_extr,
                "ILUMINAÇÃO PUBLICA(pontos)": area_ilupu,
                "AR CONDICIONADO(m²)": area_arcond,
                "VENTILAÇÃO/EXAUSTÃO(m²)": area_venex,
                "GLP(m²)": area_glp,
                "GASES MEDICINAIS(m²)": area_hvac,
                "COMPAT. PROJETOS(m²)": area_comp,
                "ACÚSTICA(m²)": area_acus,
                "Un.Habitacionais": area_reurb,
                "VU-URBANISTICO(²)": area_urvi,
                "VU-PAISAGISCO(m²)": area_paisavi,
                "VU-ANTEPROJETO DE INFRA(km)": km_anti,
                "VU-GEOMÉTRICO(km)": km_geo,
                "VU-TERRAPLENAGEM(km)": km_ter,
                "VU-DRENAGEM(km)": km_dre,
                "VU-PAVIMENTAÇÃO(km)": km_pav,
                "VU-TIPO PAVIMENTAÇÃO": tipo_pavvu,
                "VU-SUB BASE": tipo_subasevu,
                "VU-SINALIZAÇÃO(km)": km_sinal,
                "VU-TIPO TOPOGRAFIA": tipo_topvu,
                "VU-TOPOGRAFIA(km)": km_top,
                "VU-ORCAMENTO(km)": km_orc,
                "VU-ORCAMENTO(m²)": area_infraorc,
                "VU-TIPO CONTENCAO": tipo_contvu,
                "VU-CONTENCAO(m²)": m2_cont,
                "VU-TIPO OAE": tipo_oaevu,
                "VU-OAE(m²)": area_oae,
                "VU-TIPO FUNDACAO": tipo_funduv,
                "VU-FUNDACAO(m²)": m2_fund,
                "VU-TIPO MEIO AMBIENTE": tipo_meivu,
                "VU-UNIDADE MEIO AMBIENTE": uni_mei,
                "VU-COMPAT. PROJETOS": area_infracomp,
                "PMSB-NUMERO HABITANTES": pmbs_habitantes,
                "EIAEDI-UN": un_eiaedi,
                "EIAEDI-AREA": area_eiaedi,
                "LACEDI-AREA": area_lacedi,
                "LACEDI-UN": un_lacedi,
                "RASEDI-AREA": area_rasedi,
                "RASEDI-UN": un_rasedi,
                "PCAEDI-UN": un_pcaedi,
                "PCAEDI-AREA": area_pcaedi,
                "RCAEDI-UN": un_rcaedi,
                "RCAEDI-AREA": area_rcaedi,
                "PRADAEDI-UN": un_pradaedi,
                "PRADAEDI-AREA": area_pradaedi,
                "PMGIRSEDI-AREA": un_pmgirsedi,
                "PMGIRSEDI-UNI": area_pmgirsedi,
                "PIAEDI-UN": un_piaedi,
                "PIAEDI-AREA": area_piaedi,
                "RDOEDI-UN": un_rdoedi,
                "RDOEDI-AREA": area_rdoedi,
                "DDOEDI-UN": un_ddoedi,
                "DDOEDI-AREA": area_ddoedi,
                "DDLEDI-UN": un_ddledi,
                "DDLEDI-AREA": area_ddledi,
                "IFPMEDI-UN": un_ifpmedi,
                "IFPMEDI-AREA": area_ifpmedi,
                "EIAINF-UN": un_eiainf,
                "EIAINF-AREA": area_eiainf,
                "LACINF-AREA": area_lacinf,
                "LACINF-UN": un_lacinf,
                "RASINF-AREA": area_rasinf,
                "RASINF-UN": un_rasinf,
                "PCAINF-UN": un_pcainf,
                "PCAINF-AREA": area_pcainf,
                "RCAINF-UN": un_rcainf,
                "RCAINF-AREA": area_rcainf,
                "PRADAINF-UN": un_pradainf,
                "PRADAINF-AREA": area_pradainf,
                "PMGIRSINF-AREA": un_pmgirsinf,
                "PMGIRSINF-UNI": area_pmgirsinf,
                "PIAINF-UN": un_piainf,
                "PIAINF-AREA": area_piainf,
                "RDOINF-UN": un_rdoinf,
                "RDOINF-AREA": area_rdoinf,
                "DDOINF-UN": un_ddoinf,
                "DDOINF-AREA": area_ddoinf,
                "DDLINF-UN": un_ddlinf,
                "DDLINF-AREA": area_ddlinf,
                "IFPMINF-UN": un_ifpminf,
                "IFPMINF-AREA": area_ifpminf,
                "PDI-NUMERO HABITANTE": pdi_habitantes,
                "REUR_HABITANTES": reur_habitantes,
                "PR-AREAUR": area_urpr,
                "PR-AREAPAISA": area_paisapr,
                "PR-KMANT": km_antipr,
                "PR-KMGEO": km_geopr,
                "PR-KMTER": km_terpr,
                "PR-KMDRE": km_drepr,
                "PR-KMPAV:": km_pavpr,
                "PR-MPAV": m_pavpr,
                "PR-TIPOPAV": tipo_pavpr,
                "PR-TIPOSUB": tipo_subasepr,
                "PR-KMSINAL": km_sinalpr,
                "PR-TIPOTOP": tipo_toppr,
                "PR-CADASTRALTOP": cadastral_toppr,
                "PR-KMTOP": km_toppr,
                "PR-AREATOP": area_toppr,
                "PR-KMORC": km_orcpr,
                "PR-AREAINFRAORCTIPO": area_infraorcprtipo_contpr,
                "PR-MCONT": m_contpr,
                "PR-M2CONT": m2_contpr,
                "PR-M3CONT": m3_contpr,
                "PR-TIPOOAE": tipo_oaevupr,
                "PR-AREAOAE": area_oaepr,
                "PR-VAOOAE": vao_oaepr,
                "PR-TIPOFUNDU": tipo_funduvpr,
                "PR-M2FUND": m2_fundpr,
                "PR-TIPOMEI": tipo_meivupr,
                "PR-UNIMEI": uni_meipr,
                "PR-AREAINFRA": area_infracomppr,
                "PS-TIPOFUNS": tipo_fundps,
                "PS-AREAFUSA": area_fusaps,
                "PS-TIPOTOPS": Tipo_topps,
                "PS-CADASTRAL": cadastral_ps,
                "PS-DRONE": drone_os,
                "PS-AREATOP": area_topsaps,
                "PS-AREAELESA": area_elesaps,
                "PS-KVA": kva_ps,
                "PS-AREAORC": area_orcsaps,
                "PS-MREDECOLE": m_redecoleps,
                "PS-MINTERCEP": m_interceptorps,
                "PS-MELEVATORIO": m_elevatoriops,
                "PS-VAZAOETES": vazao_eteps,
                "PS-MADUTORA": m_adutoraps,
                "PS-MELEVATORIA": m_elevatoriaps,
                "PS-VAZAOETA": vazao_etaps,
                "PS-VOLETA":vol_etaps,
                "PS-MREDEDIS": m_rededisps,
                "TIPO-SONDA": tipo_sonda,
                "FUROS-SONDA": furos_geo,
                "METRA-SONDA": m_geo,
                "TIPO-SOLO": tipo_solo,
                "UNI_SOLO": uni_solos,
                "TIPO-ASFALTO": tipo_asfalto,
                "UNI-ASFALTO": uni_asfalto,
                "TIPO-CONCRETO": tipo_concreto,
                "UNI-CONCRETO": uni_Concreto,
                "TIPO-ACO": tipo_aco,
                "UNI-ACO": uni_aco
            }

            # Se tiver PDF, adiciona no dicionário
            if pdf_url:
                dados_atestado["PDF_URL"] = pdf_url

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

with abas[2]:
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

with abas[0]:

    col1, col2 = st.columns([2,1])
    with col1:
        st.title("Biblioteca de Atestados")
    with col2:
        st.image("logoprojeta.png", width=350)

    # Buscar todos os documentos da coleção "atestados"
    docs = db.collection("atestados").stream()

    # Lista para armazenar os dados
    registros = []

    # Extrair os campos desejados
    for doc in docs:
        data = doc.to_dict()

        # Criar link amigável
        pdf_url = data.get("PDF_URL")
        pdf_link = f'<a href="{pdf_url}" target="_blank">Visualizar PDF</a>' if pdf_url else ""

        registros.append({
            "Empresa": data.get("Empresa"),
            "Participação": data.get("Participação"),
            "Cliente": data.get("Cliente"),
            "CAT": data.get("CAT"),
            "PDF": pdf_link,
            "Coordenação": data.get("Profissional-Cordenação"),
            "Serviço": data.get("Servico"),
            "Objeto": data.get("Objeto"),
            "Disciplinas": data.get("Disciplina"),
            "Área": data.get("Área (m²)"),
            "Data Inicial": data.get("Data Início"),
            "Data Final": data.get("Data Final")
        })

    # Criar DataFrame
    df = pd.DataFrame(registros)

    # Filtros
    colf1, colf2, colf3, colf4, colf5 = st.columns(5)

    with colf1:
        empresas_disponiveis = df["Empresa"].dropna().unique().tolist()
        filtro_empresas = st.multiselect("Filtrar por Empresa", empresas_disponiveis)

    with colf2:
        servicos_disponiveis = df["Serviço"].dropna().unique().tolist()
        filtro_servicos = st.multiselect("Filtrar por Tipo de Serviço", servicos_disponiveis)

    with colf3:
        filtro_CAT = st.text_input("Número CAT (parcial ou completo)", key="filtronumcat")

    with colf4:
        filtro_objeto = st.text_input("Objeto (parcial ou completo)", key="filtroobjeto")

    with colf5:
        # Filtro de Área com valores fixos
        area_minima, area_maxima = st.slider("Filtrar por Área (m²)", 0.0, 10000.0, (0.0, 10000.0))

    # Aplicar os filtros
    empresas_filtradas = empresas_disponiveis if not filtro_empresas or "Todos" in filtro_empresas else filtro_empresas
    servicos_filtrados = servicos_disponiveis if not filtro_servicos or "Todos" in filtro_servicos else filtro_servicos

    df_filtrado = df[
        (df["Empresa"].isin(empresas_filtradas)) &
        (df["Serviço"].isin(servicos_filtrados)) &
        (df["CAT"].str.contains(filtro_CAT, case=False, na=False) if filtro_CAT else True) &
        (df["Objeto"].str.contains(filtro_objeto, case=False, na=False) if filtro_objeto else True) &
        (df["Área"] >= area_minima) & (df["Área"] <= area_maxima)  # Aplicando filtro de área
        ]

    # Garantir que todas as disciplinas sejam strings
    df_filtrado["Disciplinas"] = df_filtrado["Disciplinas"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else str(x) if x is not None else ""
    )

    # Contador de atestados com filtros aplicados
    total = len(df_filtrado)
    st.markdown(f"##### Atestados Encontrados: {total}")


    # Mostrar a tabela
    st.write(df_filtrado.to_html(escape=False, index=False), unsafe_allow_html=True)

    # Função para buscar dados do Firebase
    def obter_dados_firebase():
        colecao = db.collection("atestados")  # Nome correto da coleção no Firebase
        documentos = colecao.stream()

        data = []
        for doc in documentos:
            doc_data = doc.to_dict()
            if "Profissional" in doc_data and "Data Início" in doc_data and "Data Final" in doc_data:
                data.append({
                    "Profissional": doc_data["Profissional"],
                    "Data Início": pd.to_datetime(doc_data["Data Início"]),
                    "Data Final": pd.to_datetime(doc_data["Data Final"]),
                })

        return pd.DataFrame(data)


    # Buscar os dados
    df = obter_dados_firebase()

    # Garantir que "Profissional" seja sempre uma string ou lista
    df["Profissional"] = df["Profissional"].apply(lambda x: x if isinstance(x, list) else [x])

    # Expandir os profissionais (explode transforma listas em múltiplas linhas)
    df = df.explode("Profissional")

    # Dicionário de formações dos profissionais
    formacoes = {
        "Matheus": "Engenheiro Civil",
        "Juliana": "Engenheiro Civil",
        "Danilo": "Engenheiro Civil",
        "Moises": "Engenheiro Eletricista",
        "Tiago": "Engenheiro Mecânico",
        "Pablo": "Engenheiro Agrimensor",
        "Sergio": "Engenheiro Civil",
        "Ayana": "Engenheiro Ambiental",
        "Ana": "Engenheiro Ambiental",
        "Christian": "Engenheiro Florestal",
        "Grazielle": "Engenheiro Ambiental",
        "Mauricio": "Engenheiro Civil",
        "Sayuri": "Arquiteto",
        "Isabela": "Arquiteto",
        "Debora": "Arquiteto",
        "Marcio": "Arquiteto",
        "Daniel": "Engenheiro Eletricista",
        "André": "Engenheiro Eletricista",
        "Bruno": "Engenheiro Mecânico",
        "Patricia": "Arquiteto",
        "Vicente": "Engenheiro Civil",
        "Cláudio": "Engenheiro Civil",
        "Emanuel": "Engenheiro Civil",
        "Érika": "Engenheiro Civil",
    }


    # Função para calcular a experiência de cada profissional
    def calcular_experiencia(df):
        experiencia_por_profissional = {}

        for profissional in df["Profissional"].unique():
            df_profissional = df[df["Profissional"] == profissional].sort_values("Data Início")
            periodos = []
            inicio_atual, fim_atual = df_profissional.iloc[0]["Data Início"], df_profissional.iloc[0]["Data Final"]

            for _, row in df_profissional.iterrows():
                if row["Data Início"] <= fim_atual:  # Há sobreposição
                    fim_atual = max(fim_atual, row["Data Final"])
                else:  # Novo período
                    periodos.append((inicio_atual, fim_atual))
                    inicio_atual, fim_atual = row["Data Início"], row["Data Final"]

            periodos.append((inicio_atual, fim_atual))
            dias_experiencia = sum((fim - inicio).days + 1 for inicio, fim in periodos)
            anos_experiencia = round(dias_experiencia / 365, 1)

            experiencia_por_profissional[profissional] = {
                "Formação": formacoes.get(profissional, "Desconhecida"),  # Pega a formação do profissional
                "Experiência (Dias)": dias_experiencia,
                "Experiência (Anos)": anos_experiencia
            }

        return experiencia_por_profissional


    # Calcular experiência se houver dados
    if not df.empty:
        experiencia = calcular_experiencia(df)
        df_experiencia = pd.DataFrame.from_dict(experiencia, orient="index").reset_index()
        df_experiencia.columns = ["Profissional", "Formação", "Experiência (Dias)", "Experiência (Anos)"]

        st.write("### Tempo De Experiência")
        st.dataframe(df_experiencia, use_container_width=True, hide_index=True)
    else:
        st.write("Nenhum dado encontrado.")
