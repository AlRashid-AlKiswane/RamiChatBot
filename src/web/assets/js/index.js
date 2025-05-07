const loadPage = async (page) => {
    const pages = {
        hello: '/web/html/hello.html',
        upload: '/web/html/upload.html',
        to_chunks: '/web/html/to_chunks.html',
        chunks_to_embedding: '/web/html/chunks_to_embedding.html',
        llms_config: '/web/html/llms_config.html',
        chat_manager: '/web/html/chat_manager.html'
    };

    // Remove 'active' class from all links
    const navLinks = document.querySelectorAll('nav ul li a');
    navLinks.forEach(link => link.classList.remove('active'));

    // Add 'active' class to the clicked link
    const activeLink = document.querySelector(`nav ul li a[href='#${page}']`);
    if (activeLink) activeLink.classList.add('active');

    const response = await fetch(pages[page]);
    if (!response.ok) {
        document.getElementById('content-container').innerHTML = `<p>Error loading ${page}</p>`;
        return;
    }

    const content = await response.text();
    document.getElementById('content-container').innerHTML = content;
};
