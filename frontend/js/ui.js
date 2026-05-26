function showApp() {
    authPage.classList.add("d-none");
    appPage.classList.remove("d-none");

    loadHomeFeed();
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

function setActiveNav(activeItem) {
    navItems.forEach(function (item) {
        item.classList.remove("active");
    });

    activeItem.classList.add("active");
}

function handleNavigation(page) {
    if (page === "home") {
        pageTitle.textContent = "Home";
        pageSubtitle.textContent = "Catch up with the latest moments.";
        loadHomeFeed();
        return;
    }

    if (page === "explore") {
        pageTitle.textContent = "Explore";
        pageSubtitle.textContent = "Discover public posts people are liking.";
        loadExploreFeed();
        return;
    }

    pageTitle.textContent = capitalize(page);
    pageSubtitle.textContent = "This section is coming next.";

    feedList.innerHTML = `
        <div class="empty-state">
            <h5>${capitalize(page)} is not ready yet</h5>
            <p>We will connect this section to the backend step by step.</p>
        </div>
    `;
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
            <article class="post-card" data-post-id="${post.id}">
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
                    <button
                        class="btn btn-light like-btn ${post.is_liked ? "liked" : ""}"
                        data-post-id="${post.id}"
                        data-liked="${post.is_liked}"
                        data-likes-count="${post.likes_count || 0}"
                    >
                        ${post.is_liked ? "♥" : "♡"} ${post.likes_count || 0}
                    </button>

                    <button class="btn btn-light">
                        💬 ${post.comments_count || 0}
                    </button>

                    <button class="btn btn-light">
                        ${post.is_saved ? "Saved" : "Save"}
                    </button>
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

function updateLikeButton(button, isLiked, likesCount) {
    button.dataset.liked = isLiked;
    button.dataset.likesCount = likesCount;
    button.classList.toggle("liked", isLiked);
    button.innerHTML = `${isLiked ? "♥" : "♡"} ${likesCount}`;
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

function capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
}