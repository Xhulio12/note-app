document.addEventListener("DOMContentLoaded", function() {
    const path = window.location.pathname.replace(/\/$/, ""); // remove trailing slash
    const navLinks = document.querySelectorAll(".nav-link");

    // Remove active from all links first
    navLinks.forEach(link => link.classList.remove("active"));

    // Set active based on pathname
    navLinks.forEach(link => {
        const href = link.getAttribute("href").replace(/\/$/, ""); // remove trailing slash
        if (href === path || (href !== '' && path.startsWith(href + '/'))) {
            link.classList.add("active");
        }
    });
});

document.getElementById('currentYear').textContent = new Date().getFullYear();