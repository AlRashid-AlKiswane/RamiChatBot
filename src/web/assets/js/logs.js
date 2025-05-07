async function fetchLogs() {
    try {
      const response = await fetch("http://192.168.100.55:5000/api/logs");
      const logs = await response.text();
      document.getElementById("log-output").textContent = logs;
      document.getElementById("last-updated").textContent =
        "Last updated: " + new Date().toLocaleTimeString();
    } catch (error) {
      document.getElementById("log-output").textContent = "Failed to fetch logs.";
      console.error("Error fetching logs:", error);
    }
  }

  fetchLogs(); // Fetch initially
  setInterval(fetchLogs, 60000); // Update every 60 seconds