// ==========================================================================
// AgriSmart AI - Tabs Logic (Desktop & Android Mobile Navigation Sync)
// ==========================================================================

function switchTab(target) {
    if (!target) return;

    // Update desktop nav-tabs
    document.querySelectorAll('.nav-tab').forEach(t => {
        if (t.dataset.tab === target) {
            t.classList.add('active');
        } else {
            t.classList.remove('active');
        }
    });

    // Update mobile bottom navigation items
    document.querySelectorAll('.mobile-nav-item').forEach(m => {
        if (m.dataset.tab === target) {
            m.classList.add('active');
        } else {
            m.classList.remove('active');
        }
    });

    // Update tab sections
    document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
    const section = document.getElementById('tab-' + target);
    if (section) {
        section.classList.add('active');
        // Scroll smoothly to top of the view
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Expose globally for buttons across the app
window.switchTab = switchTab;

// Bind desktop tabs
document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        switchTab(tab.dataset.tab);
    });
});

// Bind mobile bottom nav items
document.querySelectorAll('.mobile-nav-item').forEach(item => {
    item.addEventListener('click', () => {
        switchTab(item.dataset.tab);
    });
});
