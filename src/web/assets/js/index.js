document.addEventListener('DOMContentLoaded', () => {
    const links = document.querySelectorAll('.nav a');
    const content = document.getElementById('page-content');

    const handlers = {
        'upload.html': () => {
            const uploadBtn = document.getElementById("uploadBtn");
            if (!uploadBtn) return;

            uploadBtn.addEventListener("click", () => {
                const fileInput = document.getElementById("fileInput");
                if (!fileInput || !fileInput.files.length) {
                    return alert("Please choose a file.");
                }

                const formData = new FormData();
                formData.append("file", fileInput.files[0]);

                fetch("/api/upload", {
                    method: "POST",
                    body: formData
                })
                .then(res => res.json())
                .then(data => alert("Upload successful!"))
                .catch(err => {
                    console.error(err);
                    alert("Upload failed.");
                });
            });
        },

        'hello.html': () => {
            console.log("Hello page loaded.");
        },

        'to_chunks.html': () => {
            console.log("Chunk Generator page loaded.");
            // Example logic:
            // const btn = document.getElementById('generateChunks');
            // btn.addEventListener('click', () => { ... });
        },

        'chunks_to_embedding.html': () => {
            console.log("Embed Chunks page loaded.");
            // Example logic:
            // const btn = document.getElementById('embedChunks');
            // btn.addEventListener('click', () => { ... });
        },

        'llms_config.html': () => {
            console.log("LLM Configuration page loaded.");
            // Example logic:
            // const saveBtn = document.getElementById('saveConfig');
            // saveBtn.addEventListener('click', () => { ... });
        },

        'chat_manager.html': () => {
            console.log("Chat Memory page loaded.");
            // Example logic:
            // loadChatSessions();
        },

        'monitoring.html': () => {
            console.log("System Monitoring page loaded.");
            // Example logic:
            // fetch stats from API and update charts
        },

        'logs.html': () => {
            console.log("System Logs page loaded.");
            // Example logic:
            // fetch("/api/logs").then(...);
        },
    };

    async function loadPage(path) {
        content.innerHTML = "<p>Loading...</p>";

        try {
            const res = await fetch(path);
            if (!res.ok) throw new Error(`Failed to fetch ${path}`);
            const html = await res.text();
            content.innerHTML = html;

            const pageKey = path.split('/').pop();
            if (handlers[pageKey]) {
                handlers[pageKey]();
            }
        } catch (err) {
            console.error(err);
            content.innerHTML = "<p>Error loading page.</p>";
        }
    }

    links.forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            const page = link.getAttribute('data-page');
            if (page) loadPage(page);
        });
    });

    const firstLink = document.querySelector('.nav a[data-page]');
    if (firstLink) {
        const defaultPage = firstLink.getAttribute('data-page');
        if (defaultPage) loadPage(defaultPage);
    }
});
