# calculos.py
from math import pow
import numpy_financial as npf  # Para cálculos precisos de VAN y TIR
# ==============================================
# 📊 MÓDULO 1: FINANZAS PERSONALES
# ==============================================
def tasa_efectiva_anual_a_mensual(tea):
    """Convierte Tasa Efectiva Anual a Tasa Efectiva Mensual"""
    return pow(1 + tea / 100, 1/12) - 1
def calcular_cuota_mensual(monto, tasa_mensual, plazo_meses):
    """Calcula valor de cuota fija con fórmula de amortización"""
    if tasa_mensual == 0:
        return monto / plazo_meses
    return monto * (tasa_mensual * pow(1 + tasa_mensual, plazo_meses)) / (pow(1 + tasa_mensual, plazo_meses) - 1)
def plan_pago_bola_nieve(deudas):
    """Ordena deudas de menor a mayor monto total"""
    return sorted(deudas, key=lambda d: d.monto_actual)
def plan_pago_avalancha(deudas):
    """Ordena deudas de mayor a menor tasa de interés"""
    return sorted(deudas, key=lambda d: d.tasa_interes_anual, reverse=True)
def ahorro_mensual_para_meta(monto_objetivo, plazo_meses, rendimiento_mensual=0.005):
    """Cuánto debes ahorrar cada mes para alcanzar una meta"""
    if rendimiento_mensual == 0:
        return monto_objetivo / plazo_meses
    return monto_objetivo * rendimiento_mensual / (pow(1 + rendimiento_mensual, plazo_meses) - 1)
def calcular_caja_actual(usuario):
    """Saldo disponible: ingresos - gastos - cuotas deudas"""
    ingresos = sum(t.monto for t in usuario.transacciones if t.tipo == "ingreso")
    gastos_variables = sum(t.monto for t in usuario.transacciones if t.tipo == "gasto")
    gastos_fijos = sum(g.monto for g in usuario.gastos_fijos if g.activo)
    cuotas_deudas = sum(d.cuota_mensual for d in usuario.deudas if d.estado == "activa")
    return ingresos - gastos_variables - gastos_fijos - cuotas_deudas

# ==============================================
# 💼 MÓDULO 2: ANÁLISIS DE VIABILIDAD DE PROYECTOS
# ==============================================

def margen_contribucion_unitario(pvu, cvu):
    """PVU = Precio Venta Unitario | CVU = Costo Variable Unitario"""
    return pvu - cvu

def punto_equilibrio_unidades(costos_fijos, pvu, cvu):
    """Cantidad de unidades que debes vender para no perder ni ganar"""
    margen = margen_contribucion_unitario(pvu, cvu)
    if margen <= 0:
        return None  # No hay forma de llegar a equilibrio
    return costos_fijos / margen

def punto_equilibrio_dinero(costos_fijos, pvu, cvu):
    """Valor en dinero del punto de equilibrio"""
    unidades = punto_equilibrio_unidades(costos_fijos, pvu, cvu)
    return unidades * pvu if unidades else None

def calcular_van(inversion_inicial, flujos_futuros, tasa_mensual):
    """Valor Actual Neto: si > 0 → el proyecto genera valor"""
    return npf.npv(tasa_mensual, [-inversion_inicial] + flujos_futuros)

def calcular_tir(inversion_inicial, flujos_futuros):
    """Tasa Interna de Retorno: rentabilidad real del proyecto"""
    flujos_completos = [-inversion_inicial] + flujos_futuros
    tir = npf.irr(flujos_completos)
    return tir * 100  # Convertir a porcentaje

def calcular_payback(inversion_inicial, flujos_futuros):
    """Tiempo en meses para recuperar la inversión"""
    acumulado = 0
    for mes, flujo in enumerate(flujos_futuros, start=1):
        acumulado += flujo
        if acumulado >= inversion_inicial:
            fraccion = (acumulado - flujo) / inversion_inicial
            return mes - 1 + fraccion
    return None  # Nunca recupera

def evaluar_viabilidad(van, tir, tasa_referencia):
    """Devuelve estado y recomendación según resultados"""
    if van > 0 and tir > tasa_referencia:
        return "viable", "✅ El proyecto es viable: genera ganancias y supera la rentabilidad de referencia."
    elif van >= -100000 and tir >= tasa_referencia * 0.9:
        return "ajustes", "⚠️ Viable con ajustes: mejora precios o reduce costos para aumentar rentabilidad."
    else:
        return "no viable", "❌ No recomendado: no cubre la inversión ni genera rentabilidad suficiente."
