document.addEventListener('DOMContentLoaded', () => {
      const tbody = document.getElementById('salasTbody');
      fetch('http://localhost:5000/api/salas')
        .then(r => { if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); })
        .then(data => {
          if (!Array.isArray(data) || data.length===0){ tbody.innerHTML='<tr><td colspan="4">Sin salas</td></tr>'; return; }
          data.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${s.nombre_sala}</td><td>${s.edificio}</td><td>${s.capacidad}</td><td>${s.tipo_sala}</td>`;
            tbody.appendChild(tr);
          });
        })
        .catch(e => { tbody.innerHTML='<tr><td colspan="4">Error cargando salas</td></tr>'; console.error(e); });
    });
  