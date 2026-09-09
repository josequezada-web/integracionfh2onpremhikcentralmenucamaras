// Enhance the existing forms; submission still uses the Flask routes.
document.querySelectorAll('[data-delete-name]').forEach(button => {
    button.addEventListener('click', event => {
        if (!window.confirm(`¿Eliminar ${button.dataset.deleteName}?`)) event.preventDefault();
    });
});
const search = document.getElementById('camera-search');
search?.addEventListener('input', () => {
    const query = search.value.trim().toLocaleLowerCase('es');
    let visible = 0;
    document.querySelectorAll('[data-camera-search]').forEach(card => {
        card.hidden = !card.dataset.cameraSearch.toLocaleLowerCase('es').includes(query);
        if (!card.hidden) visible++;
    });
    document.getElementById('camera-no-results').hidden = visible > 0 || !query;
});
