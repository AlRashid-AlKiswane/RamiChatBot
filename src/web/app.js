document.getElementById("appForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const modelName = document.getElementById("model_name").value;
    const configPath = document.getElementById("config_path").value;

    const responseBox = document.getElementById("response");
    responseBox.textContent = "Submitting...";

    try {
        const res = await fetch("http://192.168.100.55:5000/application", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model_name: modelName, config_path: configPath }),
        });

        const data = await res.json();
        responseBox.textContent = data.message;
    } catch (error) {
        responseBox.textContent = "Error submitting the request.";
    }
});
