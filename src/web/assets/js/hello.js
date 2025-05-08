async function fetchAppInfo() {
    try {
        const response = await fetch('http://192.168.100.55:5000/api/hello');
        const data = await response.json();
        document.getElementById('response').innerHTML = `
            <strong>App Name:</strong> ${data["App Name"]}<br>
            <strong>Version:</strong> ${data["Version"]}<br>
            <strong>Message:</strong> ${data["Message"]}
        `;
    } catch (error) {
        document.getElementById('response').innerHTML = `<span style="color: red;">Error fetching data</span>`;
        console.error("Fetch error:", error);
    }
}
