// TOMA DATOS -> ENVIA A PYTHON -> MUESTRA RESULTADO
const f = document.getElementById('f');
const r = document.getElementById('r');

f.addEventListener('submit', async e => {
  e.preventDefault();
  const datos = {
    ingreso: f.ingreso.value,
    egresos: f.egresos.value,
    cuotas_deuda: f.cuotas_deuda.value || 0,
    monto_meta: f.monto_meta.value,
    plazo: f.plazo.value
  };
  // LLAMA A TU API
  const resp = await fetch('/calcular', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(datos)
  });
  const d = await resp.json();

  // PINTA
  r.classList.remove('oculto');
  const color = d.meta.viabilidad.includes('✅')?'ok' : d.meta.viabilidad.includes('⚠️')?'av':'no';
  r.innerHTML = `
    <h3>📈 Capacidad real mensual</h3>
    <p>Dinero libre: <b>$${Number(d.capacidad.disponible_mes).toLocaleString('es-CO')}</b></p>
    <p>Carga de deudas: ${d.capacidad.pct_deuda}% → ${d.capacidad.alerta_deuda}</p>
    <hr>
    <h3>🎯 Análisis de tu meta</h3>
    <p class="${color}">${d.meta.viabilidad}</p>
    <p>Necesitas apartar: <b>$${Number(d.meta.cuota_necesaria).toLocaleString('es-CO')} / mes</b></p>
    <p>Realmente puedes: <b>$${Number(d.meta.cuota_posible_real).toLocaleString('es-CO')} / mes</b></p>
    <p>Plazo que pediste: ${d.meta.plazo_deseado || f.plazo.value} meses</p>
    <p>⏱️ Plazo REAL estimado: <b>${d.meta.plazo_real_meses} meses</b></p>
    <p style="margin-top:.8rem;padding:.6rem;background:#eff6ff;border-radius:6px">💡 Consejo: ${d.meta.consejo_asesor}</p>
  `;
});