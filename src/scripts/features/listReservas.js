document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('reservasTbody');
  if (!tbody) return;

  function render(msg) {
    tbody.innerHTML = `<tr><td colspan="7">${msg}</td></tr>`;
  }
  function paint(list) {
    if (!Array.isArray(list) || list.length === 0) {
      render('Sin reservas');
      return;
    }
    tbody.innerHTML = '';
    list.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.id_reserva}</td>
        <td>${r.nombre_sala}</td>
        <td>${r.edificio}</td>
        <td>${r.fecha}</td>
        <td>${r.hora_inicio || ''}</td>
        <td>${r.hora_fin || ''}</td>
        <td>${r.estado || ''}</td>`;
      tbody.appendChild(tr);
    });
  }

  fetch('http://localhost:5000/api/reservas?cb=' + Date.now())
    .then(r => r.json().then(j => ({ ok: r.ok, body: j })))
    .then(res => {
      if (!res.ok) {
        render('Error cargando reservas');
        return;
      }
      paint(res.body);
    })
    .catch(() => render('Error cargando reservas'));
});
