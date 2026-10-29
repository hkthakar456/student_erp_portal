// Beacon Student ERP Portal - Frontend Interactivity

document.addEventListener("DOMContentLoaded", () => {
    // 1. Mobile Sidebar Navigation Toggle
    const mobileToggle = document.getElementById("mobileToggle");
    const sidebar = document.getElementById("appSidebar");
    const sidebarBackdrop = document.getElementById("sidebarBackdrop");

    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener("click", () => {
            sidebar.classList.toggle("open");
            if (sidebarBackdrop) {
                sidebarBackdrop.classList.toggle("active");
            }
        });
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener("click", () => {
            if (sidebar) sidebar.classList.remove("open");
            sidebarBackdrop.classList.remove("active");
        });
    }

    // 2. Flash Message Dismissal
    document.querySelectorAll(".alert-close").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const alert = e.target.closest(".alert");
            if (alert) {
                alert.style.opacity = "0";
                setTimeout(() => alert.remove(), 200);
            }
        });
    });

    // 3. Client-side quick filter on data tables (instant search)
    const quickSearchInput = document.getElementById("quickTableFilter");
    if (quickSearchInput) {
        quickSearchInput.addEventListener("input", (e) => {
            const term = e.target.value.toLowerCase().trim();
            const table = document.querySelector(".filterable-table tbody");
            if (!table) return;

            const rows = table.querySelectorAll("tr");
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(term) ? "" : "none";
            });
        });
    }

    // 4. Score percentage calculation preview on grade input
    const scoreInput = document.getElementById("gradeScoreInput");
    const maxScoreInput = document.getElementById("gradeMaxScoreInput");
    const pctPreview = document.getElementById("gradePercentagePreview");

    function updatePct() {
        if (!scoreInput || !maxScoreInput || !pctPreview) return;
        const score = parseFloat(scoreInput.value);
        const maxScore = parseFloat(maxScoreInput.value);
        if (!isNaN(score) && !isNaN(maxScore) && maxScore > 0) {
            const pct = ((score / maxScore) * 100).toFixed(1);
            pctPreview.textContent = `Calculated: ${pct}%`;
            pctPreview.style.color = pct >= 60 ? "#10b981" : "#ef4444";
        } else {
            pctPreview.textContent = "";
        }
    }

    if (scoreInput && maxScoreInput) {
        scoreInput.addEventListener("input", updatePct);
        maxScoreInput.addEventListener("input", updatePct);
    }
});
