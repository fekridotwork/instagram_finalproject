async function getRequest(endpoint) {
    const accessToken = localStorage.getItem("accessToken");

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${accessToken}`,
        },
    });

    const data = await response.json();

    return {
        response,
        data,
    };
}

async function postRequest(endpoint, payload = {}) {
    const accessToken = localStorage.getItem("accessToken");

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": accessToken ? `Bearer ${accessToken}` : "",
        },
        body: JSON.stringify(payload),
    });

    const data = await response.json();

    return {
        response,
        data,
    };
}

async function deleteRequest(endpoint) {
    const accessToken = localStorage.getItem("accessToken");

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${accessToken}`,
        },
    });

    const data = await response.json();

    return {
        response,
        data,
    };
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
async function postFormRequest(endpoint, formData) {
    const accessToken = localStorage.getItem("accessToken");

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${accessToken}`,
        },
        body: formData,
    });

    const data = await response.json();

    return {
        response,
        data,
    };
}