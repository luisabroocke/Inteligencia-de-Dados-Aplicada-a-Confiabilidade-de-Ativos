# ILIOT - Dashboard de análise do SLA de 4 horas
# Executar: pip install -r requirements.txt
#           streamlit run app.py

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


# 1. Configuração
st.set_page_config(page_title="ILIOT | SLA de 4 horas", page_icon="🛠️", layout="wide")
PASTA_DADOS = Path(__file__).parent / "data"


# 2. Carregamento e preparação dos dados
@st.cache_data
def carregar_dados():
    arquivo_os = PASTA_DADOS / "ordem_servico.csv"
    if not arquivo_os.exists():  # aceita o nome com acento também
        arquivo_os = PASTA_DADOS / "ordem_serviço.csv"
    if not arquivo_os.exists():
        raise FileNotFoundError("Coloque ordem_servico.csv dentro da pasta data/.")

    os = pd.read_csv(arquivo_os)
    datas = ["data_agendada", "data_inicio_real", "data_fim_real", "limite_sla_solucao"]
    for coluna in datas:
        os[coluna] = pd.to_datetime(os[coluna], errors="coerce")

    # O foco é a manutenção corretiva já concluída.
    os = os[(os["status_os"] == "CONCLUÍDA") & (os["tipo_os"] == "CORRETIVA")].copy()

    # Indicadores calculados a partir dos horários registrados.
    os["sla_horas"] = (
        (os["limite_sla_solucao"] - os["data_agendada"]).dt.total_seconds() / 3600
    ).round().astype("Int64")
    os["atraso_min"] = (
        (os["data_inicio_real"] - os["data_agendada"]).dt.total_seconds() / 60
    )
    os["reparo_min"] = (
        (os["data_fim_real"] - os["data_inicio_real"]).dt.total_seconds() / 60
    )
    os["reparo_h"] = os["reparo_min"] / 60
    os["estourou"] = os["sla_solucao_cumprido"].astype(str).str.lower().eq("false")
    os["ano"] = os["data_agendada"].dt.year
    os["mes"] = os["data_agendada"].dt.to_period("M").dt.to_timestamp()

    # Acrescenta faturamento sem duplicar ordens de serviço.
    arquivo_fat = PASTA_DADOS / "faturamento_os.csv"
    if arquivo_fat.exists():
        fat = pd.read_csv(arquivo_fat)
        fat = fat.groupby("id_ordem_servico", as_index=False)["valor_total_faturado"].sum()
        os = os.merge(fat, on="id_ordem_servico", how="left")
    else:
        os["valor_total_faturado"] = 0
    os["valor_total_faturado"] = os["valor_total_faturado"].fillna(0)
    return os


try:
    dados = carregar_dados()
except Exception as erro:
    st.error(f"Erro ao carregar os dados: {erro}")
    st.info("Confira os arquivos dentro da pasta data/.")
    st.stop()


# 3. Filtro de ano
st.sidebar.header("Filtro")
anos = sorted(dados["ano"].dropna().unique())
ano = st.sidebar.selectbox("Ano", ["Todos"] + [str(int(a)) for a in anos])
corretivas = dados if ano == "Todos" else dados[dados["ano"] == int(ano)]
os_4h = corretivas[corretivas["sla_horas"] == 4].copy()

if corretivas.empty or os_4h.empty:
    st.warning("Não há ordens corretivas com SLA de 4 horas nesse período.")
    st.stop()


# 4. Indicadores principais
st.title("🛠️ ILIOT — Confiabilidade de Ativos")
st.subheader("Foco: reduzir o estouro do SLA nas ordens corretivas de 4 horas")
st.write("Painel de análise dos atrasos para iniciar o atendimento e do tempo necessário para reparar o ativo.")

n_corretivas = len(corretivas)
n_4h = len(os_4h)
n_estouros = int(os_4h["estourou"].sum())
taxa = n_estouros / n_4h
mttr = os_4h["reparo_h"].mean()
custo = corretivas["valor_total_faturado"].sum()

kpis = st.columns(6)
valores = [
    ("Corretivas concluídas", f"{n_corretivas:,}".replace(",", ".")),
    ("Corretivas com SLA 4h", f"{n_4h:,}".replace(",", ".")),
    ("Estouro nas OS de 4h", f"{n_estouros:,}".replace(",", ".")),
    ("Taxa de estouro (4h)", f"{taxa:.1%}".replace(".", ",")),
    ("MTTR médio (OS 4h)", f"{mttr:.2f} h".replace(".", ",")),
    ("Faturamento corretivo", f"R$ {custo / 1_000_000:.1f} mi".replace(".", ",")),
]
for coluna, (nome, valor) in zip(kpis, valores):
    coluna.metric(nome, valor)
st.caption("O faturamento é um indicador de contexto, não uma estimativa do prejuízo causado pelo SLA.")
st.divider()


# 5. Gráfico: percentual de estouro por prazo contratado
st.subheader("1. Em qual prazo contratado ocorrem os estouros?")
por_sla = corretivas.groupby("sla_horas").agg(
    total=("id_ordem_servico", "count"), estouros=("estourou", "sum")
).reset_index()
por_sla["taxa"] = por_sla["estouros"] / por_sla["total"] * 100
por_sla["prazo"] = por_sla["sla_horas"].astype(str) + " horas"
fig = px.bar(
    por_sla, x="prazo", y="taxa", text=por_sla["taxa"].map(lambda x: f"{x:.1f}%"),
    hover_data=["total", "estouros"],
    labels={"prazo": "Prazo do SLA", "taxa": "Ordens fora do SLA (%)"},
    title="Taxa de estouro por prazo de solução",
)
st.plotly_chart(fig, use_container_width=True)
st.caption("No histórico completo, os 866 estouros das corretivas estão concentrados nas OS com SLA de 4 horas.")
st.divider()


# 6. Gráfico: atraso para iniciar x duração do reparo
st.subheader("2. Como o atraso de início e o tempo de reparo se relacionam?")
def faixa_reparo(h):
    if h <= 3:
        return "Até 3h"
    if h <= 3.5:
        return "De 3h a 3h30"
    return "De 3h30 a 4h"

os_4h["faixa_reparo"] = os_4h["reparo_h"].apply(faixa_reparo)
os_4h["faixa_atraso"] = os_4h["atraso_min"].apply(
    lambda x: "Até 30 min" if x <= 30 else "Acima de 30 min"
)
linhas = ["Até 3h", "De 3h a 3h30", "De 3h30 a 4h"]
colunas = ["Até 30 min", "Acima de 30 min"]
matriz = os_4h.pivot_table(
    index="faixa_reparo", columns="faixa_atraso", values="estourou", aggfunc="mean"
).reindex(index=linhas, columns=colunas) * 100
fig = px.imshow(
    matriz, text_auto=".1f", aspect="auto", color_continuous_scale="Reds",
    labels={"x": "Atraso para iniciar", "y": "Tempo de reparo", "color": "Estouro (%)"},
    title="Percentual de estouro nas ordens com SLA de 4 horas",
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Na faixa de reparo de 3h30 a 4h, 100% das OS iniciadas mais de 30 minutos após o agendamento estouraram o SLA.")
st.divider()


# 7. Gráfico: simulação de início mais rápido
st.subheader("3. Simulação: o que mudaria com um início mais rápido?")
def simular(limite_minutos):
    # Mantém a duração real do reparo e limita somente atrasos acima do limite.
    atraso_novo = os_4h["atraso_min"].clip(upper=limite_minutos)
    return int((atraso_novo + os_4h["reparo_min"] > 240).sum())

simulacao = pd.DataFrame({
    "Cenário": ["Situação atual", "Início em até 30 min", "Início em até 15 min"],
    "Estouro": [int(corretivas["estourou"].sum()), simular(30), simular(15)],
})
simulacao["Taxa geral"] = simulacao["Estouro"] / n_corretivas * 100
simulacao["Rótulo"] = simulacao.apply(
    lambda x: f"{int(x['Estouro'])} OS | {x['Taxa geral']:.1f}%", axis=1
)
fig = px.bar(
    simulacao, x="Cenário", y="Taxa geral", text="Rótulo",
    labels={"Taxa geral": "Estouro sobre todas as corretivas (%)", "Cenário": ""},
    title="Cenários simulados mantendo o tempo de reparo observado",
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Simulação exploratória, não resultado validado em operação. Os percentuais usam todas as OS corretivas como denominador.")
st.divider()


# 8. Gráfico: evolução mensal
st.subheader("4. Evolução mensal dos estouros nas OS de 4 horas")
mensal = os_4h.groupby("mes").agg(
    total=("id_ordem_servico", "count"), estouros=("estourou", "sum")
).reset_index()
mensal["taxa"] = mensal["estouros"] / mensal["total"] * 100
fig = px.line(
    mensal, x="mes", y="taxa", markers=True, hover_data=["total", "estouros"],
    labels={"mes": "Mês", "taxa": "OS fora do SLA (%)"},
    title="Percentual mensal de estouro",
)
st.plotly_chart(fig, use_container_width=True)


# 9. Consulta e explicação dos indicadores
with st.expander("Consultar ordens que estouraram o SLA"):
    tabela = os_4h[os_4h["estourou"]][[
        "id_ordem_servico", "data_agendada", "data_inicio_real", "data_fim_real", "atraso_min", "reparo_h"
    ]].sort_values("atraso_min", ascending=False).head(100)
    tabela = tabela.rename(columns={
        "id_ordem_servico": "ID da OS", "data_agendada": "Agendamento",
        "data_inicio_real": "Início real", "data_fim_real": "Fim real",
        "atraso_min": "Atraso (min)", "reparo_h": "Reparo (h)"
    })
    st.dataframe(tabela, use_container_width=True)
    st.caption("Exibição limitada às 100 ordens com maior atraso para iniciar.")

with st.expander("Como os indicadores são calculados"):
    st.markdown("""
    - **Bases:** `ordem_servico.csv` e `faturamento_os.csv`.
    - **Recorte:** ordens `CORRETIVA` com status `CONCLUÍDA`.
    - **Prazo do SLA:** `limite_sla_solucao` menos `data_agendada`.
    - **Atraso de início:** `data_inicio_real` menos `data_agendada`.
    - **Tempo de reparo:** `data_fim_real` menos `data_inicio_real`.
    - **Estouro:** `sla_solucao_cumprido = False` na base.
    - **Simulação:** limita o atraso de início e preserva o tempo de reparo observado.

    Os resultados mostram associações históricas. Eles não comprovam, isoladamente,
    causalidade nem garantem o mesmo efeito em uma operação real.
    """)

st.caption("Projeto ILIOT — Inteligência de Dados Aplicada à Confiabilidade de Ativos")
