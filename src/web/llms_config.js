document.getElementById("modelType").addEventListener("change", function () {
    const selectedModelType = this.value;
    document.getElementById("huggingfaceConfig").style.display = selectedModelType === "huggingface" ? "block" : "none";
    document.getElementById("llamaConfig").style.display = selectedModelType === "llama_cpp" ? "block" : "none";
});

document.getElementById("llmConfigForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const modelType = document.getElementById("modelType").value;
    const configData = new FormData(this);

    let url = "";
    let bodyData = {};

    if (modelType === "huggingface") {
        url = "http://192.168.100.55:5000/api/llms_config/huggingface";
        bodyData = {
            model_name: configData.get("huggingfaceModelName"),
            max_new_tokens: parseInt(configData.get("huggingfaceMaxNewTokens")),
            temperature: parseFloat(configData.get("huggingfaceTemperature")),
            top_k: parseInt(configData.get("huggingfaceTopK")),
            top_p: parseFloat(configData.get("huggingfaceTopP")),
            trust_remote_code: configData.get("huggingfaceTrustRemoteCode") === "true",
            do_sample: configData.get("huggingfaceTrustDoSample") === "true",
            quantization: configData.get("huggingfaceTrustQuantization") === "true",
            quantization_type: "4bit"
        };
    } else {
        url = "http://192.168.100.55:5000/api/llms_config/llama_cpp";
        bodyData = {
            filename: configData.get("llamaFilename"),
            max_new_tokens: parseInt(configData.get("llamaMaxNewTokens")),
            temperature: parseFloat(configData.get("llamaTemperature")),
            top_p: parseFloat(configData.get("llamaTopP")),
            seed: parseInt(configData.get("llamaSeed")),
            verbose: configData.get("llamaVerbose") === "true",
            n_ctx: 512,
            n_gpus: -1,
            n_threads: 4,
            repo_id: "TheBloke/Llama-2-7b-Chat-GGUF",
            stop: ["string"]
        };
    }

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(bodyData),
        });

        const data = await response.json();
        const responseDiv = document.getElementById("responseMessage");
        responseDiv.innerHTML = `
            <strong>Configuration Saved Successfully!</strong><br>
            <code>Status: ${data.status}</code><br>
            <code>Message: ${data.message}</code><br>
            <code>Saved File: ${data.file}</code>
        `;
    } catch (error) {
        document.getElementById("responseMessage").innerHTML = `<span style="color:red;">Error saving configuration: ${error.message}</span>`;
        console.error(error);
    }
});
