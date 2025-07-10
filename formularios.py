# formularios.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField, DateField, TextAreaField
from wtforms.validators import InputRequired, Length, Email, NumberRange

class FormularioRegistro(FlaskForm):
    nombre_usuario = StringField('Nombre de usuario', validators=[InputRequired(), Length(min=4, max=150)])
    correo = StringField('Correo electrónico', validators=[InputRequired(), Email()])
    contrasena = PasswordField('Contraseña', validators=[InputRequired()])
    enviar = SubmitField('Registrarse')

class FormularioInicioSesion(FlaskForm):
    correo = StringField('Correo electrónico', validators=[InputRequired(), Email()])
    contrasena = PasswordField('Contraseña', validators=[InputRequired()])
    enviar = SubmitField('Iniciar sesión')

class FormularioTransaccion(FlaskForm):
    monto = DecimalField('Monto', validators=[InputRequired(), NumberRange(min=0.01)])
    tipo = SelectField('Tipo de transacción', choices=[('Ingreso', 'Ingreso'), ('Egreso', 'Egreso')], validators=[InputRequired()])
    categoria = SelectField('Categoría', coerce=int, validators=[InputRequired()])
    fecha = DateField('Fecha', format='%Y-%m-%d', validators=[InputRequired()])
    descripcion = TextAreaField('Descripción (opcional)')
    enviar = SubmitField('Guardar transacción')

class FormularioCategoria(FlaskForm):
    nombre = StringField('Nombre de la categoría', validators=[InputRequired(), Length(max=100)])
    enviar = SubmitField('Guardar categoría')
