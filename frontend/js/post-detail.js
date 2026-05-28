let activePostId = null;
let activeReplyParentId = null;
let activeReplyUsername = null;

async function openPostDetail(postId) {
    activePostId = postId;
    activeReplyParentId = null;
    activeReplyUsername = null;

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
    activeReplyParentId = null;
    activeReplyUsername = null;

    postModal.classList.add("d-none");
    postModalContent.innerHTML = "";
}

function renderPostDetail(post) {
    const mediaUrl = post.media ? getMediaUrl(post.media) : "";
    const comments = post.comments || [];

    postModalContent.innerHTML = `
        <div class="post-detail post-detail-glass">
            <div class="post-detail-media">
                ${
                    mediaUrl
                        ? `<img src="${mediaUrl}" alt="Post">`
                        : `<div class="post-detail-placeholder">No media</div>`
                }
            </div>

            <div class="post-detail-info">
                <button
                    class="post-detail-close-btn"
                    type="button"
                    onclick="closePostDetail()"
                >
                    ×
                </button>

                <div class="post-detail-user">
                    <div class="avatar post-detail-avatar">
                        ${renderUserAvatar(post)}
                    </div>

                    <div>
                        <strong>${post.username || "User"}</strong>
                        <p class="mb-0 text-white-50">${formatDate(post.created_at)}</p>
                    </div>

                    <button
                        class="post-detail-more-btn"
                        id="postDetailMoreBtn"
                        data-post-id="${post.id}"
                        type="button"
                    >
                        <i data-lucide="more-horizontal"></i>
                    </button>
                </div>

                <div class="post-detail-caption-block">
                    <strong>${post.username || "User"}</strong>

                    <p class="post-detail-caption">
                        ${post.caption || ""}
                    </p>
                </div>

                <div class="post-detail-meta">
                    <span>♡ ${post.likes_count || 0} likes</span>
                    <span id="postDetailCommentsCount">💬 ${post.comments_count || comments.length} comments</span>
                </div>

                <div class="post-detail-section-title">
                    <strong>Comments</strong>
                </div>

                <div id="postDetailComments" class="post-detail-comments">
                    ${renderPostComments(comments)}
                </div>

                <div class="reply-banner d-none" id="replyBanner">
                    <span id="replyBannerText"></span>

                    <button id="cancelReplyBtn" class="cancel-reply-btn" type="button">
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

                    <button id="submitCommentBtn" class="btn btn-primary" type="button">
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
        return renderCommentThread(comment);
    }).join("");
}

function renderCommentThread(comment) {
    const replies = flattenReplies(comment.replies || [], 1, comment.username || "User");

    return `
        <div class="post-detail-comment main-comment-card" data-comment-id="${comment.id}">
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
                        type="button"
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
                        type="button"
                    >
                        Reply
                    </button>
                </div>

                ${
                    replies.length
                        ? `
                            <div class="comment-thread">
                                ${replies.map(renderReplyRow).join("")}
                            </div>
                        `
                        : ""
                }
            </div>
        </div>
    `;
}

function flattenReplies(replies, level = 1, parentUsername = null, result = []) {
    replies.forEach(function (reply) {
        result.push({
            ...reply,
            replyLevel: Math.min(level, 3),
            parentUsername: parentUsername,
        });

        if (reply.replies && reply.replies.length) {
            flattenReplies(
                reply.replies,
                level + 1,
                reply.username || "User",
                result
            );
        }
    });

    return result;
}

function renderReplyRow(reply) {
    return `
        <div
            class="reply-thread-row"
            data-reply-level="${reply.replyLevel}"
            data-comment-id="${reply.id}"
        >
            <div class="comment-avatar reply-avatar">
                ${renderUserAvatar(reply)}
            </div>

            <div class="reply-thread-content">
                <div class="comment-row">
                    <p class="mb-0">
                        <strong>${reply.username || "User"}</strong>

                        ${
                            reply.parentUsername
                                ? `<span class="reply-target">replying to @${reply.parentUsername}</span>`
                                : ""
                        }

                        ${reply.text || ""}
                    </p>

                    <button
                        class="delete-comment-btn"
                        data-comment-id="${reply.id}"
                        title="Delete comment"
                        type="button"
                    >
                        ×
                    </button>
                </div>

                <div class="comment-meta-row">
                    <span class="comment-date">${formatDate(reply.created_at)}</span>

                    <button
                        class="reply-comment-btn"
                        data-comment-id="${reply.id}"
                        data-username="${reply.username || "User"}"
                        type="button"
                    >
                        Reply
                    </button>
                </div>
            </div>
        </div>
    `;
}

function bindCommentForm() {
    const commentInput = document.getElementById("commentInput");
    const submitCommentBtn = document.getElementById("submitCommentBtn");
    const commentsBox = document.getElementById("postDetailComments");
    const cancelReplyBtn = document.getElementById("cancelReplyBtn");

    if (!commentInput || !submitCommentBtn || !commentsBox) {
        console.warn("Comment form elements not found.");
        return;
    }

    submitCommentBtn.addEventListener("click", function (event) {
        event.preventDefault();
        submitComment(commentInput);
    });

    commentInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
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

    if (cancelReplyBtn) {
        cancelReplyBtn.addEventListener("click", resetReplyMode);
    }
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

    if (commentsBox) {
        commentsBox.innerHTML = renderPostComments(comments);
    }

    if (commentsCount) {
        commentsCount.textContent = `💬 ${countAllComments(comments)} comments`;
    }

    refreshFeedAfterCommentChange();
}

function countAllComments(comments) {
    return comments.reduce(function (total, comment) {
        const replies = comment.replies || [];
        return total + 1 + countAllComments(replies);
    }, 0);
}

function showCommentMessage(message, type) {
    const commentMessage = document.getElementById("commentMessage");

    if (!commentMessage) {
        return;
    }

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

    if (replyBanner) {
        replyBanner.classList.remove("d-none");
    }

    if (replyBannerText) {
        replyBannerText.textContent = `Replying to @${username}`;
    }

    if (commentInput) {
        commentInput.placeholder = `Reply to ${username}...`;
        commentInput.focus();
    }
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

async function openPostOwnerMenu(post) {
    const confirmedEdit = await openConfirmModal({
        title: "Edit post",
        description: "Do you want to edit this post caption?",
        confirmText: "Edit",
        cancelText: "Delete instead",
    });

    if (confirmedEdit) {
        await openEditPostModal(post);
        return;
    }

    const confirmedDelete = await openConfirmModal({
        title: "Delete post",
        description: "This post will be permanently deleted.",
        confirmText: "Delete",
        cancelText: "Cancel",
        danger: true,
    });

    if (confirmedDelete) {
        await deletePost(post.id);
    }
}

async function openEditPostModal(post) {
    const newCaption = await openInputModal({
        title: "Edit caption",
        description: "Update your post caption.",
        initialValue: post.caption || "",
        confirmText: "Save",
        required: false,
    });

    if (newCaption === null) {
        return;
    }

    try {
        const { response, data } = await patchRequest(`/posts/${post.id}/`, {
            caption: newCaption,
        });

        if (!response.ok) {
            showToast(getErrorMessage(data), "error");
            return;
        }

        showToast("Post updated.", "success");
        await openPostDetail(post.id);
        refreshFeedAfterCommentChange();
    } catch (error) {
        console.error(error);
        showToast("Could not edit post.", "error");
    }
}

async function deletePost(postId) {
    try {
        const { response, data } = await deleteRequest(`/posts/${postId}/`);

        if (!response.ok) {
            showToast(getErrorMessage(data), "error");
            return;
        }

        showToast("Post deleted.", "success");
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
        showToast("Could not delete post.", "error");
    }
}