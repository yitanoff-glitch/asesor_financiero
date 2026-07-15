# LOGICA FINANCIERA - NUNCA SE MODIFICA
def capacidad_libre(ingreso, egresos, cuotas_deuda=0):
    disponible = ingreso - egresos - cuotas_deuda
    pct_deuda = (cuotas_deuda/ingreso*100) if ingreso>0 else 0
    alerta = "✅ Saludable" if pct_deuda<=35 else "⚠️ Alto" if pct_deuda<=50 else "❌ Crítico"
    return {"disponible_mes":round(disponible,2),"pct_deuda":round(pct_deuda,1),"alerta_deuda":alerta}

def analizar_meta(cap, monto, plazo):
    if plazo<=0 or monto<=0: return {"error":"valores malos"}
    dinero = cap["disponible_mes"]
    ideal = round(monto/plazo,2)
    if dinero >= ideal*1.05:
        v,cuota,real,consejo = "✅ VIABLE",ideal,plazo,"Cumples holgadamente, puedes guardar mas"
    elif dinero >= ideal*0.7:
        v,cuota,real = "⚠️ AJUSTABLE",round(dinero,2),round(monto/dinero) if dinero>0 else 999
        consejo = f"No en {plazo} meses, SI lo haces en {real} meses"
    else:
        v,cuota,real = "❌ NO VIABLE",round(dinero,2),round(monto/dinero) if dinero>0 else 999
        consejo = "PRIMERO: baja gastos / renegocia deudas / sube ingresos"
    return {"viabilidad":v,"cuota_necesaria":ideal,"cuota_posible_real":cuota,"plazo_real_meses":real,"consejo_asesor":consejo}