import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore, storage


st.set_page_config(page_title="Grupo Projeta", layout="wide")

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
        area_minima, area_maxima = st.slider(
            "Filtrar por Área (m²)", 0.0, 10000.0, (0.0, 10000.0)
        )

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

with abas[1]:

    col1, col2 = st.columns([2,1])
    with col1:
        st.title("Tempo De Experiência")
    with col2:
        st.image("logoprojeta.png", width=350)

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
        "Ana Carolina": "Engenheira Sanitarista e Ambiental",
        "André": "Engenheiro Eletricista",
        "Ayana Lemos": "Engenheira Ambiental e Engenheira de Segurança do Trabalho",
        "Bárbara Izabela": "Engenheira Civil",
        "Bruno Andrelli": "Engenheiro Mecânico",
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
        "Fabiane Ferreira": "Engenheira ?",
        "Grazielle": "Engenheira Ambiental",
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
        "Ana Carolina": "-",
        "André": "-",
        "Ayana Lemos": "-",
        "Bárbara Izabela": "-",
        "Bruno Andrelli": "-",
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
        "Grazielle": "-",
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
                "Formação": formacoes.get(profissional, "Desconhecida"),
                "Especialização": especializacao.get(profissional, "Desconhecida"),
                "Experiência (Dias)": dias_experiencia,
                "Experiência (Anos)": anos_experiencia
            }

        return experiencia_por_profissional


    # Calcular experiência se houver dados
    if not df.empty:
        experiencia = calcular_experiencia(df)
        df_experiencia = pd.DataFrame.from_dict(experiencia, orient="index").reset_index()
        df_experiencia.columns = ["Profissional", "Formação", "especialização", "Experiência (Dias)", "Experiência (Anos)"]

        st.dataframe(df_experiencia, use_container_width=True, hide_index=True)
    else:
        st.write("Nenhum dado encontrado.")

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
        "ARQUITETÔNICO ANTEPROJETO": {"area": "ARQUITETÔNICO ANTEPROJETO(m²)"},
        "ARQUITETÔNICO CONSTRUÇÃO": {"area": "ARQUITETÔNICO CONSTRUÇÃO(m²)"},
        "ARQUITETÔNICO REFORMA": {"area": "ARQUITETÔNICO REFORMA(m²)"},
        "ARQUITETÔNICO RESTAURO": {"area": "ARQUITETÔNICO RESTAURO(m²)"},
        "COMUNICAÇÃO VISUAL": {"area": "COMUNICAÇÃO VISUAL(m²)"},
        "MOBILIÁRIO": {"tipo": "TIPO MOBILIÁRIO", "area": "MOBILIÁRIO(m²)"},
        "URBANISTICO": {"area": "URBANISTICO(m²)"},
        "PAISAGISTICO": {"area": "PAISAGISTICO(m²)"},
        "AS BUILT": {"tipo": "TIPO AS BUILT", "area": "AS BUILT(m²)"},
        "MAQ ELET / 3D": {"tipo": "TIPO MAQ ELET/3D", "area": "MAQ ELET / 3D(m²)"},
        "ESTRUTURAL": {"tipo": "TIPO ESTRUTURAL", "area": "ESTRUTURAL(m²)"},
        "FUNDAÇÃO": {"tipo": "TIPO FUNDAÇÃO", "area": "FUNDAÇÃO(m²)"},
        "CONTENÇÃO": {"tipo": "TIPO CONTENÇÃO", "area": ["CONTENÇÃO(m)", "CONTENÇÃO(m²)",  "CONTENÇÃO(m³)"]},
        "HIDROSANITÁRIO": {"area": "HIDROSANITÁRIO(m²)"},
        "IRRIGAÇÃO": {"area": "IRRIGAÇÃO(m²)"},
        "SPCI": {"area": "SPCI(m²)"},
        "TERRAPLENAGEM": {"area": "TERRAPLENAGEM (PLANTA/SEÇÕES)(m²)"},
        "TOPOGRAFIA": {"tipo": "TIPO TOPOGRAFIA", "cadastral": "CADASTRAL-TOP", "drone": "DRONE-TOP", "area": "TOPOGRAFIA(m²)"},
        "ORÇAMENTO": {"area": "ORÇAMENTO(m²)"},
        "ELÉTRICO": {"area": "ELÉTRICO(m²)", "kva": "KVA"},
        "CAB. ESTRUTURADO": {"area": "CAB. ESTRUTURADO(m²)"},
        "SPDA": {"area": "SPDA(m²)"},
        "ALARME/CFTV": {"area": "ALARME/CFTV(m²)"},
        "EXTENSÃO DE REDE": {"area": "EXTENSÃO DE REDE(km)"},
        "ILUMINAÇÃO PUBLICA": {"area": "ILUMINAÇÃO PUBLICA(pontos)"},
        "AR CONDICIONADO": {"area": "AR CONDICIONADO(m²)"},
        "VENTILAÇÃO/EXAUSTÃO": {"area": "VENTILAÇÃO/EXAUSTÃO(m²)"},
        "GLP": {"area": "GLP(m²)"},
        "GASES MEDICINAIS": {"area": "GASES MEDICINAIS(m²)"},
        "COMPAT. PROJETOS": {"area": "COMPAT. PROJETOS(m²)"},
        "ACÚSTICA": {"area": "ACÚSTICA(m²)"},
        "UNI.HABITACIONAIS": {"area": "Un.Habitacionais"}
    }

    disciplinas_vu = {
        "URBANISTICO": {"area": ["PR-URBANISTICO(m²)", "VU-URBANISTICO(m²)"] },
        "PAISAGISTICO": {"area": ["PR-PAISAGISTICO(m²)", "VU-PAISAGISCO(m²)"]},
        "ANTEPROJETO DE INFRA": {"area": ["VU-ANTEPROJETO DE INFRA(km)", "PR-ANTEPROJETO DE INFRA(km)"]},
        "GEOMÉTRICO": {"area": ["VU-GEOMÉTRICO(km)", "PR-GEOMÉTRICO(km)"]},
        "TERRAPLENAGEM": {"area": ["VU-TERRAPLENAGEM(km)", "PR-TERRAPLENAGEM(km)"]},
        "DRENAGEM": {"area": ["VU-DRENAGEM(km)", "PR-DRENAGEM(km)"]},
        "ESTRUTURAL": {"tipo": ["VU-TIPO ESTRUTURAL", "PR-TIPO ESTRUTURAL"], "area": ["VU-ESTRUTURAL(m²)", "PR-ESTRUTURAL(m²)"]},
        "PAVIMENTAÇÃO": {"tipo": ["PR-TIPO PAVIMENTAÇÃO", "VU-TIPO PAVIMENTAÇÃO"], "Base sub base": ["VU-SUB BASE", "PR-SUB BASE"], "area": ["PR-PAVIMENTAÇÃO(km)", "PR-PAVIMENTAÇÃO(m²)", "VU-PAVIMENTAÇÃO(km)", "VU-PAVIMENTAÇÃO(m²)" ] },
        "SINALIZAÇÃO": {"area": ["VU-SINALIZAÇÃO(km)", "PR-SINALIZAÇÃO(km)"]},
        "TOPOGRAFIA": {"tipo": ["PR-TIPO TOPOGRAFIA", "VU-TIPO TOPOGRAFIA"], "cadastral": ["VU-CADASTRAL TOP", "PR-CADASTRAL TOP"], "area": ["PR-TOPOGRAFIA(m²)", "PR-TOPOGRAFIA(km)","VU-TOPOGRAFIA(km)", "VU-TOPOGRAFIA(m²)"]},
        "ORÇAMENTO": {"area": ["PR-ORÇAMENTO(km)", "PR-ORÇAMENTO(m²)", "VU-ORCAMENTO(km)", "VU-ORCAMENTO(m²)"] },
        "CONTENÇÃO": {"tipo": ["PR-TIPO CONTENÇÃO", "VU-TIPO CONTENCAO"], "area": ["PR-CONTENÇÃO(m)", "PR-CONTENÇÃO(m²)", "PR-CONTENÇÃO(m³)", "VU-CONTENCAO(m)", "VU-CONTENCAO(m²)", "VU-CONTENCAO(m³)"]},
        "OAE": {"tipo": ["PR-TIPO OAE", "VU-TIPO OAE"], "area": ["PR-OAE(m²)", "PR-OAE(vao)", "VU-OAE(m²)", "VU- VAO OAE"]},
        "FUNDAÇÃO": {"tipo": ["PR-TIPO FUNDAÇÃO", "VU-TIPO FUNDACAO"], "area": ["PR-FUNDAÇÃO(m²)", "VU-FUNDACAO(m²)"]},
        "MEIO AMBIENTE": {"tipo": ["PR-TIPO MEIO AMBIENTE", "VU-TIPO MEIO AMBIENTE"], "area": ["PR-UNIDADE MEIO AMBIENTE", "VU-UNIDADE MEIO AMBIENTE"]},
        "COMPAT. PROJETOS": {"area": ["VU-COMPAT. PROJETOS(m²)", "PR-COMPAT. PROJETOS(m²)"]},
        "ELÉTRICO": {"area": ["PR-ELETRICO(m²)", "VU-ELETRICO(m²)"], "kva": ["PR-KVA", "VU-KVA"]},
        "EXTENSÃO DE REDE": {"area": ["PR-EXTENSÃO DE REDE", "VU-EXTENSAO DE REDE(km)"]},
        "ILUMINAÇÃO PUBLICA": {"area": ["PR-ILUMINAÇÃO PUBLICA","VU-ILUMINACAO PUBLICA(pontos)"]}

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

    else:
        disciplinas_info = {**disciplinas_edificacoes, **disciplinas_vu}

    with col2:
        disciplina_selecionada = st.selectbox("Selecione uma disciplina", ["Selecione"] + list(disciplinas_info.keys()))

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
        colunas_basicas = ["Empresa", "Cliente", "Servico", "CAT", "Objeto", "Tempo do projeto"]
        colunas_exibir = [col for col in colunas_basicas if col in df_filtrado.columns]
        st.markdown("#### Atestados (sem disciplina específica)")
        st.dataframe(df_filtrado[colunas_exibir], use_container_width=True, hide_index=True)

    else:
        # Recupera campos da disciplina
        col_area = disciplinas_info[disciplina_selecionada].get("area")
        col_tipo = disciplinas_info[disciplina_selecionada].get("tipo")
        col_base = disciplinas_info[disciplina_selecionada].get("Base sub base")
        col_kva = disciplinas_info[disciplina_selecionada].get("kva")
        col_cadastral = disciplinas_info[disciplina_selecionada].get("cadastral")
        col_drone = disciplinas_info[disciplina_selecionada].get("drone")

        # Garante que todos sejam listas
        col_area = [col_area] if isinstance(col_area, str) else col_area or []
        col_tipo = [col_tipo] if isinstance(col_tipo, str) else col_tipo or []
        col_base = [col_base] if isinstance(col_base, str) else col_base or []
        col_kva = [col_kva] if isinstance(col_kva, str) else col_kva or []
        col_cadastral = [col_cadastral] if isinstance(col_cadastral, str) else col_cadastral or []
        col_drone = [col_drone] if isinstance(col_drone, str) else col_drone or []

        # Prefixo para colunas válidas
        prefixo_servico = None
        if servico_selecionado == "Projeto Vias Urbanas":
            prefixo_servico = "VU-"
        elif servico_selecionado == "Projeto Rodovias":
            prefixo_servico = "PR-"

        col_area_existentes = [
            col for col in col_area if
            col in df.columns and (prefixo_servico is None or col.startswith(prefixo_servico))
        ]
        col_tipo_existentes = [
            col for col in col_tipo if
            col in df.columns and (prefixo_servico is None or col.startswith(prefixo_servico))
        ]

        if not col_area_existentes:
            st.warning("Nenhum atestado possui a disciplina ou campo selecionado.")
        else:
            df_filtrado = df_filtrado[df_filtrado[col_area_existentes].notnull().any(axis=1)]
            df_filtrado = df_filtrado[df_filtrado[col_area_existentes].ge(area_filtro).any(axis=1)]

            colunas_tabela = ["Empresa", "Cliente", "Servico", "CAT", "Objeto", "Tempo do projeto"]

            colunas_tabela.extend([
                col for col in col_tipo_existentes if df_filtrado[col].notnull().any()
            ])
            colunas_tabela.extend([
                col for col in col_area_existentes if df_filtrado[col].notnull().any()
            ])
            colunas_tabela.extend([
                col for col in col_base if col in df_filtrado.columns and df_filtrado[col].notnull().any()
            ])
            colunas_tabela.extend([
                col for col in col_kva if col in df_filtrado.columns and df_filtrado[col].notnull().any()
            ])
            colunas_tabela.extend([
                col for col in col_cadastral if col in df_filtrado.columns and df_filtrado[col].notnull().any()
            ])
            colunas_tabela.extend([
                col for col in col_drone if col in df_filtrado.columns and df_filtrado[col].notnull().any()
            ])

            st.markdown(f"#### Atestados com disciplina **{disciplina_selecionada}**")

            if df_filtrado.empty:
                st.warning("Nenhum atestado encontrado com os filtros aplicados.")
            else:
                st.dataframe(df_filtrado[colunas_tabela], use_container_width=True, hide_index=True)
