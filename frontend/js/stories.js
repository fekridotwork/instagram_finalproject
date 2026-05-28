let currentStories = [];
let currentStoryGroups = [];

let activeStoryGroupIndex = 0;
let activeStoryItemIndex = 0;

async function loadHomeStories() {
    storiesRow.classList.remove("d-none");

    storiesRow.innerHTML = `
        <div class="text-white-50">
            Loading stories...
        </div>
    `;

    try {
        const { response, data } = await getRequest("/stories/feed/");

        if (!response.ok) {
            storiesRow.innerHTML = `
                ${await renderYourStoryButton(false)}
                <div class="text-white-50">
                    Could not load stories.
                </div>
            `;
            bindCreateStoryButton();
            return;
        }

        currentStories = Array.isArray(data) ? data : data.results || [];
        currentStoryGroups = groupStoriesByUser(currentStories);

        await renderStories(currentStoryGroups);
    } catch (error) {
        console.error(error);

        storiesRow.innerHTML = `
            ${await renderYourStoryButton(false)}
            <div class="text-white-50">
                Cannot connect to stories.
            </div>
        `;

        bindCreateStoryButton();
    }
}

function groupStoriesByUser(stories) {
    const groupsMap = new Map();

    stories.forEach(function (story) {
        const username = story.username || story.user?.username || "User";
        const userId = story.user_id || story.user?.id || username;

        if (!groupsMap.has(userId)) {
            groupsMap.set(userId, {
                userId: userId,
                username: username,
                profile_image: story.profile_image || story.user?.profile_image || "",
                stories: [],
            });
        }

        groupsMap.get(userId).stories.push(story);
    });

    return Array.from(groupsMap.values());
}

async function renderStories(storyGroups) {
    const yourStoryButton = await renderYourStoryButton(true);

    if (!storyGroups.length) {
        storiesRow.innerHTML = `
            ${yourStoryButton}
            <div class="text-white-50">
                No stories yet
            </div>
        `;

        bindCreateStoryButton();
        return;
    }

    storiesRow.innerHTML = `
        ${yourStoryButton}

        ${storyGroups.map(function (group, index) {
            return renderStoryBubble(group, index);
        }).join("")}
    `;

    bindStoryClicks();
    bindCreateStoryButton();
}

async function renderYourStoryButton(hasStory = false) {
    try {
        const { response, data } = await getRequest("/profile/me/");

        if (!response.ok) {
            return renderFallbackYourStoryButton();
        }

        return `
            <button class="story-bubble story-add" type="button">
                <div class="story-avatar-wrap">
                    ${renderAvatar({
                        username: data.username || "User",
                        profileImage: data.profile_image,
                        hasStory: hasStory,
                        size: 72
                    })}

                    <span class="story-plus-badge">+</span>
                </div>

                <span>Your story</span>
            </button>
        `;
    } catch (error) {
        console.error(error);
        return renderFallbackYourStoryButton();
    }
}

function renderFallbackYourStoryButton() {
    return `
        <button class="story-bubble story-add" type="button">
            <div class="story-avatar-wrap">
                ${renderAvatar({
                    username: "User",
                    profileImage: "",
                    hasStory: false,
                    size: 72
                })}

                <span class="story-plus-badge">+</span>
            </div>

            <span>Your story</span>
        </button>
    `;
}

function renderStoryBubble(group, index) {
    return `
        <button class="story-bubble" type="button" data-story-group-index="${index}">
            <div class="story-avatar-wrap">
                ${renderAvatar({
                    username: group.username,
                    profileImage: group.profile_image,
                    hasStory: true,
                    size: 72
                })}
            </div>

            <span>${group.username}</span>
        </button>
    `;
}

function bindStoryClicks() {
    document.querySelectorAll(".story-bubble:not(.story-add)").forEach(function (button) {
        button.addEventListener("click", function () {
            const groupIndex = Number(button.dataset.storyGroupIndex);
            openStoryViewer(groupIndex, 0);
        });
    });
}

function openStoryViewer(groupIndex, itemIndex = 0) {
    const group = currentStoryGroups[groupIndex];

    if (!group || !group.stories.length) {
        return;
    }

    activeStoryGroupIndex = groupIndex;
    activeStoryItemIndex = itemIndex;

    storyViewerModal.classList.remove("d-none");

    renderActiveStory();
}

function renderActiveStory() {
    const group = currentStoryGroups[activeStoryGroupIndex];

    if (!group) {
        closeStoryViewer();
        return;
    }

    const story = group.stories[activeStoryItemIndex];

    if (!story) {
        closeStoryViewer();
        return;
    }

    const mediaUrl = story.media ? getMediaUrl(story.media) : "";

    storyViewerContent.innerHTML = `
        <div class="story-viewer-shell">
            <div class="story-progress-row">
                ${group.stories.map(function (_, index) {
                    return `
                        <div class="story-progress-segment">
                            <div class="story-progress-fill ${index <= activeStoryItemIndex ? "active" : ""}"></div>
                        </div>
                    `;
                }).join("")}
            </div>

            <div class="story-viewer-header">
                <div class="story-viewer-avatar">
                    ${renderAvatar({
                        username: group.username,
                        profileImage: group.profile_image,
                        hasStory: true,
                        size: 42
                    })}
                </div>

                <div>
                    <strong>${group.username}</strong>
                    <p>${formatDate(story.created_at)}</p>
                </div>

                <button class="story-close-btn" type="button" onclick="closeStoryViewer()">
                    ×
                </button>
            </div>

            <button class="story-nav-zone story-nav-prev" type="button" onclick="goToPreviousStory()"></button>
            <button class="story-nav-zone story-nav-next" type="button" onclick="goToNextStory()"></button>

            <div class="story-viewer-media">
                ${
                    mediaUrl
                        ? renderStoryMedia(story, mediaUrl)
                        : `<div class="story-viewer-text">${story.text || "No media"}</div>`
                }

            </div>
        </div>
    `;
}

function goToNextStory() {
    const group = currentStoryGroups[activeStoryGroupIndex];

    if (!group) {
        closeStoryViewer();
        return;
    }

    if (activeStoryItemIndex < group.stories.length - 1) {
        activeStoryItemIndex += 1;
        renderActiveStory();
        return;
    }

    if (activeStoryGroupIndex < currentStoryGroups.length - 1) {
        activeStoryGroupIndex += 1;
        activeStoryItemIndex = 0;
        renderActiveStory();
        return;
    }

    closeStoryViewer();
}

function goToPreviousStory() {
    if (activeStoryItemIndex > 0) {
        activeStoryItemIndex -= 1;
        renderActiveStory();
        return;
    }

    if (activeStoryGroupIndex > 0) {
        activeStoryGroupIndex -= 1;
        const previousGroup = currentStoryGroups[activeStoryGroupIndex];
        activeStoryItemIndex = previousGroup.stories.length - 1;
        renderActiveStory();
        return;
    }

    renderActiveStory();
}

function renderStoryMedia(story, mediaUrl) {
    if (story.media_type === "video") {
        return `
            <video controls autoplay class="story-viewer-image">
                <source src="${mediaUrl}">
            </video>
        `;
    }

    return `
        <img class="story-viewer-image" src="${mediaUrl}" alt="Story">
    `;
}

function closeStoryViewer() {
    storyViewerModal.classList.add("d-none");
    storyViewerContent.innerHTML = "";
}

function hideStories() {
    storiesRow.classList.add("d-none");
    storiesRow.innerHTML = "";
}