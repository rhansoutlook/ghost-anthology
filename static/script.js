document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.book-checkbox');
    const submitBtn = document.getElementById('submit-btn');
    const selectionCount = document.getElementById('selection-count');
    const validationMessage = document.getElementById('validation-message'); // Our new message area
    const filenameInput = document.getElementById('filename');
    const loadingDiv = document.getElementById('loading');

    // Restore the full validation logic
    function updateSelectionInfo() {
        const selectedBoxes = document.querySelectorAll('.book-checkbox:checked');
        selectionCount.textContent = `${selectedBoxes.length} book${selectedBoxes.length !== 1 ? 's' : ''} selected`;
        validateSelection(selectedBoxes);
    }

    // This function calls the server to validate the user's selection
    function validateSelection(selectedBoxes) {
        const selectedIds = Array.from(selectedBoxes).map(cb => cb.value);
        
        // Clear previous messages and disable button before validating
        validationMessage.textContent = '';
        if (selectedIds.length === 0) {
            submitBtn.disabled = true;
            return;
        }

        // Call the server-side validation API
        fetch('/api/validate_selection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ selected_ids: selectedIds })
        })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                // If valid, enable the button and show useful info
                submitBtn.disabled = false;
                validationMessage.style.color = '#333'; // Use normal text color
                validationMessage.textContent = `~${data.estimated_words.toLocaleString()} words`;
            } else {
                // If invalid, disable the button and show the reason
                submitBtn.disabled = true;
                validationMessage.style.color = '#c00'; // Use red error color
                validationMessage.textContent = data.reason;
            }
        })
        .catch(error => {
            console.error('Validation error:', error);
            submitBtn.disabled = true;
            validationMessage.textContent = 'Error during validation.';
        });
    }

    // Add event listeners to checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectionInfo);
    });

    // Handle form submission
    submitBtn.addEventListener('click', function() {
        const selectedBoxes = document.querySelectorAll('.book-checkbox:checked');
        const selectedIds = Array.from(selectedBoxes).map(cb => cb.value);
        const filename = filenameInput.value.trim() || 'gutenberg_books.pdf';

        if (selectedIds.length === 0) { return; } // Should be disabled anyway

        const finalFilename = filename.endsWith('.pdf') ? filename : filename + '.pdf';

        loadingDiv.classList.remove('hidden');
        submitBtn.disabled = true;

        fetch('/generate_pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                selected_ids: selectedIds,
                filename: finalFilename
            })
        })
        .then(response => {
            if (!response.ok) {
                // Try to get a specific error message from the server
                return response.json().then(err => { throw new Error(err.error || 'PDF generation failed') });
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = finalFilename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            loadingDiv.classList.add('hidden');
            updateSelectionInfo(); // Re-validate the selection
        })
        .catch(error => {
            console.error('Error:', error);
            alert(`Error generating PDF: ${error.message}`);
            loadingDiv.classList.add('hidden');
            updateSelectionInfo(); // Re-validate to re-enable button if possible
        });
    });

    // Initialize on page load
    updateSelectionInfo();
    
    // This listener prevents clicks on any element with the 'disabled' class.
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('disabled')) {
            event.preventDefault();
            event.stopPropagation();
        }
    }, true);
});