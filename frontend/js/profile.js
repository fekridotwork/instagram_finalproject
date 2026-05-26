let currentProfile = null;

async function loadProfilePage() {
    pageTitle.textContent = "Profile";
    pageSubtitle.textContent = "Your posts and saved moments.";

    feedList.innerHTML = `
        <div class="text-center text-muted py-5">
            Loading profile...
        </div>
    `;

    try {
        const profileResult = await getRequest("/profile/me/");
        const postsResult = await getRequest("/posts/");

        if (!profileResult.response.ok) {
            feedList.innerHTML = `
                <div class="empty-state">
                    <h5>Could not load profile</h5>
                    <p>${getErrorMessage(profileResult.data)}</p>
                </div>
            `;
            return;
        }

        currentProfile = profileResult.data;

        const allPosts = Array.isArray(postsResult.data)
            ? postsResult.data
            : postsResult.data.results || [];

        const myPosts = allPosts.filter(function (post) {
            return post.username === currentProfile.username;
        });

        renderProfile(currentProfile, myPosts);
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

async function loadSavedPostsGrid() {
    feedList.querySelector("#profileGrid").innerHTML = `
        <div class="text-center text-muted py-5">
            Loading saved posts...
        </div>
    `;

    try {
        const { response, data } = await getRequest("/me/saved-posts/");

        if (response.ok) {
            const savedPosts = Array.isArray(data) ? data : data.results || [];
            renderProfileGrid(savedPosts);
        } else {
            feedList.querySelector("#profileGrid").innerHTML = `
                <div class="empty-state">
                    <h5>Could not load saved posts</h5>
                    <p>${getErrorMessage(data)}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error(error);

        feedList.querySelector("#profileGrid").innerHTML = `
            <div class="empty-state">
                <h5>Cannot connect to server</h5>
            </div>
        `;
    }
}

function renderProfile(profile, posts) {
    const profileImage = profile.profile_image
        ? getMediaUrl(profile.profile_image)
        : "";

    feedList.innerHTML = `
        <section class="profile-page">
            <div class="profile-header">
                <div class="profile-avatar">
                    ${
                        profileImage
                            ? `<img src="${profileImage}" alt="${profile.username}">`
                            : `<span>${profile.username ? profile.username[0].toUpperCase() : "U"}</span>`
                    }
                </div>

                <div class="profile-info">
                    <h3>${profile.display_name || profile.username}</h3>
                    <p class="profile-username">@${profile.username}</p>

                    ${
                        profile.bio
                            ? `<p class="profile-bio">${profile.bio}</p>`
                            : `<p class="profile-bio text-muted">No bio yet.</p>`
                    }

                    <div class="profile-stats">
                        <div>
                            <strong>${posts.length}</strong>
                            <span>posts</span>
                        </div>
                        <div>
                            <strong>-</strong>
                            <span>followers</span>
                        </div>
                        <div>
                            <strong>-</strong>
                            <span>following</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="profile-tabs">
                <button class="profile-tab active" data-profile-tab="posts">
                    Posts
                </button>
                <button class="profile-tab" data-profile-tab="saved">
                    Saved
                </button>
            </div>

            <div id="profileGrid" class="profile-grid"></div>
        </section>
    `;

    renderProfileGrid(posts);
    bindProfileTabs(posts);
}

function renderProfileGrid(posts) {
    const grid = document.getElementById("profileGrid");

    if (!posts.length) {
        grid.innerHTML = `
            <div class="empty-state profile-empty">
                <h5>No posts found</h5>
                <p>Nothing to show here yet.</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = posts.map(function (post) {
        const mediaUrl = post.media ? getMediaUrl(post.media) : "";

        return `
            <article class="profile-grid-item">
                ${
                    mediaUrl
                        ? `<img src="${mediaUrl}" alt="Post">`
                        : `<div class="profile-grid-placeholder">No media</div>`
                }
            </article>
        `;
    }).join("");
}

function bindProfileTabs(myPosts) {
    const tabs = document.querySelectorAll(".profile-tab");

    tabs.forEach(function (tab) {
        tab.addEventListener("click", function () {
            tabs.forEach(function (item) {
                item.classList.remove("active");
            });

            tab.classList.add("active");

            if (tab.dataset.profileTab === "posts") {
                renderProfileGrid(myPosts);
            }

            if (tab.dataset.profileTab === "saved") {
                loadSavedPostsGrid();
            }
        });
    });
}

function getMediaUrl(path) {
    if (!path) {
        return "";
    }

    return path.startsWith("http")
        ? path
        : `${BACKEND_BASE_URL}${path}`;
}