// Add speech debugging panel
function addSpeechDebugger() {
  const debug = document.createElement('div');
  debug.id = 'speech-debugger';
  debug.style.position = 'fixed';
  debug.style.bottom = '10px';
  debug.style.right = '10px';
  debug.style.backgroundColor = 'rgba(0,0,0,0.7)';
  debug.style.color = 'white';
  debug.style.padding = '10px';
  debug.style.borderRadius = '5px';
  debug.style.zIndex = '9999';
  debug.style.maxWidth = '300px';
  debug.style.fontSize = '12px';
  debug.innerHTML = `
      <div>Status: <span id="speech-status">Not initialized</span></div>
      <div>Heard: <span id="speech-heard">Nothing yet</span></div>
      <div>Command detected: <span id="command-detected">No</span></div>
  `;
  document.body.appendChild(debug);
}

// Update speech debugger panel
function updateSpeechDebugger(type, text) {
  if (document.getElementById('speech-debugger')) {
      if (type === 'status') {
          document.getElementById('speech-status').textContent = text;
      } else if (type === 'heard') {
          document.getElementById('speech-heard').textContent = text;
          
          // Check if "hey chat" is in the text
          if (text && text.toLowerCase().includes('hey chat')) {
              document.getElementById('command-detected').textContent = "YES";
              document.getElementById('command-detected').style.color = '#4CAF50';
              
              // Reset after 2 seconds
              setTimeout(() => {
                  document.getElementById('command-detected').textContent = "No";
                  document.getElementById('command-detected').style.color = 'white';
              }, 2000);
          }
      }
  }
}