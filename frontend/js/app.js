const authPage = document.getElementById("authPage");
const appPage = document.getElementById("appPage");

const authTitle = document.getElementById("authTitle");
const authSubtitle = document.getElementById("authSubtitle");
const switchText = document.getElementById("switchText");
const switchAuthBtn = document.getElementById("switchAuthBtn");

const identifierInput = document.getElementById("identifierInput");
const sendOtpBtn = document.getElementById("sendOtpBtn");

const otpSection = document.getElementById("otpSection");
const otpInput = document.getElementById("otpInput");
const verifyOtpBtn = document.getElementById("verifyOtpBtn");

const messageBox = document.getElementById("messageBox");
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

const editProfileModalBackdrop = document.getElementById("editProfileModalBackdrop");
const closeEditProfileModalBtn = document.getElementById("closeEditProfileModalBtn");
const submitEditProfileBtn = document.getElementById("submitEditProfileBtn");

if (editProfileModalBackdrop) {
    editProfileModalBackdrop.addEventListener("click", closeEditProfileModal);
}

if (closeEditProfileModalBtn) {
    closeEditProfileModalBtn.addEventListener("click", closeEditProfileModal);
}

if (submitEditProfileBtn) {
    submitEditProfileBtn.addEventListener("click", submitEditProfile);
}

const sidebarProfileCard = document.getElementById("sidebarProfileCard");
const topProfileBtn = document.getElementById("topProfileBtn");

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

checkAuthState();

sendOtpBtn.addEventListener("click", requestOtp);
verifyOtpBtn.addEventListener("click", verifyOtp);
switchAuthBtn.addEventListener("click", switchAuthMode);
logoutBtn.addEventListener("click", logout);

feedList.addEventListener("click", handleFeedClick);

postModalBackdrop.addEventListener("click", closePostDetail);
closePostModalBtn.addEventListener("click", closePostDetail);

newPostBtn.addEventListener("click", openCreatePostModal);
createPostModalBackdrop.addEventListener("click", closeCreatePostModal);
closeCreatePostModalBtn.addEventListener("click", closeCreatePostModal);
submitPostBtn.addEventListener("click", submitPost);

globalSearchInput.addEventListener("input", handleGlobalSearchInput);

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

refreshIcons();