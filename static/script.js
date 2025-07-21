document.addEventListener('DOMContentLoaded', function () {
    const checkboxes = document.querySelectorAll('.book-checkbox');
    const submitBtn = document.getElementById('submit-btn');
    const selectionCount = document.getElementById('selection-count');
    const wordEstimate = document.getElementById('word-estimate');
    const filenameInput = document.getElementById('filename');
    const loadingDiv = document.getElementById('loading');

    // Update selection info
    function updateSelectionInfo() {
        const selectedBoxes = document.querySelectorAll('.book-checkbox:checked');
        const count = selectedBoxes.length;

        let totalWords = 0;
        selectedBoxes.forEach(checkbox => {
            totalWords += parseInt(checkbox.dataset.words) || 0;
        });

        selectionCount.textContent = `${count} book${count !== 1 ? 's' : ''} selected`;

        if (count > 0) {
            wordEstimate.textContent = `~${totalWords.toLocaleString()} words estimated`;
        } else {
            wordEstimate.textContent = '';
        }

        // Validate selection
        validateSelection(selectedBoxes);
    }

    // Validate selection against constraints
    function validateSelection(selectedBoxes) {
        const selectedIds = Array.from(selectedBoxes).map(cb => cb.value);

        if (selectedIds.length === 0) {
            submitBtn.disabled = true;
            return;
        }

        // Client-side validation
        if (selectedIds.length > 10) {
            submitBtn.disabled = true;
            wordEstimate.textContent = 'Maximum 10 books allowed';
            wordEstimate.style.color = '#c00';
            return;
        }

        // Server-side validation
        fetch('/api/validate_selection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ selected_ids: selectedIds })
        })
            .then(response => response.json())
            .then(data => {
                if (data.valid) {
                    submitBtn.disabled = false;
                    wordEstimate.style.color = '#666';
                } else {
                    submitBtn.disabled = true;
                    wordEstimate.textContent = data.reason;
                    wordEstimate.style.color = '#c00';
                }
            })
            .catch(error => {
                console.error('Validation error:', error);
                submitBtn.disabled = true;
            });
    }

    // Add event listeners to checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectionInfo);
    });

    // Handle form submission
    submitBtn.addEventListener('click', function () {
        const selectedBoxes = document.querySelectorAll('.book-checkbox:checked');
        const selectedIds = Array.from(selectedBoxes).map(cb => cb.value);
        const filename = filenameInput.value.trim() || 'gutenberg_books.pdf';

        if (selectedIds.length === 0) {
            alert('Please select at least one book.');
            return;
        }

        // Ensure filename ends with .pdf
        const finalFilename = filename.endsWith('.pdf') ? filename : filename + '.pdf';

        // Show loading
        loadingDiv.classList.remove('hidden');
        submitBtn.disabled = true;

        // Generate PDF
        fetch('/generate_pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                selected_ids: selectedIds,
                filename: finalFilename
            })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('PDF generation failed');
                }
                return response.blob();
            })
            .then(blob => {
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = finalFilename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                // Hide loading
                loadingDiv.classList.add('hidden');
                submitBtn.disabled = false;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error generating PDF. Please try again.');
                loadingDiv.classList.add('hidden');
                submitBtn.disabled = false;
            });
    });

    // Initialize
    updateSelectionInfo();

    // Add this to the end of static/script.js

    // This function forcefully prevents clicks on any element with the 'disabled' class.
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('disabled')) {
            event.preventDefault();
            event.stopPropagation();
        }
    }, true); // The 'true' at the end is important; it makes the rule fire early.
});
