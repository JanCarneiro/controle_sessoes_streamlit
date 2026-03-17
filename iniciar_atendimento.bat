@echo off
echo Iniciando o Sistema de Gestao...
call .venv\Scripts\activate
streamlit run src/main.py
pause