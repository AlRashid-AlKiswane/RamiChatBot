document.getElementById("chunkForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const resultBox = document.getElementById("chunkResult");
    const filePath = document.getElementById("filePath").value.trim();
    const doReset = document.getElementById("doReset").value;

    const payload = {
        file_path: filePath || null,
        do_reset: parseInt(doReset)
    };

    resultBox.innerHTML = "Processing...";

    try {
        const response = await fetch("http://192.168.100.55:5000/api/to_chunks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            resultBox.innerHTML = `✅ ${data.inserted_chunks} chunks inserted.\n\nDocuments:\n` +
                JSON.stringify(data.documents, null, 2);
        } else {
            resultBox.innerHTML = `❌ Error: ${data.message}`;
        }
    } catch (error) {
        resultBox.innerHTML = "❌ Failed to connect to the server.";
        console.error("Error:", error);
    }
});
