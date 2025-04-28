// main.js - Main initialization and coordination

document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners
    toggleBtn.addEventListener("click", () => {
        if (isDetecting) {
            stopDetection();
        } else {
                streamModal.show(); 
                startDetection();
        }
    });
  
    // Initialize all components
    initSpeechRecognition();
    
    // Request webcam access
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            mediaStream = stream;
            video.srcObject = stream;

            video.onloadeddata = () => {
                // Automatically start detection when video is ready
                // startDetection();
            }
        })
        .catch(err => {
            console.error("Error accessing webcam:", err);
    });
});