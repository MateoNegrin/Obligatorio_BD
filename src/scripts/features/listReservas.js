document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('reservasTbody');
  fetch('http://localhost:5000/api/reservas')
    .then(r=>r.json())
    .then(data=>{
      if(!Array.isArray(data)||data.length===0){ tbody.innerHTML='<tr><td colspan="8">Sin reservas</td></tr>'; return;}
      data.forEach(rv=>{
        const tr=document.createElement('tr');
        tr.innerHTML=`
          <td>${rv.id_reserva}</td>
          <td>${rv.nombre_sala}</td>
          <td>${rv.edificio}</td>
          <td>${rv.fecha}</td>
          <td>${rv.hora_inicio||''}</td>
          <td>${rv.hora_fin||''}</td>
          <td>${rv.estado||''}</td>
          <td>
            <button class="action-btn action-edit" data-act="edit" data-id="${rv.id_reserva}">Modificar</button>
            <button class="action-btn action-del" data-act="del" data-id="${rv.id_reserva}">Eliminar</button>
          </td>`;
        tbody.appendChild(tr);
      });
    });
  tbody.addEventListener('click', e=>{
    const b=e.target.closest('.action-btn'); if(!b) return;
    const id=b.dataset.id;
    if(b.dataset.act==='edit'){
      location.href=`../forms/formReserva.html?edit=1&id_reserva=${encodeURIComponent(id)}`;
    }else{
      if(!confirm('Eliminar reserva?')) return;
      fetch(`http://localhost:5000/api/reservas/${encodeURIComponent(id)}`, {method:'DELETE'})
        .then(r=>r.json().then(j=>({ok:r.ok,j})))
        .then(res=>{ if(res.ok){ b.closest('tr').remove(); } else alert('Error: '+(res.j.error||'')); });
    }
  });
});
