function enableEditing() {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => input.removeAttribute('readonly'));
}
