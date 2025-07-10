

from flask import Flask, render_template, redirect, url_for, flash, request
from extensiones import db
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from formularios import FormularioRegistro, FormularioInicioSesion, FormularioCategoria, FormularioTransaccion
from modelos import Transaccion, Categoria, Usuario
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/finansmart'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secreto2'

db.init_app(app)
from modelos import Usuario, Categoria, Transaccion
#esto crea una instancaidel manejador de sesiones del usuario ,conecta con la aplicacion flask,y define la vista que se mostrara primero
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
#define una funcion para cargar un usuario desde la sesion
@login_manager.user_loader
#recibe lo que es la funcion guardado para soltar el objeto usuario que corresponde ese id
def cargar_usuario(usuario_id):
      return db.session.get(Usuario, int(usuario_id))


#metodo para generar el registro del usuario y si existe te suelta un error 
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    formulario = FormularioRegistro()
    if formulario.validate_on_submit():
        existente = Usuario.query.filter(
            (Usuario.nombre_usuario == formulario.nombre_usuario.data) | (Usuario.correo == formulario.correo.data)
        ).first()
        if existente:
            flash('El nombre de usuario o correo ya está registrado.')
            return render_template('registro.html', formulario=formulario)
        #esto encripta lo que es la contraseña 
        clave_encriptada = generate_password_hash(formulario.contrasena.data)
        nuevo_usuario = Usuario(nombre_usuario=formulario.nombre_usuario.data, correo=formulario.correo.data, contrasena=clave_encriptada)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.')
        return redirect(url_for('login'))
    return render_template('registro.html', formulario=formulario)
#esto es el metodo pal login donde flitramos por corroe y contraseña para verificar si existe 
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

#esto es el inicio donde se muestra los datos que vallamos creando mas el grafico(falta arreglar eso xd)
@app.route('/panel')
@login_required
def panel():
    transacciones = Transaccion.query.filter_by(usuario_id=current_user.id).all()
    ingresos = sum(t.monto for t in transacciones if t.tipo == 'Ingreso')
    egresos = sum(t.monto for t in transacciones if t.tipo == 'Egreso')
    saldo = ingresos - egresos

    from collections import defaultdict
    categorias_gasto = defaultdict(float)

    for t in transacciones:
        if t.tipo == 'Egreso' and t.categoria:
            categorias_gasto[t.categoria.nombre] += t.monto

    etiquetas = list(categorias_gasto.keys())
    valores = list(categorias_gasto.values())

    return render_template('panel.html', ingresos=ingresos, egresos=egresos, saldo=saldo, etiquetas=etiquetas, valores=valores)
#esto muestra la lista de transacciones 
@app.route('/transacciones')
@login_required
def listar_transacciones():
    print("Entró a listar_transacciones")
    transacciones = Transaccion.query.filter_by(usuario_id=current_user.id).all()
    print(f"Cantidad transacciones: {len(transacciones)}")
    return render_template('transacciones.html', transacciones=transacciones)


#metodo para agregar lo que es la transaccion 
@app.route('/agregar_transaccion', methods=['GET', 'POST'])
@login_required
def agregar_transaccion():
    formulario = FormularioTransaccion()
    formulario.categoria.choices = [(c.id, c.nombre) for c in Categoria.query.filter_by(usuario_id=current_user.id).all()]

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
        flash('Transacción agregada con éxito')
        return redirect(url_for('panel'))

    return render_template('agregar_transaccion.html', form=formulario)
#metodo de  las categoria :V
@app.route('/categorias', methods=['GET', 'POST'])
@login_required
def categorias():
    form = FormularioCategoria()
        #filtramos la categorias por el id del usuaario 
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


#metodo paara editar las categoria por id :V
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
#metodo pa eliminar las categoria por id :V
@app.route('/categorias/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    if categoria.usuario_id != current_user.id:
        flash("No tienes permiso para eliminar esta categoría.")
        return redirect(url_for('categorias'))

    if categoria.transacciones:
        flash("No puedes eliminar una categoría con transacciones asociadas.")
        return redirect(url_for('categorias'))

    db.session.delete(categoria)
    db.session.commit()
    flash("Categoría eliminada.")
    return redirect(url_for('categorias'))

@app.route('/transacciones/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_transaccion(id):
    transaccion = Transaccion.query.get_or_404(id)
    if transaccion.usuario_id != current_user.id:
        flash("No tienes permiso para editar esta transacción.", "error")
        return redirect(url_for('panel'))

    form = FormularioTransaccion(obj=transaccion)
    # cargamos la categoria pal usuario en el selectt
    form.categoria.choices = [(c.id, c.nombre) for c in Categoria.query.filter_by(usuario_id=current_user.id).all()]

    if form.validate_on_submit():
        transaccion.monto = form.monto.data
        transaccion.tipo = form.tipo.data
        transaccion.categoria_id = form.categoria.data
        transaccion.fecha = form.fecha.data
        transaccion.descripcion = form.descripcion.data
        db.session.commit()
        flash("Transacción actualizada.", "success")
        return redirect(url_for('panel'))

    return render_template('editar_transaccion.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
