const authPage = document.getElementById("authPage");
const appPage = document.getElementById("appPage");

const logoutBtn = document.getElementById("logoutBtn");

const feedList = document.getElementById("feedList");
const pageTitle = document.getElementById("pageTitle");
const pageSubtitle = document.getElementById("pageSubtitle");
const navItems = document.querySelectorAll(".app-nav-item");

const postModal = document.getElementById("postModal");
const postModalContent = document.getElementById("postModalContent");
const postModalBackdrop = document.getElementById("postModalBackdrop");
const closePostModalBtn = document.getElementById("closePostModalBtn");

const newPostBtn = document.getElementById("newPostBtn");

const createPostModal = document.getElementById("createPostModal");
const createPostModalBackdrop = document.getElementById("createPostModalBackdrop");
const closeCreatePostModalBtn = document.getElementById("closeCreatePostModalBtn");
const postMediaInput = document.getElementById("postMediaInput");
const postCaptionInput = document.getElementById("postCaptionInput");
const postVisibilityInput = document.getElementById("postVisibilityInput");
const submitPostBtn = document.getElementById("submitPostBtn");
const createPostMessage = document.getElementById("createPostMessage");

const globalSearchInput = document.getElementById("globalSearchInput");

const storiesRow = document.getElementById("storiesRow");

const storyViewerModal = document.getElementById("storyViewerModal");
const storyViewerBackdrop = document.getElementById("storyViewerBackdrop");
const closeStoryViewerBtn = document.getElementById("closeStoryViewerBtn");
const storyViewerContent = document.getElementById("storyViewerContent");

const createStoryModal = document.getElementById("createStoryModal");
const createStoryModalBackdrop = document.getElementById("createStoryModalBackdrop");
const closeCreateStoryModalBtn = document.getElementById("closeCreateStoryModalBtn");
const storyMediaInput = document.getElementById("storyMediaInput");
const storyTextInput = document.getElementById("storyTextInput");
const storyVisibilityInput = document.getElementById("storyVisibilityInput");
const submitStoryBtn = document.getElementById("submitStoryBtn");
const createStoryMessage = document.getElementById("createStoryMessage");

const storyPreviewCanvas = document.getElementById("storyPreviewCanvas");
const storyPreviewImage = document.getElementById("storyPreviewImage");
const storyTextOverlay = document.getElementById("storyTextOverlay");
const storyEmptyState = document.getElementById("storyEmptyState");

const storyTextSizeInput = document.getElementById("storyTextSizeInput");
const storyColorButtons = document.querySelectorAll(".story-color-btn");
const storyImageZoomInput = document.getElementById("storyImageZoomInput");

const editProfileModalBackdrop = document.getElementById("editProfileModalBackdrop");
const closeEditProfileModalBtn = document.getElementById("closeEditProfileModalBtn");
const submitEditProfileBtn = document.getElementById("submitEditProfileBtn");

const sidebarProfileCard = document.getElementById("sidebarProfileCard");
const topProfileBtn = document.getElementById("topProfileBtn");

const followModal = document.getElementById("followModal");
const followModalBackdrop = document.getElementById("followModalBackdrop");
const closeFollowModalBtn = document.getElementById("closeFollowModalBtn");
const followModalTitle = document.getElementById("followModalTitle");
const followModalList = document.getElementById("followModalList");

if (storyImageZoomInput) {
    storyImageZoomInput.addEventListener("input", handleStoryImageZoomChange);
}

if (storyPreviewImage) {
    storyPreviewImage.addEventListener("mousedown", startDraggingStoryImage);
}

if (editProfileModalBackdrop) {
    editProfileModalBackdrop.addEventListener("click", closeEditProfileModal);
}

if (closeEditProfileModalBtn) {
    closeEditProfileModalBtn.addEventListener("click", closeEditProfileModal);
}

if (submitEditProfileBtn) {
    submitEditProfileBtn.addEventListener("click", submitEditProfile);
}

if (sidebarProfileCard) {
    sidebarProfileCard.addEventListener("click", function () {
        handleNavigation("profile");
    });
}

if (topProfileBtn) {
    topProfileBtn.addEventListener("click", function () {
        handleNavigation("profile");
    });
}

if (followModalBackdrop) {
    followModalBackdrop.addEventListener("click", closeFollowModal);
}

if (closeFollowModalBtn) {
    closeFollowModalBtn.addEventListener("click", closeFollowModal);
}

if (logoutBtn) {
    logoutBtn.addEventListener("click", logout);
}

if (feedList) {
    feedList.addEventListener("click", handleFeedClick);
}

if (postModalBackdrop) {
    postModalBackdrop.addEventListener("click", closePostDetail);
}

if (closePostModalBtn) {
    closePostModalBtn.addEventListener("click", closePostDetail);
}

if (newPostBtn) {
    newPostBtn.addEventListener("click", openCreatePostModal);
}

if (createPostModalBackdrop) {
    createPostModalBackdrop.addEventListener("click", closeCreatePostModal);
}

if (closeCreatePostModalBtn) {
    closeCreatePostModalBtn.addEventListener("click", closeCreatePostModal);
}

if (submitPostBtn) {
    submitPostBtn.addEventListener("click", submitPost);
}

if (globalSearchInput) {
    globalSearchInput.addEventListener("input", handleGlobalSearchInput);
}

if (storyViewerBackdrop) {
    storyViewerBackdrop.addEventListener("click", closeStoryViewer);
}

if (closeStoryViewerBtn) {
    closeStoryViewerBtn.addEventListener("click", closeStoryViewer);
}

if (createStoryModalBackdrop) {
    createStoryModalBackdrop.addEventListener("click", closeCreateStoryModal);
}

if (closeCreateStoryModalBtn) {
    closeCreateStoryModalBtn.addEventListener("click", closeCreateStoryModal);
}

if (submitStoryBtn) {
    submitStoryBtn.addEventListener("click", submitStory);
}

if (storyMediaInput) {
    storyMediaInput.addEventListener("change", handleStoryMediaPreview);
}

if (storyTextInput) {
    storyTextInput.addEventListener("input", handleStoryTextPreview);
}

if (storyTextOverlay) {
    storyTextOverlay.addEventListener("mousedown", startDraggingStoryText);
}

if (storyTextSizeInput) {
    storyTextSizeInput.addEventListener("input", handleStoryTextSizeChange);
}

storyColorButtons.forEach(function (button) {
    button.addEventListener("click", function () {
        handleStoryTextColorChange(button.dataset.color);
    });
});

navItems.forEach(function (item) {
    item.addEventListener("click", function () {
        const page = item.dataset.page;

        setActiveNav(item);
        handleNavigation(page);
    });
});

async function hydrateSidebarProfileCard() {
    try {
        const { response, data } = await getRequest("/profile/me/");

        if (!response.ok) {
            return;
        }

        const sidebarAvatar = document.querySelector(".sidebar-user-avatar");
        const sidebarUsername = document.querySelector(".sidebar-user-info strong");
        const topAvatar = document.querySelector(".glass-user-avatar");

        const avatarHtml = data.profile_image
            ? `<img src="${getMediaUrl(data.profile_image)}" alt="${data.username}">`
            : `<span>${data.username ? data.username[0].toUpperCase() : "U"}</span>`;

        if (sidebarAvatar) {
            sidebarAvatar.innerHTML = avatarHtml;
        }

        if (topAvatar) {
            topAvatar.innerHTML = avatarHtml;
        }

        if (sidebarUsername) {
            sidebarUsername.textContent = data.username || "My profile";
        }
    } catch (error) {
        console.error(error);
    }
}

window.hydrateSidebarProfileCard = hydrateSidebarProfileCard;

checkAuthState();
hydrateSidebarProfileCard();
refreshIcons();