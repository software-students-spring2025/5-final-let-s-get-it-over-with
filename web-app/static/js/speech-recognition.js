// Voice recognition variables
let recognition = null;
let isListening = false;
let commandInProgress = false;

// Initialize speech recognition
function initSpeechRecognition() {
    // Add debugging tools
    addSpeechDebugger();
    updateSpeechDebugger('status', 'Initializing...');

    // Check browser support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn("Your browser doesn't support speech recognition. Try Chrome or Edge.");
        return;
    }

    // Create speech recognition object
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

    // Configure recognition
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    // Handle recognition start
    recognition.onstart = function () {
        console.log("Speech recognition started successfully");
        updateSpeechDebugger('status', 'Listening actively');
    };

    // Process speech results
    recognition.onresult = function (event) {
        console.log("Speech recognition result event received:", event);

        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                finalTranscript += transcript;
                updateSpeechDebugger('heard', finalTranscript);
                processVoiceInput(finalTranscript);
            } else {
                interimTranscript += transcript;
                updateSpeechDebugger('heard', interimTranscript + ' (interim)');
            }
        }
    };

    // Handle errors
    recognition.onerror = function (event) {
        console.error('Speech recognition error:', event.error);
        updateSpeechDebugger('status', 'Error: ' + event.error);
    };

    // Handle recognition end
    recognition.onend = function () {
        if (isListening) {
            recognition.start();
            updateSpeechDebugger('status', 'Restarted listening');
        } else {
            updateSpeechDebugger('status', 'Stopped');
        }
    };

    updateSpeechDebugger('status', 'Initialized, ready to start');
}

// Process voice commands
function processVoiceInput(text) {
    console.log("Heard:", text);

    // Check for wake phrase "hey chat"
    const lowerText = text.toLowerCase().trim();

    if (lowerText.includes("hey chat")) {
        // Extract question after "hey chat"
        const questionIndex = lowerText.indexOf("hey chat") + 8;
        let question = text.slice(questionIndex).trim();

        if (question && !commandInProgress) {
            commandInProgress = true;
            sendQuestionToAPI(question);
        }
    }
}

// Send voice question to backend
function sendQuestionToAPI(question) {
    const responseCount = Math.floor(Math.random() * 4) + 1;

    fetch("/process-question", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question, responseCount: responseCount })
    })
        .then(res => res.json())
        .then(data => {
            if (Array.isArray(data.responses)) {
                data.responses.forEach(response => {
                    showComment(response);
                });
            } else {
                console.error("Invalid format received:", data);
            }
            commandInProgress = false;
        })
        .catch(err => {
            console.error("Error sending question:", err);
            commandInProgress = false;
        });
}

// Display multiple responses with staggered timing
function showMultipleResponses(responses) {
    if (!responses || responses.length === 0) return;

    // Show first response immediately
    showBotResponse(responses[0]);

    // Show remaining responses with staggered delays to simulate typing
    responses.slice(1).forEach((response, index) => {
        // Add increasing delay for each response (500-1500ms)
        const delay = 800 + (index * 700);
        setTimeout(() => {
            showBotResponse(response);
        }, delay);
    });
}