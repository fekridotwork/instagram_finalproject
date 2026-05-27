let currentStories = [];

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
                <div class="text-white-50">
                    Could not load stories.
                </div>
            `;
            return;
        }

        currentStories = Array.isArray(data) ? data : data.results || [];
        renderStories(currentStories);
    } catch (error) {
        console.error(error);

        storiesRow.innerHTML = `
            <div class="text-white-50">
                Cannot connect to stories.
            </div>
        `;
    }
}

function renderStories(stories) {
    if (!stories.length) {
        storiesRow.innerHTML = `
            <button class="story-item story-add" type="button">
                +
            </button>
            <div class="text-white-50">
                No stories yet
            </div>
        `;

        bindCreateStoryButton();

        return;
    }

    storiesRow.innerHTML = `
        <button class="story-item story-add" type="button">
            +
        </button>

        ${stories.map(function (story, index) {
            const username = story.username || story.user?.username || "User";
            const mediaUrl = story.media ? getMediaUrl(story.media) : "";

            return `
                <button class="story-bubble" type="button" data-story-index="${index}">
                    <div class="story-avatar">
                        ${
                            mediaUrl
                                ? `<img src="${mediaUrl}" alt="${username}">`
                                : `<span>${username[0].toUpperCase()}</span>`
                        }
                    </div>
                    <span>${username}</span>
                </button>
            `;
        }).join("")}
    `;

    bindStoryClicks();
    bindCreateStoryButton();
}

function bindStoryClicks() {
    document.querySelectorAll(".story-bubble").forEach(function (button) {
        button.addEventListener("click", function () {
            const storyIndex = Number(button.dataset.storyIndex);
            openStoryViewer(storyIndex);
        });
    });
}

function openStoryViewer(index) {
    const story = currentStories[index];

    if (!story) {
        return;
    }

    storyViewerModal.classList.remove("d-none");

    const username = story.username || story.user?.username || "User";
    const mediaUrl = story.media ? getMediaUrl(story.media) : "";

    storyViewerContent.innerHTML = `
        <div class="story-viewer-header">
            <div class="story-viewer-avatar">
                ${username[0].toUpperCase()}
            </div>

            <div>
                <strong>${username}</strong>
                <p>${formatDate(story.created_at)}</p>
            </div>
        </div>

        <div class="story-viewer-media">
            ${
                mediaUrl
                    ? renderStoryMedia(story, mediaUrl)
                    : `<div class="story-viewer-text">${story.text || "No media"}</div>`
            }
        </div>

        ${
            story.text
                ? `<p class="story-viewer-caption">${story.text}</p>`
                : ""
        }
    `;
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