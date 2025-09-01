// Add some interactivity
document.addEventListener('DOMContentLoaded', function() {
    // Set progress bar widths and animate them on load
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.getAttribute('data-width') + '%';
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });

    // Add click events to cards for better UX
    const paymentItems = document.querySelectorAll('.list-group-item');
    paymentItems.forEach(item => {
        item.style.cursor = 'pointer';
        item.addEventListener('click', function() {
            // You can add navigation logic here
            console.log('Item clicked:', this);
        });
    });
});