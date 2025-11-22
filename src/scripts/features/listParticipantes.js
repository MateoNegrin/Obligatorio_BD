document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('participantesTbody');
  const empty = document.getElementById('participantesEmpty');
  fetch('http://localhost:5000/api/participantes')
    .then(r => r.json())
    .then(data => {
      if (!Array.isArray(data) || data.length === 0) { empty.style.display='block'; return; }
      data.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${p.ci}</td>
          <td>${p.nombre}</td>
          <td>${p.apellido}</td>
          <td>${p.fecha_nac||''}</td>
          <td>${p.genero||''}</td>
          <td>
            <button class="action-btn action-edit" data-act="edit" data-id="${p.ci}">Modificar</button>
            <button class="action-btn action-del" data-act="del" data-id="${p.ci}">Eliminar</button>
          </td>`;
        tbody.appendChild(tr);
      });
    });
  tbody.addEventListener('click', e => {
    const btn = e.target.closest('.action-btn'); if(!btn) return;
    const ci = btn.dataset.id;
    if (btn.dataset.act === 'edit') {
      location.href = `../forms/formParticipante.html?edit=1&ci=${encodeURIComponent(ci)}`;
    } else {
      if (!confirm('Eliminar participante?')) return;
      fetch(`http://localhost:5000/api/participantes/${encodeURIComponent(ci)}`, {method:'DELETE'})
        .then(r=>r.json().then(j=>({ok:r.ok,j})))
        .then(res=>{
          if(res.ok){ btn.closest('tr').remove(); }
          else alert('Error: '+(res.j.error||'')); 
        });
    }
  });
});