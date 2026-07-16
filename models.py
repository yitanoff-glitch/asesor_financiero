# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Creamos db aquí, no la traemos de app
db = SQLAlchemy()

# ──────────────────────────────────────────────────────────────
# 1. USUARIOS
# ──────────────────────────────────────────────────────────────
class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    gastos_fijos = db.relationship('GastoFijo', backref='usuario', lazy=True, cascade="all, delete-orphan")
    deudas = db.relationship('Deuda', backref='usuario', lazy=True, cascade="all, delete-orphan")
    metas = db.relationship('Meta', backref='usuario', lazy=True, cascade="all, delete-orphan")
    transacciones = db.relationship('Transaccion', backref='usuario', lazy=True, cascade="all, delete-orphan")
    proyectos = db.relationship('Proyecto', backref='usuario', lazy=True, cascade="all, delete-orphan")


# ──────────────────────────────────────────────────────────────
# 2. GASTOS FIJOS
# ──────────────────────────────────────────────────────────────
class GastoFijo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    dia_vencimiento = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, default=True)


# ──────────────────────────────────────────────────────────────
# 3. DEUDAS
# ──────────────────────────────────────────────────────────────
class Deuda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    entidad = db.Column(db.String(100))
    monto_original = db.Column(db.Float, nullable=False)
    monto_actual = db.Column(db.Float, nullable=False)
    tasa_interes_anual = db.Column(db.Float, default=0)
    cuota_mensual = db.Column(db.Float, default=0)
    dia_pago = db.Column(db.Integer)
    fecha_inicio = db.Column(db.Date)
    fecha_liquidacion_proyectada = db.Column(db.Date)
    estado = db.Column(db.String(20), default="activa")


# ──────────────────────────────────────────────────────────────
# 4. METAS FINANCIERAS
# ──────────────────────────────────────────────────────────────
class Meta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    monto_objetivo = db.Column(db.Float, nullable=False)
    monto_actual = db.Column(db.Float, default=0)
    plazo_meses = db.Column(db.Integer, nullable=False)
    tipo_plazo = db.Column(db.String(20), nullable=False)
    prioridad = db.Column(db.Integer, default=3)
    completada = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    hitos = db.relationship('HitoMeta', backref='meta', lazy=True, cascade="all, delete-orphan")


class HitoMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meta_id = db.Column(db.Integer, db.ForeignKey('meta.id'), nullable=False)
    descripcion = db.Column(db.String(250), nullable=False)
    monto_requerido = db.Column(db.Float)
    completado = db.Column(db.Boolean, default=False)


# ──────────────────────────────────────────────────────────────
# 5. TRANSACCIONES
# ──────────────────────────────────────────────────────────────
class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(250))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)


# ──────────────────────────────────────────────────────────────
# 6. PROYECTOS DE EMPRENDIMIENTO
# ──────────────────────────────────────────────────────────────
class Proyecto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    inversion_inicial = db.Column(db.Float, nullable=False)
    plazo_meses = db.Column(db.Integer, nullable=False)
    tasa_descuento = db.Column(db.Float, default=1.5)

    precio_venta_unitario = db.Column(db.Float)
    costo_variable_unitario = db.Column(db.Float)
    costos_fijos_mensuales = db.Column(db.Float)

    punto_equilibrio_unidades = db.Column(db.Float)
    punto_equilibrio_dinero = db.Column(db.Float)
    margen_contribucion = db.Column(db.Float)
    van = db.Column(db.Float)
    tir = db.Column(db.Float)
    payback_meses = db.Column(db.Float)
    viabilidad = db.Column(db.String(20))
    recomendaciones = db.Column(db.Text)

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)