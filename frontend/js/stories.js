let currentStories = [];
let currentStoryGroups = [];

let activeStoryGroupIndex = 0;
let activeStoryItemIndex = 0;

let storyTimer = null;
let storyStartedAt = null;
let storyRemainingTime = 5000;
let isStoryPaused = false;

const DEFAULT_STORY_DURATION = 5000;
const SEEN_STORIES_STORAGE_KEY = "moment_seen_stories";

function getSeenStoriesMap() {
    try {
        return JSON.parse(localStorage.getItem(SEEN_STORIES_STORAGE_KEY)) || {};
    } catch (error) {
        return {};
    }
}

function saveSeenStoriesMap(map) {
    localStorage.setItem(SEEN_STORIES_STORAGE_KEY, JSON.stringify(map));
}

function markStoryGroupAsSeen(group) {
    if (!group || !group.stories.length) {
        return;
    }

    const latestStoryId = group.stories[group.stories.length - 1].id;
    const seenMap = getSeenStoriesMap();

    seenMap[group.userId] = latestStoryId;
    saveSeenStoriesMap(seenMap);
}

function hasUnseenStories(group) {
    if (!group || !group.stories.length) {
        return false;
    }

    const latestStoryId = group.stories[group.stories.length - 1].id;
    const seenMap = getSeenStoriesMap();

    return String(seenMap[group.userId]) !== String(latestStoryId);
}

async function loadHomeStories() {
    storiesRow.classList.remove("d-none");

    storiesRow.innerHTML = `
        <div class="text-white-50">Loading stories...</div>
    `;

    try {
        const { response, data } = await getRequest("/stories/feed/");

        if (!response.ok) {
            storiesRow.innerHTML = `
                ${await renderYourStoryButton(false)}
                <div class="text-white-50">Could not load stories.</div>
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
            <div class="text-white-50">Cannot connect to stories.</div>
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
            <div class="text-white-50">No stories yet</div>
        `;

        bindCreateStoryButton();
        return;
    }

    storiesRow.innerHTML = `
        ${yourStoryButton}
        ${storyGroups.map(renderStoryBubble).join("")}
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
    const hasUnseenStory = hasUnseenStories(group);

    return `
        <button class="story-bubble ${hasUnseenStory ? "" : "story-seen"}" type="button" data-story-group-index="${index}">
            <div class="story-avatar-wrap">
                ${renderAvatar({
                    username: group.username,
                    profileImage: group.profile_image,
                    hasStory: hasUnseenStory,
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
            const startIndex = getFirstUnseenStoryIndex(currentStoryGroups[groupIndex]);

            openStoryViewer(groupIndex, startIndex);
        });
    });
}

function getFirstUnseenStoryIndex(group) {
    if (!group || !group.stories.length) {
        return 0;
    }

    const seenMap = getSeenStoriesMap();
    const seenLatestId = seenMap[group.userId];

    if (!seenLatestId) {
        return 0;
    }

    const firstUnseenIndex = group.stories.findIndex(function (story) {
        return String(story.id) > String(seenLatestId);
    });

    return firstUnseenIndex >= 0 ? firstUnseenIndex : 0;
}

function openStoryViewer(groupIndex, itemIndex = 0) {
    const group = currentStoryGroups[groupIndex];

    if (!group || !group.stories.length) {
        return;
    }

    activeStoryGroupIndex = groupIndex;
    activeStoryItemIndex = itemIndex;

    markStoryGroupAsSeen(group);
    renderStories(currentStoryGroups);

    storyViewerModal.classList.remove("d-none");
    document.addEventListener("keydown", handleStoryKeyboard);

    renderActiveStory();
}

function renderActiveStory() {
    clearStoryTimer();

    const group = currentStoryGroups[activeStoryGroupIndex];
    const story = group?.stories?.[activeStoryItemIndex];

    if (!group || !story) {
        closeStoryViewer();
        return;
    }

    const mediaUrl = story.media ? getMediaUrl(story.media) : "";
    const isTextOnly = !mediaUrl;

    storyViewerContent.innerHTML = `
        <div class="story-viewer-shell ${isTextOnly ? "text-story-shell" : ""}">
            <div class="story-progress-row">
                ${group.stories.map(function (_, index) {
                    return `
                        <div class="story-progress-segment">
                            <div
                                class="story-progress-fill ${
                                    index < activeStoryItemIndex
                                        ? "completed"
                                        : index === activeStoryItemIndex
                                            ? "running"
                                            : ""
                                }"
                            ></div>
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
                    <p>${timeAgo(story.created_at)}</p>
                </div>

                <button class="story-close-btn" type="button" onclick="closeStoryViewer()">×</button>
            </div>

            <button class="story-nav-zone story-nav-prev" type="button" onclick="goToPreviousStory()"></button>
            <button class="story-nav-zone story-nav-next" type="button" onclick="goToNextStory()"></button>

            <div class="story-hold-zone"></div>

            <div class="story-viewer-media">
                ${
                    mediaUrl
                        ? renderStoryMedia(story, mediaUrl)
                        : `<div class="story-viewer-text">${story.text || "No media"}</div>`
                }
            </div>

            <div id="storyHeartBurst" class="story-heart-burst">♥</div>
        </div>
    `;

    bindStoryPauseEvents();
    bindStoryDoubleTap();
    preloadNextStory();
    refreshIcons();

    if (story.media_type === "video") {
        bindVideoDuration();
    } else {
        startStoryTimer(DEFAULT_STORY_DURATION);
    }
}

function renderStoryMedia(story, mediaUrl) {
    if (story.media_type === "video") {
        return `
            <video autoplay muted playsinline class="story-viewer-image" id="activeStoryVideo">
                <source src="${mediaUrl}">
            </video>
        `;
    }

    return `
        <img class="story-viewer-image" src="${mediaUrl}" alt="Story">
    `;
}

function bindVideoDuration() {
    const video = document.getElementById("activeStoryVideo");

    if (!video) {
        startStoryTimer(DEFAULT_STORY_DURATION);
        return;
    }

    video.addEventListener("loadedmetadata", function () {
        const duration = video.duration && Number.isFinite(video.duration)
            ? Math.max(video.duration * 1000, 2500)
            : DEFAULT_STORY_DURATION;

        startStoryTimer(duration);
    });

    video.addEventListener("ended", goToNextStory);

    setTimeout(function () {
        if (!storyTimer) {
            startStoryTimer(DEFAULT_STORY_DURATION);
        }
    }, 800);
}

function bindStoryPauseEvents() {
    const shell = document.querySelector(".story-viewer-shell");
    const holdZone = document.querySelector(".story-hold-zone");

    if (!shell || !holdZone) {
        return;
    }

    holdZone.addEventListener("mousedown", pauseStoryTimer);
    holdZone.addEventListener("mouseup", resumeStoryTimer);
    holdZone.addEventListener("mouseleave", resumeStoryTimer);

    holdZone.addEventListener("touchstart", pauseStoryTimer);
    holdZone.addEventListener("touchend", resumeStoryTimer);
}

function bindStoryDoubleTap() {
    const shell = document.querySelector(".story-viewer-shell");

    if (!shell) {
        return;
    }

    let lastTap = 0;

    shell.addEventListener("click", function () {
        const now = Date.now();

        if (now - lastTap < 280) {
            showStoryHeartBurst();
        }

        lastTap = now;
    });
}

function showStoryHeartBurst() {
    const heart = document.getElementById("storyHeartBurst");

    if (!heart) {
        return;
    }

    heart.classList.remove("show");
    void heart.offsetWidth;
    heart.classList.add("show");
}

function startStoryTimer(duration) {
    storyRemainingTime = duration;
    storyStartedAt = Date.now();
    isStoryPaused = false;

    const shell = document.querySelector(".story-viewer-shell");
    const progress = document.querySelector(".story-progress-fill.running");

    shell?.classList.remove("story-paused");

    if (progress) {
        progress.style.animationDuration = `${duration}ms`;
    }

    storyTimer = setTimeout(goToNextStory, duration);
}

function pauseStoryTimer() {
    if (isStoryPaused || !storyTimer) {
        return;
    }

    clearTimeout(storyTimer);
    storyTimer = null;

    storyRemainingTime = Math.max(
        storyRemainingTime - (Date.now() - storyStartedAt),
        0
    );

    isStoryPaused = true;

    document.querySelector(".story-viewer-shell")?.classList.add("story-paused");

    const video = document.getElementById("activeStoryVideo");
    if (video) {
        video.pause();
    }
}

function resumeStoryTimer() {
    if (!isStoryPaused) {
        return;
    }

    isStoryPaused = false;
    storyStartedAt = Date.now();

    document.querySelector(".story-viewer-shell")?.classList.remove("story-paused");

    const video = document.getElementById("activeStoryVideo");
    if (video) {
        video.play().catch(function () {});
    }

    storyTimer = setTimeout(goToNextStory, storyRemainingTime);
}

function clearStoryTimer() {
    if (storyTimer) {
        clearTimeout(storyTimer);
        storyTimer = null;
    }

    storyStartedAt = null;
    storyRemainingTime = DEFAULT_STORY_DURATION;
    isStoryPaused = false;
}

function goToNextStory() {
    clearStoryTimer();

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

        const nextGroup = currentStoryGroups[activeStoryGroupIndex];
        markStoryGroupAsSeen(nextGroup);
        renderStories(currentStoryGroups);

        renderActiveStory();
        return;
    }

    closeStoryViewer();
}

function goToPreviousStory() {
    clearStoryTimer();

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

function handleStoryKeyboard(event) {
    if (storyViewerModal.classList.contains("d-none")) {
        return;
    }

    if (event.key === "ArrowRight") {
        goToNextStory();
    }

    if (event.key === "ArrowLeft") {
        goToPreviousStory();
    }

    if (event.key === "Escape") {
        closeStoryViewer();
    }

    if (event.key === " ") {
        event.preventDefault();

        if (isStoryPaused) {
            resumeStoryTimer();
        } else {
            pauseStoryTimer();
        }
    }
}

function preloadNextStory() {
    const group = currentStoryGroups[activeStoryGroupIndex];

    if (!group) {
        return;
    }

    const nextStory =
        group.stories[activeStoryItemIndex + 1] ||
        currentStoryGroups[activeStoryGroupIndex + 1]?.stories?.[0];

    if (!nextStory || !nextStory.media) {
        return;
    }

    const mediaUrl = getMediaUrl(nextStory.media);

    if (nextStory.media_type === "video") {
        const video = document.createElement("video");
        video.preload = "auto";
        video.src = mediaUrl;
        return;
    }

    const img = new Image();
    img.src = mediaUrl;
}

function closeStoryViewer() {
    clearStoryTimer();

    document.removeEventListener("keydown", handleStoryKeyboard);

    storyViewerModal.classList.add("d-none");
    storyViewerContent.innerHTML = "";
}

function hideStories() {
    storiesRow.classList.add("d-none");
    storiesRow.innerHTML = "";
}