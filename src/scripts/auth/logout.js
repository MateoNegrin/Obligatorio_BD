document.addEventListener('DOMContentLoaded', function () {
  // Verificar si el usuario está logueado
  let isLoggedIn = false;
  try { isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'; } catch (e) { isLoggedIn = false; }
  
  const logoutBtn = document.getElementById('logoutBtn');
  const loginBtn = document.getElementById('loginBtn');
  
  // Mostrar/ocultar botones según estado de login (para páginas públicas como consultas)
  if (loginBtn && logoutBtn) {
    if (isLoggedIn) {
      loginBtn.style.display = 'none';
      logoutBtn.style.display = 'inline-block';
    } else {
      loginBtn.style.display = 'inline-block';
      logoutBtn.style.display = 'none';
    }
  }
  
  if (!logoutBtn) return;
  
  logoutBtn.addEventListener('click', function (e) {
    e.preventDefault();
    try { localStorage.removeItem('isLoggedIn'); } catch (err) {}
    // Detectar la ruta correcta basada en la ubicación actual
    const currentPath = window.location.pathname;
    let homepagePath = 'homepage.html';
    
    if (currentPath.includes('/features/') || currentPath.includes('/forms/')) {
      homepagePath = '../homepage.html';
    } else if (currentPath.includes('/login/')) {
      homepagePath = '../homepage.html';
    }
    
    window.location.href = homepagePath;
  });
});
