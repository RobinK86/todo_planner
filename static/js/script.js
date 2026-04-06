console.log("JS loaded");

document.addEventListener("DOMContentLoaded", function () {
    const categoryField = document.querySelector('[name="category"]');

    const lifeFields = document.getElementById('life-fields');
    const schoolFields = document.getElementById('school-fields');
    const workFields = document.getElementById('work-fields');

    function updateCategoryFields() {
        if (!categoryField || !lifeFields || !schoolFields || !workFields) return;

        const value = categoryField.value;

        lifeFields.style.display = 'none';
        schoolFields.style.display = 'none';
        workFields.style.display = 'none';

        if (value === 'life') {
            lifeFields.style.display = 'block';
        } else if (value === 'school') {
            schoolFields.style.display = 'block';
        } else if (value === 'work') {
            workFields.style.display = 'block';
        }
    }

    if (categoryField) {
        categoryField.addEventListener('change', updateCategoryFields);
        updateCategoryFields();
    }

    // Completed task toggle
    const completedCards = document.querySelectorAll('.task-card.completed');
    const toggleBtn = document.getElementById('toggle-completed-btn');

    if (completedCards.length > 0 && toggleBtn) {
        completedCards.forEach(card => card.style.display = 'none');
        toggleBtn.textContent = `Show completed (${completedCards.length})`;
        toggleBtn.style.display = 'inline-block';

        let showing = false;
        toggleBtn.addEventListener('click', function () {
            showing = !showing;
            completedCards.forEach(card => {
                card.style.display = showing ? '' : 'none';
            });
            toggleBtn.textContent = showing
                ? `Hide completed (${completedCards.length})`
                : `Show completed (${completedCards.length})`;
        });
    }

    const checklistContainer = document.getElementById('checklist-container');
    const addChecklistBtn = document.getElementById('add-checklist-item-btn');

    function attachRemoveHandlers() {
        const removeButtons = document.querySelectorAll('.remove-item-btn');

        removeButtons.forEach(button => {
            button.onclick = function () {
                const rows = document.querySelectorAll('.checklist-input-row');

                if (rows.length > 1) {
                    button.parentElement.remove();
                } else {
                    const input = button.parentElement.querySelector('input[name="checklist_items"]');
                    if (input) {
                        input.value = '';
                    }
                }
            };
        });
    }

    if (checklistContainer && addChecklistBtn) {
        addChecklistBtn.addEventListener('click', function () {
            const row = document.createElement('div');
            row.className = 'checklist-input-row';

            row.innerHTML = `
                <input type="text" name="checklist_items" placeholder="Enter checklist item">
                <button type="button" class="remove-item-btn">Remove</button>
            `;

            checklistContainer.appendChild(row);
            attachRemoveHandlers();
        });

        attachRemoveHandlers();
    }
});