async function openPostDetail(postId) {
    postModal.classList.remove("d-none");

    postModalContent.innerHTML = `
        <div class="text-center text-muted py-5">
            Loading post...
        </div>
    `;

    try {
        const { response, data } = await getRequest(`/posts/${postId}/`);

        if (response.ok) {
            renderPostDetail(data);
        } else {
            postModalContent.innerHTML = `
                <div class="empty-state">
                    <h5>Could not load post</h5>
                    <p>${getErrorMessage(data)}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error(error);

        postModalContent.innerHTML = `
            <div class="empty-state">
                <h5>Cannot connect to server</h5>
            </div>
        `;
    }
}

function closePostDetail() {
    postModal.classList.add("d-none");
    postModalContent.innerHTML = "";
}

function renderPostDetail(post) {
    const mediaUrl = post.media ? getMediaUrl(post.media) : "";

    postModalContent.innerHTML = `
        <div class="post-detail">
            <div class="post-detail-media">
                ${
                    mediaUrl
                        ? `<img src="${mediaUrl}" alt="Post">`
                        : `<div class="post-detail-placeholder">No media</div>`
                }
            </div>

            <div class="post-detail-info">
                <div class="post-detail-user">
                    <div class="avatar">
                        ${post.username ? post.username[0].toUpperCase() : "U"}
                    </div>
                    <strong>${post.username}</strong>
                </div>

                ${
                    post.caption
                        ? `<p class="post-detail-caption">${post.caption}</p>`
                        : `<p class="text-muted">No caption.</p>`
                }

                <div class="post-detail-meta">
                    <span>${post.likes_count || 0} likes</span>
                    <span>${post.comments_count || 0} comments</span>
                </div>

                <div class="post-detail-comments">
                    ${renderPostComments(post.comments || [])}
                </div>
            </div>
        </div>
    `;
}

function renderPostComments(comments) {
    if (!comments.length) {
        return `
            <p class="text-muted mt-3">
                No comments yet.
            </p>
        `;
    }

    return comments.map(function (comment) {
        return `
            <div class="post-detail-comment">
                <strong>${comment.username || "User"}</strong>
                <span>${comment.text || comment.content || ""}</span>
            </div>
        `;
    }).join("");
}