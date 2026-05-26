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

checkAuthState();

sendOtpBtn.addEventListener("click", requestOtp);
verifyOtpBtn.addEventListener("click", verifyOtp);
switchAuthBtn.addEventListener("click", switchAuthMode);
logoutBtn.addEventListener("click", logout);