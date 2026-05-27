function openCreatePostModal() {
    createPostModal.classList.remove("d-none");
    clearCreatePostMessage();
}

function closeCreatePostModal() {
    createPostModal.classList.add("d-none");
    postMediaInput.value = "";
    postCaptionInput.value = "";
    postVisibilityInput.value = "public";
    clearCreatePostMessage();
}

async function submitPost() {
    const mediaFile = postMediaInput.files[0];
    const caption = postCaptionInput.value.trim();
    const visibility = postVisibilityInput.value;

    if (!mediaFile) {
        showCreatePostMessage("Please choose an image or video.", "danger");
        return;
    }

    const mediaType = mediaFile.type.startsWith("video/")
        ? "video"
        : "image";

    const formData = new FormData();
    formData.append("media", mediaFile);
    formData.append("caption", caption);
    formData.append("media_type", mediaType);
    formData.append("visibility", visibility);

    submitPostBtn.disabled = true;
    submitPostBtn.textContent = "Publishing...";

    try {
        const { response, data } = await postFormRequest("/posts/", formData);

        if (response.ok) {
            closeCreatePostModal();
            loadHomeFeed();
        } else {
            showCreatePostMessage(getErrorMessage(data), "danger");
        }
    } catch (error) {
        console.error(error);
        showCreatePostMessage("Could not publish post.", "danger");
    } finally {
        submitPostBtn.disabled = false;
        submitPostBtn.textContent = "Publish";
    }
}

function showCreatePostMessage(message, type) {
    createPostMessage.textContent = message;
    createPostMessage.className = `alert alert-${type}`;
}

function clearCreatePostMessage() {
    createPostMessage.textContent = "";
    createPostMessage.className = "alert d-none";
}