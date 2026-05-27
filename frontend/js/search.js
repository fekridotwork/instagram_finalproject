let searchTimeout = null;

function handleGlobalSearchInput(event) {
    const query = event.target.value.trim();

    const activeNav = document.querySelector(".app-nav-item.active");
    const activePage = activeNav ? activeNav.dataset.page : null;

    if (activePage !== "explore") {
        return;
    }

    clearTimeout(searchTimeout);

    searchTimeout = setTimeout(function () {
        if (!query) {
            loadExploreFeed();
            return;
        }

        runExploreSearch(query);
    }, 400);
}

async function runExploreSearch(query) {
    pageTitle.textContent = "Search";
    pageSubtitle.textContent = `Results for "${query}"`;

    feedList.innerHTML = `
        <div class="text-center text-white-50 py-5">
            Searching...
        </div>
    `;

    try {
        const { response, data } = await getRequest(
            `/search/?search=${encodeURIComponent(query)}&type=all`
        );

        if (!response.ok) {
            feedList.innerHTML = `
                <div class="empty-state">
                    <h5>Search failed</h5>
                    <p>${getErrorMessage(data)}</p>
                </div>
            `;
            return;
        }

        const results = normalizeSearchResults(data);
        renderSearchResults(results, query);
    } catch (error) {
        console.error(error);

        feedList.innerHTML = `
            <div class="empty-state">
                <h5>Search failed</h5>
                <p>Could not search right now.</p>
            </div>
        `;
    }
}

function normalizeSearchResults(data) {
    return {
        users: data.users || [],
        posts: data.posts || [],
        hashtags: data.hashtags || [],
    };
}

function renderSearchResults(results, query) {
    const users = results.users;
    const hashtags = results.hashtags;
    const posts = results.posts;

    if (!users.length && !hashtags.length && !posts.length) {
        feedList.innerHTML = `
            <div class="empty-state">
                <h5>No results</h5>
                <p>No users, hashtags, or posts found for "${query}".</p>
            </div>
        `;
        return;
    }

    feedList.innerHTML = `
        <section class="search-results glass-card">
            ${
                users.length
                    ? `
                        <div class="search-section">
                            <h5>Users</h5>
                            <div class="search-list">
                                ${users.map(renderUserSearchResult).join("")}
                            </div>
                        </div>
                    `
                    : ""
            }

            ${
                hashtags.length
                    ? `
                        <div class="search-section">
                            <h5>Hashtags</h5>
                            <div class="search-list">
                                ${hashtags.map(renderHashtagSearchResult).join("")}
                            </div>
                        </div>
                    `
                    : ""
            }

            ${
                posts.length
                    ? `
                        <div class="search-section">
                            <h5>Posts containing this search</h5>
                            <p class="search-hint">
                                These posts matched the username, hashtag, or caption text.
                            </p>

                            <div class="clean-grid">
                                ${posts.map(renderSearchPostResult).join("")}
                            </div>
                        </div>
                    `
                    : ""
            }
        </section>
    `;

    bindSearchResultClicks();
}

function renderUserSearchResult(user) {
    const username = user.username || "unknown";
    const displayName = user.display_name || user.full_name || username;
    const image = user.profile_image ? getMediaUrl(user.profile_image) : "";

    return `
        <article class="search-result-item user-search-result" data-username="${username}" data-user-id="${user.id || user.user_id}">
            <div class="search-result-avatar">
                ${
                    image
                        ? `<img src="${image}" alt="${username}">`
                        : `<span>${username[0].toUpperCase()}</span>`
                }
            </div>

            <div>
                <strong>${username}</strong>
                <p>${displayName}</p>
            </div>
        </article>
    `;
}

function renderHashtagSearchResult(hashtag) {
    const name = hashtag.name || hashtag.hashtag || "";

    return `
        <article class="search-result-item hashtag-search-result" data-hashtag="${name}">
            <div class="search-hashtag-icon">#</div>

            <div>
                <strong>#${name}</strong>
                <p>Found in captions and hashtags</p>
            </div>
        </article>
    `;
}

function renderSearchPostResult(post) {
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
}

function bindSearchResultClicks() {
    document.querySelectorAll(".user-search-result").forEach(function (item) {
        item.addEventListener("click", async function () {
            const username = item.dataset.username;

            try {
                await await loadPublicProfile(username, item.dataset.userId);(username);
            } catch (error) {
                console.error(error);
                alert("Could not load profile.");
            }
        });
    });

    document.querySelectorAll(".hashtag-search-result").forEach(function (item) {
        item.addEventListener("click", function () {
            const hashtag = item.dataset.hashtag;
            globalSearchInput.value = hashtag;
            runExploreSearch(hashtag);
        });
    });
}

async function loadPublicProfile(username, userId = null) {
    const { response, data } = await getRequest(`/users/${username}/`);
    console.log(data);

    if (!response.ok) {
        alert("Could not load profile.");
        return;
    }

    pageTitle.textContent = data.username;
    pageSubtitle.textContent = data.bio || "Profile";

    feedList.innerHTML = `
        <section class="public-profile-page">
            <div class="public-profile-hero glass-card">
                <div class="public-profile-avatar">
                    ${
                        data.profile_image
                            ? `<img src="${getMediaUrl(data.profile_image)}" alt="${data.username}">`
                            : `<span>${data.username[0].toUpperCase()}</span>`
                    }
                </div>

                <div class="public-profile-info">
                    <div class="public-profile-top">
                        <div>
                            <h3>${data.username}</h3>
                            <p>${data.display_name || data.full_name || ""}</p>
                        </div>

                        <button
                            class="public-follow-btn"
                            id="publicFollowBtn"
                            data-user-id="${userId}"
                            data-following="${data.is_following || false}"
                        >
                            ${data.is_following ? "Following" : "Follow"}
                        </button>
                    </div>

                    <p class="public-profile-bio">
                        ${data.bio || "No bio yet."}
                    </p>

                    <div class="public-profile-stats">
                        <div>
                            <strong id="publicPostsCount">-</strong>
                            <span>posts</span>
                        </div>

                        <div>
                            <strong id="publicFollowersCount">${data.followers_count ?? "-"}</strong>
                            <span>followers</span>
                        </div>

                        <div>
                            <strong>${data.following_count || "-"}</strong>
                            <span>following</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="public-profile-tabs glass-card">
                <button class="active">
                    <i data-lucide="grid-3x3"></i>
                    Posts
                </button>

                <button>
                    <i data-lucide="bookmark"></i>
                    Saved
                </button>
            </div>

            <section id="publicProfilePosts" class="public-profile-grid"></section>
        </section>
    `;

refreshIcons();
bindPublicProfileActions();

    await loadPublicProfilePosts(username);
}

async function loadPublicProfilePosts(username) {
    const container = document.getElementById("publicProfilePosts");

    const { response, data } = await getRequest(`/users/${username}/posts/`);

    if (!response.ok) {
        container.innerHTML = `<p class="text-white-50">Could not load posts.</p>`;
        return;
    }

    const posts = Array.isArray(data) ? data : data.results || [];

    if (!posts.length) {
        container.innerHTML = `
            <div class="empty-state">
                <h5>No posts</h5>
                <p>This user has no visible posts.</p>
            </div>
        `;
        return;
    }

    document.getElementById("publicPostsCount").textContent = posts.length;
    container.innerHTML = posts.map(renderPublicProfilePost).join("");
}

function renderPublicProfilePost(post) {
    const mediaUrl = post.media ? getMediaUrl(post.media) : "";

    return `
        <article class="public-profile-grid-item clean-grid-item" data-post-id="${post.id}">
            ${
                mediaUrl
                    ? `<img src="${mediaUrl}" alt="Post">`
                    : `<div class="clean-grid-placeholder">No media</div>`
            }
        </article>
    `;
}
function bindPublicProfileActions() {
    const followButton = document.getElementById("publicFollowBtn");

    if (!followButton) {
        return;
    }

    followButton.addEventListener("click", function () {
        togglePublicProfileFollow(followButton);
    });
}

async function togglePublicProfileFollow(button) {
    const userId = button.dataset.userId;
    const isFollowing = button.dataset.following === "true";

    button.disabled = true;
    button.textContent = isFollowing ? "Unfollowing..." : "Following...";

    try {
        let result;

        if (isFollowing) {
            result = await deleteRequest(`/users/${userId}/follow/`);
        } else {
            result = await postRequest(`/users/${userId}/follow/`);
        }

        if (result.response.ok) {
            const newState = !isFollowing;

            button.dataset.following = newState;
            button.textContent = newState ? "Following" : "Follow";
            button.classList.toggle("following", newState);

            updatePublicFollowersCount(newState);
        } else {
            alert(getErrorMessage(result.data));
            button.textContent = isFollowing ? "Following" : "Follow";
        }
    } catch (error) {
        console.error(error);
        alert("Could not update follow state.");
        button.textContent = isFollowing ? "Following" : "Follow";
    } finally {
        button.disabled = false;
    }
}

function updatePublicFollowersCount(isFollowing) {
    const followersCountElement = document.getElementById("publicFollowersCount");

    if (!followersCountElement) {
        return;
    }

    const currentValue = Number(followersCountElement.textContent);

    if (Number.isNaN(currentValue)) {
        return;
    }

    const newValue = isFollowing
        ? currentValue + 1
        : Math.max(currentValue - 1, 0);

    followersCountElement.textContent = newValue;
}