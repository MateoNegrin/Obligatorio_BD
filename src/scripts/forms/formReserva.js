import sanitizeInput from '../utils/sanitize.js';

document.addEventListener('DOMContentLoaded', () => {
  const f=document.getElementById('formReserva'); if(!f) return;
  const params=new URLSearchParams(location.search);
  const edit=params.get('edit')==='1';
  const idR=params.get('id_reserva');

  const salasPorEdificio={'Edificio Mullin':['1A','1B','2A'],'Edificio Sacre Coeur':['1A','1B']};
  f.edificio.addEventListener('change',()=>{
    const sel=f.nombre_sala; sel.innerHTML='<option value="">Seleccionar...</option>';
    (salasPorEdificio[f.edificio.value]||[]).forEach(s=>{
      const opt=document.createElement('option'); opt.value=s; opt.textContent=s; sel.appendChild(opt);
    });
  });

  if(edit && idR){
    fetch(`http://localhost:5000/api/reservas/${encodeURIComponent(idR)}`)
      .then(r=>r.json())
      .then(rv=>{
        if(rv && !rv.error){
          f.id_reserva.value = rv.id_reserva;
          f.id_reserva.disabled = true;
          f.edificio.value = rv.edificio;
          f.edificio.dispatchEvent(new Event('change'));
          f.nombre_sala.value = rv.nombre_sala;
          f.fecha.value = rv.fecha;
          if(rv.id_turno) f.id_turno.value = rv.id_turno;
          f.estado.value = rv.estado;
        }
      });
  }

  f.addEventListener('submit', e=>{
    e.preventDefault();
    const payload={
      id_reserva: parseInt(f.id_reserva.value,10),
      nombre_sala: sanitizeInput(f.nombre_sala.value,10),
      edificio: sanitizeInput(f.edificio.value,60),
      fecha: f.fecha.value,
      id_turno: parseInt(f.id_turno.value,10),
      estado: f.estado.value
    };
    const method=edit?'PUT':'POST';
    const url=edit?`http://localhost:5000/api/reservas/${encodeURIComponent(idR)}`:'http://localhost:5000/api/reservas';
    fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
      .then(r=>r.json().then(j=>({ok:r.ok,j})))
      .then(res=>{
        if(res.ok){ alert(edit?'Reserva actualizada':'Reserva agregada'); location.href='../features/reservas.html'; }
        else alert('Error: '+(res.j.error||'')); 
      }).catch(()=>alert('Error de red'));
  });
});
