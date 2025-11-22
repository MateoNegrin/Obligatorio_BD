document.addEventListener('DOMContentLoaded', () => {
  const f=document.getElementById('formSancion'); if(!f) return;
  const params=new URLSearchParams(location.search);
  const edit=params.get('edit')==='1';
  const ci=params.get('participante_ci');
  const fi=params.get('fecha_inicio');
  const ff=params.get('fecha_fin');

  if(edit && ci && fi && ff){
    fetch(`http://localhost:5000/api/sanciones/${encodeURIComponent(ci)}/${encodeURIComponent(fi)}/${encodeURIComponent(ff)}`)
      .then(r=>r.json())
      .then(s=>{
        if(s && !s.error){
          f.participante_ci.value=s.participante_ci;
          f.participante_ci.disabled=true;
          f.fecha_inicio.value=s.fecha_inicio;
          f.fecha_fin.value=s.fecha_fin;
        }
      });
  }

  f.addEventListener('submit', e=>{
    e.preventDefault();
    const payload={
      participante_ci: f.participante_ci.value.trim(),
      fecha_inicio: f.fecha_inicio.value,
      fecha_fin: f.fecha_fin.value
    };
    const method=edit?'PUT':'POST';
    const url=edit
      ? `http://localhost:5000/api/sanciones/${encodeURIComponent(ci)}/${encodeURIComponent(fi)}/${encodeURIComponent(ff)}`
      : 'http://localhost:5000/api/sanciones';
    // En PUT permitimos cambiar fechas (enviamos fecha_inicio_new / fecha_fin_new opcional)
    if(edit){
      payload.fecha_inicio_new = payload.fecha_inicio;
      payload.fecha_fin_new = payload.fecha_fin;
    }
    fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
      .then(r=>r.json().then(j=>({ok:r.ok,j})))
      .then(res=>{
        if(res.ok){ alert(edit?'Sanción actualizada':'Sanción agregada'); location.href='../features/sanciones.html'; }
        else alert('Error: '+(res.j.error||'')); 
      }).catch(()=>alert('Error de red'));
  });
});
