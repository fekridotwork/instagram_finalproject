let authPurpose = "login";

function checkAuthState() {
    const accessToken = localStorage.getItem("accessToken");

    if (accessToken) {
        showApp();
    } else {
        showAuth();
    }
}

async function requestOtp() {
    const identifier = identifierInput.value.trim();

    if (!identifier) {
        showMessage("Please enter your email or phone.", "danger");
        return;
    }

    try {
        const { response, data } = await postRequest("/auth/request-otp/", {
            identifier: identifier,
            purpose: authPurpose,
        });

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
}

async function verifyOtp() {
    const identifier = identifierInput.value.trim();
    const code = otpInput.value.trim();

    if (!identifier || !code) {
        showMessage("Please enter your email/phone and verification code.", "danger");
        return;
    }

    try {
        const { response, data } = await postRequest("/auth/verify-otp/", {
            identifier: identifier,
            purpose: authPurpose,
            code: code,
        });

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
}

function switchAuthMode() {
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

        showAuth();
    }
}