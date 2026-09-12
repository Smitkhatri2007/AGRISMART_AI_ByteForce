// ==========================================================================
// AgriSmart AI - Tabs Logic
// ==========================================================================

document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const target = tab.dataset.tab;

        // Update tab buttons
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Update tab sections
        document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
        const section = document.getElementById('tab-' + target);
        if (section) section.classList.add('active');
    });
});
