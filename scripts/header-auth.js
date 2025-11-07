document.addEventListener('DOMContentLoaded', function () {
  let isLoggedIn = false;
  try { isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'; } catch (e) { isLoggedIn = false; }
  if (!isLoggedIn) return;

  const headerLink = document.querySelector('.header-link');
  if (!headerLink) return;

  headerLink.setAttribute('href', 'adminDashboard.html');
});
