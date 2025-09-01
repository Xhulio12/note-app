document.addEventListener("DOMContentLoaded", () => {
    console.log("payments.js loaded");

    const urlParams = new URLSearchParams(window.location.search);

    // --- Case 1: Editing a payment (payment_id in URL) ---
    const paymentId = urlParams.get("payment_id");
    if (paymentId) {
        const paymentToEditRow = document.querySelector(`tr[data-id="${paymentId}"]`);
        if (paymentToEditRow) {
            document.getElementById("paymentModalLabel").innerText = "Edit Payment";
            document.getElementById("modal_payment_id").value = paymentToEditRow.dataset.id;
            document.getElementById("modal_name").value = paymentToEditRow.dataset.name;
            document.getElementById("modal_pmt_date").value = paymentToEditRow.dataset.pmt_date;
            document.getElementById("modal_pmt_amount").value = paymentToEditRow.dataset.pmt_amount;
            document.getElementById("modal_notes").value = paymentToEditRow.dataset.notes;
            document.getElementById("modal_is_active").checked = paymentToEditRow.dataset.is_active === "true";

            new bootstrap.Modal(document.getElementById('paymentModal')).show();
        }
    }

    // --- Case 2: Adding a new payment (add_payment=true OR show_form=1) ---
    if (urlParams.get("add_payment") === "true" || urlParams.get("show_form") === "1") {
        console.log("Opening Add Payment form...");
        resetForm();
    }

    // --- Edit buttons inside table ---
    document.querySelectorAll(".edit-payment-btn").forEach(button => {
        button.addEventListener("click", () => {
            const row = button.closest("tr");
            document.getElementById("paymentModalLabel").innerText = "Edit Payment";
            document.getElementById("modal_payment_id").value = row.dataset.id;
            document.getElementById("modal_name").value = row.dataset.name;
            document.getElementById("modal_pmt_date").value = row.dataset.pmt_date;
            document.getElementById("modal_pmt_amount").value = row.dataset.pmt_amount;
            document.getElementById("modal_notes").value = row.dataset.notes;
            document.getElementById("modal_is_active").checked = row.dataset.is_active === "true";

            new bootstrap.Modal(document.getElementById('paymentModal')).show();
        });
    });
});

// --- Reset function for Add Payment ---
function resetForm() {
    document.getElementById("paymentModalLabel").innerText = "Add Payment";
    document.getElementById("modal_payment_id").value = "";
    document.getElementById("modal_name").value = "";
    document.getElementById("modal_pmt_date").value = "";
    document.getElementById("modal_pmt_amount").value = "";
    document.getElementById("modal_notes").value = "";
    document.getElementById("modal_is_active").checked = true;

    new bootstrap.Modal(document.getElementById('paymentModal')).show();
}
