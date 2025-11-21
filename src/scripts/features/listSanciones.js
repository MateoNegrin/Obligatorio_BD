document.addEventListener('DOMContentLoaded', () => {
      const tbody = document.getElementById('sancionesTbody');
      fetch('http://localhost:5000/api/sanciones')
        .then(r => { if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); })
        .then(data => {
          if (!Array.isArray(data) || data.length===0){ tbody.innerHTML='<tr><td colspan="3">Sin sanciones</td></tr>'; return; }
          data.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${s.participante_ci}</td><td>${s.fecha_inicio}</td><td>${s.fecha_fin}</td>`;
            tbody.appendChild(tr);
          });
        })
        .catch(e => { tbody.innerHTML='<tr><td colspan="3">Error cargando sanciones</td></tr>'; console.error(e); });
    });
  