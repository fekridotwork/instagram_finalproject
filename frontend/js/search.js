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
            ${users.length ? `
                <div class="search-section">
                    <h5>Users</h5>
                    <div class="search-list">
                        ${users.map(renderUserSearchResult).join("")}
                    </div>
                </div>
            ` : ""}

            ${hashtags.length ? `
                <div class="search-section">
                    <h5>Hashtags</h5>
                    <div class="search-list">
                        ${hashtags.map(renderHashtagSearchResult).join("")}
                    </div>
                </div>
            ` : ""}

            ${posts.length ? `
                <div class="search-section">
                    <h5>Posts</h5>
                    <div class="clean-grid">
                        ${posts.map(renderSearchPostResult).join("")}
                    </div>
                </div>
            ` : ""}
        </section>
    `;
}

function renderUserSearchResult(user) {
    const username = user.username || "unknown";
    const displayName = user.display_name || user.full_name || username;
    const image = user.profile_image ? getMediaUrl(user.profile_image) : "";

    return `
        <article class="search-result-item">
            <div class="search-result-avatar">
                ${image ? `<img src="${image}" alt="${username}">` : `<span>${username[0].toUpperCase()}</span>`}
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
        <article class="search-result-item">
            <div class="search-hashtag-icon">#</div>

            <div>
                <strong>#${name}</strong>
                <p>Hashtag</p>
            </div>
        </article>
    `;
}

function renderSearchPostResult(post) {
    const mediaUrl = post.media ? getMediaUrl(post.media) : "";

    return `
        <article class="clean-grid-item" data-post-id="${post.id}">
            ${mediaUrl ? `<img src="${mediaUrl}" alt="Post">` : `<div class="clean-grid-placeholder">No media</div>`}
        </article>
    `;
}