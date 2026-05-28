function renderUserAvatar(user, className = "") {
    const image = user?.profile_image ? getMediaUrl(user.profile_image) : "";
    const username = user?.username || "User";
    const letter = username[0]?.toUpperCase() || "U";

    if (image) {
        return `<img src="${image}" alt="${username}" class="${className}">`;
    }

    return `<span class="${className}">${letter}</span>`;
}
function renderAvatar({
    username = "User",
    profileImage = "",
    hasStory = false,
    size = 48
}) {
    const firstLetter = username ? username[0].toUpperCase() : "U";

    return `
        <div
            class="avatar-ring ${hasStory ? "has-story" : "no-story"}"
            style="width:${size}px; height:${size}px;"
        >
            <div class="avatar-inner">
                ${
                    profileImage
                        ? `<img src="${getMediaUrl(profileImage)}" alt="${username}">`
                        : `<span>${firstLetter}</span>`
                }
            </div>
        </div>
    `;
}
function showApp() {
    authPage.classList.add("d-none");
    appPage.classList.remove("d-none");

    pageTitle.textContent = "Home";
    pageSubtitle.textContent = "Catch up with the latest moments.";

    document.querySelector(".glass-search")?.classList.add("d-none");

    loadHomeStories();
    loadHomeFeed();
    hydrateSidebarProfileCard();
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
    const searchBar = document.querySelector(".glass-search");

    if (searchBar) {
        searchBar.classList.toggle("d-none", page !== "explore");
    }
    if (page === "home") {
        pageTitle.textContent = "Home";
        pageSubtitle.textContent = "Catch up with the latest moments.";
        globalSearchInput.value = "";
        loadHomeStories();
        loadHomeFeed();
        return;
    }

    if (page === "explore") {
        hideStories();
        pageTitle.textContent = "Explore";
        pageSubtitle.textContent = "Search people and discover public posts.";
        globalSearchInput.value = "";
        loadExploreFeed();
        return;
    }

    if (page === "profile") {
        hideStories();
        loadProfilePage();
        return;
    }

    if (page === "messages") {
        hideStories();
        pageTitle.textContent = "Messages";
        pageSubtitle.textContent = "Your direct conversations.";
        globalSearchInput.value = "";
        loadMessagesPage();
        return;
    }

    pageTitle.textContent = capitalize(page);
    pageSubtitle.textContent = "This section is coming next.";

    hideStories();

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
                            ${renderUserAvatar(post)}
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

                        <button
                            class="post-action-button comment-btn"
                            data-post-id="${post.id}"
                        >
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

                        <div class="post-grid-hover">
                            <span>♥ ${post.likes_count || 0}</span>
                            <span>💬 ${post.comments_count || 0}</span>
                            <span>↗ ${post.shares_count || 0}</span>
                        </div>
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
function timeAgo(dateString) {
    if (!dateString) {
        return "";
    }

    const date = new Date(dateString);
    const now = new Date();

    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) {
        return "just now";
    }

    const minutes = Math.floor(seconds / 60);

    if (minutes < 60) {
        return `${minutes}m ago`;
    }

    const hours = Math.floor(minutes / 60);

    if (hours < 24) {
        return `${hours}h ago`;
    }

    const days = Math.floor(hours / 24);

    if (days < 7) {
        return `${days}d ago`;
    }

    return formatDate(dateString);
}

function capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1);
}

function refreshIcons() {
    if (window.lucide) {
        lucide.createIcons();
    }
}
let appToastTimer = null;
let appModalResolver = null;

function showToast(message, type = "info") {
    const toast = document.getElementById("appToast");

    if (!toast) {
        console.log(message);
        return;
    }

    clearTimeout(appToastTimer);

    toast.textContent = message;
    toast.className = `app-toast app-toast-${type}`;

    appToastTimer = setTimeout(function () {
        toast.className = "app-toast d-none";
        toast.textContent = "";
    }, 3000);
}

function closeAppModal(result = null) {
    const overlay = document.getElementById("appModalOverlay");
    const input = document.getElementById("appModalInput");
    const error = document.getElementById("appModalError");

    overlay.classList.add("d-none");
    input.classList.add("d-none");
    input.value = "";
    error.classList.add("d-none");
    error.textContent = "";

    if (appModalResolver) {
        appModalResolver(result);
        appModalResolver = null;
    }
}

function openConfirmModal({
    title = "Confirm action",
    description = "Are you sure?",
    confirmText = "Confirm",
    cancelText = "Cancel",
    danger = false,
} = {}) {
    return new Promise(function (resolve) {
        const overlay = document.getElementById("appModalOverlay");
        const titleEl = document.getElementById("appModalTitle");
        const descriptionEl = document.getElementById("appModalDescription");
        const input = document.getElementById("appModalInput");
        const confirmBtn = document.getElementById("appModalConfirmBtn");
        const cancelBtn = document.getElementById("appModalCancelBtn");

        appModalResolver = resolve;

        titleEl.textContent = title;
        descriptionEl.textContent = description;
        input.classList.add("d-none");

        confirmBtn.textContent = confirmText;
        cancelBtn.textContent = cancelText;
        confirmBtn.className = danger ? "btn btn-danger" : "btn btn-primary";

        overlay.classList.remove("d-none");

        confirmBtn.onclick = function () {
            closeAppModal(true);
        };

        cancelBtn.onclick = function () {
            closeAppModal(false);
        };

        overlay.onclick = function (event) {
            if (event.target === overlay) {
                closeAppModal(false);
            }
        };
    });
}

function openInputModal({
    title = "Edit",
    description = "",
    initialValue = "",
    placeholder = "",
    confirmText = "Save",
    cancelText = "Cancel",
    required = true,
} = {}) {
    return new Promise(function (resolve) {
        const overlay = document.getElementById("appModalOverlay");
        const titleEl = document.getElementById("appModalTitle");
        const descriptionEl = document.getElementById("appModalDescription");
        const input = document.getElementById("appModalInput");
        const error = document.getElementById("appModalError");
        const confirmBtn = document.getElementById("appModalConfirmBtn");
        const cancelBtn = document.getElementById("appModalCancelBtn");

        appModalResolver = resolve;

        titleEl.textContent = title;
        descriptionEl.textContent = description;
        input.classList.remove("d-none");
        input.value = initialValue;
        input.placeholder = placeholder;

        error.classList.add("d-none");
        error.textContent = "";

        confirmBtn.textContent = confirmText;
        cancelBtn.textContent = cancelText;
        confirmBtn.className = "btn btn-primary";

        overlay.classList.remove("d-none");

        setTimeout(function () {
            input.focus();
            input.setSelectionRange(input.value.length, input.value.length);
        }, 50);

        confirmBtn.onclick = function () {
            const value = input.value.trim();

            if (required && !value) {
                error.textContent = "This field cannot be empty.";
                error.classList.remove("d-none");
                return;
            }

            closeAppModal(value);
        };

        cancelBtn.onclick = function () {
            closeAppModal(null);
        };

        overlay.onclick = function (event) {
            if (event.target === overlay) {
                closeAppModal(null);
            }
        };
    });
}