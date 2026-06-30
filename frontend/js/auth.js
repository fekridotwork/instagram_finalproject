const authTitle = document.getElementById("authTitle");
const authSubtitle = document.getElementById("authSubtitle");
const authLoginTab = document.getElementById("authLoginTab");
const authRegisterTab = document.getElementById("authRegisterTab");
const authModeSwitch = document.querySelector(".auth-mode-switch");

const switchText = document.getElementById("switchText");
const switchAuthBtn = document.getElementById("switchAuthBtn");

const identifierSection = document.getElementById("identifierSection");
const identifierInput = document.getElementById("identifierInput");
const identifierLabel = document.getElementById("identifierLabel");
const identifierHelp = document.getElementById("identifierHelp");
const identifierTabs = document.querySelectorAll(".auth-identifier-tab");

const authSubmitBtn = document.getElementById("authSubmitBtn");
const messageBox = document.getElementById("messageBox");

const otpSection = document.getElementById("otpSection");
const otpInput = document.getElementById("otpInput");
const verifyOtpBtn = document.getElementById("verifyOtpBtn");
const authIdentifierPreview = document.getElementById("authIdentifierPreview");
const changeIdentifierBtn = document.getElementById("changeIdentifierBtn");
const resendOtpBtn = document.getElementById("resendOtpBtn");
const otpCooldownText = document.getElementById("otpCooldownText");

const OTP_LENGTH = 5;

let authMode = "login";
let identifierType = "auto";
let currentIdentifier = "";
let resendTimer = null;
let resendSeconds = 0;

if (authLoginTab) {
    authLoginTab.addEventListener("click", function () {
        switchAuthMode("login");
    });
}

if (authRegisterTab) {
    authRegisterTab.addEventListener("click", function () {
        switchAuthMode("register");
    });
}

if (switchAuthBtn) {
    switchAuthBtn.addEventListener("click", function () {
        switchAuthMode(authMode === "login" ? "register" : "login");
    });
}

identifierTabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
        setIdentifierType(tab.dataset.identifierType);
    });
});

if (authSubmitBtn) {
    authSubmitBtn.addEventListener("click", requestOtp);
}

if (verifyOtpBtn) {
    verifyOtpBtn.addEventListener("click", verifyOtp);
}

if (changeIdentifierBtn) {
    changeIdentifierBtn.addEventListener("click", resetAuthStep);
}

if (resendOtpBtn) {
    resendOtpBtn.addEventListener("click", requestOtp);
}

if (otpInput) {
    otpInput.addEventListener("input", function () {
        otpInput.value = otpInput.value.replace(/\D/g, "").slice(0, OTP_LENGTH);
    });

    otpInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            verifyOtp();
        }
    });
}

function switchAuthMode(mode) {
    authMode = mode;
    resetAuthStep();

    authLoginTab?.classList.toggle("active", mode === "login");
    authRegisterTab?.classList.toggle("active", mode === "register");

    if (switchText) {
        switchText.textContent =
            mode === "login" ? "Don't have an account?" : "Already have an account?";
    }

    if (switchAuthBtn) {
        switchAuthBtn.textContent =
            mode === "login" ? "Create one" : "Log in";
    }
}

function setIdentifierType(type) {
    identifierType = type;

    identifierTabs.forEach(function (tab) {
        tab.classList.toggle("active", tab.dataset.identifierType === type);
    });

    if (type === "email") {
        identifierLabel.textContent = "Email";
        identifierInput.placeholder = "example@email.com";
        identifierInput.type = "email";
        identifierHelp.textContent = "We will send your code to this email.";
        return;
    }

    if (type === "phone") {
        identifierLabel.textContent = "Phone";
        identifierInput.placeholder = "0912...";
        identifierInput.type = "tel";
        identifierHelp.textContent = "We will send your code to this phone number.";
        return;
    }

    identifierLabel.textContent = "Email or phone";
    identifierInput.placeholder = "example@email.com or 0912...";
    identifierInput.type = "text";
    identifierHelp.textContent = "We will send you a one-time verification code.";
}

async function requestOtp() {
    const identifier = identifierInput.value.trim();

    if (!validateIdentifier(identifier)) {
        showAuthMessage("Enter a valid email or phone number.", "danger");
        return;
    }

    currentIdentifier = identifier;
    setPrimaryLoading(true, "Sending code...");

    try {
        const { response, data } = await postRequest("/auth/request-otp/", {
            identifier,
            purpose: authMode,
        });

        if (!response.ok) {
            showAuthMessage(getErrorMessage(data), "danger");
            return;
        }

        showOtpStep(identifier);
        startResendCooldown(120);
    } catch (error) {
        console.error(error);
        showAuthMessage("Could not send code. Try again.", "danger");
    } finally {
        setPrimaryLoading(false);
    }
}

function showOtpStep(identifier) {
    clearAuthMessage();
    clearOtpInput();

    identifierSection?.classList.add("d-none");
    authModeSwitch?.classList.add("d-none");
    otpSection?.classList.remove("d-none");

    if (authTitle) {
        authTitle.textContent = "Enter verification code";
    }

    if (authSubtitle) {
        authSubtitle.textContent = "Type the 5-digit code we sent you.";
    }

    if (authIdentifierPreview) {
        authIdentifierPreview.textContent = maskIdentifier(identifier);
    }

    setTimeout(function () {
        otpInput?.focus();
    }, 100);
}

async function verifyOtp() {
    const code = getOtpValue();

    if (code.length !== OTP_LENGTH) {
        showAuthMessage("Enter the complete 5-digit verification code.", "danger");
        return;
    }

    setVerifyLoading(true);

    try {
        const { response, data } = await postRequest("/auth/verify-otp/", {
            identifier: currentIdentifier,
            code,
            purpose: authMode,
        });

        if (!response.ok) {
            clearOtpInput();
            showAuthMessage(
                getErrorMessage(data) || "The code is incorrect or expired.",
                "danger"
            );
            return;
        }

        localStorage.setItem("accessToken", data.access);
        localStorage.setItem("refreshToken", data.refresh);

        clearAuthMessage();
        await checkAuthState();
    } catch (error) {
        console.error(error);
        showAuthMessage("Could not verify code. Try again.", "danger");
    } finally {
        setVerifyLoading(false);
    }
}

function resetAuthStep() {
    currentIdentifier = "";

    if (identifierInput) {
        identifierInput.disabled = false;
        identifierInput.value = "";
    }

    identifierSection?.classList.remove("d-none");
    authModeSwitch?.classList.remove("d-none");
    otpSection?.classList.add("d-none");

    if (authTitle) {
        authTitle.textContent =
            authMode === "login" ? "Welcome back" : "Create your account";
    }

    if (authSubtitle) {
        authSubtitle.textContent =
            authMode === "login"
                ? "Log in with your email or phone number."
                : "Register with your email or phone number.";
    }

    if (authSubmitBtn) {
        authSubmitBtn.disabled = false;
        authSubmitBtn.textContent =
            authMode === "login" ? "Send login code" : "Send register code";
    }

    clearOtpInput();
    clearAuthMessage();

    clearInterval(resendTimer);
    resendTimer = null;
    resendSeconds = 0;

    if (resendOtpBtn) {
        resendOtpBtn.disabled = true;
        resendOtpBtn.textContent = "Resend code";
    }

    if (otpCooldownText) {
        otpCooldownText.textContent = "You can request a new code soon.";
    }

    setTimeout(function () {
        identifierInput?.focus();
    }, 100);
}

function startResendCooldown(seconds) {
    resendSeconds = seconds;

    if (!resendOtpBtn) {
        return;
    }

    resendOtpBtn.disabled = true;

    clearInterval(resendTimer);
    updateCooldownText();

    resendTimer = setInterval(function () {
        resendSeconds -= 1;
        updateCooldownText();

        if (resendSeconds <= 0) {
            clearInterval(resendTimer);
            resendTimer = null;

            resendOtpBtn.disabled = false;
            resendOtpBtn.textContent = "Resend code";

            if (otpCooldownText) {
                otpCooldownText.textContent = "Didn't receive the code?";
            }
        }
    }, 1000);
}

function updateCooldownText() {
    const minutes = String(Math.floor(resendSeconds / 60)).padStart(2, "0");
    const seconds = String(resendSeconds % 60).padStart(2, "0");

    if (resendOtpBtn) {
        resendOtpBtn.textContent = `Resend in ${minutes}:${seconds}`;
    }
}

function getOtpValue() {
    return otpInput ? otpInput.value.replace(/\D/g, "").slice(0, OTP_LENGTH) : "";
}

function clearOtpInput() {
    if (otpInput) {
        otpInput.value = "";
    }
}

function validateIdentifier(identifier) {
    if (identifierType === "email") {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(identifier);
    }

    if (identifierType === "phone") {
        return /^\+?\d{8,15}$/.test(identifier);
    }

    return (
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(identifier) ||
        /^\+?\d{8,15}$/.test(identifier)
    );
}

function maskIdentifier(identifier) {
    if (identifier.includes("@")) {
        const [name, domain] = identifier.split("@");
        return `${name.slice(0, 2)}***@${domain}`;
    }

    return `${identifier.slice(0, 4)}***${identifier.slice(-3)}`;
}

function setPrimaryLoading(isLoading, text = "") {
    if (!authSubmitBtn) {
        return;
    }

    authSubmitBtn.disabled = isLoading;

    if (isLoading) {
        authSubmitBtn.dataset.originalText = authSubmitBtn.textContent;
        authSubmitBtn.textContent = text;
        return;
    }

    authSubmitBtn.textContent =
        authSubmitBtn.dataset.originalText ||
        (authMode === "login" ? "Send login code" : "Send register code");
}

function setVerifyLoading(isLoading) {
    if (!verifyOtpBtn) {
        return;
    }

    verifyOtpBtn.disabled = isLoading;
    verifyOtpBtn.textContent = isLoading ? "Verifying..." : "Continue";
}

function showAuthMessage(message, type = "danger") {
    if (!messageBox) {
        return;
    }

    messageBox.textContent = message;
    messageBox.className = `alert alert-${type}`;
    messageBox.classList.remove("d-none");
}

function clearAuthMessage() {
    if (!messageBox) {
        return;
    }

    messageBox.textContent = "";
    messageBox.className = "alert d-none";
}

async function logout() {
    const refreshToken = localStorage.getItem("refreshToken");

    try {
        if (refreshToken) {
            await postRequest("/auth/logout/", {
                refresh: refreshToken,
            });
        }
    } catch (error) {
        console.error("Logout request failed:", error);
    } finally {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");

        resetAuthStep();

        if (typeof currentUser !== "undefined") {
            currentUser = null;
        }

        showAuth();
    }
}

async function checkAuthState() {
    const accessToken = localStorage.getItem("accessToken");

    if (!accessToken) {
        resetAuthStep();
        showAuth();
        return;
    }

    try {
        const { response, data } = await getRequest("/profile/me/");

        if (!response.ok) {
            localStorage.removeItem("accessToken");
            localStorage.removeItem("refreshToken");
            resetAuthStep();
            showAuth();
            return;
        }

        currentUser = data;
        showApp(data);
    } catch (error) {
        console.error(error);
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        resetAuthStep();
        showAuth();
    }
}