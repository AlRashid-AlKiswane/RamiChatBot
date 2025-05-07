async function fetchAppInfo() {
    const resultBox = document.getElementById("result");
    resultBox.innerHTML = "Loading...";

    try {
        const response = await fetch("http://192.168.100.55:5000/api/hello");
        const data = await response.json();

        resultBox.innerHTML = `
            <strong>App Name:</strong> ${data["App Name"]}<br>
            <strong>Version:</strong> ${data["Version"]}<br>
            <strong>Message:</strong> ${data["Message"]}
        `;
    } catch (error) {
        resultBox.innerHTML = "Failed to fetch app info.";
        console.error("Error fetching data:", error);
    }
}
