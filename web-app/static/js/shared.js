// shared.js - Global variables and DOM references shared across modules

// Global DOM elements 
window.video = null;
window.toggleBtn = null;

// Global state
window.chatWindow = null;
window.isDetecting = false;
window.detectionTimeout = null;
window.mediaStream = null;
window.recognition = null;
window.isListening = false;
window.commandInProgress = false;

// Create canvas for webcam capture
window.canvas = document.createElement("canvas");
window.ctx = canvas.getContext("2d");

// Initialize DOM references when document is ready
document.addEventListener('DOMContentLoaded', function() {
    window.video = document.getElementById("video");
    window.toggleBtn = document.getElementById("toggle-btn");
});