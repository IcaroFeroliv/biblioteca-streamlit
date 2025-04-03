import time
import streamlit as st
import pandas as pd
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Corrigir quebra de linha da chave
firebase_config = dict(st.secrets["firebase"])
firebase_config["private_key"] = firebase_config["private_key"].replace("\\n", "\n")

# Inicializar Firebase somente se ainda não foi iniciado
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
db = firestore.client()

st.set_page_config(page_title="Grupo Projeta", layout="wide")

st.markdown("""
    <style>
        /* Esconde a barra de ferramentas do Streamlit */
        .stAppHeader.st-emotion-cache-h4xjwg.e4hpqof0 {
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
    empresas = ["OBJETIVA", "PROJETA", "SONDA", "PLATOR", "MINAS PROJETOS Objetiva", "PITAGORAS Objetiva", "METAVERSO Compasso", "DIAMANTE Compasso", "VITORIA   Objetiva"]
    empresas_grupo = st.selectbox("Empresa do Grupo", ["Selecione"] + empresas)

    # Cliente
    c1, c2, c3 = st.columns(3)
    with c1:
        cliente = st.text_input("Cliente")

    # Seleção de serviços
    with c2:
        servicos = ["Projeto Edificação", "Projeto Vias Urbanas", "Projeto Rodovias", "Plano Saneamento Básico - PMSB", "Projeto Saneamento", "Projeto Praças e Parques", "Estudos e Projetos Ambientais - EIA_RIMA_PCA", "EVTEA", "Plano Diretor", "Supervisão_Gerenciamento Edificação", "Supervisão_Gerenciamento Rodovias", "Supervisão_Gerenciamento Vias Urbanas", "Supervisão_Gerenciamento Saneamento", "Diversos", "Projeto_Laudo_Reforço OAE", "Sondagem", "Controle Teconlógico", "REURB_Regularização Fundiária", "Topografia"]
        servico = st.selectbox("Tipo de serviço", ["Selecione"] + servicos)

    with c3:
        participacao = st.number_input("Participação (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.2f")

    co1, co2 = st.columns(2)
    with co1:
        cat_numero = st.text_input("Número da CAT")
    with co2:
        caminho_rede = st.text_input("Caminho da Rede")
        
    colf1, colf2 = st.columns(2)
    with colf1:
        objeto = st.text_input("Objeto")
    with colf2:
        nome_profissionais = ["Juliana", "Matheus", "Danilo", "Isabela", "Tiago", "Ayana", "Moises", "Márcio", "Sayuri", "Ana", "Christian", "Daniel", "Vicente", "André", "Debora", "Pablo", "Sérgio", "Érika", "Bruno", "Cláudio", "Emanuel", "Grazielle", "Mauricio", "Patricia"]
        nome_profissional = st.multiselect("Nome dos Profissionais", nome_profissionais)


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

    if "Projeto Edificação" in servico or "Projeto Praças e Parques" in servico:
        tipo_servicos = ["ARQUITETÔNICO ANTEPROJETO", "ARQUITETÔNICO CONSTRUÇÃO", "ARQUITETÔNICO REFORMA", "ARQUITETÔNICO RESTAURO", "COMUNICAÇÃO VISUAL", "MOBILIÁRIO", "URBANISTICO", "AS BUILT", "MAQ ELET / 3D", "ESTRUTURAL", "METÁLICA", "FUNDAÇÃO", "CONTENÇÃO", "HIDROSANITÁRIO", "IRRIGAÇÃO", "SPCI", "TERRAPLENAGEM (PLANTA/SEÇÕES)","TOPOGRAFIA", "ORÇAMENTO", "ELÉTRICO", "CAB. ESTRUTURADO", "SPDA", "ALARME/CFTV", "EXTENSÃO DE REDE", "ILUMINAÇÃO PUBLICA", "AR CONDICIONADO", "VENTILAÇÃO/EXAUSTÃO", "GLP", "GASES MEDICINAIS", "COMPAT. PROJETOS", "ACÚSTICA", "REURB", "PAISAGISTICO"]
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
                edi_urb = st.selectbox("Tipo", ["Edificação", "Urbano"])
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
                tipo = st.selectbox("Tipo", ["C/ Matteport", "S/ Matteport"])
            with d3:
                area_abu = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_abu")

        if "MAQ ELET / 3D" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMAQ ELET / 3D""")
            with d2:
                Tipo = st.selectbox("Tipo", ["Modelagem 3D", "Maquete Eletrônica"])
            with d3:
                area_me3d = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_me3d")

        if "ESTRUTURAL" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nEstrutural""")
            with d2:
                tipo = st.selectbox("Tipo", ["Concreto", "Madeira"])
            with d3:
                area_est = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_est")

        if "METÁLICA" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMetálica""")
            with d2:
                area_mt = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_mt")
            with d3:
                ton = st.number_input("TON", min_value=0.0, step=1.0)

        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                tipo = st.selectbox("Tipo", ["Rasa(sapata, blocos e radier", "Profunda(estaca, tubulaão e caixões", "Rasa e Profunda"])
            with d3:
                area_fu = st.number_input("M²", min_value=0.0, step=1.0, key="area_fu")

        if "CONTENÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nContenção""")
            with d2:
                tipo = st.selectbox("Tipo", ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"])
            with d3:
                area_con = st.number_input("M", min_value=0.0, step=1.0, key="area_con")
            with d4:
                m2 = st.number_input("M²", min_value=0.0, step=1.0)
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
                Tipo = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria", "Planialtimétrico georreferenciado", "Planialtimétrico georreferenciado e aerofotogrametrico", "Planialtimétrico aerofotogrametrico"])
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
                area_reurb = st.number_input("Un. Habitacionais", min_value=0.0, step=1.0, key="area_reurn")

    if "Projeto Vias Urbanas" in servico:
        tipo_servicos = ["URBANISTICO", "PAISAGISTICO", "ANTEPROJETO DE INFRA", "GEOMÉTRICO", "TERRAPLENAGEM", "HIDROLOGIA", "DRENAGEM", "PAVIMENTAÇÃO", "SINALIZAÇÃO", "TOPOGRAFIA", "ORÇAMENTO", "CONTENÇÃO", "OAE", "FUNDAÇÃO", "MEIO AMBIENTE", "COMPAT. PROJETOS"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)


        if "URBANISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nUrbanistico""")
            with d2:
                area_ue = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_urvi")

        if "PAISAGISTICO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nPaisagisco""")
            with d2:
                area_paisa = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_paisavi")


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

        if "PAVIMENTAÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nPavimentação""")
            with d2:
                km_pav = st.number_input("KM", min_value=0.0, step=1.0, key="km_pav")
            with d3:
                m_pav = st.number_input("M²", min_value=0.0, step=0.1, key="m_pav")
            with d4:
                asfalto_pav = st.selectbox("Tipo", ["Não informa", "CBUQ", "CONCRETO", "TSD"])
            with d5:
                sub_base = st.selectbox("Base sub base", ["Não informa", "Mistura na pista","Solo estabilizado granulometricamente"])

        if "SINALIZAÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSinalização""")
            with d2:
                km_sinal = st.number_input("KM", min_value=0.0, step=1.0, key="km_sinal")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nTopografia""")
            with d2:
                sel_topogra = st.selectbox("Tipo",["Planialtimétrico", "Georreferenciado", "Aerofotogrametria", "Planialtimétrico georreferenciado", "Planialtimétrico georreferenciado e aerofotogrametrico", "Planialtimétrico aerofotogrametrico"])
            with d3:
                km_top = st.number_input("KM", min_value=0.0, step=1.0, key="km_top")

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
                tipo_cont = st.selectbox("Tipo", ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"])
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
                tipo_cont = st.selectbox("Tipo", ["Não informa o tipo", "Concreto armado", "Concreto protendido", "Balanço sucessivo", "Ponte estaiada"])
            with d3:
                area_oae = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_oae")
            with d4:
                vao_oae = st.number_input("VÃO(m)", min_value=0.0, step=0.1, key="vao_oae")

        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                sel_fund = st.selectbox("Tipo",["Rasa(sapata, blocos e radier)", "Profunda(estaca, tubulão, caixões)", "Rasa e Profunda"])
            with d3:
                m2_fund = st.number_input("M²", min_value=0.0, step=1.0, key="m2_fund")

        if "MEIO AMBIENTE" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMeio Ambiente""")
            with d2:
                sel_mei = st.selectbox("Tipo",["EIA/RIMA", "RCA/PCA", "RCA", "PCA", "RADA", "PRADA", "Inventário Florestal"])
            with d3:
                uni_mei = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_mei")

        if "COMPAT. PROJETOS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nCompat.Projeto""")
            with d2:
                area_infracomp = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_infracomp")

    if "Controle Teconlógico" in servico:
        tipo_servicos = ["SONDAGEM", "ENSAIOS","SOLOS", "ASFALTO", "CONCRETO", "AÇO", "ESPECIAIS"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

        if "SONDAGEM" in tipo_servico:
            d1, d2,d3, d4 = st.columns(4)
            with d1:
                st.write("""###### \nSondagem""")
            with d2:
                tipo_sonda = st.selectbox("Tipo", ["Percussão SPT", "Rotativa", "Trado", "Mista"])
            with d3:
                furos_geo = st.number_input("Furos", min_value=0.0, step=1.0, key="furos_geo")
            with d4:
                m_geo = st.number_input("Metros", min_value=0.0, step=0.1, key="m_geo")

        if "SOLOS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSolos""")
            with d2:
                uni_solos = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_solos")

        if "ASFALTO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAsfalto""")
            with d2:
                uni_asfalto = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_asfalto")

        if "CONCRETO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nConcreto""")
            with d2:
                uni_Concreto = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_concreto")

        if "AÇO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAço""")
            with d2:
                uni_aco = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_aco")

        if "ESPECIAIS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nEspeciais""")
            with d2:
                uni_especiais = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_especiais")

    if "Projeto Saneamento" in servico:
        tipo_servicos = ["FUNDAÇÃO", "TOPOGRAFIA", "ELÉTRICO", "ORÇAMENTO", "REDE COLETORA", "INTERCEPTOR", "ELEVATÓRIO", "ETE", "ADUTORA", "ELEVATÓRIA", "ETA", "REDE DE DISTRIBUIÇÃO"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)


        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                tipo = st.selectbox("Tipo", ["Rasa(sapata, blocos e radier", "Profunda(estaca, tubulaão e caixões",
                                                 "Rasa e Profunda"])
            with d3:
                area_fusa = st.number_input("M²", min_value=0.0, step=1.0, key="area_fusa")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nTopografia""")
            with d2:
                Tipo = st.selectbox("Tipo", ["Planialtimétrico", "Georreferenciado", "Aerogotogrametria",
                                                 "Planialtimétrico georreferenciado",
                                                 "Planialtimétrico georreferenciado e aerofotogrametrico",
                                                 "Planialtimétrico aerofotogrametrico"])
            with d3:
                cadastral = st.selectbox("Cadastral", ["Não", "Sim"])
            with d4:
                drone = st.selectbox("Drone", ["Não", "Sim"])
            with d5:
                area_topsa = st.number_input("M²", min_value=0.0, step=1.0, key="area_topsa")

        if "ELÉTRICO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nElétrico""")
            with d2:
                area_elesa = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_elesa")
            with d3:
                kva = st.number_input("KVA", min_value=0.0, step=0.1)

        if "ORÇAMENTO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nOrçamento""")
            with d2:
                area_orcsa = st.number_input("Área (m²)", min_value=0.0, step=1.0, key="area_orcsa")

        if "REDE COLETORA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nRede Coletora""")
            with d2:
                    m_redecole = st.number_input("M", min_value=0.0, step=1.0, key= "m_redecole")

        if "INTERCEPTOR" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nInterceptor""")
            with d2:
                m_interceptor = st.number_input("M", min_value=0.0, step=1.0, key="m_interceptor")

        if "ELEVATÓRIO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nElevatório""")
            with d2:
                m_elevatorio = st.number_input("M", min_value=0.0, step=1.0, key="m_elevatório")

        if "ETE" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nETE""")
            with d2:
                vazao_ete = st.number_input("Vazão(l/s)", min_value=0.0, step=1.0, key="vazao_ete")

        if "ADUTORA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nAdutora""")
            with d2:
                m_adutora = st.number_input("M", min_value=0.0, step=1.0, key="m_adutora")

        if "ELEVATÓRIA" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nElevatória""")
            with d2:
                m_elevatoria = st.number_input("M", min_value=0.0, step=1.0, key="m_elevatoria")

        if "ETA" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nETA""")
            with d2:
                vazao_eta = st.number_input("Vazão(l/s)", min_value=0.0, step=1.0, key="vazao_eta")
            with d3:
                vol_eta = st.number_input("VOL(m³)", min_value=0.0, step=1.0, key="vol_eta")

        if "REDE DE DISTRIBUIÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nRede de Distribuição""")
            with d2:
                m_rededis = st.number_input("M", min_value=0.0, step=1.0, key="m_rededis")

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

    if "Projeto_Laudo_Reforço OAE" in servico:
        tipo_servicos = ["ANTEPROJETO DE INFRA", "GEOMÉTRICO", "TERRAPLENAGEM", "HIDROLOGIA", "DRENAGEM",
                               "PAVIMENTAÇÃO", "SONDAGEM", "SINALIZAÇÃO", "TOPOGRAFIA", "ORÇAMENTO", "CONTENÇÃO", "OAE", "FUNDAÇÃO",
                               "MEIO AMBIENTE", "COMPAT. PROJETOS"]
        tipo_servico = st.multiselect("Selecione as disciplinas desejadas", tipo_servicos)

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

        if "PAVIMENTAÇÃO" in tipo_servico:
            d1, d2, d3, d4, d5 = st.columns(5)
            with d1:
                st.write("""###### \nPavimentação""")
            with d2:
                km_ter = st.number_input("KM", min_value=0.0, step=1.0, key="km_ter")
            with d3:
                m_ter = st.number_input("M²", min_value=0.0, step=0.1, key="m_ter")
            with d4:
                asfalto_pav = st.selectbox("Tipo", ["Não informa", "CBUQ", "CONCRETO", "TSD"])
            with d5:
                sub_base = st.selectbox("Base sub base", ["Não informa", "Mistura na pista","Solo estabilizado granulometricamente"])

        if "SONDAGEM" in tipo_servico:
            d1, d2,d3, d4 = st.columns(4)
            with d1:
                st.write("""###### \nSondagem""")
            with d2:
                tipo_sonda = st.selectbox("Tipo", ["Percussão SPT", "Rotativa", "Trado", "Mista"])
            with d3:
                furos_geo = st.number_input("Furos", min_value=0.0, step=1.0, key="furos_geo")
            with d4:
                m_geo = st.number_input("Metros", min_value=0.0, step=0.1, key="m_geo")

        if "SINALIZAÇÃO" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nSinalização""")
            with d2:
                km_sinal = st.number_input("KM", min_value=0.0, step=1.0, key="km_sinal")

        if "TOPOGRAFIA" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nTopografia""")
            with d2:
                sel_topogra = st.selectbox("Tipo",["Planialtimétrico", "Georreferenciado", "Aerofotogrametria", "Planialtimétrico georreferenciado", "Planialtimétrico georreferenciado e aerofotogrametrico", "Planialtimétrico aerofotogrametrico"])
            with d3:
                km_top = st.number_input("KM", min_value=0.0, step=1.0, key="km_top")

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
                tipo_cont = st.selectbox("Tipo", ["Concreto", "Muro de arrimo", "Gabião", "Terra armada", "Cortina atirantada"])
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
                tipo_cont = st.selectbox("Tipo", ["Não informa o tipo", "Concreto armado", "Concreto protendido", "Balanço sucessivo", "Ponte estaiada"])
            with d3:
                area_oae = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_oae")
            with d4:
                vao_oae = st.number_input("VÃO(m)", min_value=0.0, step=0.1, key="vao_oae")

        if "FUNDAÇÃO" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nFundação""")
            with d2:
                sel_fund = st.selectbox("Tipo",["Rasa(sapata, blocos e radier)", "Profunda(estaca, tubulão, caixões)", "Rasa e Profunda"])
            with d3:
                m2_fund = st.number_input("M²", min_value=0.0, step=1.0, key="m2_fund")

        if "MEIO AMBIENTE" in tipo_servico:
            d1, d2, d3 = st.columns(3)
            with d1:
                st.write("""###### \nMeio Ambiente""")
            with d2:
                sel_mei = st.selectbox("Tipo",["EIA/RIMA", "RCA/PCA", "RCA", "PCA", "RADA", "PRADA", "Inventário Florestal"])
            with d3:
                uni_mei = st.number_input("Unidade", min_value=0.0, step=1.0, key="uni_mei")

        if "COMPAT. PROJETOS" in tipo_servico:
            d1, d2 = st.columns(2)
            with d1:
                st.write("""###### \nCompat.Projeto""")
            with d2:
                area_infracomp = st.number_input("Área(m²)", min_value=0.0, step=1.0, key="area_infracomp")

    if "REURB_Regularização Fundiária" in servico:
        d1, d2= st.columns(2)
        with d1:
            st.write("""###### \nREURB_Regularização Fundiária""")
        with d2:
            tipo_servico = st.number_input("Unidade Habitacional²", min_value=0.0, step=1.0, key="uni_reurb")

    if cliente and data_inicial and servico:
        nome_atestado = f"{empresas_grupo}_{cliente}_{cat_numero}_{servico}"
        nome_atestado_formatado = nome_atestado.replace("/", "-")
    else:
        nome_atestado_formatado = None

    st.write(f"Nome do Atestado: `{nome_atestado_formatado}`")

    if st.button("Enviar"):

        if nome_atestado:
            # Criar dicionário com os dados
            dados_atestado = {
                "Empresa": empresas_grupo,
                "Cliente": cliente,
                "Servico": servico,
                "Profissional" : nome_profissional,
                "Disciplina": tipo_servico,
                "Participação": participacao,
                "Caminho": caminho_rede,
                "CAT": cat_numero,
                "Data Início": str(data_inicial),
                "Data Final": str(data_final),
                "Objeto": objeto,
                "Extensão (km)": extensao,
                "Área (m²)": area,
                "BIM": bim,
                "Patrimônio Tombado": patrimonio,
            }

            # Enviar para o Firebase com nome personalizado como ID
            db.collection("atestados").document(nome_atestado_formatado).set(dados_atestado)

            st.success(f"Atestado `{nome_atestado_formatado}` salvo com sucesso!")
            time.sleep(1)

            # JavaScript para recarregar a pagina
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
        registros.append({
            "Empresa": data.get("Empresa"),
            "Participação": data.get("Participação"),
            "Cliente": data.get("Cliente"),
            "CAT": data.get("CAT"),
            "Caminho": data.get("Caminho"),
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
    colf1, colf2, colf3, colf4 = st.columns(4)
    
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
    
    # Aplicar os filtros
    empresas_filtradas = empresas_disponiveis if not filtro_empresas or "Todos" in filtro_empresas else filtro_empresas
    servicos_filtrados = servicos_disponiveis if not filtro_servicos or "Todos" in filtro_servicos else filtro_servicos
    
    df_filtrado = df[
        (df["Empresa"].isin(empresas_filtradas)) &
        (df["Serviço"].isin(servicos_filtrados)) &
        (df["CAT"].str.contains(filtro_CAT, case=False, na=False)
         if filtro_CAT else True) &
        (df["Objeto"].str.contains(filtro_objeto, case=False, na=False)
         if filtro_objeto else True)
        
    ]
    
    # Garantir que todas as disciplinas sejam strings
    df_filtrado["Disciplinas"] = df_filtrado["Disciplinas"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else str(x) if x is not None else ""
    )
    
    # Mostrar contador de atestados encontrados
    total = len(df_filtrado)
    st.markdown(f"### Atestados encontrados: **{total}**")
    
    # Mostrar tabela
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

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
