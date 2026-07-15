# BASE DE DATOS - TABLAS
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    clave_hash = db.Column(db.String(200), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    analisis = db.relationship('AnalisisFinanciero', backref='usuario', lazy=True)

    def poner_clave(self, c):
        from werkzeug.security import generate_password_hash
        self.clave_hash = generate_password_hash(c)
    def comprobar_clave(self, c):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.clave_hash, c)

class AnalisisFinanciero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    ingreso=db.Column(db.Float); egresos=db.Column(db.Float); cuotas_deuda=db.Column(db.Float)
    monto_meta=db.Column(db.Float); plazo_deseado=db.Column(db.Integer)
    capacidad_mes=db.Column(db.Float); viabilidad=db.Column(db.String(30))
    cuota_necesaria=db.Column(db.Float); plazo_real=db.Column(db.Integer)
    fecha=db.Column(db.DateTime, default=datetime.utcnow)