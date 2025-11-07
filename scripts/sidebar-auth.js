document.addEventListener('DOMContentLoaded', function () {
  let isLoggedIn = false;
  try { isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'; } catch (e) { isLoggedIn = false; }

  const sidebar = document.querySelector('.sidebar');
  if (!sidebar) return;

  if (isLoggedIn) return;


  const links = sidebar.querySelectorAll('.sidebar-link');
  const currentPage = (location.pathname || '').split('/').pop();
  links.forEach(link => {
    const a = link.querySelector('a.sidebar-anchor');
    if (!a) return;
    const isPublic = a.getAttribute('data-public') === 'true';
    const hrefPage = (a.getAttribute('href') || '').split('/').pop();
    if (!isPublic && hrefPage !== currentPage) {
      link.style.display = 'none';
    }
  });

});
