import sanitizeInput from '../utils/sanitize.js';

document.addEventListener('DOMContentLoaded', () => {
  const f=document.getElementById('formSala'); if(!f) return;
  const params=new URLSearchParams(location.search);
  const edit=params.get('edit')==='1';
  const edificio=params.get('edificio');
  const nombre=params.get('nombre_sala');
  if(edit && edificio && nombre){
    fetch(`http://localhost:5000/api/salas/${encodeURIComponent(edificio)}/${encodeURIComponent(nombre)}`)
      .then(r=>r.json())
      .then(s=>{
        if(s && !s.error){
          f.edificio.value = s.edificio;
          f.nombre_sala.value = s.nombre_sala;
          f.nombre_sala.disabled = true;
          f.edificio.disabled = true;
          f.capacidad.value = s.capacidad;
          f.tipo_sala.value = s.tipo_sala;
        }
      });
  }
  f.addEventListener('submit', e=>{
    e.preventDefault();
    const payload={
      nombre_sala: sanitizeInput(f.nombre_sala.value, 10),
      edificio: sanitizeInput(f.edificio.value, 60),
      capacidad: parseInt(f.capacidad.value,10),
      tipo_sala: f.tipo_sala.value
    };
    const method = edit ? 'PUT':'POST';
    const url = edit
      ? `http://localhost:5000/api/salas/${encodeURIComponent(edificio)}/${encodeURIComponent(nombre)}`
      : 'http://localhost:5000/api/salas';
    fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
      .then(r=>r.json().then(j=>({ok:r.ok,j})))
      .then(res=>{
        if(res.ok){ alert(edit?'Sala actualizada':'Sala agregada'); location.href='../features/salas.html'; }
        else alert('Error: '+(res.j.error||'')); 
      }).catch(()=>alert('Error de red'));
  });
});
