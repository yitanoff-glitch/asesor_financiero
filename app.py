# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Importamos db desde models
from models import db, Usuario, GastoFijo, Deuda, Meta, HitoMeta, Transaccion, Proyecto
from calculos import *

# Configuración de la app
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_asesor_financiero_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "instance", "asesor.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos la base de datos
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Crear tablas
with app.app_context():
    db.create_all()
    print("✅ Base de datos y tablas creadas correctamente")


# ───────────────── RUTAS DE AUTENTICACIÓN ─────────────────
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contraseña = request.form['contraseña']
        
        usuario_existe = Usuario.query.filter_by(email=email).first()
        if usuario_existe:
            flash("El correo ya está registrado")
            return redirect(url_for('registro'))
        
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            contraseña=generate_password_hash(contraseña, method='pbkdf2:sha256')
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Registro exitoso, inicia sesión")
        return redirect(url_for('login'))
    
    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.contraseña, contraseña):
            login_user(usuario)
            return redirect(url_for('dashboard'))
        else:
            flash("Correo o contraseña incorrectos")
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ───────────────── RUTAS PRINCIPALES ─────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html',
        usuario=current_user,
        datos=None,
        resultado=None
    )

@app.route('/gasto/nuevo', methods=['POST'])
@login_required
def agregar_gasto():
    datos = request.form
    nuevo_gasto = GastoFijo(
        usuario_id=current_user.id,
        nombre=datos['nombre'],
        monto=float(datos['monto']),
        dia_vencimiento=int(datos['dia_vencimiento']),
        categoria=datos['categoria']
    )
    db.session.add(nuevo_gasto)
    db.session.commit()
    flash("Gasto guardado correctamente")
    return redirect(url_for('dashboard'))


@app.route('/deuda/nueva', methods=['POST'])
@login_required
def agregar_deuda():
    datos = request.form
    tasa_mensual = tasa_efectiva_anual_a_mensual(float(datos['tea']))
    cuota = calcular_cuota_mensual(
        monto=float(datos['monto']),
        tasa_mensual=tasa_mensual,
        plazo_meses=int(datos['plazo'])
    )
    
    nueva_deuda = Deuda(
        usuario_id=current_user.id,
        nombre=datos['nombre'],
        entidad=datos['entidad'],
        monto_original=float(datos['monto']),
        monto_actual=float(datos['monto']),
        tasa_interes_anual=float(datos['tea']),
        cuota_mensual=cuota,
        dia_pago=int(datos['dia_pago'])
    )
    db.session.add(nueva_deuda)
    db.session.commit()
    flash("Deuda registrada y cuota calculada")
    return redirect(url_for('dashboard'))


@app.route('/meta/nueva', methods=['POST'])
@login_required
def agregar_meta():
    datos = request.form
    ahorro_necesario = ahorro_mensual_para_meta(
        monto_objetivo=float(datos['monto_objetivo']),
        plazo_meses=int(datos['plazo_meses'])
    )
    
    nueva_meta = Meta(
        usuario_id=current_user.id,
        nombre=datos['nombre'],
        descripcion=datos['descripcion'],
        monto_objetivo=float(datos['monto_objetivo']),
        monto_actual=0,
        plazo_meses=int(datos['plazo_meses']),
        tipo_plazo=datos['tipo_plazo'],
        prioridad=int(datos.get('prioridad', 3))
    )
    db.session.add(nueva_meta)
    db.session.commit()
    flash(f"Meta creada: necesitas ahorrar ${ahorro_necesario:,.0f} cada mes")
    return redirect(url_for('dashboard'))


@app.route('/proyecto/analizar', methods=['POST'])
@login_required
def analizar_proyecto():
    datos = request.form
    inversion = float(datos['inversion_inicial'])
    pvu = float(datos['precio_venta'])
    cvu = float(datos['costo_variable'])
    cf = float(datos['costos_fijos'])
    plazo = int(datos['plazo_meses'])
    tasa_ref = float(datos['tasa_referencia']) / 100 / 12
    
    pe_unidades = punto_equilibrio_unidades(cf, pvu, cvu)
    pe_dinero = punto_equilibrio_dinero(cf, pvu, cvu)
    margen = margen_contribucion_unitario(pvu, cvu)
    
    ventas_mensuales = float(datos['ventas_mensuales'])
    flujos = []
    for _ in range(plazo):
        utilidad = (ventas_mensuales * margen) - cf
        flujos.append(utilidad)
    
    van = calcular_van(inversion, flujos, tasa_ref)
    tir = calcular_tir(inversion, flujos)
    payback = calcular_payback(inversion, flujos)
    viabilidad, recomendacion = evaluar_viabilidad(van, tir, tasa_ref * 12 * 100)
    
    nuevo_proyecto = Proyecto(
        usuario_id=current_user.id,
        nombre=datos['nombre'],
        descripcion=datos['descripcion'],
        inversion_inicial=inversion,
        plazo_meses=plazo,
        precio_venta_unitario=pvu,
        costo_variable_unitario=cvu,
        costos_fijos_mensuales=cf,
        punto_equilibrio_unidades=pe_unidades,
        punto_equilibrio_dinero=pe_dinero,
        margen_contribucion=margen,
        van=van,
        tir=tir,
        payback_meses=payback,
        viabilidad=viabilidad,
        recomendaciones=recomendacion
    )
    db.session.add(nuevo_proyecto)
    db.session.commit()
    
    return jsonify({
        "viabilidad": viabilidad,
        "recomendacion": recomendacion,
        "van": round(van, 2),
        "tir": round(tir, 2),
        "payback": round(payback, 2) if payback else "No recuperable"
    })

@app.route('/analizar_guardar', methods=['POST'])
@login_required
def analizar_guardar():
    # Leemos datos del formulario
    ingreso = float(request.form.get('ingreso', 0))
    egresos = float(request.form.get('egresos', 0))
    cuotas_deuda = float(request.form.get('cuotas_deuda', 0))
    monto_meta = float(request.form.get('monto_meta', 0))
    plazo = int(request.form.get('plazo', 1))

    # Cálculos
    capacidad = ingreso - egresos - cuotas_deuda
    ahorro_necesario = ahorro_mensual_para_meta(monto_meta, plazo)
    alcanza = capacidad >= ahorro_necesario
    recomendaciones = []

    if alcanza:
        mensaje = f"✅ ¡Sí puedes lograr tu meta en {plazo} meses! Te sobran ${capacidad - ahorro_necesario:,.0f} al mes."
        clase = "ok"
        recomendaciones.append("Automatiza el ahorro en cuanto entre tu sueldo.")
        recomendaciones.append("Invierte el excedente para que no pierda valor.")
    else:
        faltante = ahorro_necesario - capacidad
        mensaje = f"⚠️ No alcanzas por ahora. Te faltan ${faltante:,.0f} mensuales para cumplir en {plazo} meses."
        clase = "mal"
        nuevo_plazo = int(monto_meta / capacidad) + 1 if capacidad > 0 else plazo * 2
        recomendaciones.append(f"Opción 1: Aumenta el plazo a {nuevo_plazo} meses y sí alcanzas.")
        recomendaciones.append("Opción 2: Reduce gastos no esenciales (suscripciones, gastos hormiga).")
        recomendaciones.append("Opción 3: Busca ingresos extra para cubrir el faltante.")

    # Guardamos en base de datos
    tipo_plazo = "corto" if plazo <= 6 else "mediano" if plazo <= 18 else "largo"
    nueva_meta = Meta(
        usuario_id=current_user.id,
        nombre=f"Meta ${monto_meta:,.0f} en {plazo} meses",
        monto_objetivo=monto_meta,
        plazo_meses=plazo,
        tipo_plazo=tipo_plazo
    )
    db.session.add(nueva_meta)
    db.session.commit()

    # Preparamos todo para mostrar en la página
    resultado = {
        'capacidad': capacidad,
        'ahorro_necesario': ahorro_necesario,
        'alcanza': alcanza,
        'mensaje': mensaje,
        'clase': clase,
        'recomendaciones': recomendaciones
    }

    flash("✅ Análisis y meta guardados correctamente")

    return render_template('index.html',
        usuario=current_user,
        datos=None,
        resultado=resultado
    )

@app.route('/')
def inicio():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
    