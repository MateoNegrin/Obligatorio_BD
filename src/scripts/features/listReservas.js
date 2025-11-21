document.addEventListener('DOMContentLoaded', () => {
      const tbody = document.getElementById('reservasTbody');
      fetch('http://localhost:5000/api/reservas')
        .then(r => { if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); })
        .then(data => {
          if (!Array.isArray(data) || data.length===0){ tbody.innerHTML='<tr><td colspan="7">Sin reservas</td></tr>'; return; }
          data.forEach(rv => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${rv.id_reserva}</td><td>${rv.nombre_sala}</td><td>${rv.edificio}</td><td>${rv.fecha}</td><td>${rv.hora_inicio}</td><td>${rv.hora_fin}</td><td>${rv.estado||''}</td>`;
            tbody.appendChild(tr);
          });
        })
        .catch(e => { tbody.innerHTML='<tr><td colspan="7">Error cargando reservas</td></tr>'; console.error(e); });
    });
  