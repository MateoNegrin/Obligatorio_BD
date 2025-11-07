document.addEventListener('DOMContentLoaded', function () {
  const logoutBtn = document.getElementById('logoutBtn');
  if (!logoutBtn) return;
  logoutBtn.addEventListener('click', function (e) {
    e.preventDefault();
    try { localStorage.removeItem('isLoggedIn'); } catch (err) {}
    window.location.href = 'homepage.html';
  });
});
