const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');

// Highlight drop zone on drag over
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

// Remove highlight on drag leave
dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

// Handle file drop
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = e.dataTransfer.files;
    fileInput.files = files; // Assign dropped files to the hidden input

    // Clear and update file list
    fileList.innerHTML = ""; // Reset file list
    for (let file of files) {
        const li = document.createElement('li');
        li.textContent = file.name;
        fileList.appendChild(li);
    }
});

// Handle click to open file dialog
dropZone.addEventListener('click', () => {
    fileInput.click();
});

// Handle file selection via input
fileInput.addEventListener('change', () => {
    const files = fileInput.files;

    // Clear and update file list
    fileList.innerHTML = ""; // Reset file list
    for (let file of files) {
        const li = document.createElement('li');
        li.textContent = file.name;
        fileList.appendChild(li);
    }
});