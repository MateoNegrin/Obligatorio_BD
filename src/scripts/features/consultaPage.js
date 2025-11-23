document.addEventListener('DOMContentLoaded', () => {
  const key = document.body.getAttribute('data-key');
  const tbody = document.getElementById('consultaTbody');
  const limitInput = document.getElementById('consultaLimit');
  if (!key || !tbody) return;

  function render(rows) {
    if (!Array.isArray(rows) || rows.length === 0) {
      tbody.innerHTML = '<tr><td colspan="99">Sin datos</td></tr>';
      return;
    }
    let cols = Object.keys(rows[0]);
    
    if (key === 'turnos_top') {
      const idxInicio = cols.indexOf('Hora inicio');
      const idxFin = cols.indexOf('Hora fin');
      if (idxInicio !== -1 && idxFin !== -1) {
        [cols[idxInicio], cols[idxFin]] = [cols[idxFin], cols[idxInicio]];
      }
    }

    // Crear thead si no existe
    const thead = document.getElementById('consultaThead');
    if (thead && thead.children.length === 0) {
      thead.innerHTML = '<tr>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr>';
    }
    tbody.innerHTML = rows.map(r =>
      '<tr>' + cols.map(c => `<td data-label="${c}">${r[c] ?? ''}</td>`).join('') + '</tr>'
    ).join('');
  }

  function load() {
    let url = `http://localhost:5000/api/consultas/${encodeURIComponent(key)}`;
    if (limitInput && limitInput.value) {
      const v = parseInt(limitInput.value, 10);
      if (v > 0) url += `?limit=${v}`;
    }
    tbody.innerHTML = '<tr><td colspan="99">Cargando...</td></tr>';
    fetch(url)
      .then(r => r.json())
      .then(data => render(data))
      .catch(() => { tbody.innerHTML = '<tr><td colspan="99">Error de red</td></tr>'; });
  }

  if (limitInput) limitInput.addEventListener('change', load);
  load();
});
