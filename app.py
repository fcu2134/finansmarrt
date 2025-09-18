from flask import Flask, render_template, redirect, url_for, flash, request
from extensiones import db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from formularios import FormularioRegistro, FormularioInicioSesion, FormularioCategoria, FormularioTransaccion
from modelos import Transaccion, Categoria, Usuario
from datetime import datetime
import numpy as np  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/finansmart'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secreto2'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ================================
#  paggina USUARIOS pe 
# ================================
@login_manager.user_loader
def cargar_usuario(usuario_id):
    return db.session.get(Usuario, int(usuario_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    formulario = FormularioRegistro()
    if formulario.validate_on_submit():
        existente = Usuario.query.filter(
            (Usuario.nombre_usuario == formulario.nombre_usuario.data) |
            (Usuario.correo == formulario.correo.data)
        ).first()
        if existente:
            flash('El nombre de usuario o correo ya está registrado.', 'error')
            return render_template('registro.html', formulario=formulario)

        clave_encriptada = generate_password_hash(formulario.contrasena.data)
        nuevo_usuario = Usuario(
            nombre_usuario=formulario.nombre_usuario.data,
            correo=formulario.correo.data,
            contrasena=clave_encriptada
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html', formulario=formulario)

@app.route('/login', methods=['GET', 'POST'])
def login():
    formulario = FormularioInicioSesion()
    if formulario.validate_on_submit():
        usuario = Usuario.query.filter_by(correo=formulario.correo.data).first()
        if usuario and check_password_hash(usuario.contrasena, formulario.contrasena.data):
            login_user(usuario)
            return redirect(url_for('panel'))
        flash('Correo o contraseña incorrectos.', 'error')
    return render_template('login.html', formulario=formulario)

@app.route('/cerrar_sesion')
@login_required
def cerrar_sesion():
    logout_user()
    return redirect(url_for('login'))

# ================================
# PANEL PRINCIPAL
# ================================
@app.route('/panel')
@login_required
def panel():
    transacciones = Transaccion.query.filter_by(usuario_id=current_user.id).all()
    ingresos = int(sum(t.monto for t in transacciones if t.tipo == 'Ingreso'))
    egresos = int(sum(t.monto for t in transacciones if t.tipo == 'Egreso'))
    saldo = ingresos - egresos

    # esto es pa los graficos 
    from collections import defaultdict
    categorias_gasto = defaultdict(float)
    for t in transacciones:
        if t.tipo == 'Egreso' and t.categoria:
            categorias_gasto[t.categoria.nombre] += t.monto
    labels = list(categorias_gasto.keys())
    values = list(categorias_gasto.values())

    # esto predice para el siguiente mes 
    gastos_por_mes = defaultdict(float)
    for t in transacciones:
        if t.tipo == 'Egreso':
            mes = t.fecha.strftime("%Y-%m")
            gastos_por_mes[mes] += t.monto

    prediccion = None
    alerta = None
    if len(gastos_por_mes) >= 2:
        meses_sorted = sorted(gastos_por_mes.keys())
        gastos_mensuales = np.array([gastos_por_mes[m] for m in meses_sorted])
        prediccion = int(np.mean(gastos_mensuales))

        # esto basicamente alertas si ya paso el promedio pa predecir 
        mes_actual = datetime.now().strftime("%Y-%m")
        gasto_actual_mes = gastos_por_mes.get(mes_actual, 0)
        if gasto_actual_mes > prediccion * 1.5:
            alerta = f"¡Cuidado! Este mes has gastado ${gasto_actual_mes}, que es mayor al promedio histórico."

    return render_template(
        'panel.html',
        ingresos=ingresos,
        egresos=egresos,
        saldo=saldo,
        labels=labels,
        values=values,
        prediccion=prediccion,
        alerta=alerta
    )

# ================================
# TRANSACCIONES pe 
# ================================
@app.route('/transacciones')
@login_required
def listar_transacciones():
    transacciones = Transaccion.query.filter_by(usuario_id=current_user.id).all()
    return render_template('transacciones.html', transacciones=transacciones)

@app.route('/agregar_transaccion', methods=['GET', 'POST'])
@login_required
def agregar_transaccion():
    formulario = FormularioTransaccion()
    formulario.categoria.choices = [(c.id, c.nombre) for c in Categoria.query.filter_by(usuario_id=current_user.id).all()]

    
    if formulario.descripcion.data:
        desc = formulario.descripcion.data.lower()
        if "uber" in desc:
            auto = Categoria.query.filter_by(nombre="Transporte", usuario_id=current_user.id).first()
            if auto:
                formulario.categoria.data = auto.id
        elif "super" in desc or "mercado" in desc:
            auto = Categoria.query.filter_by(nombre="Comida", usuario_id=current_user.id).first()
            if auto:
                formulario.categoria.data = auto.id

    if formulario.validate_on_submit():
        nueva = Transaccion(
            monto=formulario.monto.data,
            tipo=formulario.tipo.data,
            categoria_id=formulario.categoria.data,
            fecha=formulario.fecha.data,
            descripcion=formulario.descripcion.data,
            usuario_id=current_user.id
        )
        db.session.add(nueva)
        db.session.commit()
        flash('Transacción agregada con éxito', 'success')
        return redirect(url_for('panel'))

    return render_template('agregar_transaccion.html', form=formulario)

@app.route('/transacciones/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_transaccion(id):
    transaccion = Transaccion.query.get_or_404(id)
    if transaccion.usuario_id != current_user.id:
        flash("No tienes permiso para editar esta transacción.", "error")
        return redirect(url_for('panel'))

    form = FormularioTransaccion(obj=transaccion)
    form.categoria.choices = [(c.id, c.nombre) for c in Categoria.query.filter_by(usuario_id=current_user.id).all()]

    if form.validate_on_submit():
        transaccion.monto = form.monto.data
        transaccion.tipo = form.tipo.data
        transaccion.categoria_id = form.categoria.data
        transaccion.fecha = form.fecha.data
        transaccion.descripcion = form.descripcion.data
        db.session.commit()
        flash("Transacción actualizada.", "success")
        return redirect(url_for('listar_transacciones'))

    return render_template('editar_transaccion.html', form=form)

@app.route('/transacciones/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_transaccion(id):
    transaccion = Transaccion.query.get_or_404(id)
    if transaccion.usuario_id != current_user.id:
        flash("No tienes permiso para eliminar esta transacción.", "error")
        return redirect(url_for('listar_transacciones'))

    db.session.delete(transaccion)
    db.session.commit()
    flash("Transacción eliminada.", "success")
    return redirect(url_for('listar_transacciones'))

# ================================
# CATEGORÍAS pe
# ================================
@app.route('/categorias', methods=['GET', 'POST'])
@login_required
def categorias():
    form = FormularioCategoria()
    categorias = Categoria.query.filter_by(usuario_id=current_user.id).all()

    if form.validate_on_submit():
        existe = Categoria.query.filter_by(usuario_id=current_user.id, nombre=form.nombre.data).first()
        if existe:
            flash("Esa categoría ya existe.", "error")
            return redirect(url_for('categorias'))

        nueva = Categoria(nombre=form.nombre.data, usuario_id=current_user.id)
        db.session.add(nueva)
        db.session.commit()
        flash('Categoría agregada.', 'success')
        return redirect(url_for('categorias'))

    return render_template('categorias.html', form=form, categorias=categorias)

@app.route('/categorias/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    if categoria.usuario_id != current_user.id:
        flash("No tienes permiso para editar esta categoría.", "error")
        return redirect(url_for('categorias'))

    form = FormularioCategoria(obj=categoria)
    if form.validate_on_submit():
        categoria.nombre = form.nombre.data
        db.session.commit()
        flash("Categoría actualizada.", "success")
        return redirect(url_for('categorias'))

    return render_template('editar_categoria.html', form=form)

@app.route('/categorias/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    if categoria.usuario_id != current_user.id:
        flash("No tienes permiso para eliminar esta categoría.", "error")
        return redirect(url_for('categorias'))

    if categoria.transacciones:
        flash("No puedes eliminar una categoría con transacciones asociadas.", "error")
        return redirect(url_for('categorias'))

    db.session.delete(categoria)
    db.session.commit()
    flash("Categoría eliminada.", "success")
    return redirect(url_for('categorias'))

# ================================
# arranque de motores !
# ================================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
