document.getElementById('manageForm').addEventListener('submit', async function (e) {
    e.preventDefault();
  
    const user_id = document.getElementById('user_id').value.trim();
    const reset_memory = document.getElementById('reset_memory').checked;
    const clear_chat = document.getElementById('clear_chat').checked;
    const remove_chunks = document.getElementById('remove_chunks').checked;
    const remove_embeddings = document.getElementById('remove_embeddings').checked;
    const remove_query_response = document.getElementById('remove_query_response').checked;
    const reseting = document.getElementById('reseting').checked;
  
    const bodyData = {
      reset_memory,
      clear_chat
    };
  
    const params = new URLSearchParams({
      user_id,
      remove_chunks: String(remove_chunks),
      remove_embeddings: String(remove_embeddings),
      remove_query_response: String(remove_query_response),
      reseting: String(reseting)
    });
  
    const responseBox = document.getElementById('responseBox');
    responseBox.style.display = 'none';
  
    try {
      const response = await fetch(`http://192.168.100.55:5000/api/chat/manage?${params.toString()}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyData)
      });
  
      const result = await response.json();
  
      responseBox.className = 'response-box';
      responseBox.classList.add(response.ok ? 'success' : 'error');
      responseBox.innerText = result.message || 'Unknown response.';
      responseBox.style.display = 'block';
  
    } catch (err) {
      responseBox.className = 'response-box error';
      responseBox.innerText = 'Failed to submit request.';
      responseBox.style.display = 'block';
    }
  });
  