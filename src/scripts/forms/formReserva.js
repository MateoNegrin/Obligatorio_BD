document.addEventListener('DOMContentLoaded', () => {
  const f = document.getElementById('formReserva');
  if (!f) return;

  // Dependiente: salas según edificio (simple filtrado predefinido)
  const salasPorEdificio = {
    'Edificio Mullin': ['1A','1B','2A'],
    'Edificio Sacre Coeur': ['1A','1B']
  };
  f.edificio.addEventListener('change', () => {
    const sel = f.nombre_sala;
    sel.innerHTML = '<option value="">Seleccionar...</option>';
    (salasPorEdificio[f.edificio.value]||[]).forEach(s=>{
      const opt=document.createElement('option');
      opt.value=s; opt.textContent=s;
      sel.appendChild(opt);
    });
  });

  f.addEventListener('submit', e => {
    e.preventDefault();
    const payload = {
      id_reserva: parseInt(f.id_reserva.value,10),
      nombre_sala: f.nombre_sala.value,
      edificio: f.edificio.value,
      fecha: f.fecha.value,
      id_turno: parseInt(f.id_turno.value,10),
      estado: f.estado.value
    };
    fetch('http://localhost:5000/api/reservas', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload)
    }).then(r=>r.json().then(j=>({ok:r.ok,j})))
      .then(res=>{
        if(res.ok){ alert('Reserva agregada'); location.href='../features/reservas.html'; }
        else alert('Error: '+(res.j.error||''));
      }).catch(()=>alert('Error de red'));
  });
});
