document.addEventListener('DOMContentLoaded', () => {
      const tbody = document.getElementById('participantesTbody');
      const empty = document.getElementById('participantesEmpty');
      fetch('http://localhost:5000/api/participantes')
        .then(r => {
          if (!r.ok) throw new Error('HTTP '+r.status);
          return r.json();
        })
        .then(data => {
          if (!Array.isArray(data) || data.length===0) { empty.style.display='block'; return; }
          data.forEach(p => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${p.ci}</td><td>${p.nombre}</td><td>${p.apellido}</td><td>${p.fecha_nac||''}</td><td>${p.genero||''}</td>`;
            tbody.appendChild(tr);
          });
        })
        .catch(e => { empty.style.display='block'; empty.textContent='Error cargando participantes'; console.error(e); });
    });