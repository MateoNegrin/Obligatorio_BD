document.addEventListener('DOMContentLoaded', () => {
  const tbody = document.getElementById('reservasTbody');
  if (!tbody) return;
  const hosts = ['http://localhost:5000','http://127.0.0.1:5000'];

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
  function fetchJson(url, ok, fail) {
    fetch(url)
      .then(r => r.json().then(j => ({ok:r.ok,status:r.status,body:j})).catch(()=>({ok:r.ok,status:r.status,body:null})))
      .then(res => {
        if (!res.ok) fail(`HTTP ${res.status}`, res.body);
        else ok(res.body);
      })
      .catch(e => fail('network', e));
  }
  function loadHost(i=0) {
    if (i>=hosts.length) { render('Error cargando reservas (sin conexión)'); return; }
    const base = hosts[i];
    const mainUrl = `${base}/api/reservas?cb=${Date.now()}`;
    fetchJson(mainUrl,
      data => {
        if (!Array.isArray(data) || data.length === 0) {
          const simpleUrl = `${base}/api/reservas/simple?cb=${Date.now()}`;
          fetchJson(simpleUrl,
            simple => {
              if (!Array.isArray(simple) || simple.length === 0) {
                loadHost(i+1);
              } else paint(simple);
            },
            () => loadHost(i+1)
          );
        } else paint(data);
      },
      () => {
        const simpleUrl = `${base}/api/reservas/simple?cb=${Date.now()}`;
        fetchJson(simpleUrl,
          simple => {
            if (!Array.isArray(simple) || simple.length === 0) loadHost(i+1);
            else paint(simple);
          },
          () => loadHost(i+1)
        );
      }
    );
  }
  loadHost();
});
