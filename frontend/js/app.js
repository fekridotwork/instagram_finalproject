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

navItems.forEach(function (item) {
    item.addEventListener("click", function () {
        const page = item.dataset.page;

        setActiveNav(item);
        handleNavigation(page);
    });
});

refreshIcons();