# Psi Gestão de Atendimento 

O **Psi Gestão de Atendimento** é uma aplicação desenvolvida para psicólogos que buscam ter maior controle sobre seus atendimentos e faturamento. Todos os dados são armazenados localmente em um banco de dados relacional (SQLite).


## Funcionalidades

* **Gestão de Pacientes:** Cadastro completo com controle de status (Ativo/Inativo).
* **Integridade de Dados:** Implementação de **Hash SHA-256** para gerar chaves únicas e evitar duplicidade de cadastros.
* **Fluxo de Atendimento:** Registro de sessões com distinção entre faltas cobradas e não cobradas.
* **Relatórios Dinâmicos:** Filtros por paciente, mensal e histórico com visualização em tabelas.
* **Dashboard Financeiro:** Visualização de KPIs (faturamento dos últimos 30 dias e mês atual) e gráficos interativos de tendência e comparação mensal.
* **Exportação de Dados:** Motor de exportação para **Excel (.xlsx)** com tratamento de caracteres especiais e nomes de arquivos dinâmicos.

## Ferramentas e Tecnologias

* **Linguagem:** Python 3.13
* **Interface:** Streamlit
* **Banco de Dados:** SQLite (SQL nativo)
* **Processamento de Dados:** Pandas
* **Visualização:** Plotly Express
* **Exportação:** Openpyxl

---

## Configuração do Ambiente

Siga os passos abaixo para configurar o ambiente de desenvolvimento usando `venv`.

### 1. Requisitos
* Python 3.13 instalado.

### 2. Configurar o Ambiente Virtual
No terminal, dentro da pasta do projeto:

```bash
# Criar o ambiente virtual
python -m venv .venv

# Ativar o ambiente virtual
# No Windows:
.venv\Scripts\activate
# No Linux/Mac:
source .venv/bin/activate

# Com o ambiente virtual ativado, instale todas as bibliotecas necessárias de uma só vez:

pip install -r requirements.txt
```

### 3. Como executar o projeto
No terminal, dentro da pasta do projeto:

```bash
streamlit run src/main.py
```

### 4. Estrutura das pastas

```bash
PsiGestao/
├── .venv/                     # Ambiente virtual (isolamento de pacotes)
├── data/                      # Banco de dados SQLite (clinica.db)
├── src/
│   └── main.py                 # Script principal da aplicação
├── iniciar_atendimento.bat    # Arquivo bat para inicializar a execução
├── Iniciar.vbs                # Arquivo vbs para chamar o .bat sem terminal
├── requirements.txt           # Lista de dependências do projeto
└── README.md                  # Documentação e guia de uso
```