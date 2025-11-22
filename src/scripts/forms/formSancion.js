import sanitizeInput from '../utils/sanitize.js';

document.addEventListener('DOMContentLoaded', () => {
  const f=document.getElementById('formSancion'); if(!f) return;
  const params=new URLSearchParams(location.search);
  const edit=params.get('edit')==='1';
  const ci0=params.get('participante_ci');
  const fi0=params.get('fecha_inicio');
  const ff0=params.get('fecha_fin');

  if(edit && ci0 && fi0 && ff0){
    fetch(`http://localhost:5000/api/sanciones/${encodeURIComponent(ci0)}/${encodeURIComponent(fi0)}/${encodeURIComponent(ff0)}`)
      .then(r=>r.json())
      .then(s=>{
        if(s && !s.error){
          f.participante_ci.value=s.participante_ci;
          f.participante_ci.disabled=true;
          f.fecha_inicio.value=s.fecha_inicio;
          f.fecha_fin.value=s.fecha_fin;
        } else {
          alert('No se pudo cargar la sanción.');
        }
      })
      .catch(()=>alert('Error de red al cargar sanción'));
  }

  f.addEventListener('submit', e=>{
    e.preventDefault();
    const payload={
      participante_ci: sanitizeInput(f.participante_ci.value, 20),
      fecha_inicio: f.fecha_inicio.value,
      fecha_fin: f.fecha_fin.value
    };
    let method='POST';
    let url='http://localhost:5000/api/sanciones';

    if(edit && ci0 && fi0 && ff0){
      method='PUT';
      url=`http://localhost:5000/api/sanciones/${encodeURIComponent(ci0)}/${encodeURIComponent(fi0)}/${encodeURIComponent(ff0)}`;
      payload.fecha_inicio_new = payload.fecha_inicio;
      payload.fecha_fin_new = payload.fecha_fin;
    }

    fetch(url,{
      method,
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload)
    })
      .then(r=>r.json().then(j=>({ok:r.ok,j})))
      .then(res=>{
        if(res.ok){
          alert(edit?'Sanción actualizada':'Sanción agregada');
          location.href='../features/sanciones.html';
        } else {
          alert('Error: '+(res.j.error||''));
        }
      })
      .catch(()=>alert('Error de red'));
  });
});
