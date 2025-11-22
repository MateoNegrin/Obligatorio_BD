document.addEventListener('DOMContentLoaded', () => {
  const f = document.getElementById('formSala');
  if (!f) return;
  f.addEventListener('submit', e => {
    e.preventDefault();
    const payload = {
      nombre_sala: f.nombre_sala.value.trim(),
      edificio: f.edificio.value,
      capacidad: parseInt(f.capacidad.value,10),
      tipo_sala: f.tipo_sala.value
    };
    fetch('http://localhost:5000/api/salas', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload)
    }).then(r=>r.json().then(j=>({ok:r.ok,j})))
      .then(res=>{
        if(res.ok){ alert('Sala agregada'); location.href='../features/salas.html'; }
        else alert('Error: '+(res.j.error||''));
      }).catch(()=>alert('Error de red'));
  });
});
