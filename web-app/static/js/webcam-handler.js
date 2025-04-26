// Capture frames from the video 
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");

// Send webcam frame to backend
function sendFrame() {
    if (!isDetecting) return;

    console.log("Sending Frames ... ")
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Copy the current webcam frame onto the canvas aka screenshot
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert the canvas image into a base64-encoded jpeg
    const dataURL = canvas.toDataURL("image/jpeg");

    // Send the image to the ML-client via JSON string
    fetch("/generate-comment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataURL })
    })
        .then(res => res.json())
        .then(data => {
            if (isDetecting){
                showComment(data);
            }
        });

    detectionTimeout = setTimeout(sendFrame, 5000); // send a snapshot every 5 seconds
}

let chatActivityInterval;

// Start webcam capture and processing
function startDetection() {
    isDetecting = true;
    toggleBtn.textContent = "Stop Live Stream";

    if (!chatWindow || chatWindow.closed) {
        chatWindow = window.open("/chat", "_blank", "width=400,height=600");
    } 

    // Start voice recognition
    if (recognition) {
        isListening = true; 
        recognition.start();  
        updateSpeechDebugger('status', 'Listening');
    } else {
        updateSpeechDebugger('status', 'ERROR: Recognition not initialized');
    }

    sendFrame();

    chatActivityInterval = setInterval(() => {
        const [min, max] = viewerSlider.noUiSlider.get().map(v => parseInt(v));
        const viewerCount = Math.floor(Math.random() * (max - min + 1)) + min;

        let commentDelay;
        if (viewerCount > 8000) commentDelay = 8000;
        else if (viewerCount > 5000) commentDelay = 10000;
        else if (viewerCount > 2000) commentDelay = 12000;
        else commentDelay = 15000;

        clearInterval(chatActivityInterval); // Reset previous interval
        chatActivityInterval = setInterval(() => {
            sendFrame();
        }, commentDelay);
    }, 10000) // Re-evaluate frequency every 10s
}

// Stop webcam capture and processing
function stopDetection() {
    isDetecting = false;
    toggleBtn.textContent = "Start Live Streaming";
    clearTimeout(detectionTimeout);  

    if (recognition) {
        isListening = false; 
        recognition.stop();  
        updateSpeechDebugger('status', 'Stopped');
    }

    clearInterval(chatActivityInterval);
    document.getElementById('displayed-title').textContent = 'Fake It Till You Make It - Live Stream';
    document.getElementById('genre-badge').textContent = '';
    document.getElementById('viewer-number').textContent = '0';
}