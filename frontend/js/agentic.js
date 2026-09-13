// ==========================================================================
// AgriSmart AI - Autonomous Agentic Advisor Engine (Bonus Module G)
// Implements the 4-Stage Decision Loop: Perceive -> Reason -> Decide -> Notify
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    initAgenticAdvisor();
});

function initAgenticAdvisor() {
    const runBtn = document.getElementById('btnRunAgentCycle');
    if (runBtn) {
        runBtn.addEventListener('click', () => runAgentCycle());
    }

    const scenarioBtns = document.querySelectorAll('.agent-scenario-btn');
    scenarioBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            scenarioBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const scenario = btn.dataset.scenario;
            applyAgentScenario(scenario);
        });
    });

    // Run initial cycle on load after short delay
    setTimeout(() => {
        runAgentCycle();
    }, 1500);
}

function applyAgentScenario(scenario) {
    let crop = "Tomato";
    let stage = "Flowering";
    let disease = "Tomato Early Blight";
    let severity = "High";
    let moisture = 30;

    if (scenario === 'blight_storm') {
        crop = "Tomato";
        stage = "Flowering";
        disease = "Tomato Early Blight";
        severity = "Critical";
        moisture = 42;
    } else if (scenario === 'drought_vegetative') {
        crop = "Corn";
        stage = "Vegetative";
        disease = "Healthy";
        severity = "None";
        moisture = 22;
    } else if (scenario === 'healthy_equilibrium') {
        crop = "Potato";
        stage = "Maturity";
        disease = "Healthy";
        severity = "None";
        moisture = 55;
    }

    runAgentCycle(crop, stage, disease, severity, moisture);
}

async function runAgentCycle(crop = "Tomato", stage = "Flowering", disease = "Tomato Early Blight", severity = "High", moisture = 32) {
    const runBtn = document.getElementById('btnRunAgentCycle');
    const visualizer = document.getElementById('agentVisualizer');
    const alertBanner = document.getElementById('agentProactiveBanner');

    if (runBtn) {
        runBtn.disabled = true;
        runBtn.innerHTML = `<span class="spinner" style="width:14px;height:14px;display:inline-block;vertical-align:-2px;margin-right:6px;"></span> Reasoning...`;
    }

    // Highlight loop animation
    animateLoopStep('step-perceive');

    try {
        const lat = currentFarmLocation ? currentFarmLocation.lat : 23.02;
        const lon = currentFarmLocation ? currentFarmLocation.lon : 72.57;

        const cycle = await fetchAgenticCycle(
            crop,
            stage,
            disease,
            severity,
            moisture,
            "Loamy",
            lat,
            lon
        );

        // Sequence animation through the steps
        setTimeout(() => animateLoopStep('step-reason'), 400);
        setTimeout(() => animateLoopStep('step-decide'), 800);
        setTimeout(() => {
            animateLoopStep('step-notify');
            renderAgenticOutput(cycle);
        }, 1200);

    } catch (e) {
        console.error("Agentic cycle error:", e);
    } finally {
        setTimeout(() => {
            if (runBtn) {
                runBtn.disabled = false;
                runBtn.innerHTML = `⚡ Run Agentic Reasoning Cycle`;
            }
        }, 1300);
    }
}

function animateLoopStep(stepId) {
    document.querySelectorAll('.loop-step-card').forEach(c => c.classList.remove('active-step'));
    const target = document.getElementById(stepId);
    if (target) target.classList.add('active-step');
}

function renderAgenticOutput(cycle) {
    if (!cycle) return;

    // 1. Proactive Alert Banner
    const banner = document.getElementById('agentProactiveBanner');
    const bannerTitle = document.getElementById('agentBannerTitle');
    const bannerMsg = document.getElementById('agentBannerMsg');
    const bannerBadge = document.getElementById('agentBannerBadge');

    if (banner && cycle.notifications && cycle.notifications.length > 0) {
        const topNotif = cycle.notifications[0];
        if (bannerTitle) bannerTitle.textContent = topNotif.title;
        if (bannerMsg) bannerMsg.textContent = topNotif.message;
        if (bannerBadge) {
            bannerBadge.textContent = topNotif.badge;
            bannerBadge.className = `status-pill pill-${topNotif.severity === 'urgent' ? 'red' : 'amber'}`;
        }
        banner.style.display = 'flex';
    }

    // 2. Trace Accordion Details
    const trace = cycle.decision_loop_trace || {};

    // Perceive Log
    const percEl = document.getElementById('tracePerceiveList');
    if (percEl && trace.perceive) {
        percEl.innerHTML = trace.perceive.map(p => `
            <div class="trace-item">
                <span class="trace-tag">${p.source}</span>
                <p>${p.observation}</p>
            </div>
        `).join('');
    }

    // Reason Log
    const reasEl = document.getElementById('traceReasonList');
    if (reasEl && trace.reason) {
        reasEl.innerHTML = trace.reason.map(r => `
            <div class="trace-item trace-reason">
                <span class="trace-bullet">🧠</span>
                <p>${r}</p>
            </div>
        `).join('');
    }

    // Decide Log
    const decEl = document.getElementById('traceDecideList');
    if (decEl && trace.decide) {
        decEl.innerHTML = trace.decide.map(d => `
            <div class="trace-item trace-decision">
                <span class="status-pill pill-${d.priority === 'Critical' ? 'red' : 'amber'}">${d.priority}</span>
                <strong>${d.directive}</strong>
                <p style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">${d.rationale}</p>
            </div>
        `).join('');
    }

    // Notifications List
    const notifContainer = document.getElementById('agentNotifList');
    if (notifContainer && cycle.notifications) {
        notifContainer.innerHTML = cycle.notifications.map(n => `
            <div class="notif-card notif-${n.severity}">
                <div class="notif-header">
                    <span class="status-pill pill-${n.severity === 'urgent' ? 'red' : 'amber'}">${n.badge}</span>
                    <span class="notif-time">${n.created_at}</span>
                </div>
                <h4 class="notif-title">${n.title}</h4>
                <p class="notif-body">${n.message}</p>
                <div class="notif-actions">
                    <button class="btn-sm-action" onclick="acknowledgeAgentAction('${n.action_code}')">${n.action_label} ✓</button>
                </div>
            </div>
        `).join('');
    }
}

window.acknowledgeAgentAction = function(actionCode) {
    alert(`Autonomous Directive [${actionCode}] acknowledged and applied to active farm plan.`);
    const banner = document.getElementById('agentProactiveBanner');
    if (banner) banner.style.display = 'none';
};
