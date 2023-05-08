// Fetch the article data from the backend
fetch('/api/v1/articless/<int:id>')  // Replace with the appropriate endpoint for retrieving the article data
    .then(response => response.json())
    .then(data => {
        const articleContainer = document.getElementById('article-container');

        // Iterate over the article data and create clickable elements
        for (const section in data) {
            const sectionData = data[section];
            const sectionElement = document.createElement('div');

            for (const item of sectionData) {
                const itemElement = document.createElement('span');
                itemElement.innerText = item.Text;

                // Add a click event listener to show the translation dialog
                itemElement.addEventListener('click', () => {
                    showTranslationDialog(item.Text);
                });

                sectionElement.appendChild(itemElement);
            }

            articleContainer.appendChild(sectionElement);
        }
    });

// Show the translation dialog with the translation of the clicked word
function showTranslationDialog(word) {
    // Fetch the translation from the backend
    fetch('/api/v1/dictionary/add/', {
        method: 'POST',
        body: JSON.stringify({ word: word }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const translationText = document.getElementById('translation-text');
        translationText.innerText = data.translation;

        const translationDialog = document.getElementById('translation-dialog');
        translationDialog.classList.remove('hide');
    });
}

// Hide the translation dialog
function hideTranslationDialog() {
    const translationDialog = document.getElementById('translation-dialog');
    translationDialog.classList.add('hide');
}

// Add event listener to the save button in the translation dialog
const saveButton = document.getElementById('save-button');
saveButton.addEventListener('click', () => {
    // Perform the save operation to the backend
    // ...

    // Hide the translation dialog
    hideTranslationDialog();
});
