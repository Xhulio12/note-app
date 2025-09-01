document.addEventListener("DOMContentLoaded", function() {
    const editButtons = document.querySelectorAll(".edit-note-btn");
    const noteForm = document.getElementById("noteForm");

    editButtons.forEach(button => {
        button.addEventListener("click", function() {
            const row = button.closest("tr");
            const noteId = row.dataset.id;
            const title = row.dataset.title;
            const text = row.dataset.text;

            // Fill the form
            document.getElementById("note_id").value = noteId;
            document.getElementById("title").value = title;
            document.getElementById("text_content").value = text;

            // Change form action to edit route
            noteForm.action = `/notes/edit/${noteId}`;
        });
    });
});
