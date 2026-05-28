let activePostId = null;
let activeReplyParentId = null;
let activeReplyUsername = null;

async function openPostDetail(postId) {
    activePostId = postId;
    postModal.classList.remove("d-none");

    postModalContent.innerHTML = `
        <div class="text-center text-white-50 py-5">
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
    activePostId = null;
    postModal.classList.add("d-none");
    postModalContent.innerHTML = "";
}

function renderPostDetail(post) {
    const mediaUrl = post.media ? getMediaUrl(post.media) : "";
    const comments = post.comments || [];

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
                        ${renderUserAvatar(post)}
                    </div>
                    <div>
                        <strong>${post.username}</strong>
                        <p class="mb-0 text-white-50">${formatDate(post.created_at)}</p>
                    </div>
                    <button
                        class="post-detail-more-btn"
                        id="postDetailMoreBtn"
                        data-post-id="${post.id}"
                    >
                        <i data-lucide="more-horizontal"></i>
                    </button>
                </div>

                ${
                    post.caption
                        ? `
                            <div class="post-detail-caption-block">
                                <strong>${post.username}</strong>
                                <p class="post-detail-caption">${post.caption}</p>
                            </div>
                        `
                        : ""
                }

                <div class="post-detail-meta">
                    <span>${post.likes_count || 0} likes</span>
                    <span id="postDetailCommentsCount">${post.comments_count || comments.length} comments</span>
                </div>

                <div id="postDetailComments" class="post-detail-comments">
                    ${renderPostComments(comments)}
                </div>

                <div class="reply-banner d-none" id="replyBanner">
                    <span id="replyBannerText"></span>

                    <button id="cancelReplyBtn" class="cancel-reply-btn">
                        Cancel
                    </button>
                </div>

                <div class="comment-form">
                    <input
                        id="commentInput"
                        type="text"
                        class="form-control"
                        placeholder="Add a comment..."
                    >

                    <button id="submitCommentBtn" class="btn btn-primary">
                        Post
                    </button>
                </div>

                <div id="commentMessage" class="comment-message"></div>
            </div>
        </div>
    `;

    bindCommentForm();
    bindPostOwnerActions(post);
    refreshIcons();
}

function renderPostComments(comments) {
    if (!comments.length) {
        return `
            <p class="text-white-50 mt-3 mb-0">
                No comments yet.
            </p>
        `;
    }

    return comments.map(function (comment) {
        return renderCommentItem(comment);
    }).join("");
}

function renderCommentItem(comment) {
    return `
        <div class="post-detail-comment" data-comment-id="${comment.id}">
            <div class="comment-avatar">
                ${renderUserAvatar(comment)}
            </div>

            <div class="comment-content">
                <div class="comment-row">
                    <p class="mb-0">
                        <strong>${comment.username || "User"}</strong>
                        ${comment.text || ""}
                    </p>

                    <button
                        class="delete-comment-btn"
                        data-comment-id="${comment.id}"
                        title="Delete comment"
                    >
                        ×
                    </button>
                </div>

                <div class="comment-meta-row">
                    <span class="comment-date">${formatDate(comment.created_at)}</span>

                    <button
                        class="reply-comment-btn"
                        data-comment-id="${comment.id}"
                        data-username="${comment.username || "User"}"
                    >
                        Reply
                    </button>
                </div>
                ${
                    comment.replies && comment.replies.length
                        ? `
                            <div class="comment-replies">
                                ${comment.replies.map(function (reply) {
                                    return renderCommentItem(reply);
                                }).join("")}
                            </div>
                        `
                        : ""
                }
            </div>
        </div>
    `;
}

function bindCommentForm() {
    const commentInput = document.getElementById("commentInput");
    const submitCommentBtn = document.getElementById("submitCommentBtn");
    const commentsBox = document.getElementById("postDetailComments");
    const cancelReplyBtn = document.getElementById("cancelReplyBtn");

    submitCommentBtn.addEventListener("click", function () {
        submitComment(commentInput);
    });

    commentInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            submitComment(commentInput);
        }
    });

    commentsBox.addEventListener("click", function (event) {
        const deleteButton = event.target.closest(".delete-comment-btn");
        const replyButton = event.target.closest(".reply-comment-btn");

        if (deleteButton) {
            deleteComment(deleteButton.dataset.commentId);
            return;
        }

        if (replyButton) {
            activateReplyMode(
                replyButton.dataset.commentId,
                replyButton.dataset.username
            );
        }
    });

    cancelReplyBtn.addEventListener("click", resetReplyMode);
}

async function submitComment(input) {
    const text = input.value.trim();

    if (!text) {
        showCommentMessage("Comment cannot be empty.", "danger");
        return;
    }

    try {
        const payload = {
            text: text,
        };

        if (activeReplyParentId) {
            payload.parent = activeReplyParentId;
        }

        const { response, data } = await postRequest(
            `/posts/${activePostId}/comments/`,
            payload
        );

        if (response.ok) {
            input.value = "";
            resetReplyMode();
            await reloadPostComments();
        } else {
            showCommentMessage(getErrorMessage(data), "danger");
        }
    } catch (error) {
        console.error(error);
        showCommentMessage("Could not add comment.", "danger");
    }
}

async function deleteComment(commentId) {
    try {
        const { response, data } = await deleteRequest(`/posts/comment/${commentId}/`);

        if (response.ok) {
            await reloadPostComments();
        } else {
            showCommentMessage(getErrorMessage(data), "danger");
        }
    } catch (error) {
        console.error(error);
        showCommentMessage("Could not delete comment.", "danger");
    }
}

async function reloadPostComments() {
    const { response, data } = await getRequest(`/posts/${activePostId}/comments/`);

    if (!response.ok) {
        showCommentMessage(getErrorMessage(data), "danger");
        return;
    }

    const comments = Array.isArray(data) ? data : data.results || [];

    const commentsBox = document.getElementById("postDetailComments");
    const commentsCount = document.getElementById("postDetailCommentsCount");

    commentsBox.innerHTML = renderPostComments(comments);
    commentsCount.textContent = `${comments.length} comments`;

    refreshFeedAfterCommentChange();
}

function showCommentMessage(message, type) {
    const commentMessage = document.getElementById("commentMessage");

    commentMessage.textContent = message;
    commentMessage.className = `comment-message comment-message-${type}`;
}

function refreshFeedAfterCommentChange() {
    const activeNav = document.querySelector(".app-nav-item.active");

    if (!activeNav) {
        return;
    }

    const page = activeNav.dataset.page;

    if (page === "home") {
        loadHomeFeed();
    }

    if (page === "explore") {
        loadExploreFeed();
    }
}

function activateReplyMode(commentId, username) {
    activeReplyParentId = commentId;
    activeReplyUsername = username;

    const replyBanner = document.getElementById("replyBanner");
    const replyBannerText = document.getElementById("replyBannerText");
    const commentInput = document.getElementById("commentInput");

    replyBanner.classList.remove("d-none");
    replyBannerText.textContent = `Replying to @${username}`;
    commentInput.placeholder = `Reply to ${username}...`;
    commentInput.focus();
}

function resetReplyMode() {
    activeReplyParentId = null;
    activeReplyUsername = null;

    const replyBanner = document.getElementById("replyBanner");
    const commentInput = document.getElementById("commentInput");

    if (replyBanner) {
        replyBanner.classList.add("d-none");
    }

    if (commentInput) {
        commentInput.placeholder = "Add a comment...";
    }
}
function bindPostOwnerActions(post) {
    const moreBtn = document.getElementById("postDetailMoreBtn");

    if (!moreBtn) {
        return;
    }

    moreBtn.addEventListener("click", function () {
        openPostOwnerMenu(post);
    });
}

function openPostOwnerMenu(post) {
    const action = prompt("Type edit or delete:");

    if (action === "edit") {
        openEditPostPrompt(post);
        return;
    }

    if (action === "delete") {
        deletePost(post.id);
    }
}

async function openEditPostPrompt(post) {
    const newCaption = prompt("Edit caption:", post.caption || "");

    if (newCaption === null) {
        return;
    }

    try {
        const { response, data } = await patchRequest(`/posts/${post.id}/`, {
            caption: newCaption,
        });

        if (!response.ok) {
            alert(getErrorMessage(data));
            return;
        }

        await openPostDetail(post.id);
        refreshFeedAfterCommentChange();
    } catch (error) {
        console.error(error);
        alert("Could not edit post.");
    }
}

async function deletePost(postId) {
    if (!confirm("Delete this post?")) {
        return;
    }

    try {
        const { response, data } = await deleteRequest(`/posts/${postId}/`);

        if (!response.ok) {
            alert(getErrorMessage(data));
            return;
        }

        closePostDetail();

        const activeNav = document.querySelector(".app-nav-item.active");
        const page = activeNav ? activeNav.dataset.page : "home";

        if (page === "home") {
            loadHomeFeed();
        }

        if (page === "explore") {
            loadExploreFeed();
        }

        if (page === "profile") {
            loadProfilePage();
        }
    } catch (error) {
        console.error(error);
        alert("Could not delete post.");
    }
}