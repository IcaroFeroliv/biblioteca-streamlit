import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore, storage

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
        "Gracielle": "Engenheira Ambiental",
        "Isabela": "Arquiteta",
         "Juliana Goncalves": "Engenheira Civil e Engenheira de Segurança do Trabalho",
        "Julio Cesar": "Engenheiro Civil",
        "Lucas Bastos": "Engenheiro Civil",
        "Luiz Felipe": "Engenheiro Civil",
         "Mariane de Paula": "Engenheira Civil",
        "Matheus Comanduci": "Engenheiro Civil",
        "Mauricio Otavio": "Engenheiro Civil",
        "Márcio": "Arquiteto",
        "Moises Coelho": "Engenheiro Agrimensor",
        "Pablo Otoni": "Engenheiro Agrimensor",
         "Patricia": "Arquiteta",
        "Sarah Malta": "Engenheira Agrimensora",
        "Sayuri": "Arquiteta",
        "Sérgio Henrique": "Engenheiro Civil",
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
        "Gracielle": "-",
        "Isabela": "-",
         "Juliana Goncalves": "Engenharia Geotécnica",
        "Julio Cesar": "-",
        "Lucas Bastos": "-",
        "Luiz Felipe": "MBA em Plataforma BIM - Modelagem 3D, Planejamento 4D e Orçamento 5D, 6D e 7D",
         "Mariane de Paula": "-",
        "Matheus Comanduci": "-",
        "Mauricio Otavio": "Engenharia Sanitaria e Ambiental",
        "Márcio": "-",
        "Moises Coelho": "-",
        "Pablo Otoni": "-",
         "Patricia": "-",
        "Sarah Malta": "-",
        "Sayuri": "-",
        "Sérgio Henrique": "-",
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

    df = pd.DataFrame(registros)

    # Dicionário de disciplinas com os campos de tipo e área relacionados
    disciplinas_edificacoes = {
    "ACÚSTICA": {
        "area": "ACÚSTICA(m²)",
        "prancha": "PRANCHA ACÚSTICA"
    },
    "ALARME/CFTV": {
        "area": "ALARME/CFTV(m²)",
        "prancha": "PRANCHA ALARME/CFTV"
    },
    "AR CONDICIONADO": {
        "area": "AR CONDICIONADO(m²)",
        "prancha": "PRANCHA AR CONDICIONADO"
    },
    "ARQUITETÔNICO ANTEPROJETO": {
        "area": "ARQUITETÔNICO ANTEPROJETO(m²)",
        "prancha": "PRANCHA ARQUITETÔNICO ANTEPROJETO"
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
        "area": "DRENAGEM(m²)",
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
    "HIDROSANITÁRIO": {
        "area": "HIDROSANITÁRIO(m²)",
        "prancha": "PRANCHA HIDROSANITÁRIO"
    },
    "ILUMINAÇÃO PUBLICA": {
        "area": "ILUMINAÇÃO PUBLICA(m²)",
        "kva": "ILUMINAÇÃO PUBLICA(ponto)",
        "prancha": "PRANCHA ILUMINAÇÃO PUBLICA"
    },
    "IRRIGAÇÃO": {
        "area": "IRRIGAÇÃO(m²)",
        "prancha": "PRANCHA IRRIGAÇÃO"
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
        "area": "TERRAPLENAGEM (PLANTA/SEÇÕES)(m²)",
        "prancha": "PRANCHA TERRAPLENAGEM (PLANTA/SEÇÕES)"
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
    "ANTEPROJETO DE INFRA": {
        "area": ["VU-ANTEPROJETO DE INFRA(KM)", "PR-ANTEPROJETO DE INFRA(KM)"],
        "prancha": ["VU-PRANCHA ANTEPROJETO DE INFRA", "PR-PRANCHA ANTEPROJETO DE INFRA"]
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
        "tipo": ["VU-FUNDAÇÃO", "PR-FUNDAÇÃO", "PS-FUNDAÇÃO"]
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
        "area": ["VU-HIDROLOGIA(l/s)", "PR-HIDROLOGIA(l/s)"],
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
        "prancha": ["VU-PRANCHA TERRAPLENAGEM", "PR-PRANCHA TERRAPLENAGEM"]
    },
    "TOPOGRAFIA": {
        "tipo": ["VU-TOPOGRAFIA", "PR-TOPOGRAFIA(m²)", "PR-TOPOGRAFIA(KM)"],
        "prancha": ["VU-PRANCHA TOPOGRAFIA", "PR-PRANCHA TOPOGRAFIA"]
    },
    "URBANISTICO": {
        "area": ["VU-URBANISTICO(m²)", "PR-URBANISTICO(m²)"],
        "prancha": ["VU-PRANCHA URBANISTICO", "PR-PRANCHA URBANISTICO"]
    }
}

    disciplinas_pmsb = {
        "Plano Saneamento Basico - PMBS": {"area": "PMSB-NUMERO HABITANTES", "prancha": "PMSB-PRANCHA"}
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
            "area": "PS-HIDROLOGIA(l/s)",
            "prancha": "PS-PRANCHA HIDROLOGIA"
        },
        "ILUMINAÇÃO PUBLICA": {
            "area": "PS-ILUMINAÇÃO PUBLICA(Pontos)",
            "prancha": "PS-PRANCHA ILUMINAÇÃO PUBLICA"
        },
        "INTERCEPTOR": {
            "area": ["PS-INTERCEPTOR(m)", "PS-INTERCEPTOR(l/s)"],
            "unidade": "PS-INTERCEPTOR(uni)",
            "prancha": "PS-PRANCHA INTERCEPTOR"
        },
        "LINHA DE RECALQUE": {
            "area": ["PS-LINHA DE RECALQUE(m)", "PS-LINHA DE RECALQUE(l/s)", "PS-LINHA DE RECALQUE(uni)"],
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
        "SINALIZAÇÃO": {
            "area": "PS-SINALIZAÇÃO(KM)",
            "prancha": "PS-PRANCHA SINALIZAÇÃO"
        },
        "SONDAGEM": {
            "tipo": "PS-SONDAGEM"
        },
        "TERRAPLENAGEM": {
            "area": "PS-TERRAPLENAGEM(KM)",
            "prancha": "PS-PRANCHA TERRAPLENAGEM"
        },
        "TOPOGRAFIA": {
            "tipo": "PS-TIPOTOPS",
            "cadastral": "PS-CADASTRAL",
            "drone": "PS-DRONE",
            "area": "PS-AREATOP(m²)"
        },
        "URBANISTICO": {
            "area": "PS-URBANISTICO(m²)",
            "prancha": "PS-PRANCHA URBANISTICO"
        },
    }

    disciplinas_projetoambientais_edi = {
        "Dispensa de licenciamento": {
            "area": "EDI-DDL(Área)",
            "unidade": "EDI-DDL(UN)",
            "prancha": "EDI-PRANCHA DDL"
        },
        "Dispensa de outorga": {
            "area": "EDI-DDO(Área)",
            "unidade": "EDI-DDO(UN)",
            "prancha": "EDI-PRANCHA DDO"
        },
        "EIA/RIMA": {
            "area": "EDI-EIA/RIMA(Área)",
            "unidade": "EDI-EIA/RIMA(UN)",
            "prancha": "EDI-PRANCHA EIA/RIMA"
        },
        "Inventário florestal/Plano Manejo": {
            "area": "EDI-IFPM(Área)",
            "unidade": "EDI-IFPM(UN)",
            "prancha": "EDI-PRANCHA If/PM"
        },
        "Licença Ambiental Concomitante": {
            "area": "EDI-LAC(Área)",
            "unidade": "EDI-LAC(UN)",
            "prancha": "EDI-PRANCHA LAC"
        },
        "PCA – Plano de Controle Ambiental": {
            "area": "EDI-PCA(Área)",
            "unidade": "EDI-PCA(UN)",
            "prancha": "EDI-PRANCHA PCA"
        },
        "PIA – Plano de Intervenção Ambiental": {
            "area": "EDI-PIA(Área)",
            "unidade": "EDI-PIA(UN)",
            "prancha": "EDI-PRANCHA PIA"
        },
        "PMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos": {
            "area": "EDI-PMGIRS(Área)",
            "unidade": "EDI-PMGIRS(UN)",
            "prancha": "EDI-PRANCHA PMGIRS"
        },
        "PRADA – Projeto de Recuperação de Águas Degradadas e Alteradas": {
            "area": "EDI-PRADA(Área)",
            "unidade": "EDI-PRADA(UN)",
            "prancha": "EDI-PRANCHA PRADA"
        },
        "RCA – Relatório de Controle Ambiental": {
            "area": "EDI-RCA(Área)",
            "unidade": "EDI-RCA(UN)",
            "prancha": "EDI-PRANCHA RCA"
        },
        "RAS – Relatório Ambiental Simplificado": {
            "area": "EDI-RAS(Área)",
            "unidade": "EDI-RAS(UN)",
            "prancha": "EDI-PRANCHA RAS"
        },
        "Relatório de Outorga": {
            "area": "EDI-RdeO(Área)",
            "unidade": "EDI-RdeO(UN)",
            "prancha": "EDI-PRANCHA RdeO"
        }
    }

    disciplinas_projetoambientais_inf = {
        "Dispensa de licenciamento": {
            "area": "INF-DDL(Área)",
            "unidade": "INF-DDL(UN)",
            "prancha": "INF-PRANCHA DDL"
        },
        "Dispensa de outorga": {
            "area": "INF-DDO(Área)",
            "unidade": "INF-DDO(UN)",
            "prancha": "INF-PRANCHA DDO"
        },
        "EIA/RIMA": {
            "area": "INF-EIA(Área)",
            "unidade": "INF-EIA(UN)",
            "prancha": "INF-PRANCHA EIA"
        },
        "Inventário florestal/Plano Manejo": {
            "area": "INF-IFPM(Área)",
            "unidade": "INF-IFPM(UN)",
            "prancha": "INF-PRANCHA IFPM"
        },
        "Licença Ambiental Concomitante": {
            "area": "INF-LAC(Área)",
            "unidade": "INF-LAC(UN)",
            "prancha": "INF-PRANCHA LAC"
        },
        "PCA – Plano de Controle Ambiental": {
            "area": "INF-PCA(Área)",
            "unidade": "INF-PCA(UN)",
            "prancha": "INF-PRANCHA PCA"
        },
        "PIA – Plano de Intervenção Ambiental": {
            "area": "INF-PIA(Área)",
            "unidade": "INF-PIA(UN)",
            "prancha": "INF-PRANCHA PIA"
        },
        "PMGIRS – Plano Municipal de Gerenciamento Integrado de Resíduos Sólidos": {
            "area": "INF-PMGIRS(Área)",
            "unidade": "INF-PMGIRS(UN)",
            "prancha": "INF-PRANCHA PMGIRS"
        },
        "PRADA – Projeto de Recuperação de Águas Degradadas e Alteradas": {
            "area": "INF-PRADA(Área)",
            "unidade": "INF-PRADA(UN)",
            "prancha": "INF-PRANCHA PRADA"
        },
        "RCA – Relatório de Controle Ambiental": {
            "area": "INF-RCA(Área)",
            "unidade": "INF-RCA(UN)",
            "prancha": "INF-PRANCHA RCA"
        },
        "RAS – Relatório Ambiental Simplificado": {
            "area": "INF-RAS(Área)",
            "unidade": "INF-RAS(UN)",
            "prancha": "INF-PRANCHA RAS"
        },
        "Relatório de Outorga": {
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
        "Plano Diretor": {
            "area": "PDI-NUMERO HABITANTE",
            "prancha": "PDI-PRANCHA"}
    }

    disciplinas_diversos = {
        "Diversos": {
            "prancha": "DIVERSOS-PRANCHA"
        }
    }

    disciplinas_topografia = {
        "Topografia": {
            "tipo": "Disciplina",
            "cadastral": "TOPOGRAFIA-CADASTRAL",
            "drone": "TOPOGRAFIA-DRONE",
            "area": "TOPOGRAFIA-AREA(m²)",
            "prancha": "TOPOGRAFIA-PRANCHA"}
    }

    disciplinas_reur = {
        "REURB Regularização Fundiária": {
            "area": "REUR_HABITANTES",
            "prancha": "REUR-PRANCHA"
        }
    }

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
    elif servico_selecionado == "Topografia":
        disciplinas_info = disciplinas_topografia
    elif servico_selecionado == "REURB Regularização Fundiária":
        disciplinas_info = disciplinas_reur
    else:
        disciplinas_info = {**disciplinas_edificacoes, **disciplinas_vu, **disciplinas_pmsb, **disciplinas_saneamento, **disciplinas_projetoambientais_edi, **disciplinas_projetoambientais_inf, **disciplinas_planodiretor, **disciplinas_ensaios, **disciplinas_diversos, **disciplinas_topografia, **disciplinas_reur}

    with col2:
        disciplina_selecionada = st.selectbox("Selecione uma Disciplina", ["Selecione"] + list(disciplinas_info.keys()))

    with col3:
        area_filtro = st.number_input("Valor Mínimo Desejado", min_value=0.0, value=0.0, step=1.0)
    with col4:
        filtro_objetodis = st.text_input("Objeto (parcial ou completo)", key="filtroobjetodis")


    # Começa com todos os dados
    df_filtrado = df.copy()

    # Aplica filtro por serviço (imediatamente)
    if servico_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Servico"] == servico_selecionado]

    # Aplica filtro de objeto (case-insensitive, parcial)
    if filtro_objetodis:
        df_filtrado = df_filtrado[df_filtrado["Objeto"].str.contains(filtro_objetodis, case=False, na=False)]

    # Se disciplina não selecionada, mostra apenas os básicos
    if disciplina_selecionada == "Selecione":
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

        # Prefixo opcional (para vias urbanas e rodovias)
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
                # Mantém apenas linhas com pelo menos uma coluna com valor >= area_filtro
                filtro_area = df_filtrado[col_area_existentes].ge(area_filtro).any(axis=1)
                df_filtrado = df_filtrado[filtro_area]

                colunas_tabela = set(["Empresa", "Cliente", "Servico", "CAT", "Objeto", "BIM", "Tempo do projeto"])


                colunas_tabela.update([
                    col for col in col_area_existentes if
                    col in df_filtrado.columns and df_filtrado[col].notnull().any()
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
                if "Projeto Edificação" in servico_selecionado or "Supervisão Gerenciamento Edificação" in servico_selecionado:
                    if "Patrimônio Tombado" in df_filtrado.columns:
                        colunas_fixas.append("Patrimonio Tombado")

                elif "Projeto Saneamento" in servico_selecionado or "Supervisão Gerenciamento Saneamento" in servico_selecionado:
                    if "População" in df_filtrado.columns:
                        colunas_fixas.append("População")

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
