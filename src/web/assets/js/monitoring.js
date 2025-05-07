async function fetchUsage(endpoint, elementId) {
    try {
      const response = await fetch(`http://192.168.100.55:5000/api/health/${endpoint}`);
      const data = await response.json();
      const value = typeof data === 'number' ? data : data[`${endpoint}_usage`] || data.gpu_usage || 0;
      document.getElementById(elementId).textContent = `${value}%`;
    } catch (error) {
      console.error(`Error fetching ${endpoint} usage:`, error);
      document.getElementById(elementId).textContent = 'N/A';
    }
  }
  
  function updateAll() {
    fetchUsage('cpu', 'cpu');
    fetchUsage('memory', 'memory');
    fetchUsage('disk', 'disk');
    fetchUsage('gpu', 'gpu');
  }
  
  updateAll();
  setInterval(updateAll, 3000); // refresh every 3 seconds
  