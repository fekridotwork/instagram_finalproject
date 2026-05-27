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
        globalSearchInput.value = "";
        loadHomeFeed();
        return;
    }

    if (page === "explore") {
        pageTitle.textContent = "Explore";
        pageSubtitle.textContent = "Search people and discover public posts.";
        globalSearchInput.value = "";
        loadExploreFeed();
        return;
    }

    if (page === "profile") {
        loadProfilePage();
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
        refreshIcons();
        return;
    }

    feedList.innerHTML = posts.map(function (post) {
        return `
            <article class="post-card" data-post-id="${post.id}">
                <div class="post-header">
                    <div class="post-user">
                        <div class="avatar">
                            ${post.username ? post.username[0].toUpperCase() : "U"}
                        </div>

                        <div>
                            <strong>${post.username}</strong>
                            <p class="post-location mb-0">${post.location || "Moment"}</p>
                        </div>
                    </div>

                    <button class="post-more-button">
                        <i data-lucide="more-horizontal"></i>
                    </button>
                </div>

                ${renderPostMedia(post)}

                <div class="post-actions-row">
                    <div class="post-left-actions">
                        <button
                            class="post-action-button like-btn ${post.is_liked ? "liked" : ""}"
                            data-post-id="${post.id}"
                            data-liked="${post.is_liked}"
                            data-likes-count="${post.likes_count || 0}"
                        >
                            <i data-lucide="heart"></i>
                        </button>

                        <button class="post-action-button">
                            <i data-lucide="message-circle"></i>
                        </button>

                        <button class="post-action-button">
                            <i data-lucide="send"></i>
                        </button>
                    </div>

                    <button
                        class="post-action-button save-btn ${post.is_saved ? "saved" : ""}"
                        data-post-id="${post.id}"
                        data-saved="${post.is_saved}"
                    >
                        <i data-lucide="bookmark"></i>
                    </button>
                </div>

                <div class="post-dots">
                    <span class="active"></span>
                    <span></span>
                    <span></span>
                    <span></span>
                </div>

                <div class="post-body">
                    <p class="post-likes mb-2">
                        <strong>${post.likes_count || 0}</strong> likes
                    </p>

                    ${
                        post.caption
                            ? `
                                <p class="post-caption-text mb-2">
                                    <strong>${post.username}</strong>
                                    ${post.caption}
                                </p>
                            `
                            : ""
                    }

                    <button class="post-comments-link">
                        View all ${post.comments_count || 0} comments
                    </button>

                    <p class="post-time mb-0">
                        ${formatDate(post.created_at)}
                    </p>
                </div>
            </article>
        `;
    }).join("");

    refreshIcons();
}

function renderPostGrid(posts) {
    if (!posts.length) {
        feedList.innerHTML = `
            <div class="empty-state">
                <h5>No posts found</h5>
                <p>Nothing to show here yet.</p>
            </div>
        `;
        return;
    }

    feedList.innerHTML = `
        <section class="clean-grid">
            ${posts.map(function (post) {
                const mediaUrl = post.media ? getMediaUrl(post.media) : "";

                return `
                    <article class="clean-grid-item" data-post-id="${post.id}">
                        ${
                            mediaUrl
                                ? `<img src="${mediaUrl}" alt="Post">`
                                : `<div class="clean-grid-placeholder">No media</div>`
                        }
                    </article>
                `;
            }).join("")}
        </section>
    `;
}

function getMediaUrl(path) {
    if (!path) {
        return "";
    }

    return path.startsWith("http")
        ? path
        : `${BACKEND_BASE_URL}${path}`;
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

    const postCard = button.closest(".post-card");
    const likesText = postCard.querySelector(".post-likes strong");

    if (likesText) {
        likesText.textContent = likesCount;
    }

    refreshIcons();
}

function updateSaveButton(button, isSaved) {
    button.dataset.saved = isSaved;
    button.classList.toggle("saved", isSaved);

    refreshIcons();
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

function refreshIcons() {
    if (window.lucide) {
        lucide.createIcons();
    }
}