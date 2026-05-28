let isDraggingStoryText = false;
let storyTextDragOffsetX = 0;
let storyTextDragOffsetY = 0;
let currentStoryTextColor = "#ffffff";

function bindCreateStoryButton() {
    const createStoryButton = document.querySelector(".story-add");

    if (!createStoryButton) {
        return;
    }

    createStoryButton.addEventListener("click", openCreateStoryModal);
}

function openCreateStoryModal() {
    createStoryModal.classList.remove("d-none");
    clearCreateStoryMessage();
}

function closeCreateStoryModal() {
    createStoryModal.classList.add("d-none");

    storyMediaInput.value = "";
    storyTextInput.value = "";
    storyVisibilityInput.value = "public";

    if (storyTextSizeInput) {
        storyTextSizeInput.value = 34;
    }

    currentStoryTextColor = "#ffffff";

    storyPreviewImage.src = "";
    storyPreviewImage.classList.add("d-none");

    storyTextOverlay.textContent = "";
    storyTextOverlay.classList.add("d-none");
    storyTextOverlay.style.left = "50%";
    storyTextOverlay.style.top = "50%";
    storyTextOverlay.style.transform = "translate(-50%, -50%)";
    storyTextOverlay.style.fontSize = "34px";
    storyTextOverlay.style.color = "#ffffff";

    storyEmptyState.classList.remove("d-none");

    clearCreateStoryMessage();
}

function handleStoryMediaPreview() {
    const file = storyMediaInput.files[0];

    if (!file) {
        storyPreviewImage.classList.add("d-none");
        storyEmptyState.classList.remove("d-none");
        return;
    }

    const imageUrl = URL.createObjectURL(file);

    storyPreviewImage.src = imageUrl;
    storyPreviewImage.classList.remove("d-none");
    storyEmptyState.classList.add("d-none");
}

function handleStoryTextPreview() {
    const text = storyTextInput.value.trim();

    if (!text) {
        storyTextOverlay.classList.add("d-none");
        storyTextOverlay.textContent = "";
        return;
    }

    storyTextOverlay.textContent = text;
    storyTextOverlay.classList.remove("d-none");
}

function handleStoryTextSizeChange() {
    storyTextOverlay.style.fontSize = `${storyTextSizeInput.value}px`;
}

function handleStoryTextColorChange(color) {
    currentStoryTextColor = color;
    storyTextOverlay.style.color = color;
}

function startDraggingStoryText(event) {
    if (storyTextOverlay.classList.contains("d-none")) {
        return;
    }

    isDraggingStoryText = true;

    const overlayRect = storyTextOverlay.getBoundingClientRect();

    storyTextDragOffsetX = event.clientX - overlayRect.left;
    storyTextDragOffsetY = event.clientY - overlayRect.top;

    storyTextOverlay.style.cursor = "grabbing";

    document.addEventListener("mousemove", dragStoryText);
    document.addEventListener("mouseup", stopDraggingStoryText);
}

function dragStoryText(event) {
    if (!isDraggingStoryText) {
        return;
    }

    const canvasRect = storyPreviewCanvas.getBoundingClientRect();

    let x = event.clientX - canvasRect.left - storyTextDragOffsetX;
    let y = event.clientY - canvasRect.top - storyTextDragOffsetY;

    const maxX = storyPreviewCanvas.clientWidth - storyTextOverlay.offsetWidth;
    const maxY = storyPreviewCanvas.clientHeight - storyTextOverlay.offsetHeight;

    x = Math.max(0, Math.min(x, maxX));
    y = Math.max(0, Math.min(y, maxY));

    storyTextOverlay.style.left = `${x}px`;
    storyTextOverlay.style.top = `${y}px`;
    storyTextOverlay.style.transform = "none";
}

function stopDraggingStoryText() {
    isDraggingStoryText = false;

    storyTextOverlay.style.cursor = "grab";

    document.removeEventListener("mousemove", dragStoryText);
    document.removeEventListener("mouseup", stopDraggingStoryText);
}

async function submitStory() {
    const mediaFile = storyMediaInput.files[0];
    const text = storyTextInput.value.trim();
    const visibility = storyVisibilityInput.value;

    if (!mediaFile && !text) {
        showCreateStoryMessage(
            "Please choose media or write text.",
            "danger"
        );
        return;
    }

    submitStoryBtn.disabled = true;
    submitStoryBtn.textContent = "Sharing...";

    try {
        const formData = new FormData();

        if (mediaFile) {
            const isVideo = mediaFile.type.startsWith("video/");
            const isImage = mediaFile.type.startsWith("image/");

            if (isVideo) {
                formData.append("media", mediaFile);
                formData.append("media_type", "video");

                if (text) {
                    formData.append("text", text);
                }
            } else if (isImage) {
                const finalImageBlob = await exportStoryCanvas();

                const finalImageFile = new File(
                    [finalImageBlob],
                    "story.png",
                    {
                        type: "image/png",
                    }
                );

                formData.append("media", finalImageFile);
                formData.append("media_type", "image");

                if (text) {
                    formData.append("text", text);
                }
            } else {
                showCreateStoryMessage(
                    "Only image and video files are supported.",
                    "danger"
                );
                return;
            }
        } else {
            formData.append("media_type", "text");
            formData.append("text", text);
        }

        formData.append("visibility", visibility);

        const { response, data } = await postFormRequest(
            "/stories/",
            formData
        );

        if (response.ok) {
            closeCreateStoryModal();
            await loadHomeStories();
        } else {
            console.log(data);
            showCreateStoryMessage(
                getErrorMessage(data),
                "danger"
            );
        }
    } catch (error) {
        console.error(error);

        showCreateStoryMessage(
            "Could not share story.",
            "danger"
        );
    } finally {
        submitStoryBtn.disabled = false;
        submitStoryBtn.textContent = "Share story";
    }
}

function exportStoryCanvas() {
    return new Promise(function (resolve, reject) {
        const image = storyPreviewImage;

        if (!image.src) {
            reject(new Error("No image selected."));
            return;
        }

        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");

        const width = 1080;
        const height = 1920;

        canvas.width = width;
        canvas.height = height;

        const imageRatio = image.naturalWidth / image.naturalHeight;
        const canvasRatio = width / height;

        let drawWidth;
        let drawHeight;
        let drawX;
        let drawY;

        if (imageRatio > canvasRatio) {
            drawHeight = height;
            drawWidth = height * imageRatio;
            drawX = (width - drawWidth) / 2;
            drawY = 0;
        } else {
            drawWidth = width;
            drawHeight = width / imageRatio;
            drawX = 0;
            drawY = (height - drawHeight) / 2;
        }

        context.drawImage(image, drawX, drawY, drawWidth, drawHeight);

        const text = storyTextInput.value.trim();

        if (text) {
            const canvasRect = storyPreviewCanvas.getBoundingClientRect();
            const textRect = storyTextOverlay.getBoundingClientRect();

            const scaleX = width / canvasRect.width;
            const scaleY = height / canvasRect.height;

            const textX = (textRect.left - canvasRect.left + textRect.width / 2) * scaleX;
            const textY = (textRect.top - canvasRect.top + textRect.height / 2) * scaleY;

            const fontSize = Number.parseInt(window.getComputedStyle(storyTextOverlay).fontSize, 10) * scaleY;

            context.font = `800 ${fontSize}px Arial`;
            context.fillStyle = currentStoryTextColor;
            context.textAlign = "center";
            context.textBaseline = "middle";

            context.shadowColor = "rgba(0, 0, 0, 0.65)";
            context.shadowBlur = 14;

            wrapCanvasText(context, text, textX, textY, width * 0.82, fontSize * 1.25);
        }

        canvas.toBlob(function (blob) {
            if (!blob) {
                reject(new Error("Could not export story."));
                return;
            }

            resolve(blob);
        }, "image/png");
    });
}

function wrapCanvasText(context, text, x, y, maxWidth, lineHeight) {
    const words = text.split(" ");
    const lines = [];
    let currentLine = "";

    words.forEach(function (word) {
        const testLine = currentLine ? `${currentLine} ${word}` : word;
        const metrics = context.measureText(testLine);

        if (metrics.width > maxWidth && currentLine) {
            lines.push(currentLine);
            currentLine = word;
        } else {
            currentLine = testLine;
        }
    });

    lines.push(currentLine);

    const startY = y - ((lines.length - 1) * lineHeight) / 2;

    lines.forEach(function (line, index) {
        context.fillText(line, x, startY + index * lineHeight);
    });
}

function showCreateStoryMessage(message, type) {
    createStoryMessage.textContent = message;
    createStoryMessage.className = `alert alert-${type}`;
}

function clearCreateStoryMessage() {
    createStoryMessage.textContent = "";
    createStoryMessage.className = "alert d-none";
}