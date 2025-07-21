document.addEventListener('DOMContentLoaded', function() {
    // --- Step 1: Get references to all HTML elements ("The Wiring") ---
    const checkboxes = document.querySelectorAll('.book-checkbox');
    const submitBtn = document.getElementById('submit-btn');
    const selectionCount = document.getElementById('selection-count');
    const validationMessage = document.getElementById('validation-message');
    const loadingDiv = document.getElementById('loading');

    // --- Step 2: Define the functions that do the work ---

    // This function calls the server to validate the user's selection
    function validateSelection(selectedBoxes) {
        const selectedIds = Array.from(selectedBoxes).map(cb => cb.value);
        
        validationMessage.textContent = ''; // Clear previous messages
        if (selectedIds.length === 0) {
            submitBtn.disabled = true;
            return;
        }

        // Call the server API
        fetch('/api/validate_selection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ selected_ids: selectedIds })
        })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                submitBtn.disabled = false;
                validationMessage.style.color = '#333'; // Normal text color
                validationMessage.textContent = `~${data.estimated_words.toLocaleString()} words`;
            } else {
                submitBtn.disabled = true;
                validationMessage.style.color = '#c00'; // Red error color
                validationMessage.textContent = data.reason;
            }
        })
        .catch(error => {
            console.error('Validation error:', error);
            submitBtn.disabled = true;
            validationMessage.textContent = 'Error during validation.';
        });
    }

    // This is the main function that runs when a checkbox is clicked
    function updateSelectionInfo() {
        const selectedBoxes = document.querySelectorAll('.book-checkbox:checked');
        selectionCount.textContent = `${selectedBoxes.length} book${selectedBoxes.length !== 1 ? 's' : ''} selected`;
        validateSelection(selectedBoxes);
    }
    
    // --- Step 3: Attach the event listeners ---

    // Listen for 'change' events on every checkbox
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectionInfo);
    });

    // Listen for 'click' events on the "Generate PDF" button
    if (submitBtn) { // Check if the button exists before adding listener
        submitBtn.addEventListener('click', function() {
            const selectedBoxes = document.querySelectorAll('.book-checkbox:checked');
            const selectedIds = Array.from(selectedBoxes).map(cb => cb.value);

            if (selectedIds.length === 0) { return; }

            // Generate the timestamped filename
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const finalFilename = `gutenberg-${year}-${month}-${day}_${hours}${minutes}${seconds}.pdf`;

            loadingDiv.classList.remove('hidden');
            submitBtn.disabled = true;

            // Fetch the PDF from the server
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
                    return response.json().then(err => { throw new Error(err.error || 'PDF generation failed') });
                }
                return response.blob();
            })
            .then(blob => {
                // Trigger the browser download
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
                updateSelectionInfo();
            });
        });
    }

    // Universal listener to prevent clicks on disabled pagination buttons
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('disabled')) {
            event.preventDefault();
            event.stopPropagation();
        }
    }, true);

    // --- Step 4: Run once on page load to set the initial button state ---
    updateSelectionInfo();
});