function showApp() {
    authPage.classList.add("d-none");
    appPage.classList.remove("d-none");

    loadFeed();
}

function showAuth() {
    appPage.classList.add("d-none");
    authPage.classList.remove("d-none");
}

function showMessage(message, type) {
    messageBox.textContent = message;
    messageBox.className = `alert alert-${type}`;
}

function clearMessage() {
    messageBox.textContent = "";
    messageBox.className = "alert d-none";
}

function resetOtpState() {
    otpSection.classList.add("d-none");
    otpInput.value = "";
    clearMessage();
}

function renderFeed(posts) {
    if (!posts.length) {
        feedList.innerHTML = `
            <div class="empty-state">
                <h5>No posts yet</h5>
                <p>Follow people or create your first post to fill your feed.</p>
            </div>
        `;
        return;
    }

    feedList.innerHTML = posts.map(function (post) {
        return `
            <article class="post-card">
                <div class="post-header">
                    <div class="avatar">
                        ${post.username ? post.username[0].toUpperCase() : "U"}
                    </div>
                    <div>
                        <strong>${post.username}</strong>
                        <p class="text-muted mb-0">${formatDate(post.created_at)}</p>
                    </div>
                </div>

                ${renderPostMedia(post)}

                <div class="post-actions">
                    <button class="btn btn-light">♡ ${post.likes_count || 0}</button>
                    <button class="btn btn-light">Comment</button>
                    <button class="btn btn-light">${post.is_saved ? "Saved" : "Save"}</button>
                </div>

                ${post.caption ? `<p class="post-caption mb-0">${post.caption}</p>` : ""}
            </article>
        `;
    }).join("");
}

function renderPostMedia(post) {
    if (!post.media) {
        return `
            <div class="post-placeholder">
                No media
            </div>
        `;
    }

    const mediaUrl = post.media.startsWith("http")
        ? post.media
        : `${BACKEND_BASE_URL}${post.media}`;

    if (post.media_type === "video") {
        return `
            <div class="post-media-frame">
                <video class="post-media" controls>
                    <source src="${mediaUrl}">
                </video>
            </div>
        `;
    }

    return `
        <div class="post-media-frame">
            <img class="post-media" src="${mediaUrl}" alt="Post media">
        </div>
    `;
}

function formatDate(dateString) {
    if (!dateString) {
        return "";
    }

    const date = new Date(dateString);

    return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
    });
}