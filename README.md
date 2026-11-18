# IIOT — Inteligência de Dados Aplicada à Confiabilidade de Ativos

**Dashboard online:** [Acessar o dashboard IIOT](https://inteligencia-de-dados-aplicada-a-confiabilidade-de-ativos-9p5t.streamlit.app)

**Modelo preditivo (Parte II):** [abrir o notebook no Colab](https://colab.research.google.com/github/luisabroocke/Inteligencia-de-Dados-Aplicada-a-Confiabilidade-de-Ativos/blob/main/modelo_preditivo_sla.ipynb)

## 1. Sobre o projeto

O projeto IIOT tem como finalidade analisar dados de ordens de serviço e indicadores operacionais para identificar oportunidades de melhoria na confiabilidade de ativos e na eficiência dos atendimentos técnicos.

A análise utiliza dados históricos de manutenção para compreender os fatores associados ao descumprimento dos prazos contratuais de atendimento (SLA), com foco nas ordens de serviço corretivas.

O projeto tem duas partes:

- **Parte I — Análise do que já aconteceu:** teste da hipótese inicial, identificação dos fatores associados ao descumprimento do SLA e dashboard (seções 2 a 11).
- **Parte II — Modelo preditivo:** teste do que os dados permitem antecipar, com previsão de demanda e estimativa de risco de descumprimento do SLA (seção 12).

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
- Planejar a demanda de ordens de serviço corretivas.
- Estimar o risco de descumprimento do SLA durante o atendimento, para priorizar as ordens.

## 4. Bases de dados utilizadas

O projeto utiliza bases relacionadas às ordens de serviço, aos ativos e ao faturamento.

| Base | Finalidade |
|---|---|
| `ordem_servico.csv` | Informações sobre ordens de serviço, datas, horários, tipos de atendimento e cumprimento do SLA. |
| `ativo.csv` | Informações cadastrais dos ativos utilizados na operação. |
| `faturamento_os.csv` | Informações financeiras associadas às ordens de serviço. |

Período analisado: janeiro de 2021 a dezembro de 2025.

As principais análises consideram as ordens de serviço corretivas concluídas.

## 5. Principais informações e indicadores

A análise inicial apresentou os seguintes resultados:

| Indicador | Resultado |
|---|---|
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
|---|---|---|
| 4 horas | 7.248 | 866 |
| 12 horas | 6.977 | 0 |
| 24 horas | 7.042 | 0 |

Os 866 descumprimentos identificados estavam concentrados nas ordens com SLA de 4 horas.

### Relação entre início do atendimento e duração do reparo

A análise também identificou diferenças importantes conforme o tempo de espera para o início do atendimento:

- Reparos com duração de até 3 horas não apresentaram descumprimentos na análise.
- Nos reparos com duração entre 3 e 3,5 horas, os descumprimentos foram mais frequentes quando o início ocorreu após 30 minutos do horário agendado.
- Nos reparos entre 3,5 e 4 horas, o risco de descumprimento foi ainda maior, principalmente quando o atendimento começou após 30 minutos.

Como o SLA conta a partir do horário agendado, o atraso no início consome o prazo disponível para o reparo. Esses resultados indicam uma associação entre o atraso no início do atendimento, a duração do reparo e o cumprimento do SLA. Não representam, isoladamente, uma comprovação de causalidade.

## 6. Simulação de cenários

Foram avaliados cenários hipotéticos de redução do tempo entre o agendamento e o início real do atendimento.

Na simulação apresentada no estudo:

| Cenário | Descumprimentos estimados |
|---|---|
| Situação atual | 866 |
| Início em até 30 minutos | 611 |
| Início em até 15 minutos | 352 |

Os valores representam cenários simulados a partir dos dados históricos, não resultados de uma intervenção operacional já realizada. A simulação é exploratória e não faz parte do modelo preditivo da Parte II.

## 7. Limitações identificadas

Durante a análise, foram identificadas algumas limitações nas bases disponíveis:

- Os textos de diagnóstico das ordens concluídas apresentavam pouca variação, dificultando sua utilização como variável explicativa.
- Foram identificados registros de manutenção corretiva anteriores à data de instalação de alguns ativos (147 ativos, cerca de 12%).
- Parte das ordens de serviço estava cancelada (3.078 OS, 8,0%).
- A cobertura de dados IoT abrangia aproximadamente 50 dos 1.200 ativos analisados.

A análise dos alertas de superaquecimento também não apresentou evidências suficientes para comprovar capacidade preditiva com os dados disponíveis.

Essas limitações afetam principalmente as previsões mais antecipadas (seção 12.4). Por isso, os resultados devem ser interpretados considerando a qualidade, a abrangência e as limitações das informações utilizadas.

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
| scikit-learn | Modelos preditivos da Parte II (notebook). |
| GitHub | Versionamento e organização do projeto. |

## 9. Estrutura do projeto

```text
IIOT/
│
├── app.py
│
├── modelo_preditivo_sla.ipynb
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

## 11. Documentação do código — app.py

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

## 12. Parte II — Modelo preditivo

A Parte I analisou o que já aconteceu. A Parte II testa o que os dados permitem **antecipar**. O código está no notebook [`modelo_preditivo_sla.ipynb`](modelo_preditivo_sla.ipynb).

### 12.1. Método

- **Treino no passado, teste no futuro:** o modelo aprende com 2021 a 2024 e é avaliado em 2025. As datas nunca são embaralhadas.
- **Sem vazamento de dados:** só são usadas variáveis conhecidas no momento da previsão. O tempo de reparo, a data de fim e o faturamento só existem depois do atendimento e ficam fora.
- **Comparação com uma referência:** cada resultado é comparado com o acaso (AUC 0,5) ou com uma regra simples.
- **Recorte:** ordens corretivas concluídas; o risco de SLA usa as 7.248 OS com prazo de 4 horas, pois nos prazos de 12 e 24 horas não há nenhum descumprimento para o modelo aprender.

### 12.2. Resultados

**Previsão de demanda de OS corretivas** (planejamento, meses à frente)

| Método | Erro médio (MAPE) em 2025 |
|---|---|
| Média geral (ignora a sazonalidade) | 10,6% |
| Mesmo mês do ano anterior | 6,2% |
| **Média sazonal (mês a mês)** | **3,5%** |

Em teste com janela crescente (2022 a 2025), o erro da média sazonal ficou entre 3,5% e 6,0%. A projeção para 2026 é de cerca de 4.250 OS corretivas, com picos de novembro a fevereiro. O volume de OS não explica a taxa de descumprimento do SLA (correlação de 0,09), então essa previsão serve ao planejamento de capacidade, não à prevenção direta de descumprimentos.

**Risco de descumprimento do SLA de 4 horas** (teste com 1.450 OS de 2025)

| Momento da previsão | Modelo | AUC |
|---|---|---|
| Abertura da OS | Regressão logística / Gradient Boosting | 0,527 / 0,519 |
| Início do atendimento | Regressão logística / Gradient Boosting | 0,781 / 0,780 |
| Início do atendimento | Regra simples (só o atraso no início) | 0,785 |

- O risco pode ser estimado **quando o atendimento começa**, usando o atraso no início, que já é conhecido antes do fim do reparo.
- **O modelo não superou a regra simples** baseada no atraso. O valor dele está em fornecer a probabilidade e as faixas de risco.
- As 10% de OS de maior risco concentram 31,2% dos descumprimentos (lift de 3,1 vezes a média); as 20% de maior risco concentram 48%.

| Faixa de risco | OS no teste | Descumprimentos | Taxa observada |
|---|---|---|---|
| Baixo (menos de 10%) | 746 | 23 | 3,1% |
| Médio (10% a 25%) | 580 | 106 | 18,3% |
| Alto (mais de 25%) | 124 | 47 | 37,9% |

### 12.3. Demonstração de vazamento de dados

Um modelo que usa também o tempo de reparo atinge AUC de 1,000, mas só refaz a conta (início + reparo acima do limite) depois que tudo aconteceu. Por isso ele não serve para prevenir nada e fica fora da solução.

### 12.4. Limites dos dados: o que não é possível antecipar

Antes do atendimento, todas as tentativas ficaram no nível do acaso:

| Tentativa | Métrica | Resultado | Acaso |
|---|---|---|---|
| Descumprimento na abertura da OS | AUC | 0,519 | 0,5 |
| + carga do técnico e histórico do ativo | AUC | 0,485 | 0,5 |
| Prever o atraso no início | R² | −0,033 | 0 |
| Prever a duração do reparo | R² | −0,045 | 0 |
| Falha do ativo no mês seguinte | AUC | 0,518 | 0,5 |

Na falha do ativo, o AUC de 0,518 está estatisticamente acima de 0,5 por causa do grande número de linhas, mas sem utilidade prática.

Também foram testadas as demais bases do projeto (seção 3.5 do notebook):

| Base | Teste | Resultado |
|---|---|---|
| `chamado` | Antecedência entre abrir o chamado e o horário agendado | Correlação de 0,007 com o atraso e 0,005 com o reparo; a descrição do defeito é a mesma em todos os chamados |
| `tecnico_especialidade` | Especialidade do técnico diferente da exigida pelo ativo | Coincide em 100% das OS, sem variação para testar |
| `resposta_checklist` | Itens não conformes x reparo e estouro | Correlação de 0,01 e −0,001 (e o checklist só existe após o atendimento) |
| `leitura_horimetro` | Temperatura, vibração e horas acumuladas x corretiva em 7 e 30 dias | AUC de 0,503 e 0,501 (acaso = 0,5) |

Com as colunas disponíveis, **não é possível antecipar o descumprimento do SLA na abertura da OS nem prever a falha de um ativo**. O que é previsível é a demanda agregada e o risco durante o atendimento.

> Os resultados são associações estatísticas e não provam causalidade.

## 13. Próximas etapas

A Parte II mostrou que os dados atuais permitem prever a demanda e estimar o risco de descumprimento do SLA **durante o atendimento**, mas não **antes** dele. Todas as bases do projeto foram testadas (seção 12.4), e nenhuma antecipa o descumprimento na abertura da OS.

### 13.1. Pode ser feito com as bases atuais

1. **Levar os resultados ao dashboard:** incluir uma aba de demanda prevista e uma de risco de SLA por faixa (Baixo, Médio e Alto).
2. **Sinalizar os dados inconsistentes:** marcar os 147 ativos com data de instalação posterior à primeira corretiva, para que não distorçam as análises.

### 13.2. Depende de novos dados

Para antecipar o risco já na abertura da ordem de serviço, é preciso coletar o que hoje não existe ou não tem variação na base:

1. **Enriquecer a abertura da OS:** registrar o tipo de falha, as peças necessárias e a complexidade estimada. Hoje a descrição do defeito (chamado) e o diagnóstico técnico são iguais em todas as ordens.
2. **Ampliar a telemetria:** mais dispositivos IoT e mais tipos de alerta, já que a telemetria dos 50 dispositivos atuais não antecipou falhas.
3. **Validar em operação:** testar se priorizar as ordens de maior risco e reduzir o atraso no início reduz, de fato, os descumprimentos, já que a simulação da seção 6 é apenas exploratória.
4. **Refazer os testes preditivos** com os novos dados, mantendo a divisão por tempo e a comparação com uma regra simples.
