# Projeto Análise de Despesas

Este projeto é uma aplicação em Python para extrair, processar e analisar dados de despesas a partir de bancos de dados corporativos (SQL Server). Ele foi estruturado de forma modular para facilitar a manutenção e a escalabilidade.

## Funcionalidades Principais

-   **Extração de Dados:** Conecta-se a diferentes fontes de dados (SQL Server, Azure, etc.) usando configurações centralizadas.
-   **Gerenciamento de Queries:** As consultas SQL são armazenadas em arquivos `.sql` separados, facilitando sua edição e manutenção.
-   **Modularidade:** O código é dividido em módulos com responsabilidades únicas (conexão, execução, extração, etc.).
-   **Logging:** Registra informações e erros durante a execução para facilitar a depuração.

## Estrutura do Projeto

```
analise-despesas/
│
├── sql/                    # Armazena os arquivos com as queries SQL.
│   └── bd.sql
│
├── analise_despesa/        # Pacote principal com toda a lógica da aplicação.
│   ├── config.py           # Dicionário com as configurações de conexão.
│   ├── database.py         # Funções para criar conexões e salvar dados.
│   ├── queries.py          # Mapeia nomes de queries aos arquivos SQL e conexões.
│   ├── query_executor.py   # Classe que executa a query e retorna um DataFrame.
│   ├── extracao.py         # Orquestra o processo de extração de dados.
│   └── main.py             # Função principal que define o fluxo da análise.
│
├── .gitignore              # Arquivos e pastas a serem ignorados pelo Git.
├── main.py                 # Ponto de entrada para executar o projeto.
├── README.md               # Esta documentação.
└── requirements.txt        # Lista de dependências Python do projeto.
```

## Pré-requisitos

-   Python 3.9+
-   Git
-   ODBC Driver for SQL Server

## Instalação

Siga os passos abaixo para configurar o ambiente de desenvolvimento local.

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd analise-despesas
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Cria o ambiente virtual na pasta .venv
    python -m venv .venv
    ```
    -   **No Windows:**
        ```powershell
        .\.venv\Scripts\Activate.ps1
        ```
    -   **No Linux ou macOS:**
        ```bash
        source .venv/bin/activate
        ```

3.  **Instale as dependências:**
    Com o ambiente virtual ativado, instale todas as bibliotecas necessárias a partir do `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## Configuração

Antes de executar, verifique o arquivo `analise_despesa/config.py`. Assegure-se de que as credenciais e os detalhes dos servidores (`servidor`, `banco`, etc.) estão corretos para o seu ambiente.

**⚠️ Atenção:** Nunca submeta senhas ou informações sensíveis diretamente no código para o repositório Git. Considere o uso de variáveis de ambiente para um ambiente de produção.

## Como Usar

Para executar a análise completa, basta rodar o `main.py` a partir da pasta raiz do projeto:

```bash
python main.py
```

O script irá iniciar, conectar-se ao banco de dados, executar a query definida e exibir os logs do processo no terminal.
