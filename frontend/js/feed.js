async function loadHomeFeed() {
    await loadFeedFromEndpoint("/posts/", "feed");
}

async function loadExploreFeed() {
    await loadFeedFromEndpoint("/explore/", "grid");
}

async function loadFeedFromEndpoint(endpoint, viewType = "feed") {
    feedList.innerHTML = `
        <div class="text-center text-muted py-5">
            Loading posts...
        </div>
    `;

    try {
        const { response, data } = await getRequest(endpoint);

        if (response.ok) {
            const posts = Array.isArray(data) ? data : data.results || [];

            if (viewType === "grid") {
                renderPostGrid(posts);
            } else {
                renderFeed(posts);
            }
        } else {
            feedList.innerHTML = `
                <div class="empty-state">
                    <h5>Could not load posts</h5>
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

async function toggleLike(button) {
    const postId = button.dataset.postId;
    const isLiked = button.dataset.liked === "true";
    const currentLikesCount = Number(button.dataset.likesCount);

    button.disabled = true;

    try {
        let result;

        if (isLiked) {
            result = await deleteRequest(`/posts/${postId}/like/`);
        } else {
            result = await postRequest(`/posts/${postId}/like/`);
        }

        if (result.response.ok) {
            const newLikedState = !isLiked;
            const newLikesCount = newLikedState
                ? currentLikesCount + 1
                : Math.max(currentLikesCount - 1, 0);

            updateLikeButton(button, newLikedState, newLikesCount);
        } else {
            showToast(getErrorMessage(result.data), "error");
        }
    } catch (error) {
        console.error(error);
        alert("Could not update like.");
    } finally {
        button.disabled = false;
    }
}

async function toggleSave(button) {
    const postId = button.dataset.postId;
    const isSaved = button.dataset.saved === "true";

    button.disabled = true;

    try {
        let result;

        if (isSaved) {
            result = await deleteRequest(`/posts/${postId}/save/`);
        } else {
            result = await postRequest(`/posts/${postId}/save/`);
        }

        if (result.response.ok) {
            updateSaveButton(button, !isSaved);
        } else {
            showToast(getErrorMessage(result.data), "error");
        }
    } catch (error) {
        console.error(error);
        alert("Could not update save state.");
    } finally {
        button.disabled = false;
    }
}

function handleFeedClick(event) {
    const likeButton = event.target.closest(".like-btn");
    const saveButton = event.target.closest(".save-btn");
    const commentButton = event.target.closest(".comment-btn");
    const commentsLink = event.target.closest(".post-comments-link");
    const gridItem = event.target.closest(".clean-grid-item, .posts-grid-item, .profile-grid-item");
    const postMedia = event.target.closest(".post-media-frame");

    if (likeButton) {
        toggleLike(likeButton);
        return;
    }

    if (saveButton) {
        toggleSave(saveButton);
        return;
    }

    if (commentButton) {
        openPostDetail(commentButton.dataset.postId);
        return;
    }

    if (commentsLink) {
        const postCard = commentsLink.closest(".post-card");
        openPostDetail(postCard.dataset.postId);
        return;
    }

    if (gridItem) {
        openPostDetail(gridItem.dataset.postId);
        return;
    }

    if (postMedia) {
        const postCard = postMedia.closest(".post-card");
        openPostDetail(postCard.dataset.postId);
    }
}