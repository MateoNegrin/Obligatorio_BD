document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('salasTbody');
  fetch('http://localhost:5000/api/salas')
    .then(r=>r.json())
    .then(data=>{
      if(!Array.isArray(data)||data.length===0){ tbody.innerHTML='<tr><td colspan="5">Sin salas</td></tr>'; return;}
      data.forEach(s=>{
        const tr=document.createElement('tr');
        tr.innerHTML=`
          <td>${s.nombre_sala}</td>
          <td>${s.edificio}</td>
          <td>${s.capacidad}</td>
          <td>${s.tipo_sala}</td>
          <td>
            <button class="action-btn action-edit" data-act="edit" data-ed="${encodeURIComponent(s.edificio)}" data-ns="${encodeURIComponent(s.nombre_sala)}">Modificar</button>
            <button class="action-btn action-del" data-act="del" data-ed="${encodeURIComponent(s.edificio)}" data-ns="${encodeURIComponent(s.nombre_sala)}">Eliminar</button>
          </td>`;
        tbody.appendChild(tr);
      });
    });
  tbody.addEventListener('click', e=>{
    const b=e.target.closest('.action-btn'); if(!b) return;
    const edificio=decodeURIComponent(b.dataset.ed);
    const nombre=decodeURIComponent(b.dataset.ns);
    if(b.dataset.act==='edit'){
      location.href=`../forms/formSala.html?edit=1&edificio=${encodeURIComponent(edificio)}&nombre_sala=${encodeURIComponent(nombre)}`;
    }else{
      if(!confirm('Eliminar sala?')) return;
      fetch(`http://localhost:5000/api/salas/${encodeURIComponent(edificio)}/${encodeURIComponent(nombre)}`, {method:'DELETE'})
        .then(r=>r.json().then(j=>({ok:r.ok,j})))
        .then(res=>{ if(res.ok){ b.closest('tr').remove(); } else alert('Error: '+(res.j.error||'')); });
    }
  });
});
