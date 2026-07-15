# APP PRINCIPAL - FLASK + LOGIN + RUTAS
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from models import db, Usuario, AnalisisFinanciero
from calculos import capacidad_libre, analizar_meta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-solo-desarrollo-cambiar-luego'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def cargar_usuario(id): return Usuario.query.get(int(id))

# CREA BD LA PRIMERA VEZ
with app.app_context(): db.create_all()

# ---------------- AUTENTICACION ----------------
@app.route('/registro', methods=['GET','POST'])
def registro():
    if current_user.is_authenticated: return redirect('/')
    if request.method=='POST':
        d=request.form
        if Usuario.query.filter_by(correo=d['correo']).first():
            flash("❌ Correo ya existe"); return render_template('registro.html')
        u=Usuario(nombre=d['nombre'],correo=d['correo']); u.poner_clave(d['clave'])
        db.session.add(u); db.session.commit(); login_user(u); return redirect('/')
    return render_template('registro.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: return redirect('/')
    if request.method=='POST':
        u=Usuario.query.filter_by(correo=request.form['correo']).first()
        if u and u.comprobar_clave(request.form['clave']): login_user(u); return redirect('/')
        flash("❌ Correo o clave malos")
    return render_template('login.html')

@app.route('/logout')
def salir(): logout_user(); return redirect('/login')

# ---------------- HERRAMIENTA ----------------
@app.route('/')
@login_required
def inicio(): return render_template('index.html', u=current_user)

# ---------------- API CALCULAR + GUARDAR ----------------
@app.route('/calcular', methods=['POST'])
@login_required
def calcular():
    d=request.get_json()
    cap=capacidad_libre(float(d['ingreso']),float(d['egresos']),float(d.get('cuotas_deuda',0)))
    res=analizar_meta(cap,float(d['monto_meta']),int(d['plazo']))
    # GUARDA HISTORIAL
    a=AnalisisFinanciero(
        usuario_id=current_user.id,
        ingreso=d['ingreso'],egresos=d['egresos'],cuotas_deuda=d.get('cuotas_deuda',0),
        monto_meta=d['monto_meta'],plazo_deseado=d['plazo'],
        capacidad_mes=cap['disponible_mes'],viabilidad=res['viabilidad'],
        cuota_necesaria=res['cuota_necesaria'],plazo_real=res['plazo_real_meses']
    )
    db.session.add(a); db.session.commit()
    return jsonify(capacidad=cap,meta=res)

if __name__=='__main__': app.run(debug=True)