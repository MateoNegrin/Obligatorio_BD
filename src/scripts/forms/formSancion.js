document.addEventListener('DOMContentLoaded', () => {
  const f = document.getElementById('formSancion');
  if (!f) return;
  f.addEventListener('submit', e => {
    e.preventDefault();
    const payload = {
      participante_ci: f.participante_ci.value.trim(),
      fecha_inicio: f.fecha_inicio.value,
      fecha_fin: f.fecha_fin.value
    };
    fetch('http://localhost:5000/api/sanciones', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload)
    }).then(r=>r.json().then(j=>({ok:r.ok,j})))
      .then(res=>{
        if(res.ok){ alert('Sanción agregada'); location.href='../features/sanciones.html'; }
        else alert('Error: '+(res.j.error||''));
      }).catch(()=>alert('Error de red'));
  });
});
