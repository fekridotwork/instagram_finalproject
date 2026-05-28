async function getRequest(endpoint) {
    return requestWithAuth(endpoint, {
        method: "GET",
    });
}

async function postRequest(endpoint, payload = {}) {
    return requestWithAuth(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });
}

async function deleteRequest(endpoint) {
    return requestWithAuth(endpoint, {
        method: "DELETE",
    });
}

async function postFormRequest(endpoint, formData) {
    return requestWithAuth(endpoint, {
        method: "POST",
        body: formData,
    });
}

async function requestWithAuth(endpoint, options = {}, retry = true) {
    const accessToken = localStorage.getItem("accessToken");

    const headers = {
        ...(options.headers || {}),
    };

    if (accessToken) {
        headers["Authorization"] = `Bearer ${accessToken}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });

    const data = await safeJson(response);

    if (response.status === 401 && retry) {
        const refreshed = await refreshAccessToken();

        if (refreshed) {
            return requestWithAuth(endpoint, options, false);
        }

        forceLogout();
    }

    return {
        response,
        data,
    };
}

async function refreshAccessToken() {
    const refreshToken = localStorage.getItem("refreshToken");

    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                refresh: refreshToken,
            }),
        });

        const data = await safeJson(response);

        if (!response.ok || !data.access) {
            return false;
        }

        localStorage.setItem("accessToken", data.access);
        return true;
    } catch (error) {
        console.error(error);
        return false;
    }
}

function forceLogout() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");

    if (typeof showAuth === "function") {
        showAuth();
    }
}

async function safeJson(response) {
    try {
        return await response.json();
    } catch {
        return {};
    }
}

function getErrorMessage(data) {
    if (data.detail) {
        return data.detail;
    }

    if (data.message) {
        return data.message;
    }

    const firstKey = Object.keys(data)[0];

    if (firstKey && Array.isArray(data[firstKey])) {
        return data[firstKey][0];
    }

    return "Something went wrong.";
}

async function patchFormRequest(endpoint, formData) {
    return requestWithAuth(endpoint, {
        method: "PATCH",
        body: formData,
    });
}
async function getFollowers() {
    return requestWithAuth("/api/me/followers/");
}

async function getFollowing() {
    return requestWithAuth("/api/me/following/");
}

async function getMutualFollowers(userId) {
    return requestWithAuth(`/api/users/${userId}/mutual-followers/`);
}
async function deleteJsonRequest(endpoint, payload) {
    return requestWithAuth(endpoint, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });
}
async function patchRequest(endpoint, payload = {}) {
    return requestWithAuth(endpoint, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });
}