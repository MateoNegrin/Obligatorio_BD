document.addEventListener('DOMContentLoaded', function () {
  let isLoggedIn = false;
  try { isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'; } catch (e) { isLoggedIn = false; }
  if (!isLoggedIn) return;

  const headerLink = document.querySelector('.header-link');
  if (!headerLink) return;

  // Detectar la ruta correcta basada en la ubicación actual
  const currentPath = window.location.pathname;
  let adminDashboardPath = 'adminDashboard.html';
  
  if (currentPath.includes('/features/') || currentPath.includes('/forms/')) {
    adminDashboardPath = '../adminDashboard.html';
  } else if (currentPath.includes('/login/')) {
    adminDashboardPath = '../adminDashboard.html';
  }
  
  headerLink.setAttribute('href', adminDashboardPath);
});
