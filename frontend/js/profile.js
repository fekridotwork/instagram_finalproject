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
    const grid = document.getElementById("profileGrid");

    grid.innerHTML = `
        <div class="empty-state profile-empty">
            <h5>Loading saved posts...</h5>
        </div>
    `;

    try {
        const { response, data } = await getRequest("/me/saved-posts/");

        if (response.ok) {
            const savedPosts = Array.isArray(data) ? data : data.results || [];
            renderProfileGrid(savedPosts);
        } else {
            grid.innerHTML = `
                <div class="empty-state profile-empty">
                    <h5>Could not load saved posts</h5>
                    <p>${getErrorMessage(data)}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error(error);

        grid.innerHTML = `
            <div class="empty-state profile-empty">
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
        <section class="public-profile-page">
            <div class="public-profile-hero glass-card">
                <div class="public-profile-avatar">
                    ${
                        profileImage
                            ? `<img src="${profileImage}" alt="${profile.username}">`
                            : `<span>${profile.username ? profile.username[0].toUpperCase() : "U"}</span>`
                    }
                </div>

                <div class="public-profile-info">
                    <div class="public-profile-top">
                        <div>
                            <h3>${profile.display_name || profile.username}</h3>
                            <p>@${profile.username}</p>
                        </div>

                        <button id="editProfileBtn" class="public-message-btn">
                            Edit profile
                        </button>
                    </div>

                    <p class="public-profile-bio">
                        ${profile.bio || "No bio yet."}
                    </p>

                    <div class="public-profile-stats">
                        <div>
                            <strong>${posts.length}</strong>
                            <span>posts</span>
                        </div>

                        <div id="profileFollowersStat" class="profile-stat-clickable">
                            <strong id="profileFollowersCount">-</strong>
                            <span>followers</span>
                        </div>

                        <div id="profileFollowingStat" class="profile-stat-clickable">
                            <strong id="profileFollowingCount">-</strong>
                            <span>following</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="public-profile-tabs glass-card">
                <button class="profile-tab active" data-profile-tab="posts">
                    <i data-lucide="grid-3x3"></i>
                    Posts
                </button>

                <button class="profile-tab" data-profile-tab="saved">
                    <i data-lucide="bookmark"></i>
                    Saved
                </button>
            </div>

            <section id="profileGrid" class="public-profile-grid"></section>
        </section>
    `;

    renderProfileGrid(posts);
    bindProfileTabs(posts);
    bindCreateStoryButton();
    bindEditProfileButton();
    bindProfileFollowStats();
    loadProfileFollowCounts();
    refreshIcons();
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
            <article class="public-profile-grid-item clean-grid-item" data-post-id="${post.id}">
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
function bindEditProfileButton() {
    const editProfileBtn = document.getElementById("editProfileBtn");

    if (!editProfileBtn) {
        return;
    }

    editProfileBtn.onclick = function () {
        openEditProfileModal();
    };
}

function openEditProfileModal() {
    const modal = document.getElementById("editProfileModal");

    modal.classList.remove("d-none");

    document.getElementById("editDisplayNameInput").value =
        currentProfile.display_name || "";

    document.getElementById("editBioInput").value =
        currentProfile.bio || "";

    clearEditProfileMessage();

    document.getElementById("editUsernameInput").value =
        currentProfile.username || "";

    document.getElementById("editFullNameInput").value =
        currentProfile.full_name || "";

    document.getElementById("editIsPrivateInput").value =
        String(Boolean(currentProfile.is_private));
}

function closeEditProfileModal() {
    document.getElementById("editProfileModal").classList.add("d-none");
    document.getElementById("editProfileImageInput").value = "";
    clearEditProfileMessage();
}

async function submitEditProfile() {
    const displayName = document.getElementById("editDisplayNameInput").value.trim();
    const bio = document.getElementById("editBioInput").value.trim();
    const imageFile = document.getElementById("editProfileImageInput").files[0];
    const username = document.getElementById("editUsernameInput").value.trim();
    const fullName = document.getElementById("editFullNameInput").value.trim();
    const isPrivate = document.getElementById("editIsPrivateInput").value;

    const formData = new FormData();

    formData.append("username", username);
    formData.append("full_name", fullName);
    formData.append("display_name", displayName);
    formData.append("bio", bio);
    formData.append("is_private", isPrivate);

    if (imageFile) {
        formData.append("profile_image", imageFile);
    }

    try {
        const { response, data } = await patchFormRequest("/profile/me/", formData);

        if (!response.ok) {
            showEditProfileMessage(getErrorMessage(data), "danger");
            return;
        }

        closeEditProfileModal();
        await loadProfilePage();
    } catch (error) {
        console.error(error);
        showEditProfileMessage("Could not update profile.", "danger");
    }
}

function showEditProfileMessage(message, type) {
    const box = document.getElementById("editProfileMessage");
    box.textContent = message;
    box.className = `alert alert-${type}`;
}

function clearEditProfileMessage() {
    const box = document.getElementById("editProfileMessage");
    box.textContent = "";
    box.className = "alert d-none";
}

function bindProfileFollowStats() {
    const followersStat = document.getElementById("profileFollowersStat");
    const followingStat = document.getElementById("profileFollowingStat");

    if (followersStat) {
        followersStat.addEventListener("click", function () {
            openFollowModal("followers");
        });
    }

    if (followingStat) {
        followingStat.addEventListener("click", function () {
            openFollowModal("following");
        });
    }
}

async function openFollowModal(type) {
    followModal.classList.remove("d-none");
    followModalTitle.textContent = type === "followers" ? "Followers" : "Following";

    followModalList.innerHTML = `
        <p class="text-white-50">Loading...</p>
    `;

    const endpoint = type === "followers"
        ? "/me/followers/"
        : "/me/following/";

    try {
        const { response, data } = await getRequest(endpoint);

        if (!response.ok) {
            followModalList.innerHTML = `
                <p class="text-white-50">${getErrorMessage(data)}</p>
            `;
            return;
        }

        const users = Array.isArray(data) ? data : data.results || [];
        renderFollowModalUsers(users);
    } catch (error) {
        console.error(error);

        followModalList.innerHTML = `
            <p class="text-white-50">Could not load users.</p>
        `;
    }
}

function closeFollowModal() {
    followModal.classList.add("d-none");
    followModalList.innerHTML = "";
}

async function renderFollowModalUsers(users) {
    if (!users.length) {
        followModalList.innerHTML = `
            <p class="text-white-50">No users found.</p>
        `;
        return;
    }

    followModalList.innerHTML = users.map(renderFollowUserItem).join("");

    await hydrateMutualFollowers(users);

    document.querySelectorAll(".follow-user-item").forEach(function (item) {
        item.addEventListener("click", function () {
            const username = item.dataset.username;
            const userId = item.dataset.userId;

            closeFollowModal();
            loadPublicProfile(username, userId);
        });
    });
}

function renderFollowUserItem(user) {
    const username = user.username || "User";
    const profileImage = user.profile_image ? getMediaUrl(user.profile_image) : "";

    return `
        <article
            class="follow-user-item"
            data-user-id="${user.id}"
            data-username="${username}"
        >
            <div class="follow-user-avatar">
                ${
                    profileImage
                        ? `<img src="${profileImage}" alt="${username}">`
                        : `<span>${username[0].toUpperCase()}</span>`
                }
            </div>

            <div class="follow-user-info">
                <strong>${username}</strong>
                <span>${user.display_name || ""}</span>
                <small id="mutualFollowers-${user.id}"></small>
            </div>

            <button class="follow-user-status" type="button">
                ${user.is_following ? "Following" : "View"}
            </button>
        </article>
    `;
}

async function hydrateMutualFollowers(users) {
    for (const user of users) {
        if (!user.id) {
            continue;
        }

        try {
            const { response, data } = await getRequest(`/users/${user.id}/mutual-followers/`);

            if (!response.ok) {
                continue;
            }

            const mutualUsers = Array.isArray(data) ? data : data.results || [];
            const target = document.getElementById(`mutualFollowers-${user.id}`);

            if (!target) {
                continue;
            }

            target.textContent = mutualUsers.length
                ? `${mutualUsers.length} mutual followers`
                : "";
        } catch (error) {
            console.error(error);
        }
    }
}
async function loadProfileFollowCounts() {
    try {
        const followersResult = await getRequest("/me/followers/");
        const followingResult = await getRequest("/me/following/");

        if (followersResult.response.ok) {
            const followers = Array.isArray(followersResult.data)
                ? followersResult.data
                : followersResult.data.results || [];

            document.getElementById("profileFollowersCount").textContent =
                followersResult.data.count ?? followers.length;
        }

        if (followingResult.response.ok) {
            const following = Array.isArray(followingResult.data)
                ? followingResult.data
                : followingResult.data.results || [];

            document.getElementById("profileFollowingCount").textContent =
                followingResult.data.count ?? following.length;
        }
    } catch (error) {
        console.error(error);
    }
}