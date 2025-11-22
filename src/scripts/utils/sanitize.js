function sanitizeInput(value, maxLen = 128) {
    if (typeof value !== 'string') return '';
    let s = value.trim();
    if (s.length > maxLen) s = s.slice(0, maxLen);
    s = s.replace(/[\u0000-\u001F\u007F<>"'`#;\\]/g, '');
    return s;
}
export default sanitizeInput;