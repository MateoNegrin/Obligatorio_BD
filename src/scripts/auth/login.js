document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('.login-box');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const formError = document.getElementById('form-error');


  function sanitizeInput(value, maxLen = 128) {
    if (typeof value !== 'string') return '';
    let s = value.trim();
    if (s.length > maxLen){
        s = s.slice(0, maxLen);
    } 
    s = s.replace(/[\u0000-\u001F\u007F<>"'`#;\\]/g, '');
    return s;
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const username = sanitizeInput(usernameInput.value, 64);
    const password = sanitizeInput(passwordInput.value, 64);

    const hardcodedUser = 'admin';
    const hardcodedPass = 'admin123';
    if (username === hardcodedUser && password === hardcodedPass) {
      try { localStorage.setItem('isLoggedIn', 'true'); } catch (e) { }
      window.location.href = '../adminDashboard.html';
    } else {
      formError.textContent = 'Usuario o contraseña inválidos.';
      passwordInput.value = '';
      passwordInput.focus();
    }
    
  });
});
