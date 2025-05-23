document.addEventListener('DOMContentLoaded', () => {

    document.getElementById("fileConvertTrigger").addEventListener("click", async () => {
        const fileInput = document.getElementById("fileSelect");
        const files = fileInput.files;
        const downloadBtn = document.getElementById("downloadBtn");

        if (files.length === 0) {
            alert("Please select at least one .ipynb file.");
            return;
        }

        // Disable download during processing
        downloadBtn.disabled = true;
        downloadBtn.innerText = "Processing...";

        const formData = new FormData();
        for (const file of files) {
            formData.append("notebooks", file);
        }

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            // Convert PDF response to Blob and create a download link
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);

            // Update download button
            downloadBtn.disabled = false;
            downloadBtn.innerText = "Download PDF";

            // Set up click to download and trigger cleanup
            downloadBtn.onclick = () => {
                const a = document.createElement("a");
                a.href = downloadUrl;
                a.download = "converted.pdf";
                document.body.appendChild(a);
                a.click();
                a.remove();

                // Tell server to delete the file
                fetch("/delete", { method: "POST" });
            };
        } catch (err) {
            alert("Conversion failed: " + err.message);
            downloadBtn.disabled = true;
            downloadBtn.innerText = "Download Failed";
        }
    });



    // const fileInput = document.getElementById('fileSelect');
    // const fileLabel = document.getElementById('selectedfile');
    // const convertTrigger = document.getElementById('fileConvertTrigger');

    // fileInput.addEventListener('change', () => {
    //     fileLabel.textContent = fileInput.files.length > 0 
    //         ? `${fileInput.files.length} files selected` 
    //         : 'No files selected';
    // });

    // convertTrigger.addEventListener('click', function (event) {
    //     event.preventDefault();

    //     // Explicitly create FormData and append files
    //     const formData = new FormData();
    //     const files = fileInput.files;

    //     if (files.length === 0) {
    //         alert("Please select at least one .ipynb file!");
    //         return;
    //     }

    //     for (let i = 0; i < files.length; i++) {
    //         formData.append('notebooks', files[i]); // Key must be "notebooks"
    //     }

    //     fetch('/upload', {
    //         method: 'POST',
    //         body: formData
    //     })
    //     .then(response => {
    //         if (!response.ok || response.headers.get("Content-Type") !== "application/pdf") {
    //             throw new Error("Failed to download PDF.");
    //         }
    //         return response.blob();
    //     })
    //     .then(blob => {
    //         const url = window.URL.createObjectURL(blob);
    //         const a = document.createElement('a');
    //         a.href = url;
    //         a.download = 'MergedNotebook_Numbered.pdf';
    //         document.body.appendChild(a);
    //         a.click();
    //         window.URL.revokeObjectURL(url);
    //     })
    //     .catch(error => {
    //         console.error('Error:', error);
    //         alert(`Error: ${error.message}`);
    //     });
    // });
});
