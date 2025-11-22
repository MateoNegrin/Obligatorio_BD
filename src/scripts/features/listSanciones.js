document.addEventListener('DOMContentLoaded', () => {
      const tbody = document.getElementById('sancionesTbody');
      fetch('http://localhost:5000/api/sanciones')
        .then(r => { if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); })
        .then(data => {
          if (!Array.isArray(data) || data.length===0){ tbody.innerHTML='<tr><td colspan="4">Sin sanciones</td></tr>'; return; }
          data.forEach(s => {
            const tr = document.createElement('tr');
            tr.innerHTML=`
          <td>${s.participante_ci}</td>
          <td>${s.fecha_inicio}</td>
          <td>${s.fecha_fin}</td>
          <td>
            <button class="action-btn action-edit" data-act="edit" data-ci="${s.participante_ci}" data-fi="${s.fecha_inicio}" data-ff="${s.fecha_fin}">Modificar</button>
            <button class="action-btn action-del" data-act="del" data-ci="${s.participante_ci}" data-fi="${s.fecha_inicio}" data-ff="${s.fecha_fin}">Eliminar</button>
          </td>`;
            tbody.appendChild(tr);
          });
        })
        .catch(e => { tbody.innerHTML='<tr><td colspan="4">Error cargando sanciones</td></tr>'; console.error(e); });
    });
    tbody.addEventListener('click', e=>{
      const b=e.target.closest('.action-btn'); if(!b) return;
      const {ci,fi,ff}=b.dataset;
      if(b.dataset.act==='edit'){
        location.href=`../forms/formSancion.html?edit=1&participante_ci=${encodeURIComponent(ci)}&fecha_inicio=${encodeURIComponent(fi)}&fecha_fin=${encodeURIComponent(ff)}`;
      }else{
        if(!confirm('Eliminar sanción?')) return;
        fetch(`http://localhost:5000/api/sanciones/${encodeURIComponent(ci)}/${encodeURIComponent(fi)}/${encodeURIComponent(ff)}`, {method:'DELETE'})
          .then(r=>r.json().then(j=>({ok:r.ok,j})))
          .then(res=>{ if(res.ok){ b.closest('tr').remove(); } else alert('Error: '+(res.j.error||'')); });
      }
    });
