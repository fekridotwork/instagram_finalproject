async function loadHomeFeed() {
    await loadFeedFromEndpoint("/posts/");
}

async function loadExploreFeed() {
    await loadFeedFromEndpoint("/explore/");
}

async function loadFeedFromEndpoint(endpoint) {
    feedList.innerHTML = `
        <div class="text-center text-muted py-5">
            Loading feed...
        </div>
    `;

    try {
        const { response, data } = await getRequest(endpoint);

        console.log("Feed response:", data);

        if (response.ok) {
            const posts = Array.isArray(data) ? data : data.results || [];
            renderFeed(posts);
        } else {
            feedList.innerHTML = `
                <div class="empty-state">
                    <h5>Could not load feed</h5>
                    <p>${getErrorMessage(data)}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error(error);

        feedList.innerHTML = `
            <div class="empty-state">
                <h5>Cannot connect to server</h5>
                <p>Please check your backend server and try again.</p>
            </div>
        `;
    }
}