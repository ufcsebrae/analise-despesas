# Robô de Análise de Despesas com IA

## 1. Visão Geral do Projeto

Este projeto é um robô de automação (`RPA - Robotic Process Automation`) construído em Python, projetado para realizar uma análise financeira e estratégica completa sobre as despesas de diferentes unidades de negócio.

O robô se conecta a bancos de dados, extrai dados brutos de despesas e orçamentos, os enriquece, e aplica uma série de modelos de análise e Inteligência Artificial para gerar insights acionáveis. O resultado final é um relatório em formato HTML, claro e intuitivo, que é automaticamente enviado por e-mail para os gestores responsáveis, com a base de dados da sua unidade anexada em `.csv`.

## 2. Principais Funcionalidades

O relatório gerado pelo robô é composto por 5 análises principais:

#### Tabela 1: Execução Orçamentária com Score de Criticidade
- Compara o Orçado vs. Realizado para cada projeto.
- **Inteligência Aplicada:** Introduz um **Score de Criticidade** (↑ Alto, → Médio, ↓ Baixo) que cruza a execução orçamentária com a ocorrência de anomalias no ano, permitindo uma priorização de atenção muito mais rápida.

#### Tabela 2: Desempenho Mensal com Detecção de Tendência
- Mostra a evolução dos gastos mensais, separados por projetos exclusivos e compartilhados.
- **Inteligência Aplicada:** Utiliza o modelo de IA **`IsolationForest`** para analisar a série temporal dos gastos totais. Ele sinaliza meses com **"Pico Atípico"** ou **"Redução Atípica"**, destacando desvios significativos no ritmo financeiro da unidade.

#### Tabela 3: Top 5 Fornecedores
- Apresenta os principais fornecedores por valor total gasto no ano, segmentado por tipo de projeto.

#### Tabela 4: Ocorrências Atípicas de Contexto
- **Inteligência Aplicada:** Utiliza uma abordagem híbrida com **Engenharia de Features e `IsolationForest`**. A IA não olha apenas para o valor, mas para o "crachá de familiaridade" de cada transação, analisando:
    1.  **Z-Score do Valor:** O quão estatisticamente incomum é um valor para sua combinação específica de Fornecedor-Projeto.
    2.  **Frequência do Fornecedor:** O quão "conhecido" é o fornecedor para a unidade.
    3.  **Frequência do Projeto:** O quão comum é a ocorrência de gastos nesse projeto.
- O resultado é uma análise que encontra combinações genuinamente estranhas (ex: um fornecedor raro em um projeto raro), eliminando os "falsos positivos" de variações normais de valor.

#### Tabela 5: Análise de Comportamento das Contas (Clusterização)
- **Inteligência Aplicada:** Utiliza o modelo de IA **`K-Means Clustering`** para analisar o "DNA financeiro" dos tipos de despesa (agrupados pelo `DESC_NIVEL_4`) dos projetos exclusivos da unidade. Ele os segmenta em perfis como "Contas de Rotina", "Contas de Eventos Esporádicos", etc., com base em:
    - Valor Total Anual
    - Frequência de Lançamentos
    - **Coeficiente de Variação (CV):** Uma medida estatística da imprevisibilidade dos gastos.

## 3. Como Funciona (Arquitetura)

O fluxo de trabalho é orquestrado pelo `main.py` e segue os seguintes passos:

1.  **Configuração:** Carrega os parâmetros do `config.py`, incluindo o `MES_ANALISE_SOBRESCRITA`, que permite "voltar no tempo" para analisar um fechamento específico.
2.  **Extração:** O `extracao.py` se conecta aos bancos de dados e extrai os dados brutos de despesas e orçamentos.
3.  **Processamento e Enriquecimento:** Os dados são limpos e novas colunas, como as de data e tipo de projeto (Exclusivo/Compartilhado), são adicionadas.
4.  **Loop por Unidade:** O robô inicia um loop para cada gestor definido no `MAPA_GESTORES` em `config.py`.
5.  **Análises de IA:** Dentro do loop, para cada unidade:
    - A **Análise de Comportamento (Tabela 5)** é executada sobre as contas dos projetos exclusivos da unidade.
    - A **Detecção de Ocorrências Atípicas (Tabela 4)** é executada sobre os dados dos projetos exclusivos.
6.  **Agregação:** As tabelas de Execução Orçamentária (com Score de Criticidade), Desempenho Mensal (com Sinalização da IA) e Top 5 Fornecedores são geradas.
7.  **Comunicação:** O `comunicacao/email.py` recebe todos os DataFrames e resumos, renderiza o template `relatorio_analise.html` com os dados, gera um `.csv` com a base de despesas da unidade e envia o e-mail final com o anexo.

## 4. Estrutura do Projeto

```
/analise-despesas
|-- /analise_despesa
|   |-- /analise
|   |   |-- agregacao.py
|   |   |-- insights_ia.py
|   |   |-- __init__.py
|   |-- /comunicacao
|   |   |-- email.py
|   |   |-- __init__.py
|   |-- /processamento
|   |   |-- enriquecimento.py
|   |   |-- __init__.py
|   |-- /templates
|   |   |-- relatorio_analise.html
|   |-- config.py
|   |-- database.py
|   |-- extracao.py
|   |-- logging_config.py
|   |-- utils.py
|   |-- __init__.py
|-- /logs
|-- /output
|-- /sql
|   |-- extracao_realizado.sql
|   |-- extracao_orcamento.sql
|-- .env
|-- .env.example
|-- .gitignore
|-- main.py
|-- requirements.txt
|-- README.md
```

## 5. Setup e Instalação

#### Pré-requisitos
- Python 3.9+
- Acesso à rede para os bancos de dados SQL Server.
- Drivers ODBC para SQL Server instalados na máquina de execução.

#### Passos para Instalação
1.  Clone este repositório:
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd analise-despesas
    ```

2.  Crie e ative um ambiente virtual:
    ```bash
    python -m venv .venv
    # No Windows
    .venv\Scripts\activate
    # No macOS/Linux
    source .venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure as variáveis de ambiente. Copie o arquivo de exemplo:
    ```bash
    copy .env.example .env
    ```
    Agora, edite o arquivo `.env` e preencha com as credenciais corretas do seu banco de dados e servidor SMTP.

## 6. Como Usar

Para executar o robô, basta rodar o script `main.py` a partir da raiz do projeto:
```bash
python main.py
```
O robô iniciará o processo e os logs serão exibidos no console e salvos no diretório `/logs`. Os relatórios em `.csv` serão salvos em `/output`.

## 7. Customização

A maior parte da customização pode ser feita diretamente no arquivo `config.py`, sem necessidade de alterar o código principal:
- **`MES_ANALISE_SOBRESCRITA`**: Defina um número de 1 a 12 para analisar um mês específico, ou `None` para usar o mês mais recente.
- **`MAPA_GESTORES`**: Adicione ou remova gestores e seus respectivos e-mails.
- **`PROJETOS_A_IGNORAR_ANOMALIAS`** e **`PROJETOS_FOLHA_PAGAMENTO`**: Ajuste as listas de projetos para refinar o escopo das análises.
