document.addEventListener('DOMContentLoaded', () => {
  const f = document.getElementById('formParticipante');
  if (!f) return;
  f.addEventListener('submit', e => {
    e.preventDefault();
    const payload = {
      ci: f.ci.value.trim(),
      nombre: f.nombre.value.trim(),
      apellido: f.apellido.value.trim(),
      fecha_nac: f.fecha_nac.value || null,
      genero: f.genero.value || null
    };
    fetch('http://localhost:5000/api/participantes', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload)
    }).then(r=>r.json().then(j=>({ok:r.ok,j})))
      .then(res=>{
        if(res.ok){ alert('Participante agregado'); location.href='../features/participantes.html'; }
        else alert('Error: '+(res.j.error||''));
      }).catch(()=>alert('Error de red'));
  });
});
