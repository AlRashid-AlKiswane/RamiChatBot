document.getElementById("convertButton").addEventListener("click", async function () {
    const resultBox = document.getElementById("embeddingResult");
    resultBox.innerHTML = "Processing...";

    try {
        const response = await fetch("http://192.168.100.55:5000/api/chunks_to_embedding", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();

        if (response.ok) {
            resultBox.innerHTML = `✅ Embedding conversion successful.`;
        } else {
            resultBox.innerHTML = `❌ Error: ${data.detail}`;
        }
    } catch (error) {
        resultBox.innerHTML = "❌ Failed to connect to the server.";
        console.error("Error:", error);
    }
});
