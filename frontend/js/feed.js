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

async function toggleLike(button) {
    const postId = button.dataset.postId;
    const isLiked = button.dataset.liked === "true";
    const currentLikesCount = Number(button.dataset.likesCount);

    button.disabled = true;

    try {
        let response;
        let data;

        if (isLiked) {
            const result = await deleteRequest(`/posts/${postId}/like/`);
            response = result.response;
            data = result.data;
        } else {
            const result = await postRequest(`/posts/${postId}/like/`);
            response = result.response;
            data = result.data;
        }

        if (response.ok) {
            const newLikedState = !isLiked;
            const newLikesCount = newLikedState
                ? currentLikesCount + 1
                : Math.max(currentLikesCount - 1, 0);

            updateLikeButton(button, newLikedState, newLikesCount);
        } else {
            alert(getErrorMessage(data));
        }
    } catch (error) {
        console.error(error);
        alert("Could not update like.");
    } finally {
        button.disabled = false;
    }
}

function handleFeedClick(event) {
    const likeButton = event.target.closest(".like-btn");

    if (likeButton) {
        toggleLike(likeButton);
    }
}