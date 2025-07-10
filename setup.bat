@echo off
echo ============================
echo Iniciando configuración virus incoming...
echo ============================

python -m venv venv
call venv\Scripts\activate

echo Instalando requerimientos...
pip install -r requirements.txt

echo ============================
echo Proyecto configurado mi kiing ✅
echo Ejecuta: 
echo     venv\Scripts\activate
echo     python app.py
echo ============================
pause
