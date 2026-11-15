# IIOT — Inteligência de Dados Aplicada à Confiabilidade de Ativos

## 1. Sobre o projeto

O projeto IIOT tem como finalidade analisar dados de ordens de serviço e indicadores operacionais para identificar oportunidades de melhoria na confiabilidade de ativos e na eficiência dos atendimentos técnicos.

A análise utiliza dados históricos de manutenção para compreender os fatores associados ao descumprimento dos prazos contratuais de atendimento (SLA), com foco nas ordens de serviço corretivas.

## 2. Problema identificado

O principal problema identificado foi o descumprimento do SLA de solução de 4 horas em ordens de serviço corretivas.

A análise inicial investigou diferenças entre fabricantes e categorias de equipamentos. Entretanto, os resultados não sustentaram essas características como explicações consistentes para os descumprimentos.

A investigação passou a considerar o tempo entre o horário agendado e o início real do atendimento, além da duração do reparo.

Os resultados indicaram uma oportunidade de melhoria na redução do tempo de espera para início dos atendimentos, especialmente nas ocorrências em que o reparo já demanda boa parte das 4 horas disponíveis.

## 3. Objetivo

Desenvolver uma solução de análise de dados que permita:

- Identificar padrões relacionados ao descumprimento do SLA.
- Monitorar indicadores de desempenho das ordens de serviço corretivas.
- Analisar a relação entre o início do atendimento e a duração dos reparos.
- Visualizar os resultados por meio de gráficos e indicadores.
- Apoiar decisões operacionais que contribuam para a redução dos atrasos.

## 4. Bases de dados utilizadas

O projeto utiliza bases relacionadas às ordens de serviço, aos ativos e ao faturamento.

| Base | Finalidade |
|---|---|
| `ordem_servico.csv` | Informações sobre ordens de serviço, datas, horários, tipos de atendimento e cumprimento do SLA. |
| `ativo.csv` | Informações cadastrais dos ativos utilizados na operação. |
| `faturamento_os.csv` | Informações financeiras associadas às ordens de serviço. |

**Período analisado:** janeiro de 2021 a dezembro de 2025.

As principais análises consideram as ordens de serviço corretivas concluídas.

## 5. Principais informações e indicadores

A análise inicial apresentou os seguintes resultados:

| Indicador | Resultado |
|---|---:|
| Total de ordens de serviço | 38.429 |
| Ordens de serviço concluídas | 35.351 |
| Ordens corretivas concluídas | 21.267 |
| Ordens com SLA de 4 horas | 7.248 |
| Descumprimentos de SLA | 866 |
| Taxa de descumprimento entre as corretivas concluídas | 4,1% |
| Taxa de descumprimento no grupo de SLA de 4 horas | 11,9% |
| MTTR médio | Aproximadamente 2,36 horas |

### Comparação entre os prazos de SLA

| Prazo contratual | Quantidade de OS | Descumprimentos |
|---|---:|---:|
| 4 horas | 7.248 | 866 |
| 12 horas | 6.977 | 0 |
| 24 horas | 7.042 | 0 |

Os 866 descumprimentos identificados estavam concentrados nas ordens com SLA de 4 horas.

### Relação entre início do atendimento e duração do reparo

A análise também identificou diferenças importantes conforme o tempo de espera para o início do atendimento:

- Reparos com duração de até 3 horas não apresentaram descumprimentos na análise.
- Nos reparos com duração entre 3 e 3,5 horas, os descumprimentos foram mais frequentes quando o início ocorreu após 30 minutos do horário agendado.
- Nos reparos entre 3,5 e 4 horas, o risco de descumprimento foi ainda maior, principalmente quando o atendimento começou após 30 minutos.

Esses resultados indicam uma associação entre o atraso no início do atendimento, a duração do reparo e o cumprimento do SLA. Não representam, isoladamente, uma comprovação de causalidade.

## 6. Simulação de cenários

Foram avaliados cenários hipotéticos de redução do tempo entre o agendamento e o início real do atendimento.

Na simulação apresentada no estudo:

| Cenário | Descumprimentos estimados |
|---|---:|
| Situação atual | 866 |
| Início em até 30 minutos | 611 |
| Início em até 15 minutos | 352 |

Os valores representam cenários simulados a partir dos dados históricos, não resultados de uma intervenção operacional já realizada.

## 7. Limitações identificadas

Durante a análise, foram identificadas algumas limitações nas bases disponíveis:

- Os textos de diagnóstico das ordens concluídas apresentavam pouca variação, dificultando sua utilização como variável explicativa.
- Foram identificados registros de manutenção corretiva anteriores à data de instalação de alguns ativos.
- Parte das ordens de serviço estava cancelada.
- A cobertura de dados IoT abrangia aproximadamente 50 dos 1.200 ativos analisados.

A análise dos alertas de superaquecimento também não apresentou evidências suficientes para comprovar capacidade preditiva com os dados disponíveis.

Por isso, os resultados devem ser interpretados considerando a qualidade, a abrangência e as limitações das informações utilizadas.

## 8. Solução desenvolvida: Dashboard PyDash

Para facilitar a interpretação dos resultados, foi desenvolvido um dashboard utilizando Python, Streamlit e Plotly.

O painel apresenta informações relacionadas ao cumprimento do SLA, permitindo acompanhar indicadores e visualizar padrões operacionais.

### Principais funcionalidades

- Indicadores gerais das ordens corretivas concluídas.
- Quantidade de ordens com SLA de 4 horas.
- Quantidade e taxa de descumprimentos.
- MTTR médio dos atendimentos.
- Comparação do descumprimento entre prazos contratuais.
- Análise da relação entre atraso no início e duração do reparo.
- Simulação de cenários de redução do tempo de início.
- Evolução mensal dos descumprimentos.
- Consulta das ordens de serviço que ultrapassaram o SLA.

### Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python | Linguagem de programação. |
| Pandas | Manipulação e análise dos dados. |
| Streamlit | Desenvolvimento da interface do dashboard. |
| Plotly | Criação dos gráficos interativos. |
| GitHub | Versionamento e organização do projeto. |

## 9. Estrutura do projeto

```text
IIOT/
│
├── app.py
│
├── requirements.txt
│
├── README.md
│
└── data/
    ├── ordem_servico.csv
    ├── ativo.csv
    └── faturamento_os.csv
```

## 10. Como executar o dashboard

### Pré-requisitos

- Python instalado.
- Arquivos CSV disponibilizados na pasta `data/`.

### Instalação das dependências

No terminal, execute:

```bash
pip install -r requirements.txt
```

### Execução

Na pasta principal do projeto, execute:

```bash
streamlit run app.py
```

O Streamlit abrirá o dashboard no navegador.

---

# 11. Documentação do código — app.py

O arquivo `app.py` concentra a implementação do dashboard e é responsável por carregar, tratar, analisar e apresentar os dados.

### 11.1. Importação das bibliotecas

O código utiliza:

- `streamlit`: construção da interface.
- `pandas`: leitura, organização e manipulação dos arquivos CSV.
- `plotly.express`: criação dos gráficos.
- `pathlib`: definição dos caminhos dos arquivos.

### 11.2. Carregamento dos dados

A função `carregar_dados()` realiza a leitura dos arquivos CSV, verifica a existência das colunas necessárias e converte os campos de data para o formato adequado.

Também realiza a seleção das ordens corretivas concluídas e prepara os dados para as análises.

### 11.3. Tratamento e cálculo dos indicadores

O código calcula:

- **Duração do SLA:** diferença entre o horário agendado e o limite contratual de solução.
- **Atraso no início:** diferença entre o horário agendado e o início real.
- **Tempo de reparo:** diferença entre o início e o fim real do atendimento.
- **Descumprimento:** identificação das ordens cujo indicador de cumprimento do SLA está marcado como falso.
- **MTTR:** média do tempo de reparo.

### 11.4. Filtros e indicadores

O usuário pode selecionar os anos que deseja visualizar.

A partir desse filtro, o dashboard atualiza os indicadores principais, incluindo a quantidade de ordens corretivas, ordens com SLA de 4 horas, descumprimentos, taxa de descumprimento e MTTR.

### 11.5. Gráficos e visualizações

O dashboard apresenta cinco áreas principais de análise:

1. **Descumprimento por prazo contratual:** compara as taxas de descumprimento entre os diferentes prazos de SLA.
2. **Relação entre atraso no início e duração do reparo:** utiliza um mapa de calor para visualizar as taxas de descumprimento conforme as faixas de tempo.
3. **Simulação de redução do tempo de início:** compara cenários hipotéticos de redução do atraso inicial.
4. **Evolução mensal:** apresenta a variação mensal da taxa de descumprimento nas ordens com SLA de 4 horas.
5. **Ordens com descumprimento:** apresenta uma tabela com informações das ordens que ultrapassaram o prazo contratual.

### 11.6. Considerações sobre as simulações

As simulações são realizadas a partir dos horários registrados na base, considerando a redução hipotética do atraso inicial e mantendo a duração observada do reparo.

Portanto, seus resultados devem ser interpretados como estimativas para análise de cenários, e não como garantia de melhoria operacional.

---

## 12. Próximas etapas

Como evolução do projeto, uma possibilidade é desenvolver um modelo de classificação supervisionada para estimar o risco de descumprimento do SLA no momento da abertura da ordem de serviço.

Essa etapa poderá utilizar informações disponíveis antes do início do atendimento, evitando o uso de dados futuros que comprometam a avaliação do modelo.

O objetivo é avançar de uma análise histórica para uma abordagem de apoio à tomada de decisão, permitindo identificar antecipadamente ordens com maior risco de atraso.
