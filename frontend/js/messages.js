let activeConversationId = null;
let activeConversationUser = null;
let messagesPollingInterval = null;
let currentUserId = null;
window.cachedConversations = [];

async function loadMessagesPage() {
    clearMessagesPolling();
    await loadCurrentMessageUser();

    feedList.innerHTML = `
        <section class="messages-page glass-card">
            <aside class="conversations-panel">
                <h5>Conversations</h5>
                <div id="conversationsList" class="conversations-list">
                    <p class="text-white-50">Loading conversations...</p>
                </div>
            </aside>

            <section class="chat-panel">
                <div id="chatHeader" class="chat-header">
                    Select a conversation
                </div>

                <div id="messagesList" class="messages-list">
                    <p class="text-white-50">Choose a conversation to start chatting.</p>
                </div>

                <div class="message-form">
                    <input
                        id="messageInput"
                        class="form-control"
                        type="text"
                        placeholder="Write a message..."
                        disabled
                    >
                    <button id="sendMessageBtn" class="btn btn-primary" disabled>
                        Send
                    </button>
                </div>
            </section>
        </section>
    `;

    await loadConversations();
}

async function loadConversations() {
    const conversationsList = document.getElementById("conversationsList");

    try {
        const { response, data } = await getRequest("/direct/conversations/");

        if (!response.ok) {
            conversationsList.innerHTML = `<p class="text-white-50">${getErrorMessage(data)}</p>`;
            return;
        }

        const conversations = Array.isArray(data) ? data : data.results || [];
        window.cachedConversations = conversations;

        renderConversations(conversations);
    } catch (error) {
        console.error(error);
        conversationsList.innerHTML = `<p class="text-white-50">Could not load conversations.</p>`;
    }
}

function renderConversations(conversations) {
    const conversationsList = document.getElementById("conversationsList");

    if (!conversations.length) {
        conversationsList.innerHTML = `<p class="text-white-50">No conversations yet.</p>`;
        return;
    }

    conversationsList.innerHTML = conversations.map(function (conversation) {
        const user = conversation.other_user || {};
        const username = user.username || "User";
        const image = user.profile_image ? getMediaUrl(user.profile_image) : "";

        return `
            <button
                class="conversation-item ${String(activeConversationId) === String(conversation.id) ? "active" : ""}"
                data-conversation-id="${conversation.id}"
            >
                <div class="conversation-avatar">
                    ${
                        image
                            ? `<img src="${image}" alt="${username}">`
                            : renderUserAvatar(user)
                    }
                </div>

                <div>
                    <strong>${username}</strong>
                    <p>${conversation.last_message || "No messages yet."}</p>
                </div>
            </button>
        `;
    }).join("");

    document.querySelectorAll(".conversation-item").forEach(function (item) {
        item.addEventListener("click", function () {
            const conversation = window.cachedConversations.find(function (conv) {
                return String(conv.id) === String(item.dataset.conversationId);
            });

            const user = conversation ? conversation.other_user : null;

            loadConversationMessages(item.dataset.conversationId, user);
        });
    });
}

async function loadConversationMessages(conversationId, user = null, options = {}) {
    activeConversationId = conversationId;
    activeConversationUser = user || activeConversationUser;

    const silent = options.silent || false;

    const messagesList = document.getElementById("messagesList");
    const messageInput = document.getElementById("messageInput");
    const sendMessageBtn = document.getElementById("sendMessageBtn");
    const chatHeader = document.getElementById("chatHeader");

    if (activeConversationUser) {
        const username = activeConversationUser.username || "User";

        chatHeader.innerHTML = `
            <div class="chat-user">
                <div class="conversation-avatar">
                    ${
                        activeConversationUser.profile_image
                            ? `<img src="${getMediaUrl(activeConversationUser.profile_image)}" alt="${username}">`
                            : renderUserAvatar(activeConversationUser)
                    }
                </div>

                <div>
                    <strong>${username}</strong>
                    <small>@${username}</small>
                </div>
            </div>
        `;
    }

    if (!silent) {
        messagesList.innerHTML = `<p class="text-white-50">Loading messages...</p>`;
    }

    try {
        const { response, data } = await getRequest(
            `/direct/conversations/${conversationId}/messages/`
        );

        if (!response.ok) {
            messagesList.innerHTML = `<p class="text-white-50">${getErrorMessage(data)}</p>`;
            return;
        }

        const messages = Array.isArray(data) ? data : data.results || [];

        renderMessages(messages);

        messageInput.disabled = false;
        sendMessageBtn.disabled = false;

        bindMessageForm();
        renderConversations(window.cachedConversations);
        startMessagesPolling();
    } catch (error) {
        console.error(error);

        if (!silent) {
            messagesList.innerHTML = `<p class="text-white-50">Could not load messages.</p>`;
        }
    }
}

function renderMessages(messages) {
    const messagesList = document.getElementById("messagesList");

    if (!messages.length) {
        messagesList.innerHTML = `<p class="text-white-50">No messages yet.</p>`;
        return;
    }

    messagesList.innerHTML = messages.map(function (message) {
        const isMine = Number(message.sender_id) === Number(currentUserId); 
        return `
            <div class="message-row ${isMine ? "mine" : "theirs"}">
                <div class="message-bubble">
                    <p>${message.text}</p>

                    <div class="message-meta">
                        <span>${formatDate(message.created_at)}</span>

                        ${
                            isMine
                                ? `
                                    <div class="message-actions">
                                        <button
                                            type="button"
                                            class="message-action-btn edit-message-btn"
                                            data-message-id="${message.id}"
                                            data-message-text="${message.text}"
                                        >
                                            Edit
                                        </button>

                                        <button
                                            type="button"
                                            class="message-action-btn delete-message-btn"
                                            data-message-id="${message.id}"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                `
                                : ""
                        }
                    </div>
                </div>
            </div>
        `;
    }).join("");

    messagesList.scrollTop = messagesList.scrollHeight;
    bindMessageActionButtons();
}

function bindMessageForm() {
    const messageInput = document.getElementById("messageInput");
    const sendMessageBtn = document.getElementById("sendMessageBtn");

    sendMessageBtn.onclick = sendMessage;

    messageInput.onkeydown = function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    };
}

async function sendMessage() {
    const messageInput = document.getElementById("messageInput");
    const text = messageInput.value.trim();

    if (!text || !activeConversationId) {
        return;
    }

    try {
        const { response, data } = await postRequest(
            `/direct/conversations/${activeConversationId}/messages/`,
            { text: text }
        );

        if (!response.ok) {
            alert(getErrorMessage(data));
            return;
        }

        messageInput.value = "";
        await loadConversationMessages(activeConversationId, activeConversationUser);
        await loadConversations();
    } catch (error) {
        console.error(error);
        alert("Could not send message.");
    }
}

function startMessagesPolling() {
    clearMessagesPolling();

    messagesPollingInterval = setInterval(function () {
        if (activeConversationId) {
            loadConversationMessages(activeConversationId, activeConversationUser, {
                silent: true,
            });
        }
    }, 5000);
}

function clearMessagesPolling() {
    if (messagesPollingInterval) {
        clearInterval(messagesPollingInterval);
        messagesPollingInterval = null;
    }
}
async function loadCurrentMessageUser() {
    if (currentUserId) {
        return;
    }

    try {
        const { response, data } = await getRequest("/auth/me/");

        if (response.ok) {
            currentUserId = data.id;
        }
    } catch (error) {
        console.error(error);
    }
}
function bindMessageActionButtons() {
    document.querySelectorAll(".edit-message-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            const messageId = button.dataset.messageId;
            const currentText = button.dataset.messageText || "";

            editMessage(messageId, currentText);
        });
    });

    document.querySelectorAll(".delete-message-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            const messageId = button.dataset.messageId;

            deleteMessage(messageId);
        });
    });
}

async function editMessage(messageId, currentText) {
    const newText = prompt("Edit message:", currentText);

    if (newText === null) {
        return;
    }

    const text = newText.trim();

    if (!text) {
        alert("Message cannot be empty.");
        return;
    }

    try {
        const { response, data } = await patchRequest(
            `/direct/messages/${messageId}/`,
            { text: text }
        );

        if (!response.ok) {
            alert(getErrorMessage(data));
            return;
        }

        await loadConversationMessages(activeConversationId, activeConversationUser);
        await loadConversations();
    } catch (error) {
        console.error(error);
        alert("Could not edit message.");
    }
}

async function deleteMessage(messageId) {
    const confirmed = confirm("Delete this message?");

    if (!confirmed) {
        return;
    }

    try {
        const { response, data } = await deleteRequest(
            `/direct/messages/${messageId}/`
        );

        if (!response.ok) {
            alert(getErrorMessage(data));
            return;
        }

        await loadConversationMessages(activeConversationId, activeConversationUser);
        await loadConversations();
    } catch (error) {
        console.error(error);
        alert("Could not delete message.");
    }
}