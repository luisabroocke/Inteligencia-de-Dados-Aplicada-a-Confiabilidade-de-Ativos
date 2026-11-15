# IIOT - Dashboard de análise do SLA de 4 horas

import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata
from pathlib import Path


# Configuração da página
st.set_page_config(
    page_title="IIOT - Análise de SLA",
    layout="wide"
)


# Caminhos dos arquivos
PASTA_DADOS = Path("data")
ARQUIVO_OS = PASTA_DADOS / "ordem_servico.csv"
ARQUIVO_FATURAMENTO = PASTA_DADOS / "faturamento_os.csv"


def normalizar_texto(valor):
    """Padroniza textos para facilitar comparações."""
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(
        caractere for caractere in texto
        if not unicodedata.combining(caractere)
    )


def converter_booleano(valor):
    if pd.isna(valor):
        return None

    valor = normalizar_texto(valor).lower()

    if valor in ["true", "1", "sim", "s", "cumprido"]:
        return True

    if valor in ["false", "0", "nao", "n", "descumprido"]:
        return False

    return None


@st.cache_data
def carregar_dados():

    if not ARQUIVO_OS.exists():
        st.error(
            "Arquivo ordem_servico.csv não encontrado. "
            "Verifique se ele está dentro da pasta data."
        )
        st.stop()

    ordens = pd.read_csv(
        ARQUIVO_OS,
        low_memory=False
    )

    colunas_obrigatorias = [
        "id_ordem_servico",
        "tipo_os",
        "status_os",
        "data_agendada",
        "data_inicio_real",
        "data_fim_real",
        "limite_sla_solucao",
        "sla_solucao_cumprido"
    ]

    faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in ordens.columns
    ]

    if faltantes:
        st.error(
            "Colunas não encontradas: "
            + ", ".join(faltantes)
        )
        st.stop()

    # Conversão das datas
    colunas_data = [
        "data_agendada",
        "data_inicio_real",
        "data_fim_real",
        "limite_sla_solucao"
    ]

    for coluna in colunas_data:
        ordens[coluna] = pd.to_datetime(
            ordens[coluna],
            errors="coerce"
        )

    # Padronização dos campos de texto
    ordens["tipo_os"] = (
        ordens["tipo_os"]
        .apply(normalizar_texto)
    )

    ordens["status_os"] = (
        ordens["status_os"]
        .apply(normalizar_texto)
    )

    ordens["sla_cumprido"] = (
        ordens["sla_solucao_cumprido"]
        .apply(converter_booleano)
    )

    # Seleção das ordens corretivas concluídas
    ordens = ordens[
        (ordens["tipo_os"] == "CORRETIVA") &
        (ordens["status_os"] == "CONCLUIDA")
    ].copy()

    # Cálculo da duração do SLA
    ordens["sla_horas"] = (
        ordens["limite_sla_solucao"] -
        ordens["data_agendada"]
    ).dt.total_seconds() / 3600

    # Tempo entre agendamento e início real
    ordens["atraso_inicio_min"] = (
        ordens["data_inicio_real"] -
        ordens["data_agendada"]
    ).dt.total_seconds() / 60

    # Tempo de execução do reparo
    ordens["tempo_reparo_min"] = (
        ordens["data_fim_real"] -
        ordens["data_inicio_real"]
    ).dt.total_seconds() / 60

    ordens["tempo_reparo_horas"] = (
        ordens["tempo_reparo_min"] / 60
    )

    # Remoção de registros incompletos
    ordens = ordens.dropna(
        subset=[
            "data_agendada",
            "data_inicio_real",
            "data_fim_real",
            "sla_horas",
            "sla_cumprido"
        ]
    ).copy()

    # Remoção de valores inválidos
    ordens = ordens[
        (ordens["sla_horas"] > 0) &
        (ordens["atraso_inicio_min"] >= 0) &
        (ordens["tempo_reparo_min"] >= 0)
    ].copy()

    # Identificação dos descumprimentos
    ordens["sla_estourado"] = (
        ordens["sla_cumprido"] == False
    )

    # Informações de período
    ordens["ano"] = ordens["data_agendada"].dt.year
    ordens["mes"] = (
        ordens["data_agendada"]
        .dt.to_period("M")
        .astype(str)
    )

    # Classificação da duração do reparo
    ordens["faixa_reparo"] = pd.cut(
        ordens["tempo_reparo_horas"],
        bins=[0, 3, 3.5, 4, float("inf")],
        labels=[
            "Ate 3 horas",
            "3 a 3,5 horas",
            "3,5 a 4 horas",
            "Acima de 4 horas"
        ],
        include_lowest=True
    )

    # Classificação do tempo de início
    ordens["faixa_inicio"] = ordens[
        "atraso_inicio_min"
    ].apply(
        lambda x: "Ate 30 minutos"
        if x <= 30
        else "Acima de 30 minutos"
    )

    # Carregamento do faturamento, quando disponível
    if ARQUIVO_FATURAMENTO.exists():

        faturamento = pd.read_csv(
            ARQUIVO_FATURAMENTO,
            low_memory=False
        )

        if (
            "id_ordem_servico" in faturamento.columns
            and "valor_total_faturado" in faturamento.columns
        ):

            faturamento["valor_total_faturado"] = pd.to_numeric(
                faturamento["valor_total_faturado"],
                errors="coerce"
            ).fillna(0)

            faturamento = (
                faturamento
                .groupby(
                    "id_ordem_servico",
                    as_index=False
                )["valor_total_faturado"]
                .sum()
            )

            ordens = ordens.merge(
                faturamento,
                on="id_ordem_servico",
                how="left"
            )

            ordens["valor_total_faturado"] = (
                ordens["valor_total_faturado"].fillna(0)
            )

    return ordens


# Carregamento dos dados
dados = carregar_dados()

if dados.empty:
    st.warning(
        "Não foram encontradas ordens corretivas concluídas "
        "com informações válidas."
    )
    st.stop()


# Filtros
st.sidebar.title("Filtros")
st.sidebar.write("Selecione os anos:")

anos_disponiveis = sorted(
    dados["ano"].dropna().unique().tolist()
)

for ano in anos_disponiveis:
    st.sidebar.checkbox(
        str(ano),
        value=True,
        key=f"filtro_ano_{ano}"
    )

anos_selecionados = [
    ano for ano in anos_disponiveis
    if st.session_state.get(f"filtro_ano_{ano}", True)
]

if not anos_selecionados:
    st.warning("Selecione pelo menos um ano.")
    st.stop()

dados = dados[
    dados["ano"].isin(anos_selecionados)
].copy()

if dados.empty:
    st.warning("Não existem registros para os anos selecionados.")
    st.stop()


# Identificação das ordens com SLA de 4 horas
dados_4h = dados[
    dados["sla_horas"].between(3.9, 4.1)
].copy()


# Indicadores principais
total_corretivas = len(dados)
total_4h = len(dados_4h)

total_estouradas = int(
    dados_4h["sla_estourado"].sum()
)

taxa_estouro = (
    total_estouradas / total_4h * 100
    if total_4h > 0 else 0
)

mttr_4h = (
    dados_4h["tempo_reparo_horas"].mean()
    if total_4h > 0 else 0
)


# Cabeçalho
st.title(
    "IIOT - Inteligência de Dados Aplicada à Confiabilidade de Ativos"
)

st.markdown(
    """
    ### Análise de cumprimento do SLA

    Este painel apresenta os principais indicadores das ordens de serviço
    corretivas concluídas, com foco nos atrasos relacionados ao SLA
    contratual de 4 horas.
    """
)

st.divider()


# Indicadores
st.subheader("Indicadores principais")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "OS corretivas concluídas",
    f"{total_corretivas:,}".replace(",", ".")
)

col2.metric(
    "OS com SLA de 4h",
    f"{total_4h:,}".replace(",", ".")
)

col3.metric(
    "Descumprimentos",
    f"{total_estouradas:,}".replace(",", ".")
)

col4.metric(
    "Taxa de descumprimento",
    f"{taxa_estouro:.1f}%"
)

col5.metric(
    "MTTR - SLA 4h",
    f"{mttr_4h:.2f} h"
)

st.divider()


# Gráfico 1 - Descumprimento por prazo contratual
st.subheader("1. Descumprimento por prazo contratual")

resumo_sla = dados.copy()

resumo_sla["prazo_horas"] = (
    resumo_sla["sla_horas"].round().astype(int)
)

resumo_sla = (
    resumo_sla
    .groupby("prazo_horas")
    .agg(
        total_os=("id_ordem_servico", "count"),
        descumprimentos=("sla_estourado", "sum")
    )
    .reset_index()
)

resumo_sla["taxa_descumprimento"] = (
    resumo_sla["descumprimentos"] /
    resumo_sla["total_os"] * 100
)

resumo_sla["prazo"] = (
    resumo_sla["prazo_horas"].astype(str) + " horas"
)

fig_sla = px.bar(
    resumo_sla,
    x="prazo",
    y="taxa_descumprimento",
    text=resumo_sla["taxa_descumprimento"].round(1).astype(str) + "%",
    labels={
        "prazo": "Prazo contratual",
        "taxa_descumprimento": "Descumprimento (%)"
    }
)

fig_sla.update_traces(textposition="outside")

fig_sla.update_layout(
    yaxis_title="Descumprimento (%)",
    xaxis_title="Prazo contratual",
    showlegend=False
)

st.plotly_chart(
    fig_sla,
    use_container_width=True
)

st.caption(
    "Comparação da frequência de descumprimento "
    "entre os diferentes prazos contratuais."
)


# Gráfico 2 - Relação entre atraso e duração do reparo
st.subheader(
    "2. Relação entre atraso no início e duração do reparo"
)

if not dados_4h.empty:

    ordem_reparo = [
        "Ate 3 horas",
        "3 a 3,5 horas",
        "3,5 a 4 horas",
        "Acima de 4 horas"
    ]

    ordem_inicio = [
        "Ate 30 minutos",
        "Acima de 30 minutos"
    ]

    tabela_calor = (
        dados_4h
        .pivot_table(
            index="faixa_reparo",
            columns="faixa_inicio",
            values="sla_estourado",
            aggfunc="mean",
            observed=False
        ) * 100
    )

    tabela_calor = tabela_calor.reindex(
        index=ordem_reparo,
        columns=ordem_inicio
    )

    fig_calor = px.imshow(
        tabela_calor,
        text_auto=".1f",
        aspect="auto",
        color_continuous_scale="Reds",
        zmin=0,
        zmax=100,
        labels={
            "x": "Tempo até o início do atendimento",
            "y": "Duração do reparo",
            "color": "Descumprimento (%)"
        }
    )

    fig_calor.update_xaxes(
        tickmode="array",
        tickvals=ordem_inicio,
        ticktext=[
            "Até 30 minutos",
            "Acima de 30 minutos"
        ]
    )

    fig_calor.update_yaxes(
        tickmode="array",
        tickvals=ordem_reparo,
        ticktext=[
            "Até 3 horas",
            "3 a 3,5 horas",
            "3,5 a 4 horas",
            "Acima de 4 horas"
        ]
    )

    fig_calor.update_layout(
        xaxis_title="Tempo até o início do atendimento",
        yaxis_title="Duração do reparo"
    )

    st.plotly_chart(
        fig_calor,
        use_container_width=True
    )

    st.caption(
        "O gráfico apresenta a taxa de descumprimento conforme "
        "o tempo de início e a duração do reparo. Células sem "
        "registros permanecem vazias."
    )

else:
    st.info(
        "Não há ordens com SLA de 4 horas para exibir este gráfico."
    )


# Gráfico 3 - Simulação de cenários
st.subheader("3. Simulação de redução do tempo de início")

if not dados_4h.empty:

    dados_4h["tempo_total_30"] = (
        dados_4h["atraso_inicio_min"].clip(upper=30) +
        dados_4h["tempo_reparo_min"]
    )

    dados_4h["tempo_total_15"] = (
        dados_4h["atraso_inicio_min"].clip(upper=15) +
        dados_4h["tempo_reparo_min"]
    )

    limite_minutos = dados_4h["sla_horas"] * 60

    atual = int(
        dados_4h["sla_estourado"].sum()
    )

    cenario_30 = int(
        (dados_4h["tempo_total_30"] > limite_minutos).sum()
    )

    cenario_15 = int(
        (dados_4h["tempo_total_15"] > limite_minutos).sum()
    )

    simulacao = pd.DataFrame({
        "Cenario": [
            "Situação atual",
            "Início em até 30 min",
            "Início em até 15 min"
        ],
        "Descumprimentos": [
            atual,
            cenario_30,
            cenario_15
        ]
    })

    fig_simulacao = px.bar(
        simulacao,
        x="Cenario",
        y="Descumprimentos",
        text="Descumprimentos",
        labels={
            "Cenario": "Cenário analisado",
            "Descumprimentos": "Quantidade de descumprimentos"
        }
    )

    fig_simulacao.update_traces(
        textposition="outside"
    )

    fig_simulacao.update_layout(
        showlegend=False,
        yaxis_title="Quantidade de descumprimentos",
        xaxis_title=""
    )

    st.plotly_chart(
        fig_simulacao,
        use_container_width=True
    )

    st.caption(
        "Simulação hipotética que considera a redução do tempo "
        "entre o agendamento e o início real, mantendo a duração "
        "observada do reparo. Os resultados não garantem "
        "uma redução real dos descumprimentos."
    )

else:
    st.info(
        "Não há ordens com SLA de 4 horas para simular."
    )


# Gráfico 4 - Evolução mensal
st.subheader("4. Evolução mensal dos descumprimentos")

if not dados_4h.empty:

    mensal = (
        dados_4h
        .groupby("mes")
        .agg(
            total_os=("id_ordem_servico", "count"),
            descumprimentos=("sla_estourado", "sum")
        )
        .reset_index()
        .sort_values("mes")
    )

    mensal["taxa_descumprimento"] = (
        mensal["descumprimentos"] /
        mensal["total_os"] * 100
    )

    fig_mensal = px.line(
        mensal,
        x="mes",
        y="taxa_descumprimento",
        markers=True,
        labels={
            "mes": "Mês",
            "taxa_descumprimento": "Descumprimento (%)"
        }
    )

    fig_mensal.update_layout(
        xaxis_title="Mês",
        yaxis_title="Descumprimento (%)"
    )

    st.plotly_chart(
        fig_mensal,
        use_container_width=True
    )

else:
    st.info(
        "Não há dados suficientes para apresentar a evolução mensal."
    )


# Tabela de ordens com descumprimento
st.divider()

st.subheader(
    "5. Ordens de serviço com descumprimento"
)

ordens_estouradas = dados_4h[
    dados_4h["sla_estourado"]
].copy()

if not ordens_estouradas.empty:

    colunas_tabela = [
        "id_ordem_servico",
        "data_agendada",
        "data_inicio_real",
        "data_fim_real",
        "atraso_inicio_min",
        "tempo_reparo_horas"
    ]

    tabela = ordens_estouradas[
        colunas_tabela
    ].copy()

    tabela = tabela.rename(columns={
        "id_ordem_servico": "ID da OS",
        "data_agendada": "Data agendada",
        "data_inicio_real": "Início real",
        "data_fim_real": "Fim real",
        "atraso_inicio_min": "Atraso no início (min)",
        "tempo_reparo_horas": "Tempo de reparo (h)"
    })

    tabela["Atraso no início (min)"] = (
        tabela["Atraso no início (min)"].round(1)
    )

    tabela["Tempo de reparo (h)"] = (
        tabela["Tempo de reparo (h)"].round(2)
    )

    st.dataframe(
        tabela.sort_values(
            "Atraso no início (min)",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

else:
    st.info(
        "Nenhuma ordem com descumprimento foi encontrada no período."
    )


# Informações finais
st.divider()

with st.expander("Sobre a análise"):

    st.markdown(
        """
        - **SLA:** prazo contratual para solucionar a ordem de serviço.
        - **MTTR:** tempo médio de reparo.
        - **Descumprimento:** ordem de serviço que ultrapassou o prazo.
        - **Simulação:** cenário hipotético de redução do tempo de início
          do atendimento.
        """
    )
