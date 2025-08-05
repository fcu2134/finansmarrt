
 ===========================
finansmart- FLASK-python
===========================

este documento explica como ejecutar el proyecto y si deseas cambiar de ordenador igualmente .v

----------------------------------
1 Requisitos del sistema
----------------------------------
- Python 3.11 (u otra versión compatible)
- pip instalado
-  instalar dependencias
----------------------------------
2 Tecnologias usadas
----------------------------------
-python
-html
-css
-javascript
-framework flask(libreria de python)

----------------------------------
3 Preparar el entorno virtual
----------------------------------
Abre una terminal (CMD, PowerShell o Terminal) dentro de la carpeta del proyecto y ejecuta:

    python -m venv venv

Esto creará un entorno virtual llamado "venv".

----------------------------------
4 Activar el entorno virtual
----------------------------------
- En Windows:

    .\venv\Scripts\activate


----------------------------------
5 Instalar dependencias
----------------------------------
Con el entorno virtual activado, ejecuta:

    pip install -r requirements.txt

Esto instalará Flask y todas las librerías necesarias.

----------------------------------
6 Ejecutar la aplicación 
----------------------------------
Una vez activado el entorno virtual y con dependencias instaladas:

    python app.py


----------------------------------
📌 Nota:
- debes eliminar la carpeta venv si fuese el caso de que este , eso es para que no genere nigun problema .


o bien ejecutar el setup,bat

 ❌si te sale esto NO haces ❌ 
[notice] A new release of pip is available: 24.0 -> 25.1.1
[notice] To update, run: python.exe -m pip install --upgrade pip

----------------------------------

funcionamiento del proyecto

----------------------------------

-basicamente es un gestor de finanzas donde el usuario podra agregar ingresos e egresos que va consumiendo y generando , separandolo por categorias(categoriza en un grupo lo que pertenece cada ingreso e egreso),transacciones(donde puede agregar los gastos y ingresos que reciba o haga)
editar lo que es el tema de transaccion y categoria , mostrar cada egreso del mes en grafico 

--------
extra  
-------
si te da error el tema del bat o la instalacion del requeriments , prueba en la cmd nomral y cuando estes en la cmd, poner cd y la ruta del proyecto,
una ves dentro creas el entorno virtual con: python -m venv venv   una vez hecho deberia salirte la carpeta , si te sale prueba el activate (\venv\Scripts\activate)
si no funciona entonces venv\Scripts\activate.bat .
si te sale (venv) C:\Users\ entonces ahi instalas los requerimientos 
