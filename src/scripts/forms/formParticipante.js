import sanitizeInput from '../utils/sanitize.js';

document.addEventListener('DOMContentLoaded', () => {
  const f = document.getElementById('formParticipante'); if(!f) return;
  const params = new URLSearchParams(location.search);
  const edit = params.get('edit')==='1';
  const ciParam = params.get('ci');
  if(edit && ciParam){
    fetch(`http://localhost:5000/api/participantes/${encodeURIComponent(ciParam)}`)
      .then(r=>r.json())
      .then(p=>{
        if(p && !p.error){
          f.ci.value = p.ci;
          f.ci.disabled = true;
          f.nombre.value = p.nombre;
          f.apellido.value = p.apellido;
          if(p.fecha_nac) f.fecha_nac.value = p.fecha_nac;
          if(p.genero) f.genero.value = p.genero;
        }
      });
  }
  f.addEventListener('submit', e=>{
    e.preventDefault();
    const payload={
      ci: sanitizeInput(f.ci.value, 20),
      nombre: sanitizeInput(f.nombre.value, 50),
      apellido: sanitizeInput(f.apellido.value, 50),
      fecha_nac: f.fecha_nac.value || null,
      genero: f.genero.value || null
    };
    const method = edit ? 'PUT' : 'POST';
    const url = edit
      ? `http://localhost:5000/api/participantes/${encodeURIComponent(ciParam)}`
      : 'http://localhost:5000/api/participantes';
    fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
      .then(r=>r.json().then(j=>({ok:r.ok,j})))
      .then(res=>{
        if(res.ok){ alert(edit?'Participante actualizado':'Participante agregado'); location.href='../features/participantes.html'; }
        else alert('Error: '+(res.j.error||'')); 
      }).catch(()=>alert('Error de red'));
  });
});
