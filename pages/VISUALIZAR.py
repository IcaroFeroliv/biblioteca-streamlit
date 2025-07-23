import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore, storage

st.set_page_config(page_title="Grupo Projeta", layout="wide")

st.markdown("""
    <style>
        /* Oculta a barra de ações (canto superior direito) */
        [data-testid="stToolbarActions"],
        /* Oculta o menu principal (os três pontinhos ...) */
        [data-testid="stMainMenu"] {
            display: none !important;
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

abas = st.tabs(["Geral","Experiência", "Disciplinas"])

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

        # Criar links amigáveis para cada PDF vinculado a profissionais
        pdfs_profissionais = data.get("PDFS_PROFISSIONAIS", {})
        if isinstance(pdfs_profissionais, dict):
            pdf_links = [
                f'<a href="{url}" target="_blank">{nome}</a>'
                for nome, url in pdfs_profissionais.items() if url
            ]
            pdf_final = "<br>".join(pdf_links)
        else:
            # fallback para PDF_URL antigo se existir
            pdf_url = data.get("PDF_URL")
            pdf_final = f'<a href="{pdf_url}" target="_blank">Visualizar PDF</a>' if pdf_url else ""

        registros.append({
            "Empresa": data.get("Empresa"),
            "Participação": data.get("Participação"),
            "Cliente": data.get("Cliente"),
            "CAT": data.get("CAT"),
            "Coordenação": data.get("Profissional-Cordenação"),
            "PDF": pdf_final,
            "Serviço": data.get("Servico"),
            "Objeto": data.get("Objeto"),
            "BIM": data.get("BIM"),
            "Disciplinas": data.get("Disciplina"),
            "Área": data.get("Área (m²)"),
            "Extensão": data.get("Extensão (km)"),
            "Data Inicial": data.get("Data Início"),
            "Data Final": data.get("Data Final")
        })

    # Criar DataFrame
    df = pd.DataFrame(registros)

    # Filtros
    colf1, colf2, colf3, colf4, colf5, colf6 = st.columns(6)

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
        filtro_area_min = st.number_input("Área mínima (m²)", min_value=0.0, step=1.0, value=0.0)

    with colf6:
        filtro_extensao_min = st.number_input("Extensão mínima (km)", min_value=0.0, step=0.1, value=0.0)

    # Aplicar os filtros
    empresas_filtradas = empresas_disponiveis if not filtro_empresas else filtro_empresas
    servicos_filtrados = servicos_disponiveis if not filtro_servicos else filtro_servicos

    df_filtrado = df[
        (df["Empresa"].isin(empresas_filtradas)) &
        (df["Serviço"].isin(servicos_filtrados)) &
        (df["CAT"].str.contains(filtro_CAT, case=False, na=False) if filtro_CAT else True) &
        (df["Objeto"].str.contains(filtro_objeto, case=False, na=False) if filtro_objeto else True) &
        ((df["Área"] >= filtro_area_min) if filtro_area_min > 0 else True) &
        ((df["Extensão"] >= filtro_extensao_min) if filtro_extensao_min > 0 else True)
        ]

    # Garantir que "Disciplinas" seja string
    df_filtrado["Disciplinas"] = df_filtrado["Disciplinas"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else str(x) if x is not None else ""
    )

    # Formatar colunas de área e extensão com duas casas decimais ou 'Não informado'
    df_filtrado["Área"] = df_filtrado["Área"].apply(
        lambda x: f"{x:.2f}" if pd.notnull(x) else "Não informado"
    )

    df_filtrado["Extensão"] = df_filtrado["Extensão"].apply(
        lambda x: f"{x:.2f}" if pd.notnull(x) else "Não informado"
    )

    # Contador
    st.markdown(f"##### Atestados Encontrados: {len(df_filtrado)}")



    st.write(df_filtrado.to_html(escape=False, index=False), unsafe_allow_html=True)

with abas[1]:

    col1, col2 = st.columns([2,1])
    with col1:
        st.title("Tempo De Experiência")
    with col2:
        st.image("logoprojeta.png", width=350)


    # Função para buscar dados do Firebase
    def obter_dados_firebase():
        colecao = db.collection("atestados")
        documentos = colecao.stream()

        data = []
        for doc in documentos:
            doc_data = doc.to_dict()
            if all(k in doc_data for k in ["Profissional", "Data Início", "Data Final", "Servico"]):
                data.append({
                    "Profissional": doc_data["Profissional"],
                    "Data Início": pd.to_datetime(doc_data["Data Início"]),
                    "Data Final": pd.to_datetime(doc_data["Data Final"]),
                    "Servico": doc_data["Servico"]
                })

        return pd.DataFrame(data)


    # Buscar os dados
    df = obter_dados_firebase()

    # Garantir que "Profissional" seja sempre lista
    df["Profissional"] = df["Profissional"].apply(lambda x: x if isinstance(x, list) else [x])
    df = df.explode("Profissional")

    # Filtro para escolher o tipo de serviço
    servicos_disponiveis = df["Servico"].dropna().unique().tolist()
    servico_selecionado = st.selectbox("Selecione o Tipo de Serviço para calcular experiência",
                                       ["Todos"] + servicos_disponiveis)

    # Se selecionou algum serviço específico, filtra
    if servico_selecionado != "Todos":
        df = df[df["Servico"] == servico_selecionado]

    # Dicionário de formações dos profissionais
    formacoes = {
        "Aline":"Engenheira Eletricista",
        "Ana Carolina": "Engenheira Sanitarista e Ambiental",
        "André": "Engenheiro Eletricista",
        "Ayana Lemos": "Engenheira Ambiental e Engenheira de Segurança do Trabalho",
        "Bárbara Izabela": "Engenheira Civil",
        "Bruno Andrelli": "Engenheiro Mecânico",
        "Bruno Tizoni": "Engenheiro Civil",
        "Cláudio": "Engenheiro Civil",
        "Christian Sorensen": "Engenheiro Florestal",
        "Daniel Pinheiro": "Engenheiro Eletricista",
        "Danilo Vitor": "Engenheiro Civil",
        "Debora": "Arquiteta",
        "Debora Dayane": "Engenheira Civil",
         "Douglas Lins": "Engenheiro Civil",
        "Emanuel da Silva": "Engenheiro Civil",
        "Emanuel Jose": "Geógrafo",
        "Érika": "Engenheira Civil",
        "Fabiane Ferreira": "Engenheira Civil",
        "Fabiano Matos":"Engenheiro Civil",
        "Fernando Martins": "Engenheiro Civil",
        "Gracielle": "Engenheira Ambiental",
        "Isabela": "Arquiteta",
        "Juliana Goncalves": "Engenheira Civil e Engenheira de Segurança do Trabalho",
        "Julio Cesar": "Engenheiro Civil",
        "Lucas Bastos": "Engenheiro Civil",
        "Luiz Felipe": "Engenheiro Civil",
        "Maria Francielle": "Engenheira Civil",
        "Mariane de Paula": "Engenheira Civil",
        "Matheus Comanduci": "Engenheiro Civil",
        "Mauricio Otavio": "Engenheiro Civil",
        "Márcio": "Arquiteto",
        "Moises Coelho": "Engenheiro Agrimensor",
        "Pablo Otoni": "Engenheiro Agrimensor",
        "Patricia": "Arquiteta",
        "Sarah Malta": "Engenheira Agrimensora",
        "Sávio": "Geólogo",
        "Sayuri": "Arquiteta",
        "Sérgio Henrique": "Engenheiro Civil",
        "Tayrine Cristina": "Engenheira Civil",
        "Thiago Figueiredo": "Engenheiro Civil",
         "Tiago Guedes": "Engenheiro Mecânico e Engenheiro do Trabalho",
        "Vicente": "Engenheiro Civil",
        "Vinicius Gama": "Engenheiro Civil",
        "Welington de Avila": "Engenheiro Agrimensor",
    }

    # Dicionário de escialização dos profissionais
    especializacao = {
        "Aline": "-",
        "Ana Carolina": "-",
        "André": "-",
        "Ayana Lemos": "-",
        "Bárbara Izabela": "-",
        "Bruno Andrelli": "-",
        "Bruno Tizoni":"-",
        "Cláudio": "-",
        "Christian Sorensen": "-",
        "Daniel Pinheiro": "-",
        "Danilo Vitor": "Engenharia Sanitária e Ambiental",
        "Debora": "-",
        "Debora Dayane": "-",
         "Douglas Lins": "-",
        "Emanuel da Silva": "-",
        "Emanuel Jose": "-",
        "Érika": "-",
        "Fabiane Ferreira": "-",
        "Fabiano Matos": "-",
        "Fernando Martins": "-",
        "Gracielle": "-",
        "Isabela": "-",
        "Juliana Goncalves": "Engenharia Geotécnica",
        "Julio Cesar": "-",
        "Lucas Bastos": "-",
        "Luiz Felipe": "MBA em Plataforma BIM - Modelagem 3D, Planejamento 4D e Orçamento 5D, 6D e 7D",
        "Maria Francielle": "-",
        "Mariane de Paula": "-",
        "Matheus Comanduci": "-",
        "Mauricio Otavio": "Engenharia Sanitaria e Ambiental",
        "Márcio": "-",
        "Moises Coelho": "-",
        "Pablo Otoni": "-",
         "Patricia": "-",
        "Sarah Malta": "-",
        "Sávio": "-",
        "Sayuri": "-",
        "Sérgio Henrique": "-",
        "Tayrine Cristina": "-",
        "Thiago Figueiredo": "-",
         "Tiago Guedes": "-",
        "Vicente": "-",
        "Vinicius Gama": "-",
        "Welington de Avila": "-",
    }


    # Função para calcular experiência de cada profissional
    def calcular_experiencia(df):
        experiencia_por_profissional = {}

        for profissional in df["Profissional"].unique():
            df_profissional = df[df["Profissional"] == profissional].sort_values("Data Início")
            if df_profissional.empty:
                continue

            periodos = []
            inicio_atual, fim_atual = df_profissional.iloc[0]["Data Início"], df_profissional.iloc[0]["Data Final"]

            for _, row in df_profissional.iterrows():
                if row["Data Início"] <= fim_atual:
                    fim_atual = max(fim_atual, row["Data Final"])
                else:
                    periodos.append((inicio_atual, fim_atual))
                    inicio_atual, fim_atual = row["Data Início"], row["Data Final"]

            periodos.append((inicio_atual, fim_atual))
            dias_experiencia = sum((fim - inicio).days + 1 for inicio, fim in periodos)
            anos_experiencia = round(dias_experiencia / 365, 1)

            experiencia_por_profissional[profissional] = {
                "Formação": formacoes.get(profissional, "Desconhecida"),
                "Especialização": especializacao.get(profissional, "Desconhecida"),
                "Experiência (Dias)": dias_experiencia,
                "Experiência (Anos)": anos_experiencia
            }

        return experiencia_por_profissional


    # Se houver dados filtrados, calcula
    if not df.empty:
        experiencia = calcular_experiencia(df)
        df_experiencia = pd.DataFrame.from_dict(experiencia, orient="index").reset_index()
        df_experiencia.columns = ["Profissional", "Formação", "Especialização", "Experiência (Dias)",
                                  "Experiência (Anos)"]

        # Exibe
        st.markdown(f"#### Profissionais com experiência em **{servico_selecionado}**")
        st.dataframe(df_experiencia, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum dado encontrado para o serviço selecionado.")

with abas[2]:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("Disciplinas")
    with col2:
        st.image("logoprojeta.png", width=350)

    # Buscar dados do Firebase
    docs = db.collection("atestados").stream()

    # Preparar registros
    registros = []
    for doc in docs:
        data = doc.to_dict()
        data["ID"] = doc.id
        registros.append(data)

    # Dicionário de disciplinas com os campos de tipo e área relacionados

    disciplinas_edificacoes = {
    "ACÚSTICA": {
        "area": "ACÚSTICA(m²)",
        "prancha": "PRANCHA ACÚSTICA"
    },
    "ADEQUAÇÃO DE ACESSIBILIDADE": {
        "area": "ADEQUAÇÃO DE ACESSIBILIADE(m²)",
        "prancha": "PRANCHA ADEQUAÇÃO DE ACESSIBILIDADE"
    },
    "ALARME/CFTV": {
        "area": "ALARME/CFTV(m²)",
        "prancha": "PRANCHA ALARME/CFTV"
    },
    "ANTEPROJETO": {
        "area": "ANTEPROJETO(m²)",
        "prancha": "PRANCHA ANTEPROJETO"
    },
    "AR CONDICIONADO": {
        "area": "AR CONDICIONADO(m²)",
        "prancha": "PRANCHA AR CONDICIONADO"
    },
    "ARQUITETÔNICO CONSTRUÇÃO": {
        "area": "ARQUITETÔNICO CONSTRUÇÃO(m²)",
        "prancha": "PRANCHA ARQUITETÔNICO CONSTRUÇÃO"
    },
    "ARQUITETÔNICO REFORMA": {
        "area": "ARQUITETÔNICO REFORMA(m²)",
        "prancha": "PRANCHA ARQUITETÔNICO REFORMA"
    },
    "ARQUITETÔNICO RESTAURO": {
        "area": "ARQUITETÔNICO RESTAURO(m²)",
        "prancha": "PRANCHA ARQUITETÔNICO RESTAURO"
    },
    "AS BUILT": {
        "tipo": "TIPO AS BUILT",
        "area": "AS BUILT(m²)",
        "prancha": "PRANCHA AS BUILT"
    },
    "AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO": {
        "area": "AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO(m²)",
        "unidade": "AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO(uni)",
        "prancha": "PRANCHA AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO"
    },
    "CAB. ESTRUTURADO": {
        "area": "CAB. ESTRUTURADO(m²)",
        "prancha": "PRANCHA CAB. ESTRUTURADO"
    },
    "CLIMATIZAÇÃO": {
        "area": "CLIMATIZAÇÃO(m²)",
        "kva": "CLIMATIZAÇÃO(kbtu/h)",
        "prancha": "PRANCHA CLIMATIZAÇÃO"
        },
    "COMUNICAÇÃO VISUAL": {
        "area": "COMUNICAÇÃO VISUAL(m²)",
        "prancha": "PRANCHA COMUNICAÇÃO VISUAL"
    },
    "COMPAT. PROJETOS": {
        "area": "COMPAT. PROJETOS(m²)",
        "prancha": "PRANCHA COMPAT. PROJETOS"
    },
    "CONTENÇÃO": {
        "tipo": "CONTENÇÃO"
    },
    "DRENAGEM": {
        "area": ["DRENAGEM(m²)", "DRENAGEM(km)"],
        "prancha": "PRANCHA DRENAGEM"
    },
    "ELÉTRICO": {
        "area": "ELÉTRICO(m²)",
        "kva": "KVA",
        "prancha": "PRANCHA ELÉTRICO"
    },
    "ESTRUTURAL": {
        "tipo": "ESTRUTURAL"
    },
    "EXTENSÃO DE REDE": {
        "area": "EXTENSÃO DE REDE(km)",
        "prancha": "PRANCHA EXTENSÃO DE REDE"
    },
    "FUNDAÇÃO": {
        "tipo": "FUNDAÇÃO"
    },
    "GASES MEDICINAIS": {
        "area": ["GASES MEDICINAIS(m²)", "GASES MEDICINAIS(m³)"],
        "prancha": "PRANCHA GASES MEDICINAIS"
    },
    "GERAÇÃO FOTOVOLTAICA": {
        "area": "GERAÇÃO FOTOVOLTAICA(m²)",
        "kva": "GERAÇÃO FOTOVOLTAICA(kva)",
        "prancha": "PRANCHA GERAÇÃO FOTOVOLTAICA"
    },
    "GLP": {
        "area": ["GLP(m²)", "GLP(m³)"],
        "prancha": "PRANCHA GLP"
    },
    "HIDROSSANITÁRIO": {
        "area": "HIDROSSANITÁRIO(m²)",
        "prancha": "PRANCHA HIDROSSANITÁRIO"
    },
    "ILUMINAÇÃO PUBLICA": {
        "area": "ILUMINAÇÃO PUBLICA(km)",
        "kva": "ILUMINAÇÃO PUBLICA(ponto)",
        "prancha": "PRANCHA ILUMINAÇÃO PUBLICA"
    },
    "IMPERMEABLIZAÇÃO":{
        "area": "IMPERMEABILIZAÇÃO(m²)",
        "prancha": "PRANCHA IMPERMEABIALIZAÇÃO"
    },
    "IRRIGAÇÃO": {
        "area": "IRRIGAÇÃO(m²)",
        "prancha": "PRANCHA IRRIGAÇÃO"
    },
    "LEVANTAMENTO ARQUITETÔNICO": {
        "tipo": "TIPO LEVANTAMENTO ARQUITETÔNICO",
        "area": "LEVANTAMENTO ARQUITETÔNICO(m²)",
        "prancha": "PRANCHA LEVANTAMENTO ARQUITETÔNICO"
    },
    "MAQ ELET / 3D": {
        "tipo": "MAQ ELET/3D"
    },
    "MOBILIÁRIO": {
        "tipo": "MOBILIÁRIO"
    },
    "ORÇAMENTO": {
        "area": "ORÇAMENTO(m²)",
        "prancha": "ORÇAMENTO(km)"
    },
    "PAISAGISTICO": {
        "area": "PAISAGISTICO(m²)",
        "prancha": "PRANCHA PAISAGISTICO"
    },
    "REURB": {
        "area": "Un.Habitacionais",
        "prancha": "PRANCHA REURB"
    },
    "SONDAGEM": {
        "tipo": "Sondagem"
    },
    "SPCI": {
        "area": "SPCI(m²)",
        "prancha": "PRANCHA SPCI"
    },
    "SPDA": {
        "area": "SPDA(m²)",
        "prancha": "PRANCHA SPDA"
    },
    "TERRAPLENAGEM": {
        "area": ["TERRAPLENAGEM(m²)", "TERRAPLENAGEM(km)"],
        "unidade": "TERRAPLENAGEM(uni)",
        "prancha": "PRANCHA TERRAPLENAGEM"
    },
    "TOPOGRAFIA": {
        "tipo": "TIPO TOPOGRAFIA",
        "cadastral": "CADASTRAL-TOP",
        "drone": "DRONE-TOP",
        "area": "TOPOGRAFIA(m²)",
        "prancha": "PRANCHA TOPOGRAFIA"
    },
    "URBANISTICO": {
        "area": "URBANISTICO(m²)",
        "prancha": "PRANCHA URBANISTICO"
    },
    "VENTILAÇÃO/EXAUSTÃO": {
        "area": "VENTILAÇÃO/EXAUSTÃO(m²)",
        "kva": "VENTILAÇÃO/EXAUSTÃO(kbtu/h)",
        "prancha": "PRANCHA VENTILAÇÃO/EXAUSTÃO"
    }
}

    disciplinas_vu = {
    "ADEQUAÇÃO DE ACESSIBILIDADE": {
        "area": ["VU-ADEQUAÇÃO DE ACESSIBILIADE(m²)", "PR-ADEQUAÇÃO DE ACESSIBILIADE(m²)"],
        "prancha": ["VU-PRANCHA ADEQUAÇÃO DE ACESSIBILIDADE", "PR-PRANCHA ADEQUAÇÃO DE ACESSIBILIDADE"]
    },
    "ANTEPROJETO": {
        "area": ["VU-ANTEPROJETO(m²)", "VU-ANTEPROJETO(m)", "PR-ANTEPROJETO(m²)", "PR-ANTEPROJETO(m)"],
        "prancha": ["VU-PRANCHA ANTEPROJETO", "PR-PRANCHA ANTEPROJETO"]
    },
    "BATIMETRIA": {
        "area": ["VU-BATIMETRIA(m²)", "PR-BATIMETRIA(m²)"],
        "prancha": ["VU-PRANCHA BATIMETRIA", "PR-PRANCHA BATIMETRIA"]
    },
    "COMPAT. PROJETOS": {
        "area": ["VU-COMPAT. PROJETOS(m²)", "PR-COMPAT. PROJETOS(m²)"],
        "prancha": ["VU-PRANCHA COMPAT. PROJETOS", "PR-PRANCHA COMPAT. PROJETOS"]
    },
    "CONTENÇÃO": {
        "tipo": ["VU-CONTENÇÃO", "PR-CONTENÇÃO"]
    },
    "DRENAGEM": {
        "area": ["VU-DRENAGEM(KM)", "PR-DRENAGEM(KM)"],
        "prancha": ["VU-PRANCHA DRENAGEM", "PR-PRANCHA DRENAGEM"]
    },
    "ELÉTRICO": {
        "area": ["VU-ELÉTRICO(m²)", "PR-ELÉTRICO(m²)"],
        "kva": ["VU-KVA", "PR-KVA"],
        "prancha": ["VU-PRANCHA ELÉTRICO", "PR-PRANCHA ELÉTRICO"]
    },
    "ESTRUTURAL": {
        "tipo": ["VU-ESTRUTURAL", "PR-ESTRUTURAL"]
    },
    "EXTENSÃO DE REDE": {
        "area": ["VU-EXTENSÃO DE REDE(KM)", "PR-EXTENSÃO DE REDE(KM)"],
        "prancha": ["VU-PRANCHA EXTENSÃO DE REDE", "PR-PRANCHA EXTENSÃO DE REDE"]
    },
    "FUNDAÇÃO": {
        "tipo": ["VU-FUNDAÇÃO", "PR-FUNDAÇÃO"]
    },
    "GEOMÉTRICO": {
        "area": ["VU-GEOMÉTRICO(KM)", "PR-GEOMÉTRICO(KM)"],
        "prancha": ["VU-PRANCHA GEOMÉTRICO", "PR-PRANCHA GEOMÉTRICO"]
    },
    "GERAÇÃO FOTOVOLTAICA": {
        "area": ["VU-GERAÇÃO FOTOVOLTAICA(m²)", "PR-GERAÇÃO FOTOVOLTAICA(m²)"],
        "kva": ["VU-GERAÇÃO FOTOVOLTAICA(kva)", "PR-GERAÇÃO FOTOVOLTAICA(kva)"],
        "prancha": ["VU-PRANCHA GERAÇÃO FOTOVOLTAICA", "PR-PRANCHA GERAÇÃO FOTOVOLTAICA"]
    },
    "HIDROLOGIA": {
        "area": ["VU-HIDROLOGIA(m²)", "PR-HIDROLOGIA(m²)"],
        "kva": ["VU-HIDROLOGIA(l/s)", "PR-HIDROLOGIA(l/s)"],
        "prancha": ["VU-PRANCHA HIDROLOGIA", "PR-PRANCHA HIDROLOGIA"]
    },
    "ILUMINAÇÃO PUBLICA": {
        "area": ["VU-ILUMINAÇÃO PUBLICA(km)", "PR-ILUMINAÇÃO PUBLICA(km)"],
        "kva": ["VU-ILUMINAÇÃO PUBLICA(Pontos)", "PR-ILUMINAÇÃO PUBLICA(Pontos)"],
        "prancha": ["VU-PRANCHA ILUMINAÇÃO PUBLICA", "PR-PRANCHA ILUMINAÇÃO PUBLICA"]
    },
    "MEIO AMBIENTE": {
        "tipo": ["VU-MEIO AMBIENTE", "PR-MEIO AMBIENTE"]
    },
    "OAE": {
        "tipo": ["VU-OAE", "PR-OAE"]
    },
    "ORÇAMENTO": {
        "area": ["VU-ORÇAMENTO(m²)", "PR-ORÇAMENTO(m²)"],
        "prancha": ["VU-ORÇAMENTO(KM)", "PR-ORÇAMENTO(KM)"]
    },
    "PAISAGISTICO": {
        "area": ["VU-PAISAGISTICO(m²)", "PR-PAISAGISTICO(m²)"],
        "prancha": ["VU-PRANCHA PAISAGISTICO", "PR-PRANCHA PAISAGISTICO"]
    },
    "PAVIMENTAÇÃO": {
        "tipo": ["VU-PAVIMENTAÇÃO", "PR-PAVIMENTAÇÃO"]
    },
    "SANEAMENTO": {
        "area": ["VU-SANEAMENTO(m)", "PR-SANEAMENTO(m)"],
        "kva": ["VU-SANEAMENTO(l/s)", "PR-SANEAMENTO(l/s)"],
        "prancha": ["VU-PRANCHA SANEAMENTO", "PR-PRANCHA SANEAMENTO"]
        },
    "SINALIZAÇÃO": {
        "area": ["VU-SINALIZAÇÃO(KM)", "PR-SINALIZAÇÃO(KM)"],
        "prancha": ["VU-PRANCHA SINALIZAÇÃO", "PR-PRANCHA SINALIZAÇÃO"]
    },
    "SONDAGEM": {
        "tipo": ["VU-SONDAGEM", "PR-SONDAGEM"]
    },
    "TERRAPLENAGEM": {
        "area": ["VU-TERRAPLENAGEM(KM)", "PR-TERRAPLENAGEM(KM)"],
        "unidade":["VU-TERRAPLENAGEM(uni)", "PR-TERRAPLENAGEM(uni)"],
        "prancha": ["VU-PRANCHA TERRAPLENAGEM", "PR-PRANCHA TERRAPLENAGEM"]
    },
    "TOPOGRAFIA": {
        "tipo": ["VU-TIPO TOPOGRAFIA", "PR-TIPO TOPOGRAFIA"],
        "cadastral": ["VU-CADASTRAL-TOP", "PR-CADASTRAL-TOP"],
        "drone": ["VU-DRONE-TOP", "PR-TOPOGRAFIA(KM)"],
        "area": ["VU-TOPOGRAFIA(m²)", "PR-TOPOGRAFIA(m²)"],
        "prancha": ["VU-PRANCHA TOPOGRAFIA", "PR-PRANCHA TOPOGRAFIA"]
    },
    "URBANISTICO": {
        "area": ["VU-URBANISTICO(m²)", "PR-URBANISTICO(m²)"],
        "prancha": ["VU-PRANCHA URBANISTICO", "PR-PRANCHA URBANISTICO"]
    }
}

    disciplinas_pmsb = {
        "PLANO SANEAMENTO BÁSICO - PMSB": {"area": "PMSB-NUMERO HABITANTES", "prancha": "PMSB-PRANCHA"}
    }

    disciplinas_saneamento = {
        "ADUTORA": {
            "area": ["PS-ADUTORA(m)", "PS-ADUTORA(l/s)"],
            "unidade": "PS-ADUTORA(uni)",
            "prancha": "PS-PRANCHA ADUTORA"
        },
        "ANTEPROJETO DE INFRA": {
            "area": "PS-ANTEPROJETO DE INFRA(km)",
            "prancha": "PS-PRANCHA ANTEPROJETO DE INFRA"
        },
        "BATIMETRIA": {
            "area": "PS-BATIMETRIA(m²)",
            "prancha": "PS-PRANCHA BATIMETRIA"
        },
        "COMPAT. PROJETOS": {
            "area": "PS-COMPAT. PROJETOS(m²)",
            "prancha": "PS-PRANCHA COMPAT. PROJETOS"
        },
        "CONJUNTO MOTOBOMBA": {
            "area": "PS-CONJUNTO MOTOBOMBA(uni)",
            "prancha": "PS-PRANCHA CONJUNTO MOTOBOMBA"
        },
        "CONTENÇÃO": {
            "tipo": "PS-CONTENÇÃO"
        },
        "DRENAGEM": {
            "area": "PS-DRENAGEM(km)",
            "prancha": "PS-PRANCHA DRENAGEM"
        },
        "ELEVATÓRIA": {
            "area": "PS-ELEVATÓRIA(l/s)",
            "unidade": "PS-ELEVATÓRIA(uni)",
            "prancha": "PS-PRANCHA ELEVATÓRIA"
        },
        "ELÉTRICO": {
            "area": "PS-ELÉTRICO(m²)",
            "kva": "PS-KVA",
            "prancha": "PS-PRANCHA ELÉTRICO"
        },
        "ESTRUTURAL": {
            "tipo": "PS-ESTRUTURAL"
        },
        "ETA": {
            "area": ["PS-ETA Vazão(l/s)", "PS-ETA VOL(m³)"],
            "unidade": "PS-ETA(uni)",
            "prancha": "PS-PRANCHA ETA"
        },
        "ETE": {
            "area": ["PS-ETE Vazão(l/s)", "PS-ETE VOL(m³)"],
            "unidade": "PS-ETE(uni)",
            "prancha": "PS-PRANCHA ETE"
        },
        "EXTENSÃO DE REDE": {
            "area": "PS-EXTENSÃO DE REDE(KM)",
            "prancha": "PS-PRANCHA EXTENSÃO DE REDE"
        },
        "FUNDAÇÃO": {
            "tipo": "PS-FUNDAÇÃO"
        },
        "GEOMÉTRICO": {
            "area": "PS-GEOMÉTRICO(KM)",
            "prancha": "PS-PRANCHA GEOMÉTRICO"
        },
        "GERAÇÃO FOTOVOLTAICA": {
            "area": "PS-GERAÇÃO FOTOVOLTAICA(m²)",
            "kva": "PS-GERAÇÃO FOTOVOLTAICA(kva)",
            "prancha": "PS-PRANCHA GERAÇÃO FOTOVOLTAICA"
        },
        "HIDROLOGIA": {
            "area": "PS-HIDROLOGIA(m²)",
            "kva": "PS-HIDROLOGIA(l/s)",
            "prancha": "PS-PRANCHA HIDROLOGIA"
        },
        "ILUMINAÇÃO PUBLICA": {
            "area": "PS-ILUMINAÇÃO PUBLICA(km)",
            "unidade": "PS-ILUMINAÇÃO PUBLICA(Pontos)",
            "prancha": "PS-PRANCHA ILUMINAÇÃO PUBLICA"
        },
        "INTERCEPTOR": {
            "area": ["PS-INTERCEPTOR(m)", "PS-INTERCEPTOR(l/s)"],
            "unidade": "PS-INTERCEPTOR(uni)",
            "prancha": "PS-PRANCHA INTERCEPTOR"
        },
        "LINHA DE RECALQUE": {
            "area": ["PS-LINHA DE RECALQUE(m)", "PS-LINHA DE RECALQUE(l/s)"],
            "unidade": "PS-LINHA DE RECALQUE(uni)",
            "prancha": "PS-PRANCHA LINHA DE RECALQUE"
        },
        "MEIO AMBIENTE": {
            "tipo": "PS-MEIO AMBIENTE"
        },
        "OAE": {
            "tipo": "PS-OAE"
        },
        "ORÇAMENTO": {
            "area": "PS-ORÇAMENTO(m²)",
            "prancha": "PS-ORÇAMENTO(km)"
        },
        "PAISAGISTICO": {
            "area": "PS-PAISAGISTICO(m²)",
            "prancha": "PS-PRANCHA PAISAGISTICO"
        },
        "PAVIMENTAÇÃO": {
            "tipo": "PS-PAVIMENTAÇÃO"
        },
        "REDE COLETORA": {
            "area": ["PS-REDE COLETORA(m)", "PS-REDE COLETORA(l/s)"],
            "unidade": "PS-REDE COLETORA(uni)" ,
            "prancha": "PS-PRANCHA REDE COLETORA"
        },
        "REDE DE DISTRIBUIÇÃO": {
            "area": ["PS-REDE DE DISTRIBUIÇÃO(m)", "PS-REDE DE DISTRIBUIÇÃO(l/s)"],
            "unidade": "PS-REDE DE DISTRIBUIÇÃO(uni)",
            "prancha": "PS-PRANCHA REDE DE DISTRIBUIÇÃO"
        },
        "SANEAMENTO": {
            "area": "PS-SANEAMENTO(m)",
            "kva": "PS-SANEAMENTO(l/s)",
            "prancha": "PS-PRANCHA SANEAMENTO"
        },
        "SINALIZAÇÃO": {
            "area": "PS-SINALIZAÇÃO(KM)",
            "prancha": "PS-PRANCHA SINALIZAÇÃO"
        },
        "SONDAGEM": {
            "tipo": "PS-SONDAGEM"
        },
        "TERRAPLENAGEM": {
            "area": "PS-TERRAPLENAGEM(KM)",
            "unidade": "PS-TERRAPLENAGEM(uni)",
            "prancha": "PS-PRANCHA TERRAPLENAGEM"
        },
        "TOPOGRAFIA": {
            "tipo": "PS-TIPO TOPOGRAFIA",
            "cadastral": "PS-CADASTRAL-TOP",
            "drone": "PS-DRONE-TOP",
            "area": "PS-TOPOGRAFIA(m²)",
            "prancha": "PS-PRANCHA TOPOGRAFIA"
        },
        "URBANISTICO": {
            "area": "PS-URBANISTICO(m²)",
            "prancha": "PS-PRANCHA URBANISTICO"
        },
    }

    disciplinas_projetoambientais_edi = {
        "DISPENSA DE LICENCIAMENTO": {
            "area": "EDI-DDL(Área)",
            "unidade": "EDI-DDL(UN)",
            "prancha": "EDI-PRANCHA DDL"
        },
        "DISPENSA DE OUTORGA": {
            "area": "EDI-DDO(Área)",
            "unidade": "EDI-DDO(UN)",
            "prancha": "EDI-PRANCHA DDO"
        },
        "EIA/RIMA": {
            "area": "EDI-EIA/RIMA(Área)",
            "unidade": "EDI-EIA/RIMA(UN)",
            "prancha": "EDI-PRANCHA EIA/RIMA"
        },
        "INVENTÁRIO FLORESTAL/PLANO MANEJO": {
            "area": "EDI-IFPM(Área)",
            "unidade": "EDI-IFPM(UN)",
            "prancha": "EDI-PRANCHA IFPM"
        },
        "LICENÇA AMBIENTAL CONCOMITANTE": {
            "area": "EDI-LAC(Área)",
            "unidade": "EDI-LAC(UN)",
            "prancha": "EDI-PRANCHA LAC"
        },
        "PCA – PLANO DE CONTROLE AMBIENTAL": {
            "area": "EDI-PCA(Área)",
            "unidade": "EDI-PCA(UN)",
            "prancha": "EDI-PRANCHA PCA"
        },
        "PIA – PLANO DE INTERVENÇÃO AMBIENTAL": {
            "area": "EDI-PIA(Área)",
            "unidade": "EDI-PIA(UN)",
            "prancha": "EDI-PRANCHA PIA"
        },
        "PMGIRS – PLANO MUNICIPAL DE GERENCIAMENTO INTEGRADO DE RESÍDUOS SÓLIDOS": {
            "area": "EDI-PMGIRS(Área)",
            "unidade": "EDI-PMGIRS(UN)",
            "prancha": "EDI-PRANCHA PMGIRS"
        },
        "PRADA – PROJETO DE RECUPERAÇÃO DE ÁGUAS DEGRADADAS E ALTERADAS": {
            "area": "EDI-PRADA(Área)",
            "unidade": "EDI-PRADA(UN)",
            "prancha": "EDI-PRANCHA PRADA"
        },
        "RAS – RELATÓRIO AMBIENTAL SIMPLIFICADO": {
            "area": "EDI-RAS(Área)",
            "unidade": "EDI-RAS(UN)",
            "prancha": "EDI-PRANCHA RAS"
        },
        "RCA – RELATÓRIO DE CONTROLE AMBIENTAL": {
            "area": "EDI-RCA(Área)",
            "unidade": "EDI-RCA(UN)",
            "prancha": "EDI-PRANCHA RCA"
        },
        "RELATÓRIO DE OUTORGA": {
            "area": "EDI-RDO(Área)",
            "unidade": "EDI-RDO(UN)",
            "prancha": "EDI-PRANCHA RDO"
        }
    }

    disciplinas_projetoambientais_inf = {
        "DISPENSA DE LICENCIAMENTO": {
            "area": "INF-DDL(Área)",
            "unidade": "INF-DDL(UN)",
            "prancha": "INF-PRANCHA DDL"
        },
        "DISPENSA DE OUTORGA": {
            "area": "INF-DDO(Área)",
            "unidade": "INF-DDO(UN)",
            "prancha": "INF-PRANCHA DDO"
        },
        "EIA/RIMA": {
            "area": "INF-EIA(Área)",
            "unidade": "INF-EIA(UN)",
            "prancha": "INF-PRANCHA EIA"
        },
        "INVENTÁRIO FLORESTAL/PLANO MANEJO": {
            "area": "INF-IFPM(Área)",
            "unidade": "INF-IFPM(UN)",
            "prancha": "INF-PRANCHA IFPM"
        },
        "LICENÇA AMBIENTAL CONCOMITANTE": {
            "area": "INF-LAC(Área)",
            "unidade": "INF-LAC(UN)",
            "prancha": "INF-PRANCHA LAC"
        },
        "PCA – PLANO DE CONTROLE AMBIENTAL": {
            "area": "INF-PCA(Área)",
            "unidade": "INF-PCA(UN)",
            "prancha": "INF-PRANCHA PCA"
        },
        "PIA – PLANO DE INTERVENÇÃO AMBIENTAL": {
            "area": "INF-PIA(Área)",
            "unidade": "INF-PIA(UN)",
            "prancha": "INF-PRANCHA PIA"
        },
        "PMGIRS – PLANO MUNICIPAL DE GERENCIAMENTO INTEGRADO DE RESÍDUOS SÓLIDOS": {
            "area": "INF-PMGIRS(Área)",
            "unidade": "INF-PMGIRS(UN)",
            "prancha": "INF-PRANCHA PMGIRS"
        },
        "PRADA – PROJETO DE RECUPERAÇÃO DE ÁGUAS DEGRADADAS E ALTERADAS": {
            "area": "INF-PRADA(Área)",
            "unidade": "INF-PRADA(UN)",
            "prancha": "INF-PRANCHA PRADA"
        },
        "RAS – RELATÓRIO AMBIENTAL SIMPLIFICADO": {
            "area": "INF-RAS(Área)",
            "unidade": "INF-RAS(UN)",
            "prancha": "INF-PRANCHA RAS"
        },
        "RCA – RELATÓRIO DE CONTROLE AMBIENTAL": {
            "area": "INF-RCA(Área)",
            "unidade": "INF-RCA(UN)",
            "prancha": "INF-PRANCHA RCA"
        },
        "RELATÓRIO DE OUTORGA": {
            "area": "INF-RDO(Área)",
            "unidade": "INF-RDO(UN)",
            "prancha": "INF-PRANCHA RDO"
        }

    }

    disciplinas_ensaios = {
        "AÇO": {"tipo": "AÇO"},
        "ASFALTO": {"tipo":"ASFALTO"},
        "CONCRETO": {"tipo":"CONCRETO"},
        "SOLO": {"tipo": "SOLO"},
        "SONDAGEM": {"tipo": "SONDAGEM"},
    }

    disciplinas_planodiretor = {
        "PLANO DIRETOR": {
            "area": "PDI-NUMERO HABITANTE",
            "prancha": "PDI-PRANCHA"}
    }

    disciplinas_diversos = {
        "ACÚSTICA": {
            "area": "DI-ACÚSTICA(m²)",
            "prancha": "DI-PRANCHA ACÚSTICA"
        },
        "AÇO": {
            "tipo": ["DI-AÇO"]
        },
        "ADEQUAÇÃO DE ACESSIBILIDADE": {
            "area": ["DI-ADEQUAÇÃO DE ACESSIBILIADE(m²)"],
            "prancha": ["DI-PRANCHA ADEQUAÇÃO DE ACESSIBILIDADE"]
        },
        "ADUTORA": {
            "area": ["DI-ADUTORA(m)"],
            "unidade": ["DI-ADUTORA(uni)"],
            "prancha": ["DI-PRANCHA ADUTORA"]
        },
        "ALARME/CFTV": {
            "area": ["DI-ALARME/CFTV(m²)"],
            "prancha": ["DI-PRANCHA ALARME/CFTV"]
        },
        "ANTEPROJETO": {
            "area": ["DI-ANTEPROJETO(m²)", "DI-ANTEPROJETO(m)"],
            "prancha": ["DI-PRANCHA ANTEPROJETO"]
        },
        "AR CONDICIONADO": {
            "area": ["DI-AR CONDICIONADO(m²)"],
            "prancha": ["DI-PRANCHA AR CONDICIONADO"]
        },
        "ARQUITETÔNICO CONSTRUÇÃO": {
            "area": ["DI-ARQUITETÔNICO CONSTRUÇÃO(m²)"],
            "prancha": ["DI- PRANCHA ARQUITETÔNICO CONSTRUÇÃO"]
        },
        "ARQUITETÔNICO REFORMA": {
            "area": [ "DI-ARQUITETÔNICO REFORMA(m²)"],
            "prancha": [ "DI-PRANCHA ARQUITETÔNICO REFORMA"]
        },
        "ARQUITETÔNICO RESTAURO": {
            "area": ["DI-ARQUITETÔNICO RESTAURO(m²)"],
            "prancha": ["DI-PRANCHA ARQUITETÔNICO RESTAURO"]
        },
        "ASFALTO": {
            "tipo": ["DI-ASFALTO"]
                    },
        "AS BUILT": {
            "tipo": ["DI-TIPO AS BUILT"],
            "area": [ "DI-AS BUILT(m²)"],
            "prancha": ["DI-PRANCHA AS BUILT"]
        },
        "AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO": {
            "area": "DI-AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO(m²)",
            "unidade": "DI-AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO(uni)",
            "prancha": "DI-PRANCHA AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO"
        },
        "BATIMETRIA": {
            "area": ["DI-BATIMETRIA(m²)"],
            "prancha": ["DI-PRANCHA BATIMETRIA"]
        },
        "CAB. ESTRUTURADO": {
            "area": ["DI-CAB. ESTRUTURADO(m²)"],
            "prancha": ["DI-PRANCHA CAB. ESTRUTURADO"]
        },
        "CLIMATIZAÇÃO": {
            "area": [ "DI-CLIMATIZAÇÃO(m²)"],
            "kva": ["DI-CLIMATIZAÇÃO(kbtu/h)"],
            "prancha": ["DI-PRANCHA CLIMATIZAÇÃO"]
        },
        "COMPAT. PROJETOS": {
            "area": ["DI-COMPAT. PROJETOS(m²)"],
            "prancha": ["DI-PRANCHA COMPAT. PROJETOS"]
        },
        "COMUNICAÇÃO VISUAL": {
            "area": ["DI-COMUNICAÇÃO VISUAL(m²)"],
            "prancha": ["DI-PRANCHA COMUNICAÇÃO VISUAL"]
        },
        "CONCRETO": {
            "tipo": ["DI-CONCRETO"]
        },
        "CONJUNTO MOTOBOMBA": {
            "area": ["DI-CONJUNTO MOTOBOMBA(uni)"],
            "prancha": ["DI-PRANCHA CONJUNTO MOTOBOMBA"]
        },
        "CONTENÇÃO": {
            "tipo": ["DI-CONTENÇÃO"]
        },
        "DISPENSA DE LICENCIAMENTO": {
            "area": ["DI-DDL(Área)"],
            "unidade": ["DI-DDL(UN)"],
            "prancha": ["DI-PRANCHA DDL"]
        },
        "DISPENSA DE OUTORGA": {
            "area": ["DI-DDO(Área)"],
            "unidade": ["DI-DDO(UN)"],
            "prancha": ["DI-PRANCHA DDO"]
        },
        "DRENAGEM": {
            "area": ["DI-DRENAGEM(m²)", "DI-DRENAGEM(km)"],
            "prancha": ["DI-PRANCHA DRENAGEM"]
        },
        "EIA/RIMA": {
            "area": ["DI-EIA/RIMA(Área)"],
            "unidade": ["DI-EIA/RIMA(UN)"],
            "prancha": ["DI-PRANCHA EIA/RIMA"]
        },
        "ELEVATÓRIA": {
            "area": ["DI-ELEVATÓRIA(l/s)"],
            "unidade": ["DI-ELEVATÓRIA(uni)"],
            "prancha": ["DI-PRANCHA ELEVATÓRIA"]
        },
        "ELÉTRICO": {
            "area": ["DI-ELÉTRICO(m²)"],
            "kva": ["KVA", "DI-KVA", "VU-KVA", "PR-KVA", "PS-KVA"],
            "prancha": ["DI-PRANCHA ELÉTRICO"]
        },
        "ESTRUTURAL": {
            "tipo": ["DI-ESTRUTURAL"]
        },
        "ETA": {
            "area": ["DI-ETA Vazão(l/s)", "DI-ETA VOL(m³)"],
            "unidade": ["DI-ETA(uni)"],
            "prancha": ["DI-PRANCHA ETA"]
        },
        "ETE": {
            "area": ["DI-ETE Vazão(l/s)", "DI-ETE VOL(m³)"],
            "unidade": ["DI-ETE(uni)"],
            "prancha": ["DI-PRANCHA ETE"]
        },
        "EXTENSÃO DE REDE": {
            "area": ["DI-EXTENSÃO DE REDE(km)"],
            "prancha": ["DI-PRANCHA EXTENSÃO DE REDE"]
        },
        "FUNDAÇÃO": {
            "tipo": ["DI-FUNDAÇÃO"]
        },
        "GASES MEDICINAIS": {
            "area": ["DI-GASES MEDICINAIS(m²)", "DI-GASES MEDICINAIS(m³)"],
            "prancha": ["DI-PRANCHA GASES MEDICINAIS"]
        },
        "GEOMÉTRICO": {
            "area": [ "DI-GEOMÉTRICO(KM)"],
            "prancha": ["DI-PRANCHA GEOMÉTRICO"]
        },
        "GERAÇÃO FOTOVOLTAICA": {
            "area": ["DI-GERAÇÃO FOTOVOLTAICA(m²)"],
            "kva": ["DI-GERAÇÃO FOTOVOLTAICA(kva)"],
            "prancha": ["DI-PRANCHA GERAÇÃO FOTOVOLTAICA"]
        },
        "GLP": {
            "area": ["DI-GLP(m²)"],
            "prancha": ["DI-PRANCHA GLP"]
        },
        "HIDROLOGIA": {
            "area": ["DI-HIDROLOGIA(m²)"],
            "kva": ["DI-HIDROLOGIA(l/s)"],
            "prancha": ["DI-PRANCHA HIDROLOGIA"]
        },
        "HIDROSSANITÁRIO": {
            "area": ["DI-HIDROSSANITÁRIO(m²)"],
            "prancha": ["DI-PRANCHA HIDROSSANITÁRIO"]
        },
        "ILUMINAÇÃO PUBLICA": {
            "area": ["DI-ILUMINAÇÃO PUBLICA(km)"],
            "kva": ["DI-ILUMINAÇÃO PUBLICA(ponto)"],
            "prancha": ["DI-PRANCHA ILUMINAÇÃO PUBLICA"]
        },
        "INTERCEPTOR": {
            "area": ["DI-INTERCEPTOR(m)", "DI-INTERCEPTOR(l/s)"],
            "unidade": "DI-INTERCEPTOR(uni)",
            "prancha": "DI-PRANCHA INTERCEPTOR"
        },
        "INVENTÁRIO FLORESTAL/PLANO MANEJO": {
            "area": ["DI-IFPM(Área)"],
            "unidade": ["DI-IFPM(UN)"],
            "prancha": ["DI-PRANCHA IFPM"]
        },
        "IRRIGAÇÃO": {
            "area": ["DI-IRRIGAÇÃO(m²)"],
            "prancha": ["DI-PRANCHA IRRIGAÇÃO"]
        },
        "LEVANTAMENTO ARQUITETÔNICO": {
            "tipo": ["DI-TIPO LEVANTAMENTO ARQUITETÔNICO"],
            "area": [ "DI-LEVANTAMENTO ARQUITETÔNICO(m²)"],
            "prancha": ["DI-PRANCHA LEVANTAMENTO ARQUITETÔNICO"]
        },
        "LICENÇA AMBIENTAL CONCOMITANTE": {
            "area": ["DI-LAC(Área)"],
            "unidade": ["DI-LAC(UN)"],
            "prancha": ["DI-PRANCHA LAC"]
        },
        "LINHA DE RECALQUE": {
            "area": ["DI-LINHA DE RECALQUE(m)", "DI-LINHA DE RECALQUE(l/s)"],
            "unidade": ["DI-LINHA DE RECALQUE(uni)"],
            "prancha": ["DI-PRANCHA LINHA DE RECALQUE"]
        },
        "MAQ ELET / 3D": {
            "tipo": ["DI-MAQ ELET/3D"]
        },
        "MEIO AMBIENTE": {
            "tipo": ["DI-MEIO AMBIENTE"]
        },
        "MOBILIÁRIO": {
            "tipo": ["DI-MOBILIÁRIO"]
        },
        "OAE": {
            "tipo": ["DI-OAE"]
        },
        "ORÇAMENTO": {
            "area": ["DI-ORÇAMENTO(m²)"],
            "prancha": ["DI-ORÇAMENTO(km)"]
        },
        "PAISAGISTICO": {
            "area": ["DI-PAISAGISTICO(m²)"],
            "prancha": ["DI-PRANCHA PAISAGISTICO"]
        },
        "PAVIMENTAÇÃO": {
            "tipo": ["DI-PAVIMENTAÇÃO"]
        },
        "PCA – PLANO DE CONTROLE AMBIENTAL": {
            "area": ["DI-PCA(Área)",],
            "unidade": ["DI-PCA(UN)"],
            "prancha": ["DI-PRANCHA PCA"]
        },
        "PIA – PLANO DE INTERVENÇÃO AMBIENTAL": {
            "area": ["DI-PIA(Área)"],
            "unidade": ["DI-PIA(UN)"],
            "prancha": ["DI-PRANCHA PIA"]
        },
        "PLANO DIRETOR": {
            "area": ["DI-NUMERO HABITANTE"],
            "prancha": ["DI-PRANCHA"]
        },
        "PLANO SANEAMENTO BÁSICO - PMSB": {
            "area": ["DI PMSB-NUMERO HABITANTES"],
            "prancha": ["DI PMSB-PRANCHA"]
        },
        "PMGIRS – PLANO MUNICIPAL DE GERENCIAMENTO INTEGRADO DE RESÍDUOS SÓLIDOS": {
            "area": ["DI-PMGIRS(Área)"],
            "unidade": ["DI-PMGIRS(UN)"],
            "prancha": ["DI-PRANCHA PMGIRS"]
        },
        "PRADA – PROJETO DE RECUPERAÇÃO DE ÁGUAS DEGRADADAS E ALTERADAS": {
            "area": ["DI-PRADA(Área)"],
            "unidade": ["DI-PRADA(UN)"],
            "prancha": ["DI-PRANCHA PRADA"]
        },
        "RAS – RELATÓRIO AMBIENTAL SIMPLIFICADO": {
            "area": ["DI-RAS(Área)"],
            "unidade": ["DI-RAS(UN)"],
            "prancha": ["DI-PRANCHA RAS"]
        },
        "RCA – RELATÓRIO DE CONTROLE AMBIENTAL": {
            "area": ["DI-RCA(Área)"],
            "unidade": ["DI-RCA(UN)"],
            "prancha": ["DI-PRANCHA RCA"]
        },
        "REDE COLETORA": {
            "area": ["DI-REDE COLETORA(m)"],
            "kva": "DI-REDE COLETORA(l/s)",
            "unidade": ["DI-REDE COLETORA(uni)"],
            "prancha": ["DI-PRANCHA REDE COLETORA"]
        },
        "REDE DE DISTRIBUIÇÃO": {
            "area": ["DI-REDE DE DISTRIBUIÇÃO(m)"],
            "kva": "DI-REDE DE DISTRIBUIÇÃO(l/s)",
            "unidade": ["DI-REDE DE DISTRIBUIÇÃO(uni)"],
            "prancha": ["DI-PRANCHA REDE DE DISTRIBUIÇÃO"]
        },
        "RELATÓRIO DE OUTORGA": {
            "area": ["DI-RDO(Área)"],
            "unidade": ["DI-RDO(UN)"],
            "prancha": ["DI-PRANCHA RDO"]
        },
        "REURB": {
            "area": ["DI-Un.Habitacionais"],
            "prancha": [ "DI-PRANCHA REURB"]
        },
        "REURB REGULARIZAÇÃO FUNDIARIA": {
            "area": [ "DI-REUR_HABITANTES"],
            "prancha": [ "DI-REUR PRANCHA"]
        },
        "SANEAMENTO": {
            "area": ["DI-SANEAMENTO(m)"],
            "kva": ["DI-SANEAMENTO(l/s)"],
            "prancha": ["DI-PRANCHA SANEAMENTO"]
        },
        "SINALIZAÇÃO": {
            "area": ["DI-SINALIZAÇÃO(KM)"],
            "prancha": ["DI-PRANCHA SINALIZAÇÃO"]
        },
        "SOLO": {
            "tipo": ["DI-SOLO"]
        },
        "SONDAGEM": {
            "tipo": ["DI-SONDAGEM"]
        },
        "SPCI": {
            "area": ["DI-SPCI(m²)"],
            "prancha": [ "DI-PRANCHA SPCI"]
        },
        "SPDA": {
            "area": ["DI-SPDA(m²)"],
            "prancha": ["DI-PRANCHA SPDA"]
        },
        "TERRAPLENAGEM": {
            "area": ["DI-TERRAPLENAGEM(m²)", "DI-TERRAPLENAGEM(km)"],
            "unidade": "DI-TERRAPLENAGEM(uni)",
            "prancha": ["DI-PRANCHA TERRAPLENAGEM"]
        },
        "TOPOGRAFIA": {
            "area": ["DI-TOPOGRAFIA(m²)"],
            "tipo": ["DI-TIPO TOPOGRAFIA"],
            "cadastral": ["DI-CADASTRAL"],
            "drone": ["DI-DRONE"],
            "prancha": ["DI-PRANCHA TOPOGRAFIA"]
        },
        "URBANISTICO": {
            "area": ["DI-URBANISTICO(m²)"],
            "prancha": ["DI-PRANCHA URBANISTICO"]
        },
        "VENTILAÇÃO/EXAUSTÃO": {
            "area": ["DI-VENTILAÇÃO/EXAUSTÃO(m²)"],
            "kva": ["DI-VENTILAÇÃO/EXAUSTÃO(kbtu/h)"],
            "prancha": ["DI-PRANCHA VENTILAÇÃO/EXAUSTÃO"]
        }
    }

    disciplinas_reur = {
        "REURB REGULARIZAÇÃO FUNDIARIA": {
            "area": "REUR_HABITANTES",
            "prancha": "REUR-PRANCHA"
        }
    }

    todas_disciplinas = {
        "ACÚSTICA": {
            "area": ["ACÚSTICA(m²)", "DI-ACÚSTICA(m²)"],
            "prancha": ["PRANCHA ACÚSTICA", "DI-PRANCHA ACÚSTICA"]
        },
        "AÇO": {
            "tipo": ["AÇO", "DI-AÇO"]
        },
        "ADEQUAÇÃO DE ACESSIBILIDADE": {
            "area": ["ADEQUAÇÃO DE ACESSIBILIADE(m²)", "DI-ADEQUAÇÃO DE ACESSIBILIADE(m²)", "VU-ADEQUAÇÃO DE ACESSIBILIADE(m²)", "PR-ADEQUAÇÃO DE ACESSIBILIADE(m²)"],
            "prancha": ["PRANCHA ADEQUAÇÃO DE ACESSIBILIDADE", "DI-PRANCHA ADEQUAÇÃO DE ACESSIBILIDADE", "VU-PRANCHA ADEQUAÇÃO DE ACESSIBILIDADE", "PR-PRANCHA ADEQUAÇÃO DE ACESSIBILIDADE"]
        },
        "ADUTORA": {
            "area": ["PS-ADUTORA(m)", "PS-ADUTORA(l/s)", "DI-ADUTORA(m)", "DI-ADUTORA(l/s)"],
            "unidade": ["PS-ADUTORA(uni)", "DI-ADUTORA(uni)"],
            "prancha": ["PS-PRANCHA ADUTORA", "DI-PRANCHA ADUTORA"]
        },
        "ALARME/CFTV": {
            "area": ["ALARME/CFTV(m²)", "DI-ALARME/CFTV(m²)"],
            "prancha": ["PRANCHA ALARME/CFTV", "DI-PRANCHA ALARME/CFTV"]
        },
        "ANTEPROJETO": {
            "area": ["ANTEPROJETO(m²)", "DI-ANTEPROJETO(m²)", "VU-ANTEPROJETO(m²)", "PR-ANTEPROJETO(m²)", "DI-ANTEPROJETO(m)", "VU-ANTEPROJETO(m)", "PR-ANTEPROJETO(m)"],
            "prancha": ["PRANCHA ANTEPROJETO", "DI-PRANCHA ANTEPROJETO", "VU-PRANCHA ANTEPROJETO", "PR-PRANCHA ANTEPROJETO"]
        },
        "ANTEPROJETO DE INFRA": {
            "area": ["PS-ANTEPROJETO DE INFRA(km)"],
            "prancha": ["PS-PRANCHA ANTEPROJETO DE INFRA"]
        },
        "AR CONDICIONADO": {
            "area": ["AR CONDICIONADO(m²)", "DI-AR CONDICIONADO(m²)"],
            "prancha": ["PRANCHA AR CONDICIONADO", "DI-PRANCHA AR CONDICIONADO"]
        },
        "ARQUITETÔNICO CONSTRUÇÃO": {
            "area": ["ARQUITETÔNICO CONSTRUÇÃO(m²)", "DI-ARQUITETÔNICO CONSTRUÇÃO(m²)"],
            "prancha": ["PRANCHA ARQUITETÔNICO CONSTRUÇÃO", "DI- PRANCHA ARQUITETÔNICO CONSTRUÇÃO"]
        },
        "ARQUITETÔNICO REFORMA": {
            "area": ["ARQUITETÔNICO REFORMA(m²)", "DI-ARQUITETÔNICO REFORMA(m²)"],
            "prancha": ["PRANCHA ARQUITETÔNICO REFORMA", "DI-PRANCHA ARQUITETÔNICO REFORMA"]
        },
        "ARQUITETÔNICO RESTAURO": {
            "area": ["ARQUITETÔNICO RESTAURO(m²)", "DI-ARQUITETÔNICO RESTAURO(m²)"],
            "prancha": ["PRANCHA ARQUITETÔNICO RESTAURO", "DI-PRANCHA ARQUITETÔNICO RESTAURO"]
        },
        "ASFALTO": {
            "tipo": ["ASFALTO", "DI-ASFALTO"]
                    },
        "AS BUILT": {
            "tipo": ["TIPO AS BUILT", "DI-TIPO AS BUILT"],
            "area": ["AS BUILT(m²)", "DI-AS BUILT(m²)"],
            "prancha": ["PRANCHA AS BUILT", "DI-PRANCHA AS BUILT"]
        },
        "AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO": {
            "area": ["AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO(m²)", "DI-AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO(m²)"],
            "unidade": ["AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO(uni)", "DI-AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO(uni)"],
            "prancha": ["PRANCHA AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO", "DI-PRANCHA AVALIAÇÃO DO ESTADO DE CONSERVAÇÃO"]
        },
        "BATIMETRIA": {
            "area": ["VU-BATIMETRIA(m²)", "DI-BATIMETRIA(m²)", "PR-BATIMETRIA(m²)", "PS-BATIMETRIA(m²)"],
            "prancha": ["VU-PRANCHA BATIMETRIA", "DI-PRANCHA BATIMETRIA", "PR-PRANCHA BATIMETRIA", "PS-PRANCHA BATIMETRIA"]
        },
        "CAB. ESTRUTURADO": {
            "area": ["CAB. ESTRUTURADO(m²)", "DI-CAB. ESTRUTURADO(m²)"],
            "prancha": ["PRANCHA CAB. ESTRUTURADO", "DI-PRANCHA CAB. ESTRUTURADO"]
        },
        "CLIMATIZAÇÃO": {
            "area": ["CLIMATIZAÇÃO(m²)", "DI-CLIMATIZAÇÃO(m²)"],
            "kva": ["CLIMATIZAÇÃO(kbtu/h)", "DI-CLIMATIZAÇÃO(kbtu/h)"],
            "prancha": ["PRANCHA CLIMATIZAÇÃO", "DI-PRANCHA CLIMATIZAÇÃO"]
        },
        "COMPAT. PROJETOS": {
            "area": ["COMPAT. PROJETOS(m²)", "DI-COMPAT. PROJETOS(m²)", "VU-COMPAT. PROJETOS(m²)", "PR-COMPAT. PROJETOS(m²)", "PS-COMPAT. PROJETOS(m²)"],
            "prancha": ["PRANCHA COMPAT. PROJETOS", "DI-PRANCHA COMPAT. PROJETOS", "VU-PRANCHA COMPAT. PROJETOS", "PR-PRANCHA COMPAT. PROJETOS", "PS-PRANCHA COMPAT. PROJETOS"]
        },
        "COMUNICAÇÃO VISUAL": {
            "area": ["COMUNICAÇÃO VISUAL(m²)", "DI-COMUNICAÇÃO VISUAL(m²)"],
            "prancha": ["PRANCHA COMUNICAÇÃO VISUAL", "DI-PRANCHA COMUNICAÇÃO VISUAL"]
        },
        "CONCRETO": {
            "tipo": ["CONCRETO", "DI-CONCRETO"]
        },
        "CONJUNTO MOTOBOMBA": {
            "area": ["PS-CONJUNTO MOTOBOMBA(uni)", "DI-CONJUNTO MOTOBOMBA(uni)"],
            "prancha": ["PS-PRANCHA CONJUNTO MOTOBOMBA", "DI-PRANCHA CONJUNTO MOTOBOMBA"]
        },
        "CONTENÇÃO": {
            "tipo": ["CONTENÇÃO", "DI-CONTENÇÃO","VU-CONTENÇÃO", "PR-CONTENÇÃO", "PS-CONTENÇÃO"]
        },
        "DISPENSA DE LICENCIAMENTO": {
            "area": ["EDI-DDL(Área)", "DI-DDL(Área)", "INF-DDL(Área)"],
            "unidade": ["EDI-DDL(UN)", "DI-DDL(UN)", "INF-DDL(UN)"],
            "prancha": ["EDI-PRANCHA DDL", "DI-PRANCHA DDL", "INF-PRANCHA DDL"]
        },
        "DISPENSA DE OUTORGA": {
            "area": ["EDI-DDO(Área)", "DI-DDO(Área)", "INF-DDO(Área)"],
            "unidade": ["EDI-DDO(UN)", "DI-DDO(UN)", "INF-DDO(UN)"],
            "prancha": ["EDI-PRANCHA DDO", "DI-PRANCHA DDO", "INF-PRANCHA DDO"]
        },
        "DRENAGEM": {
            "area": ["DRENAGEM(m²)", "DRENAGEM(km)", "DI-DRENAGEM(m²)", "DI-DRENAGEM(km)", "VU-DRENAGEM(KM)", "PR-DRENAGEM(KM)", "PS-DRENAGEM(km)"],
            "prancha": ["PRANCHA DRENAGEM", "DI-PRANCHA DRENAGEM", "VU-PRANCHA DRENAGEM", "PR-PRANCHA DRENAGEM", "PS-PRANCHA DRENAGEM"]
        },
        "EIA/RIMA": {
            "area": ["EDI-EIA/RIMA(Área)", "DI-EIA/RIMA(Área)", "INF-EIA/RIMA(Área)"],
            "unidade": ["EDI-EIA/RIMA(UN)", "DI-EIA/RIMA(UN)", "INF-EIA/RIMA(UN)"],
            "prancha": ["EDI-PRANCHA EIA/RIMA", "DI-PRANCHA EIA/RIMA", "INF-PRANCHA EIA/RIMA"]
        },
        "ELEVATÓRIA": {
            "area": ["PS-ELEVATÓRIA(l/s)", "DI-ELEVATÓRIA(l/s)"],
            "unidade": ["PS-ELEVATÓRIA(uni)", "DI-ELEVATÓRIA(uni)"],
            "prancha": ["PS-PRANCHA ELEVATÓRIA", "DI-PRANCHA ELEVATÓRIA"]
        },
        "ELÉTRICO": {
            "area": ["ELÉTRICO(m²)", "DI-ELÉTRICO(m²)", "VU-ELÉTRICO(m²)", "PR-ELÉTRICO(m²)", "PS-ELÉTRICO(m²)"],
            "kva": ["KVA", "DI-KVA", "VU-KVA", "PR-KVA", "PS-KVA"],
            "prancha": ["PRANCHA ELÉTRICO", "DI-PRANCHA ELÉTRICO", "VU-PRANCHA ELÉTRICO", "PR-PRANCHA ELÉTRICO", "PS-PRANCHA ELÉTRICO"]
        },
        "ESTRUTURAL": {
            "tipo": ["ESTRUTURAL", "DI-ESTRUTURAL", "VU-ESTRUTURAL", "PR-ESTRUTURAL", "PS-ESTRUTURAL"]
        },
        "ETA": {
            "area": ["PS-ETA Vazão(l/s)", "PS-ETA VOL(m³)", "DI-ETA Vazão(l/s)", "DI-ETA VOL(m³)"],
            "unidade": ["PS-ETA(uni)", "DI-ETA(uni)"],
            "prancha": ["PS-PRANCHA ETA", "DI-PRANCHA ETA"]
        },
        "ETE": {
            "area": ["PS-ETE Vazão(l/s)", "PS-ETE VOL(m³)", "DI-ETE Vazão(l/s)", "DI-ETE VOL(m³)"],
            "unidade": ["PS-ETE(uni)", "DI-ETE(uni)"],
            "prancha": ["PS-PRANCHA ETE", "DI-PRANCHA ETE"]
        },
        "EXTENSÃO DE REDE": {
            "area": ["EXTENSÃO DE REDE(km)", "DI-EXTENSÃO DE REDE(km)", "VU-EXTENSÃO DE REDE(KM)", "PR-EXTENSÃO DE REDE(KM)", "PS-EXTENSÃO DE REDE(KM)"],
            "prancha": ["PRANCHA EXTENSÃO DE REDE", "DI-PRANCHA EXTENSÃO DE REDE", "VU-PRANCHA EXTENSÃO DE REDE", "PR-PRANCHA EXTENSÃO DE REDE", "PS-PRANCHA EXTENSÃO DE REDE"]
        },
        "FUNDAÇÃO": {
            "tipo": ["FUNDAÇÃO", "DI-FUNDAÇÃO", "VU-FUNDAÇÃO", "PR-FUNDAÇÃO", "PS-FUNDAÇÃO"]
        },
        "GASES MEDICINAIS": {
            "area": ["GASES MEDICINAIS(m²)", "GASES MEDICINAIS(m³)", "DI-GASES MEDICINAIS(m²)", "DI-GASES MEDICINAIS(m³)"],
            "prancha": ["PRANCHA GASES MEDICINAIS", "DI-PRANCHA GASES MEDICINAIS"]
        },
        "GEOMÉTRICO": {
            "area": ["VU-GEOMÉTRICO(KM)", "PR-GEOMÉTRICO(KM)", "PS-GEOMÉTRICO(KM)", "DI-GEOMÉTRICO(KM)"],
            "prancha": ["VU-PRANCHA GEOMÉTRICO", "PR-PRANCHA GEOMÉTRICO", "PS-PRANCHA GEOMÉTRICO", "DI-PRANCHA GEOMÉTRICO"]
        },
        "GERAÇÃO FOTOVOLTAICA": {
            "area": ["GERAÇÃO FOTOVOLTAICA(m²)", "DI-GERAÇÃO FOTOVOLTAICA(m²)", "VU-GERAÇÃO FOTOVOLTAICA(m²)", "PR-GERAÇÃO FOTOVOLTAICA(m²)", "PS-GERAÇÃO FOTOVOLTAICA(m²)"],
            "kva": ["GERAÇÃO FOTOVOLTAICA(kva)", "DI-GERAÇÃO FOTOVOLTAICA(kva)", "VU-GERAÇÃO FOTOVOLTAICA(kva)", "PR-GERAÇÃO FOTOVOLTAICA(kva)", "PS-GERAÇÃO FOTOVOLTAICA(kva)"],
            "prancha": ["PRANCHA GERAÇÃO FOTOVOLTAICA", "DI-PRANCHA GERAÇÃO FOTOVOLTAICA", "VU-PRANCHA GERAÇÃO FOTOVOLTAICA", "PR-PRANCHA GERAÇÃO FOTOVOLTAICA", "PS-PRANCHA GERAÇÃO FOTOVOLTAICA"]
        },
        "GLP": {
            "area": ["GLP(m²)", "GLP(m³)", "DI-GLP(m²)", "DI-GLP(m³)"],
            "prancha": ["PRANCHA GLP", "DI-PRANCHA GLP"]
        },
        "HIDROLOGIA": {
            "area": ["VU-HIDROLOGIA(m²)", "DI-HIDROLOGIA(m²)", "PR-HIDROLOGIA(m²)", "PS-HIDROLOGIA(m²)"],
            "kva": ["VU-HIDROLOGIA(l/s)", "DI-HIDROLOGIA(l/s)", "PR-HIDROLOGIA(l/s)", "PS-HIDROLOGIA(l/s)"],
            "prancha": ["VU-PRANCHA HIDROLOGIA", "DI-PRANCHA HIDROLOGIA", "PR-PRANCHA HIDROLOGIA", "PS-PRANCHA HIDROLOGIA"]
        },
        "HIDROSSANITÁRIO": {
            "area": ["HIDROSSANITÁRIO(m²)", "DI-HIDROSSANITÁRIO(m²)"],
            "prancha": ["PRANCHA HIDROSSANITÁRIO", "DI-PRANCHA HIDROSSANITÁRIO"]
        },
        "ILUMINAÇÃO PUBLICA": {
            "area": ["ILUMINAÇÃO PUBLICA(km)", "DI-ILUMINAÇÃO PUBLICA(km)", "VU-ILUMINAÇÃO PUBLICA(km)", "PR-ILUMINAÇÃO PUBLICA(km)", "PS-ILUMINAÇÃO PUBLICA(km)"],
            "kva": ["ILUMINAÇÃO PUBLICA(ponto)", "DI-ILUMINAÇÃO PUBLICA(ponto)", "VU-ILUMINAÇÃO PUBLICA(Pontos)", "PR-ILUMINAÇÃO PUBLICA(Pontos)", "PS-ILUMINAÇÃO PUBLICA(Pontos)"],
            "prancha": ["PRANCHA ILUMINAÇÃO PUBLICA", "DI-PRANCHA ILUMINAÇÃO PUBLICA", "VU-PRANCHA ILUMINAÇÃO PUBLICA", "PR-PRANCHA ILUMINAÇÃO PUBLICA", "PS-PRANCHA ILUMINAÇÃO PUBLICA"]
        },
        "IMPERMEABLIZAÇÃO":{
            "area": ["IMPERMEABILIZAÇÃO(m²)", "DI-IMPERMEABILIZAÇÃO(m²)"],
            "prancha": ["PRANCHA IMPERMEABIALIZAÇÃO", "DI-PRANCHA IMPERMEABIALIZAÇÃO"]
        },
        "INTERCEPTOR": {
            "area": ["PS-INTERCEPTOR(m)", "PS-INTERCEPTOR(l/s)", "DI-INTERCEPTOR(m)", "DI-INTERCEPTOR(l/s)"],
            "unidade": ["PS-INTERCEPTOR(uni)", "DI-INTERCEPTOR(uni)"],
            "prancha": ["PS-PRANCHA INTERCEPTOR", "DI-PRANCHA INTERCEPTOR"]
        },
        "INVENTÁRIO FLORESTAL/PLANO MANEJO": {
            "area": ["EDI-IFPM(Área)", "DI-IFPM(Área)", "INF-IFPM(Área)"],
            "unidade": ["EDI-IFPM(UN)", "DI-IFPM(UN)", "INF-IFPM(UN)"],
            "prancha": ["EDI-PRANCHA IFPM", "DI-PRANCHA IFPM","INF-PRANCHA IFPM"]
        },
        "IRRIGAÇÃO": {
            "area": ["IRRIGAÇÃO(m²)", "DI-IRRIGAÇÃO(m²)"],
            "prancha": ["PRANCHA IRRIGAÇÃO", "DI-PRANCHA IRRIGAÇÃO"]
        },
        "LEVANTAMENTO ARQUITETÔNICO": {
            "tipo": ["TIPO LEVANTAMENTO ARQUITETÔNICO", "DI-TIPO LEVANTAMENTO ARQUITETÔNICO"],
            "area": ["LEVANTAMENTO ARQUITETÔNICO(m²)", "DI-LEVANTAMENTO ARQUITETÔNICO(m²)"],
            "prancha": ["PRANCHA LEVANTAMENTO ARQUITETÔNICO", "DI-PRANCHA LEVANTAMENTO ARQUITETÔNICO"]
        },
        "LICENÇA AMBIENTAL CONCOMITANTE": {
            "area": ["EDI-LAC(Área)", "DI-LAC(Área)", "INF-LAC(Área)"],
            "unidade": ["EDI-LAC(UN)", "DI-LAC(UN)", "INF-LAC(UN)"],
            "prancha": ["EDI-PRANCHA LAC", "DI-PRANCHA LAC", "INF-PRANCHA LAC"]
        },
        "LINHA DE RECALQUE": {
            "area": ["PS-LINHA DE RECALQUE(m)", "PS-LINHA DE RECALQUE(l/s)", "DI-LINHA DE RECALQUE(m)", "DI-LINHA DE RECALQUE(l/s)"],
            "unidade": ["PS-LINHA DE RECALQUE(uni)", "DI-LINHA DE RECALQUE(uni)"],
            "prancha": ["PS-PRANCHA LINHA DE RECALQUE", "DI-PRANCHA LINHA DE RECALQUE"]
        },
        "MAQ ELET / 3D": {
            "tipo": ["MAQ ELET/3D", "DI-MAQ ELET/3D"]
        },
        "MEIO AMBIENTE": {
            "tipo": ["VU-MEIO AMBIENTE", "PR-MEIO AMBIENTE", "PS-MEIO AMBIENTE", "DI-MEIO AMBIENTE"]
        },
        "MOBILIÁRIO": {
            "tipo": ["MOBILIÁRIO", "DI-MOBILIÁRIO"]
        },
        "OAE": {
            "tipo": ["VU-OAE", "PR-OAE", "PS-OAE", "DI-OAE"]
        },
        "ORÇAMENTO": {
            "area": ["ORÇAMENTO(m²)", "DI-ORÇAMENTO(m²)", "VU-ORÇAMENTO(m²)", "PR-ORÇAMENTO(m²)", "PS-ORÇAMENTO(m²)"],
            "prancha": ["ORÇAMENTO(km)", "DI-ORÇAMENTO(km)", "VU-ORÇAMENTO(KM)", "PR-ORÇAMENTO(KM)", "PS-ORÇAMENTO(KM)"]
        },
        "PAISAGISTICO": {
            "area": ["PAISAGISTICO(m²)", "DI-PAISAGISTICO(m²)", "VU-PAISAGISTICO(m²)", "PR-PAISAGISTICO(m²)", "PS-PAISAGISTICO(m²)"],
            "prancha": ["PRANCHA PAISAGISTICO", "DI-PRANCHA PAISAGISTICO", "VU-PRANCHA PAISAGISTICO", "PR-PRANCHA PAISAGISTICO", "PS-PRANCHA PAISAGISTICO"]
        },
        "PAVIMENTAÇÃO": {
            "tipo": ["VU-PAVIMENTAÇÃO", "PR-PAVIMENTAÇÃO", "PS-PAVIMENTAÇÃO", "DI-PAVIMENTAÇÃO"]
        },
        "PCA – PLANO DE CONTROLE AMBIENTAL": {
            "area": ["EDI-PCA(Área)", "DI-PCA(Área)", "INF-PCA(Área)"],
            "unidade": ["EDI-PCA(UN)", "DI-PCA(UN)", "INF-PCA(UN)"],
            "prancha": ["EDI-PRANCHA PCA", "DI-PRANCHA PCA", "INF-PRANCHA PCA"]
        },
        "PIA – PLANO DE INTERVENÇÃO AMBIENTAL": {
            "area": ["EDI-PIA(Área)", "DI-PIA(Área)", "INF-PIA(Área)"],
            "unidade": ["EDI-PIA(UN)", "DI-PIA(UN)", "INF-PIA(UN)"],
            "prancha": ["EDI-PRANCHA PIA", "DI-PRANCHA PIA", "INF-PRANCHA PIA"]
        },
        "PLANO DIRETOR": {
            "area": ["PDI-NUMERO HABITANTE", "DI-NUMERO HABITANTE"],
            "prancha": ["PDI-PRANCHA", "DI-PRANCHA"]
        },
        "PLANO SANEAMENTO BÁSICO - PMSB": {
            "area": ["PMSB-NUMERO HABITANTES", "DI PMSB-NUMERO HABITANTES"],
            "prancha": ["PMSB-PRANCHA", "DI PMSB-PRANCHA"]
        },
        "PMGIRS – PLANO MUNICIPAL DE GERENCIAMENTO INTEGRADO DE RESÍDUOS SÓLIDOS": {
            "area": ["EDI-PMGIRS(Área)", "DI-PMGIRS(Área)", "INF-PMGIRS(Área)"],
            "unidade": ["EDI-PMGIRS(UN)", "DI-PMGIRS(UN)", "INF-PMGIRS(UN)"],
            "prancha": ["EDI-PRANCHA PMGIRS", "DI-PRANCHA PMGIRS", "INF-PRANCHA PMGIRS"]
        },
        "PRADA – PROJETO DE RECUPERAÇÃO DE ÁGUAS DEGRADADAS E ALTERADAS": {
            "area": ["EDI-PRADA(Área)", "DI-PRADA(Área)", "INF-PRADA(Área)"],
            "unidade": ["EDI-PRADA(UN)", "DI-PRADA(UN)", "INF-PRADA(UN)"],
            "prancha": ["EDI-PRANCHA PRADA", "DI-PRANCHA PRADA", "INF-PRANCHA PRADA"]
        },
        "RAS – RELATÓRIO AMBIENTAL SIMPLIFICADO": {
            "area": ["EDI-RAS(Área)", "DI-RAS(Área)", "INF-RAS(Área)"],
            "unidade": ["EDI-RAS(UN)", "DI-RAS(UN)", "INF-RAS(UN)"],
            "prancha": ["EDI-PRANCHA RAS", "DI-PRANCHA RAS", "INF-PRANCHA RAS"]
        },
        "RCA – RELATÓRIO DE CONTROLE AMBIENTAL": {
            "area": ["EDI-RCA(Área)", "DI-RCA(Área)", "INF-RCA(Área)"],
            "unidade": ["EDI-RCA(UN)", "DI-RCA(UN)", "INF-RCA(UN)"],
            "prancha": ["EDI-PRANCHA RCA", "DI-PRANCHA RCA", "INF-PRANCHA RCA"]
        },
        "REDE COLETORA": {
            "area": ["PS-REDE COLETORA(m)", "PS-REDE COLETORA(l/s)", "DI-REDE COLETORA(m)", "DI-REDE COLETORA(l/s)"],
            "unidade": ["PS-REDE COLETORA(uni)", "DI-REDE COLETORA(uni)"],
            "prancha": ["PS-PRANCHA REDE COLETORA", "DI-PRANCHA REDE COLETORA"]
        },
        "REDE DE DISTRIBUIÇÃO": {
            "area": ["PS-REDE DE DISTRIBUIÇÃO(m)", "PS-REDE DE DISTRIBUIÇÃO(l/s)", "DI-REDE DE DISTRIBUIÇÃO(m)", "DI-REDE DE DISTRIBUIÇÃO(l/s)"],
            "unidade": ["PS-REDE DE DISTRIBUIÇÃO(uni)", "DI-REDE DE DISTRIBUIÇÃO(uni)"],
            "prancha": ["PS-PRANCHA REDE DE DISTRIBUIÇÃO", "DI-PRANCHA REDE DE DISTRIBUIÇÃO"]
        },
        "RELATÓRIO DE OUTORGA": {
            "area": ["EDI-RDO(Área)", "DI-RDO(Área)", "INF-RDO(Área)"],
            "unidade": ["EDI-RDO(UN)", "DI-RDO(UN)", "INF-RDO(UN)"],
            "prancha": ["EDI-PRANCHA RDO", "DI-PRANCHA RDO", "INF-PRANCHA RDO"]
        },
        "REURB": {
            "area": ["Un.Habitacionais", "DI-Un.Habitacionais"],
            "prancha": ["PRANCHA REURB", "DI-PRANCHA REURB"]
        },
        "REURB REGULARIZAÇÃO FUNDIARIA": {
            "area": ["REUR_HABITANTES", "DI-REUR_HABITANTES"],
            "prancha": ["REUR-PRANCHA", "DI-REUR PRANCHA"]
        },
        "SANEAMENTO": {
            "area": ["VU-SANEAMENTO(m)", "PR-SANEAMENTO(m)", "PS-SANEAMENTO(m)", "DI-SANEAMENTO(m)"],
            "kva": ["VU-SANEAMENTO(l/s)", "PR-SANEAMENTO(l/s)", "PS-SANEAMENTO(l/s)", "DI-SANEAMENTO(l/s)"],
            "prancha": ["VU-PRANCHA SANEAMENTO", "PR-PRANCHA SANEAMENTO", "PS-PRANCHA SANEAMENTO", "DI-PRANCHA SANEAMENTO"]
        },
        "SINALIZAÇÃO": {
            "area": ["VU-SINALIZAÇÃO(KM)", "PR-SINALIZAÇÃO(KM)", "PS-SINALIZAÇÃO(KM)", "DI-SINALIZAÇÃO(KM)"],
            "prancha": ["VU-PRANCHA SINALIZAÇÃO", "PR-PRANCHA SINALIZAÇÃO", "PS-PRANCHA SINALIZAÇÃO", "DI-PRANCHA SINALIZAÇÃO"]
        },
        "SOLO": {
            "tipo": ["SOLO", "DI-SOLO"]
        },
        "SONDAGEM": {
            "tipo": ["SONDAGEM", "DI-SONDAGEM", "Sondagem", "VU-SONDAGEM", "PR-SONDAGEM", "PS-SONDAGEM"]
        },
        "SPCI": {
            "area": ["SPCI(m²)", "DI-SPCI(m²)"],
            "prancha": ["PRANCHA SPCI", "DI-PRANCHA SPCI"]
        },
        "SPDA": {
            "area": ["SPDA(m²)", "DI-SPDA(m²)"],
            "prancha": ["PRANCHA SPDA", "DI-PRANCHA SPDA"]
        },
        "TERRAPLENAGEM": {
            "area": ["TERRAPLENAGEM(m²)", "DI-TERRAPLENAGEM(m²)", "TERRAPLENAGEM(km)", "DI-TERRAPLENAGEM(km)", "VU-TERRAPLENAGEM(KM)", "PR-TERRAPLENAGEM(KM)", "PS-TERRAPLENAGEM(KM)"],
            "unidade": ["TERRAPLENAGEM(uni)", "DI-TERRAPLENAGEM(uni)", "VU-TERRAPLENAGEM(uni)", "PR-TERRAPLENAGEM(uni)", "PS-TERRAPLENAGEM(uni)"],
            "prancha": ["PRANCHA TERRAPLENAGEM", "DI-PRANCHA TERRAPLENAGEM", "VU-PRANCHA TERRAPLENAGEM", "PR-PRANCHA TERRAPLENAGEM", "PS-PRANCHA TERRAPLENAGEM"]
        },
        "TOPOGRAFIA": {
            "area": ["TOPOGRAFIA(m²)", "DI-TOPOGRAFIA(m²)", "VU-TOPOGRAFIA(m²)", "PR-TOPOGRAFIA(m²)", "PS-TOPOGRAFIA(m²)"],
            "tipo": ["TIPO TOPOGRAFIA", "DI-TIPO TOPOGRAFIA", "VU-TIPO TOPOGRAFIA", "PR-TIPO TOPOGRAFIA", "PS-TIPO TOPOGRAFIA"],
            "cadastral": ["CADASTRAL-TOP", "DI-CADASTRAL", "VU-CADASTRAL-TOP", "PR-CADASTRAL-TOP", "PS-CADASTRAL-TOP"],
            "drone": ["DRONE-TOP", "DI-DRONE", "VU-DRONE-TOP", "PR-DRONE-TOP", "PS-DRONE-TOP"],
            "prancha": ["PRANCHA TOPOGRAFIA", "DI-PRANCHA TOPOGRAFIA", "VU-PRANCHA TOPOGRAFIA", "PR-PRANCHA TOPOGRAFIA", "PS-PRANCHA TOPOGRAFIA"]
        },
        "URBANISTICO": {
            "area": ["URBANISTICO(m²)", "DI-URBANISTICO(m²)", "VU-URBANISTICO(m²)", "PR-URBANISTICO(m²)", "PS-URBANISTICO(m²)"],
            "prancha": ["PRANCHA URBANISTICO", "DI-PRANCHA URBANISTICO", "VU-PRANCHA URBANISTICO", "PR-PRANCHA URBANISTICO", "PS-PRANCHA URBANISTICO"]
        },
        "VENTILAÇÃO/EXAUSTÃO": {
            "area": ["VENTILAÇÃO/EXAUSTÃO(m²)", "DI-VENTILAÇÃO/EXAUSTÃO(m²)"],
            "kva": ["VENTILAÇÃO/EXAUSTÃO(kbtu/h)", "DI-VENTILAÇÃO/EXAUSTÃO(kbtu/h)"],
            "prancha": ["PRANCHA VENTILAÇÃO/EXAUSTÃO", "DI-PRANCHA VENTILAÇÃO/EXAUSTÃO"]
        }
    }

    df = pd.DataFrame(registros)

    # Filtro por tipo de serviço
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        servicos_disponiveis = df["Servico"].dropna().unique().tolist()
        servico_selecionado = st.selectbox("Filtrar por Tipo de Serviço", ["Todos"] + servicos_disponiveis)

    # Define o dicionário de disciplinas conforme o serviço

    if servico_selecionado == "Projeto Edificação":
        disciplinas_info = disciplinas_edificacoes
    elif servico_selecionado == "Projeto Praças e Parques":
        disciplinas_info = disciplinas_edificacoes
    elif servico_selecionado == "Supervisão Gerenciamento Edificação":
        disciplinas_info = disciplinas_edificacoes
    elif servico_selecionado == "Projeto Vias Urbanas":
        disciplinas_info = disciplinas_vu
    elif servico_selecionado == "Supervisão Gerenciamento Vias Urbanas":
        disciplinas_info = disciplinas_vu
    elif servico_selecionado == "Projeto Rodovias":
        disciplinas_info = disciplinas_vu
    elif servico_selecionado == "Supervisão Gerenciamento Rodovias":
        disciplinas_info = disciplinas_vu
    elif servico_selecionado == "Projeto Saneamento":
        disciplinas_info = disciplinas_saneamento
    elif servico_selecionado == "Supervisão Gerenciamento Saneamento":
        disciplinas_info = disciplinas_saneamento
    elif servico_selecionado == "Plano Saneamento Básico - PMSB":
        disciplinas_info = disciplinas_pmsb
    elif servico_selecionado == "Estudos e Projetos Ambientais – Edificação":
        disciplinas_info = disciplinas_projetoambientais_edi
    elif servico_selecionado == "Estudos e Projetos Ambientais - Infraestrutura":
        disciplinas_info = disciplinas_projetoambientais_inf
    elif servico_selecionado == "Sondagem / Controle Tecnológico":
        disciplinas_info = disciplinas_ensaios
    elif servico_selecionado == "Plano Diretor":
        disciplinas_info = disciplinas_planodiretor
    elif servico_selecionado == "Diversos":
        disciplinas_info = disciplinas_diversos
    elif servico_selecionado == "REURB Regularização Fundiária":
        disciplinas_info = disciplinas_reur
    else:
        disciplinas_info = todas_disciplinas

    with col2:
        disciplina_selecionada = st.selectbox("Selecione uma Disciplina", ["Selecione"] + list(disciplinas_info.keys()))

    with col3:
        area_filtro = st.number_input("Valor Mínimo Desejado", min_value=0.0, value=0.0, step=1.0)
    with col4:
        filtro_objetodis = st.text_input("Objeto (parcial ou completo)", key="filtroobjetodis")

    if "Todos" in servico_selecionado:
        for nome_disciplina, dados in todas_disciplinas.items():
            # Unificação de colunas de área
            if "area" in dados and isinstance(dados["area"], list):
                colunas_area = dados["area"]
                col_area_principal = colunas_area[0]

                col_area_existentes = [col for col in colunas_area if col in df.columns]
                if col_area_existentes:
                    df[col_area_principal] = df[col_area_existentes].bfill(axis=1).iloc[:, 0]
                    for col in col_area_existentes:
                        if col != col_area_principal:
                            df.drop(columns=col, inplace=True)

            # Unificação de colunas de prancha
            if "prancha" in dados and isinstance(dados["prancha"], list):
                colunas_prancha = dados["prancha"]
                col_prancha_principal = colunas_prancha[0]

                col_prancha_existentes = [col for col in colunas_prancha if col in df.columns]
                if col_prancha_existentes:
                    df[col_prancha_principal] = df[col_prancha_existentes].bfill(axis=1).iloc[:, 0]
                    for col in col_prancha_existentes:
                        if col != col_prancha_principal:
                            df.drop(columns=col, inplace=True)

            # Unificação de colunas de tipo
            if "tipo" in dados and isinstance(dados["tipo"], list):
                colunas_tipo = dados["tipo"]
                col_tipo_principal = colunas_tipo[0]

                col_tipo_existentes = [col for col in colunas_tipo if col in df.columns]
                if col_tipo_existentes:
                    df[col_tipo_principal] = df[col_tipo_existentes].bfill(axis=1).iloc[:, 0]
                    for col in col_tipo_existentes:
                        if col != col_tipo_principal:
                            df.drop(columns=col, inplace=True)

            # Unificação de colunas de kva
            if "kva" in dados and isinstance(dados["kva"], list):
                colunas_kva = dados["kva"]
                col_kva_principal = colunas_kva[0]

                col_kva_existentes = [col for col in colunas_kva if col in df.columns]
                if col_kva_existentes:
                    df[col_kva_principal] = df[col_kva_existentes].bfill(axis=1).iloc[:, 0]
                    for col in col_kva_existentes:
                        if col != col_kva_principal:
                            df.drop(columns=col, inplace=True)

            # Unificação de colunas de cadastral
            if "cadastral" in dados and isinstance(dados["cadastral"], list):
                colunas_cadastral = dados["cadastral"]
                col_cadastral_principal = colunas_cadastral[0]

                col_cadastral_existentes = [col for col in colunas_cadastral if col in df.columns]
                if col_cadastral_existentes:
                    df[col_cadastral_principal] = df[col_cadastral_existentes].bfill(axis=1).iloc[:, 0]
                    for col in col_cadastral_existentes:
                        if col != col_cadastral_principal:
                            df.drop(columns=col, inplace=True)

            # Unificação de colunas de drone
            if "drone" in dados and isinstance(dados["drone"], list):
                colunas_drone = dados["drone"]
                col_drone_principal = colunas_drone[0]

                col_drone_existentes = [col for col in colunas_drone if col in df.columns]
                if col_drone_existentes:
                    df[col_drone_principal] = df[col_drone_existentes].bfill(axis=1).iloc[:, 0]
                    for col in col_drone_existentes:
                        if col != col_drone_principal:
                            df.drop(columns=col, inplace=True)

            # Unificação de colunas de unidade
            if "unidade" in dados and isinstance(dados["unidade"], list):
                colunas_unidade = dados["unidade"]
                col_unidade_principal = colunas_unidade[0]

                col_unidade_existentes = [col for col in colunas_unidade if col in df.columns]
                if col_unidade_existentes:
                    df[col_unidade_principal] = df[col_unidade_existentes].bfill(axis=1).iloc[:, 0]
                    for col in col_unidade_existentes:
                        if col != col_unidade_principal:
                            df.drop(columns=col, inplace=True)

    # Começa com todos os dados
    df_filtrado = df.copy()

    # Define se vai filtrar por serviço mais tarde (apenas se não for "Todos")
    filtro_por_servico = servico_selecionado != "Todos"

    # Aplica filtro de objeto (case-insensitive, parcial)
    if filtro_objetodis:
        df_filtrado = df_filtrado[df_filtrado["Objeto"].str.contains(filtro_objetodis, case=False, na=False)]

    # Se disciplina não selecionada, mostra apenas os básicos
    if disciplina_selecionada == "Selecione":
        # Aqui sim já pode aplicar filtro por serviço se necessário
        if filtro_por_servico:
            df_filtrado = df_filtrado[df_filtrado["Servico"] == servico_selecionado]

        colunas_basicas = ["Empresa", "Cliente", "Servico", "CAT", "Objeto", "BIM", "Tempo do projeto"]
        colunas_exibir = [col for col in colunas_basicas if col in df_filtrado.columns]
        st.markdown("#### Atestados (sem disciplina específica)")
        st.dataframe(df_filtrado[colunas_exibir], use_container_width=True, hide_index=True)

    else:
        # Recupera campos da disciplina
        col_area = disciplinas_info[disciplina_selecionada].get("area")
        col_tipo = disciplinas_info[disciplina_selecionada].get("tipo")
        col_kva = disciplinas_info[disciplina_selecionada].get("kva")
        col_cadastral = disciplinas_info[disciplina_selecionada].get("cadastral")
        col_drone = disciplinas_info[disciplina_selecionada].get("drone")
        col_prancha = disciplinas_info[disciplina_selecionada].get("prancha")
        col_unidade = disciplinas_info[disciplina_selecionada].get("unidade")

        col_area = [col_area] if isinstance(col_area, str) else col_area or []
        col_tipo = [col_tipo] if isinstance(col_tipo, str) else col_tipo or []
        col_kva = [col_kva] if isinstance(col_kva, str) else col_kva or []
        col_cadastral = [col_cadastral] if isinstance(col_cadastral, str) else col_cadastral or []
        col_drone = [col_drone] if isinstance(col_drone, str) else col_drone or []
        col_prancha = [col_prancha] if isinstance(col_prancha, str) else col_prancha or []
        col_unidade = [col_unidade] if isinstance(col_unidade, str) else col_unidade or []

        # Detecta todos prefixos se for "Todos"
        if servico_selecionado == "Todos":
            col_area_existentes = [col for col in df.columns for base in col_area if col == base]
            col_tipo_existentes = [col for col in df.columns for base in col_tipo if col == base]
        else:
            # mantém comportamento anterior com prefixo
            prefixo_servico = None
            if servico_selecionado == "Projeto Vias Urbanas":
                prefixo_servico = "VU-"
            elif servico_selecionado == "Projeto Rodovias":
                prefixo_servico = "PR-"

            col_area_existentes = [col for col in col_area if
                                   col in df.columns and (not prefixo_servico or col.startswith(prefixo_servico))]
            col_tipo_existentes = [col for col in col_tipo if
                                   col in df.columns and (not prefixo_servico or col.startswith(prefixo_servico))]

        # Explodir os tipos de disciplinas que são dicionários
        for col in col_tipo_existentes:
            if col in df_filtrado.columns:
                tipos_unicos = set()
                for entrada in df_filtrado[col].dropna():
                    if isinstance(entrada, dict):
                        tipos_unicos.update(entrada.keys())

                for tipo in tipos_unicos:
                    nova_col_area = f"{col} - {tipo} (área)"
                    nova_col_prancha = f"{col} - {tipo} (prancha)"
                    df_filtrado[nova_col_area] = df_filtrado[col].apply(
                        lambda d: d.get(tipo).get("área") if isinstance(d, dict) and isinstance(d.get(tipo), dict) else None
                    )
                    df_filtrado[nova_col_prancha] = df_filtrado[col].apply(
                        lambda d: d.get(tipo).get("prancha") if isinstance(d, dict) and isinstance(d.get(tipo), dict) else None
                    )
                    col_area_existentes.append(nova_col_area)

        if not col_area_existentes:
            st.warning("Nenhum atestado possui a disciplina ou campo selecionado.")
        else:
            # Explodir os tipos de disciplinas que são dicionários
            for col in col_tipo_existentes:
                if col in df_filtrado.columns:
                    tipos_unicos = set()
                    for entrada in df_filtrado[col].dropna():
                        if isinstance(entrada, dict):
                            tipos_unicos.update(entrada.keys())

                    for tipo in tipos_unicos:
                        for col in col_tipo_existentes:
                            if col in df_filtrado.columns:
                                tipos_unicos = set()
                                for entrada in df_filtrado[col].dropna():
                                    if isinstance(entrada, dict):
                                        tipos_unicos.update(entrada.keys())

                                for tipo in tipos_unicos:
                                    # Pega todas as chaves internas existentes
                                    subchaves = set()
                                    for entrada in df_filtrado[col].dropna():
                                        if isinstance(entrada, dict) and isinstance(entrada.get(tipo), dict):
                                            subchaves.update(entrada.get(tipo).keys())

                                    for subcampo in subchaves:
                                        nome_col = f"{col} - {tipo} ({subcampo})"
                                        df_filtrado[nome_col] = df_filtrado[col].apply(
                                            lambda d: d.get(tipo).get(subcampo) if isinstance(d, dict) and isinstance(
                                                d.get(tipo), dict) else None
                                        )
                                        col_area_existentes.append(nome_col)

            if not col_area_existentes:
                st.warning("Nenhum atestado possui a disciplina ou campo selecionado.")
            else:
                col_area_existentes = [col for col in col_area_existentes if col in df_filtrado.columns]

                for col in col_area_existentes:
                    df_filtrado[col] = pd.to_numeric(df_filtrado[col], errors="coerce")

                # Aplica filtro >=
                filtro_area = df_filtrado[col_area_existentes].ge(area_filtro).any(axis=1)

                # Se o filtro de serviço deve ser aplicado, filtra também por serviço
                if filtro_por_servico:
                    df_filtrado = df_filtrado[
                        filtro_area & (df_filtrado["Servico"] == servico_selecionado)
                        ]
                else:
                    df_filtrado = df_filtrado[filtro_area]

                colunas_tabela = set(["Empresa", "Cliente", "Servico", "CAT", "Objeto", "BIM", "Tempo do projeto"])

                colunas_tabela.update([
                    col for col in col_area_existentes if
                    col in df_filtrado.columns and df_filtrado[col].notnull().any()
                ])
                colunas_tabela.update([
                    col for col in col_tipo if col in df_filtrado.columns and df_filtrado[col].notnull().any()
                ])
                colunas_tabela.update([
                    col for col in col_kva if col in df_filtrado.columns and df_filtrado[col].notnull().any()
                ])
                colunas_tabela.update([
                    col for col in col_cadastral if col in df_filtrado.columns and df_filtrado[col].notnull().any()
                ])
                colunas_tabela.update([
                    col for col in col_drone if col in df_filtrado.columns and df_filtrado[col].notnull().any()
                ])
                colunas_tabela.update([
                    col for col in col_prancha if
                    col in df_filtrado.columns and df_filtrado[col].notnull().any()
                ])
                colunas_tabela.update([
                    col for col in col_unidade if
                    col in df_filtrado.columns and df_filtrado[col].notnull().any()
                ])

                # Define colunas fixas em ordem
                colunas_fixas = ["Empresa", "Cliente", "Servico", "CAT", "Objeto", "BIM", "Tempo do projeto"]

                # Adiciona colunas específicas conforme o tipo de serviço
                if "Projeto Edificação" in servico_selecionado or "Supervisão Gerenciamento Edificação" in servico_selecionado or "Projeto Praças e Parques" in servico_selecionado:
                    colunas_fixas = ["Empresa", "Cliente", "Servico", "CAT", "Objeto", "BIM", "Patrimonio Tombado","Tempo do projeto"]

                elif "Projeto Saneamento" in servico_selecionado or "Supervisão Gerenciamento Saneamento" in servico_selecionado:
                    colunas_fixas = ["Empresa", "Cliente", "Servico", "CAT", "Objeto", "BIM", "População", "Tempo do projeto"]

                # Garante que colunas fixas estejam presentes no DataFrame
                colunas_fixas = [col for col in colunas_fixas if col in df_filtrado.columns]

                # Calcula colunas dinâmicas ordenadas por nome (alfabeticamente)
                colunas_dinamicas = sorted(list(colunas_tabela - set(colunas_fixas)))

                # Junta tudo em ordem final
                colunas_tabela = colunas_fixas + colunas_dinamicas

                st.markdown(f"#### Atestados com disciplina **{disciplina_selecionada}**")

                if df_filtrado.empty:
                    st.warning("Nenhum atestado encontrado com os filtros aplicados.")
                else:
                    # Criar coluna de visualização de PDFs
                    def gerar_link_pdf(row):
                        pdfs_profissionais = row.get("PDFS_PROFISSIONAIS", {})
                        if isinstance(pdfs_profissionais, dict) and pdfs_profissionais:
                            pdf_links = [
                                f'<a href="{url}" target="_blank">{nome}</a>'
                                for nome, url in pdfs_profissionais.items() if url
                            ]
                            return "<br>".join(pdf_links)
                        else:
                            pdf_url = row.get("PDF_URL")
                            return f'<a href="{pdf_url}" target="_blank">Visualizar PDF</a>' if pdf_url else ""


                    # Aplica a função para gerar os links
                    df_filtrado["Visualizar PDF"] = df_filtrado.apply(gerar_link_pdf, axis=1)

                    if "Objeto" in colunas_tabela:
                        index_objeto = colunas_tabela.index("Objeto")
                        colunas_tabela.insert(index_objeto + 1, "Visualizar PDF")
                    else:
                        colunas_tabela.append("Visualizar PDF")

                    if df_filtrado.empty:
                        st.warning("Nenhum atestado encontrado com os filtros aplicados.")
                    else:
                        # Mapeia prefixos conhecidos para cabeçalhos mais limpos
                        colunas_renomeadas = {
                            col: col.replace("ESTRUTURAL - ", "").replace("VU-ESTRUTURAL -", "") .replace("PR-ESTRUTURAL - ", "") .replace("PS-ESTRUTURAL -", "")
                            .replace("CONTENÇÃO - ", "").replace("VU-CONTENÇÃO -", "") .replace("PR-CONTENÇÃO -", "") .replace("PS-CONTENÇÃO -", "")
                            .replace("FUNDAÇÃO - ", "") .replace("VU-FUNDAÇÃO -", "") .replace("PR-FUNDAÇÃO -", "") .replace("PS-FUNDAÇÃO", "")
                            .replace("Sondagem - ", "") .replace("VU-SONDAGEM -", "") .replace("PR-SONDAGEM -", "").replace("PS-SONDAGEM -", "")
                            .replace("MAQ ELET/3D - ", "") .replace("PS-MEIO AMBIENTE -", "")
                            .replace("MOBILIÁRIO - ", "")
                            .replace("EDI-", "") .replace("INF-", "")
                            .replace("DI-", "") .replace("VU-", "") .replace("PR-", "") .replace("PS-", "")
                            .replace("VU-OAE -", "") .replace("PR-OAE - ", "") .replace("PS-OAE -", "")
                            .replace("ASFALTO -", "") .replace("CONCRETO -", "") .replace("SOLO - ", "") .replace("SONDAGEM - ", "") .replace("AÇO - ", "")
                            .replace("VU-PAVIMENTAÇÃO - ", "") .replace("PR-PAVIMENTAÇÃO -", "") .replace("PS-PAVIMENTAÇÃO -", "")
                            for col in colunas_tabela
                            if col.startswith("ESTRUTURAL - ") or col.startswith("VU-ESTRUTURAL -") or col.startswith("PR-ESTRUTURAL - ") or col.startswith("PS-ESTRUTURAL -")
                               or col.startswith("CONTENÇÃO - ") or col.startswith("VU-CONTENÇÃO -") or col.startswith("PR-CONTENÇÃO -") or col.startswith("PS-CONTENÇÃO -")
                               or col.startswith("Sondagem - ") or col.startswith("VU-SONDAGEM -") or col.startswith("PR-SONDAGEM -") or col.startswith("PS-SONDAGEM -")
                               or col.startswith("FUNDAÇÃO - ") or col.startswith("VU-FUNDAÇÃO -") or col.startswith("PR-FUNDAÇÃO -") or col.startswith("PS-FUNDAÇÃO")
                               or col.startswith("MAQ ELET/3D - ") or col.startswith("PS-MEIO AMBIENTE -")
                               or col.startswith("VU-OAE -") or col.startswith("PR-OAE - ") or col.startswith("PS-OAE -")
                               or col.startswith("MOBILIÁRIO - ")
                               or col.startswith("EDI-") or col.startswith("INF-")
                               or col.startswith("DI-") or col.startswith("VU-") or col.startswith("PR-") or col.startswith("PS-")
                               or col.startswith("VU-PAVIMENTAÇÃO - ") or col.startswith("PR-PAVIMENTAÇÃO -") or col.startswith("PS-PAVIMENTAÇÃO -")
                               or col.startswith("ASFALTO -") or col.startswith("CONCRETO -") or col.startswith("SOLO - ") or col.startswith("SONDAGEM - ") or col.startswith("AÇO - ")
                        }
                        # Aplica renomeação apenas para exibição
                        df_visual = df_filtrado[colunas_tabela].rename(columns=colunas_renomeadas)

                        # Exibe a tabela com os nomes limpos
                        st.write(
                            df_visual.to_html(escape=False, index=False),
                            unsafe_allow_html=True
                        )
