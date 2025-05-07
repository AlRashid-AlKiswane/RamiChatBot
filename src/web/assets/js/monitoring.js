const maxStrokeValue = 314.159; // For a circle with r=50

    function updateRing(elementId, value) {
      const ring = document.getElementById(`${elementId}-ring`);
      const textEl = document.getElementById(elementId);

      if (ring) {
        ring.style.strokeDashoffset = maxStrokeValue - (maxStrokeValue * value / 100);

        // Set ring stroke color like Matrix
        if (value > 80) {
          ring.style.stroke = '#f43f5e'; // red for high
        } else if (value < 20) {
          ring.style.stroke = '#4ade80'; // green for low
        } else {
          ring.style.stroke = '#facc15'; // yellow for normal
        }
      }

      if (textEl) {
        textEl.textContent = `${value}%`;
        if (value > 80) {
          textEl.setAttribute('data-usage', 'high');
        } else if (value < 20) {
          textEl.setAttribute('data-usage', 'low');
        } else {
          textEl.setAttribute('data-usage', 'normal');
        }
      }
    }

    async function fetchUsage(endpoint, elementId) {
      try {
        const res = await fetch(`http://192.168.100.55:5000/api/health/${endpoint}`);
        const data = await res.json();

        let value = typeof data === 'number' ? data
                   : data[`${endpoint}_usage`] ?? data.gpu_usage ?? 0;

        updateRing(elementId, value);
      } catch (err) {
        console.error(`Error fetching ${endpoint}:`, err);
        const el = document.getElementById(elementId);
        if (el) el.textContent = 'N/A';
      }
    }

    function updateAll() {
      fetchUsage('cpu', 'cpu');
      fetchUsage('memory', 'memory');
      fetchUsage('disk', 'disk');
      fetchUsage('gpu', 'gpu');
    }

    updateAll();
    setInterval(updateAll, 3000);