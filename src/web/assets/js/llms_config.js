document.addEventListener("DOMContentLoaded", () => {
    const loadTypeSelector = document.getElementById("load_type");
    const hfFields = document.getElementById("hf-fields");
    const cppFields = document.getElementById("cpp-fields");
    const form = document.getElementById("modelForm");
    const successMessage = document.getElementById("successMessage");
  
    loadTypeSelector.addEventListener("change", () => {
      const selected = loadTypeSelector.value;
      hfFields.style.display = selected === "HF" ? "block" : "none";
      cppFields.style.display = selected === "lCPP" ? "block" : "none";
    });
  
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const loadType = loadTypeSelector.value;
      const endpoint = "http://192.168.100.55:5000/api/application";
  
      let payload = {
        body: null,
        cpp_body: null
      };
  
      if (loadType === "HF") {
        payload.body = {
          model_name: document.getElementById("model_name").value,
          max_new_tokens: parseInt(document.querySelector("[name='max_new_tokens']").value),
          temperature: parseFloat(document.querySelector("[name='temperature']").value),
          top_p: parseFloat(document.querySelector("[name='top_p']").value),
          top_k: parseInt(document.querySelector("[name='top_k']").value),
          trust_remote_code: document.getElementById("trust_remote_code").checked,
          do_sample: document.getElementById("do_sample").checked,
          quantization: document.getElementById("quantization_toggle").checked,
          quantization_type: document.getElementById("quantization_type").value
        };
      }
  
      if (loadType === "lCPP") {
        payload.cpp_body = {
          repo_id: document.getElementById("repo_id").value,
          filename: document.getElementById("filename").value,
          n_ctx: parseInt(document.getElementById("n_ctx").value),
          n_threads: parseInt(document.getElementById("n_threads").value),
          seed: parseInt(document.getElementById("seed").value),
          n_gpus: parseInt(document.getElementById("n_gpus").value),
          verbose: document.getElementById("verbose").checked,
          max_tokens: parseInt(document.getElementById("max_tokens").value),
          temperature: parseFloat(document.getElementById("cpp_temperature").value),
          top_p: parseFloat(document.getElementById("cpp_top_p").value),
          echo: document.getElementById("echo").checked,
          stop: document.getElementById("stop").value
            .split(",")
            .map(s => s.trim())
            .filter(s => s !== "")
        };
      }
  
      try {
        const response = await fetch(`${endpoint}?load_type=${loadType}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });
  
        const data = await response.json();
  
        successMessage.style.display = "block";
        if (response.ok) {
          successMessage.textContent = data.message || "Model initialized successfully.";
          successMessage.style.color = "green";
        } else {
          successMessage.textContent = data.detail || "Error applying model settings.";
          successMessage.style.color = "red";
        }
      } catch (err) {
        successMessage.style.display = "block";
        successMessage.textContent = "Network or parsing error: " + err.message;
        successMessage.style.color = "red";
      }
    });
  });
  