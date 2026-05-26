const API_BASE_URL = "http://127.0.0.1:8000/api";

let authPurpose = "login";

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

sendOtpBtn.addEventListener("click", async function () {
    const identifier = identifierInput.value.trim();

    if (!identifier) {
        showMessage("Please enter your email or phone.", "danger");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/request-otp/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                identifier: identifier,
                purpose: authPurpose,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            showMessage("Verification code sent. Check your email or phone.", "success");
            otpSection.classList.remove("d-none");
        } else {
            showMessage(getErrorMessage(data), "danger");
        }
    } catch (error) {
        console.error(error);
        showMessage("Cannot connect to server.", "danger");
    }
});

verifyOtpBtn.addEventListener("click", async function () {
    const identifier = identifierInput.value.trim();
    const code = otpInput.value.trim();

    if (!identifier || !code) {
        showMessage("Please enter your email/phone and verification code.", "danger");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/verify-otp/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                identifier: identifier,
                purpose: authPurpose,
                code: code,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("accessToken", data.access);
            localStorage.setItem("refreshToken", data.refresh);

            showApp();
        } else {
            showMessage(getErrorMessage(data), "danger");
        }
    } catch (error) {
        console.error(error);
        showMessage("Cannot connect to server.", "danger");
    }
});

switchAuthBtn.addEventListener("click", function () {
    if (authPurpose === "login") {
        authPurpose = "register";

        authTitle.textContent = "Create your account";
        authSubtitle.textContent = "Start sharing your world in a few seconds.";
        switchText.textContent = "Already have an account?";
        switchAuthBtn.textContent = "Login";
        sendOtpBtn.textContent = "Send signup code";

        resetOtpState();
    } else {
        authPurpose = "login";

        authTitle.textContent = "Welcome back";
        authSubtitle.textContent = "Enter your email or phone to continue.";
        switchText.textContent = "Don't have an account?";
        switchAuthBtn.textContent = "Create one";
        sendOtpBtn.textContent = "Send login code";

        resetOtpState();
    }
});

logoutBtn.addEventListener("click", function () {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    showAuth();
});

function checkAuthState() {
    const accessToken = localStorage.getItem("accessToken");

    if (accessToken) {
        showApp();
    } else {
        showAuth();
    }
}

function showApp() {
    authPage.classList.add("d-none");
    appPage.classList.remove("d-none");
}

function showAuth() {
    appPage.classList.add("d-none");
    authPage.classList.remove("d-none");
}

function showMessage(message, type) {
    messageBox.textContent = message;
    messageBox.className = `alert alert-${type}`;
}

function clearMessage() {
    messageBox.textContent = "";
    messageBox.className = "alert d-none";
}

function resetOtpState() {
    otpSection.classList.add("d-none");
    otpInput.value = "";
    clearMessage();
}

function getErrorMessage(data) {
    if (data.detail) {
        return data.detail;
    }

    const firstKey = Object.keys(data)[0];

    if (firstKey && Array.isArray(data[firstKey])) {
        return data[firstKey][0];
    }

    return "Something went wrong.";
}