import sqlite3
import hashlib
import io
import unicodedata
import re
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).parent.parent
DB_DIR = ROOT_DIR / "data"
DB_PATH = DB_DIR / "clinica.db"
DB_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(str(DB_PATH))
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        idade INTEGER,
        telefone TEXT,
        data_criacao TEXT,
        data_modificacao TEXT,
        ativo BOOLEAN DEFAULT 1,
        chave_controle TEXT NOT NULL UNIQUE
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS atendimentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER,
        data_atendimento DATE,
        data_criacao,
        compareceu BOOLEAN,
        valor REAL,
        FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
    )
''')
conn.commit()

def gerar_chave_unica(nome, telefone):
                    string_base = f"{nome.strip().lower()}{telefone.strip()}"

                    return hashlib.sha256(string_base.encode()).hexdigest()


st.set_page_config(
    page_title="Psi Gestão",
    layout="wide", 
)

st.sidebar.title("Gestão de Atendimentos")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação", 
    ["Home","Cadastro de Pacientes", "Registrar Atendimento", "Relatórios", "Dashboard Financeiro"]
)

if menu == "Home" or menu == "Início": 
    st.title("Bem-vindo(a)")
    st.write("Este sistema foi desenvolvido para facilitar o controle dos seus pacientes e automatizar a gestão financeira dos seus atendimentos.")
    
    st.divider()
    
    st.header("📌 Como usar o sistema?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1️⃣ Cadastro")
        st.markdown("""
        **Gerencie seus pacientes:**
        - **Novo Cadastro:** Adicione novos pacientes informando nome, idade e telefone.
        - **Atualizar Status:** Se um paciente receber alta ou interromper o tratamento, inative-o. Isso limpa sua lista na hora de registrar os atendimentos.
        """)

    with col2:
        st.subheader("2️⃣ Atendimento")
        st.markdown("""
        **Registre o dia a dia:**
        - Selecione um paciente ativo e a data da sessão.
        - Informe o valor e o status da consulta (Realizado, Faltou Cobrado, ou Faltou Não Cobrado).
        - *Nota: Faltas não cobradas são ignoradas no faturamento.*
        """)
        
    with col3:
        st.subheader("3️⃣ Relatórios")
        st.markdown("""
        **Acompanhe suas finanças:**
        - Analise os ganhos dos últimos 30 dias ou o histórico mensal.
        - Veja o total cobrado por cada paciente.
        - Exporte qualquer visão para **Excel (.xlsx)** com um único clique.
        """)
        
    st.divider()
    
elif menu == "Cadastro de Pacientes":
    st.header("Gestão de Pacientes")
    
    tab_novo, tab_atualizar = st.tabs(["Novo Cadastro", "Atualizar Status"])
    
    with tab_novo:
        with st.form("form_paciente", clear_on_submit=True):
            st.subheader("Cadastrar Novo Paciente")
            nome = st.text_input("Nome Completo *", placeholder="José da Silva Santos", key="novo_nome")
            
            col1, col2 = st.columns(2)
            with col1:
                idade = st.number_input("Idade", value=None, step=1, placeholder="18", key="novo_idade")
            with col2:
                telefone = st.number_input("Telefone (Apenas números)", value=None, step=1, placeholder="11999999999", key="novo_tel")
                telefone = str(telefone)
                
            ativo = st.checkbox("Paciente Ativo?", value=True, help="Desmarque se o paciente teve alta ou parou as sessões.", key="novo_ativo")
            
            submit_paciente = st.form_submit_button("Salvar Paciente")
            
            if submit_paciente:
                if nome.strip() == "":
                    st.error("O nome do paciente é obrigatório!")
                elif telefone == "None":
                    st.error("O telefone do paciente é obrigatório!")
                elif len(telefone) < 8 or len(telefone) > 12:
                    st.error(f"O telefone possui tamanho inválido. Possui {len(telefone)} dígito(s)")
                elif idade is not None and len(str(idade)) > 2:
                    st.error(f"Idade possui tamanho inválido: {len(str(idade))} dígito(s)")
                else:
                    nome = nome.title().strip()
                    today = str(datetime.now())
                    chave = gerar_chave_unica(nome, telefone)

                    try:
                        c.execute("INSERT INTO pacientes (nome, idade, telefone, data_criacao, data_modificacao, ativo, chave_controle) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  (nome, idade, telefone, today, today, ativo, chave))
                        conn.commit()
                        st.success(f"Paciente **{nome}** cadastrado com sucesso!")
                        
                    except sqlite3.IntegrityError:
                        st.error(f"**Cadastro Recusado:** Já existe um paciente cadastrado com esses dados.")
                        st.warning("Verifique se o nome e telefone estão corretos ou se o paciente já está na lista.")
                    except Exception as e:
                        st.error(f"Ocorreu um erro inesperado ao salvar: {e}")

    with tab_atualizar:
        with st.form("form_atualiza_paciente", clear_on_submit=True):
            st.subheader("Atualizar Ativação do Paciente")
            st.info("Digite o Nome e Telefone exatos usados no cadastro para localizar o paciente.")
            
            # Campos para buscar e gerar o hash
            nome_upd = st.text_input("Nome Completo Cadastrado *", placeholder="José da Silva Santos", key="upd_nome")
            telefone_upd = st.number_input("Telefone Cadastrado *", value=None, step=1, placeholder="11999999999", key="upd_tel")
            telefone_upd = str(telefone_upd)
            
            # O único campo que será alterado no banco
            ativo_upd = st.checkbox("Paciente Ativo?", value=True, help="Marque/Desmarque para alterar o status no sistema.", key="upd_ativo")
            
            submit_atualiza = st.form_submit_button("Atualizar Status")
            
            if submit_atualiza:
                if nome_upd.strip() == "":
                    st.error("O nome é obrigatório para localizar o paciente!")
                elif telefone_upd == "None":
                    st.error("O telefone é obrigatório para localizar o paciente!")
                else:
                    nome_upd = nome_upd.title().strip()
                    chave_busca = gerar_chave_unica(nome_upd, telefone_upd)
                    today_upd = str(datetime.now())

                    try:
                        c.execute("""
                            UPDATE pacientes 
                            SET ativo = ?, data_modificacao = ? 
                            WHERE chave_controle = ?
                        """, (ativo_upd, today_upd, chave_busca))
                        
                        # Verifica se alguma linha foi realmente alterada
                        if c.rowcount == 0:
                            st.error("**Paciente não encontrado!**")
                            st.warning("Nenhum paciente com esse Nome e Telefone foi localizado no banco de dados. Verifique a digitação.")
                        else:
                            conn.commit()
                            status_txt = "ATIVADO" if ativo_upd else "DESATIVADO"
                            st.success(f"Status do paciente **{nome_upd}** foi atualizado para **{status_txt}** com sucesso!")
                            
                    except Exception as e:
                        st.error(f"Ocorreu um erro inesperado ao atualizar: {e}")

elif menu == "Registrar Atendimento":
    st.header("Registrar Atendimento e Valor")
    
    # Traz apenas pacientes ATIVOS (ativo = 1)
    df_ativos = pd.read_sql_query("SELECT id, nome, telefone FROM pacientes WHERE ativo = 1 and telefone is Not Null", conn)
    
    if df_ativos.empty:
        st.warning("Nenhum paciente ATIVO encontrado. Verifique o cadastro.")
    else:
        with st.form("form_atendimento", clear_on_submit=True):
            
            def formata_paciente(id_pac):
                linha = df_ativos[df_ativos['id'] == id_pac].iloc[0]
                return f"{linha['nome']} - {linha['telefone']}"


            paciente_id_selecionado = st.selectbox(
                "Paciente (Apenas Ativos)", 
                options=df_ativos['id'].tolist(), 
                format_func=formata_paciente,
                index=None,
                placeholder="Selecione um paciente"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                data_atendimento = st.date_input("Data do Atendimento")
            with col2:
                valor = st.number_input("Valor Cobrado (R$)", placeholder="0,00", value = None, step=10.0)
            
            compareceu = st.radio("Status do Atendimento", ["Realizado", "Faltou (Cobrado)", "Faltou (Não Cobrado)"])
        
            submit_atendimento = st.form_submit_button("Salvar Registro")
            
            if submit_atendimento:
                paciente_id = int(paciente_id_selecionado)
                teve_atendimento = 1 if "Não Cobrado" not in compareceu else 0
                valor_final = valor if teve_atendimento == 1 else 0.0
                
                today = str(datetime.now())

                c.execute("INSERT INTO atendimentos (paciente_id, data_atendimento, data_criacao, compareceu, valor) VALUES (?, ?, ?, ?, ?)",
                          (paciente_id, data_atendimento, today, teve_atendimento, valor_final))
                conn.commit()
                st.success("Atendimento registrado no fluxo de caixa!")

elif menu == "Relatórios":
    st.header("Ganhos Recentes")

    report = st.selectbox(
        "Tipo Relatório", 
        ["Por Paciente", "Últimos 30 dias", "Total por Mês", "Meus Pacientes"],
        index=None,
        placeholder="Selecione uma Opção"
    )

    if report:
        if report == 'Por Paciente':
            query = """
                SELECT 
                    TRIM(pa.nome) as `Nome Paciente`, 
                    SUM(at.valor) as `Total Cobrado (R$)`, 
                    MAX(at.data_atendimento) as `Último Atendimento`
                FROM atendimentos at 
                LEFT JOIN pacientes pa ON pa.id = at.paciente_id 
                WHERE at.compareceu = 1
                GROUP BY pa.nome
            """
        elif report == "Últimos 30 dias":
            query = """
                SELECT 
                    DATE(data_atendimento) AS `Dia`,
                    SUM(valor) AS `Total Recebido (R$)`,
                    COUNT(*) AS `Quantidade Atendimentos`
                FROM atendimentos
                WHERE data_atendimento >= DATE('now', '-30 days') and compareceu = 1
                GROUP BY dia
                ORDER BY dia ASC
            """
        elif report == "Total por Mês":
            query = """
                SELECT 
                    strftime('%Y-%m', data_atendimento) AS `Mês`,
                    SUM(valor) AS `Faturamento Mensal`,
                    COUNT(*) AS `Total Atendimentos`
                FROM atendimentos
                WHERE compareceu = 1
                GROUP BY `Mês`
                ORDER BY `Mês` DESC
            """
        elif  "Meus Pacientes":
            query = """
                SELECT 
                    nome as Nome, 
                    idade as Idade, 
                    telefone as Telefone, 
                    CASE
                        WHEN ativo = 1 THEN 'Sim'
                        ELSE 'Não'
                    END AS `Status Paciente`
                FROM pacientes"""


        df = pd.read_sql_query(query, conn)

        col1, col2 = st.columns(2)

        with col1:
            show_report = st.button("Exibir Relatório", use_container_width=True)
        
        with col2:
            if not df.empty:

                def preparar_nome_arquivo(txt):
                    txt = unicodedata.normalize('NFD', txt.strip())
                    txt = re.sub(r'[\u0300-\u036f]', '', txt)
                    return txt.lower().replace(" ", "_")

                def converter_para_excel(df_input):
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df_input.to_excel(writer, index=False, sheet_name='Relatorio')
                    return output.getvalue()

                dados_excel = converter_para_excel(df)

                st.download_button(
                    label="Baixar Relatório",
                    data=dados_excel,
                    file_name=f'{preparar_nome_arquivo(report)}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True
                )
            else:
                st.button("Baixar Relatório", disabled=True, use_container_width=True)

        if show_report:
            if not df.empty:
                st.success(f"Relatório **{report}** gerado!")
                st.dataframe(df, hide_index=True, use_container_width=True)
            else:
                st.info("Nenhum dado encontrado para este período.")


elif menu == "Dashboard Financeiro":
    st.header("Dashboard Financeiro")
    
    # --- Executando a Query 1: Últimos 30 Dias ---
    query_diario = """
        SELECT 
            DATE(data_atendimento) AS `Dia`,
            SUM(valor) AS `Total Recebido (R$)`,
            COUNT(*) AS `Quantidade Atendimentos`
        FROM atendimentos
        WHERE data_atendimento >= DATE('now', '-30 days') AND compareceu = 1
        GROUP BY Dia
        ORDER BY Dia ASC
    """
    df_diario = pd.read_sql_query(query_diario, conn)

    # --- Executando a Query 2: Mensal ---
    query_mensal = """
        SELECT 
            strftime('%Y-%m', data_atendimento) AS `Mês`,
            SUM(valor) AS `Faturamento Mensal`,
            COUNT(*) AS `Total Atendimentos`
        FROM atendimentos
        WHERE compareceu = 1
        GROUP BY `Mês`
        ORDER BY `Mês` DESC
    """
    df_mensal = pd.read_sql_query(query_mensal, conn)

    # --- Tratamento caso o banco esteja vazio ---
    if df_mensal.empty and df_diario.empty:
        st.info("Nenhum dado financeiro registrado ainda. Comece a registrar atendimentos para gerar gráficos!")
    else:
        # 1. KPIs no topo da página
        st.subheader("Resumo de Ganhos")
        kpi1, kpi2 = st.columns(2)
        
        if not df_diario.empty:
            total_30d = df_diario['Total Recebido (R$)'].sum()
            atendimentos_30d = df_diario['Quantidade Atendimentos'].sum()
            kpi1.metric(label="Faturamento (Últimos 30 dias)", value=f"R$ {total_30d:.2f}", delta=f"{atendimentos_30d} sessões", delta_color="normal")
        
        if not df_mensal.empty:
            mes_atual = df_mensal.iloc[0]['Mês']
            fat_atual = df_mensal.iloc[0]['Faturamento Mensal']
            atend_atual = df_mensal.iloc[0]['Total Atendimentos']
            kpi2.metric(label=f"Faturamento (Mês Atual: {mes_atual})", value=f"R$ {fat_atual:.2f}", delta=f"{atend_atual} sessões", delta_color="normal")

        st.markdown("---")

        # 2. Renderizando os Gráficos
        st.subheader("Análise Visual")
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown("**Fluxo Diário (Últimos 30 Dias)**")
            if not df_diario.empty:
                # Gráfico de Área com Plotly
                fig_diario = px.area(
                    df_diario, 
                    x='Dia', 
                    y='Total Recebido (R$)',
                    hover_data=['Quantidade Atendimentos'], # Detalhe legal: mostra a qtd de sessões ao passar o mouse
                    markers=True,
                    color_discrete_sequence=['#0083B8']
                )
                fig_diario.update_layout(xaxis_title=None, yaxis_title="R$", margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_diario, use_container_width=True)
            else:
                st.warning("Sem ganhos nos últimos 30 dias.")

        with col_graf2:
            st.markdown("**Comparativo Mensal**")
            if not df_mensal.empty:
                # O Pandas pegou os dados em ordem DESC do SQL, vamos inverter para o gráfico ir do mês mais antigo para o mais novo (da esquerda pra direita)
                df_mensal_grafico = df_mensal.sort_values(by='Mês', ascending=True)
                
                # Gráfico de Barras com Plotly
                fig_mensal = px.bar(
                    df_mensal_grafico, 
                    x='Mês', 
                    y='Faturamento Mensal',
                    hover_data=['Total Atendimentos'],
                    text_auto='.2s', 
                    color_discrete_sequence=['#17A2B8']
                )
                fig_mensal.update_xaxes(type='category') 
                fig_mensal.update_layout(xaxis_title=None, yaxis_title="R$", margin=dict(l=0, r=0, t=10, b=0))
                fig_mensal.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                st.plotly_chart(fig_mensal, use_container_width=True)