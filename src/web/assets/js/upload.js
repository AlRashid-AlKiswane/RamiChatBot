document.getElementById("uploadForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const resultBox = document.getElementById("uploadResult");
    const fileInput = document.getElementById("fileInput");

    if (!fileInput.files.length) {
        resultBox.innerHTML = "Please select a file.";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    resultBox.innerHTML = "Uploading...";

    try {
        const response = await fetch("http://192.168.100.55:5000/api/upload/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            resultBox.innerHTML = `
                ✅ ${data.message}<br>
                <strong>Filename:</strong> ${data.filename}<br>
                <strong>Saved To:</strong> ${data.saved_to}
            `;
        } else {
            resultBox.innerHTML = `❌ Upload failed: ${data.detail}`;
        }
    } catch (error) {
        resultBox.innerHTML = "❌ Upload failed due to an error.";
        console.error("Upload error:", error);
    }
});
