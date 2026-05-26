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