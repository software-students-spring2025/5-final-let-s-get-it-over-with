// Display AI response to voice command
function showBotResponse(comment) {
  if (chatWindow && !chatWindow.closed) {
      chatWindow.postMessage({ comment }, "*");
  }
  
  displayMessage(comment);
}

// Display webcam-generated comment
function showComment(data) {
  if (chatWindow && !chatWindow.closed) {
      chatWindow.postMessage({ comment: data.comment }, "*");
  }
  
  displayMessage(data);
}

// Common function to display messages in chat
function displayMessage(data) {
  const chat = document.getElementById("chat-box");
  const messages = document.getElementById("messages");

  // Create wrapper
  const wrapper = document.createElement("div");
  wrapper.className = "message-wrapper";

  // Create inline message content container
  const content = document.createElement("div");
  content.className = "message-content";

  // Add random badges
  const badgeList = ["mod.png", "prime.png", "turbo.png"];
  const shuffledBadges = badgeList.sort(() => 0.5 - Math.random());
  const badgeCount = Math.floor(Math.random() * (badgeList.length + 1));
  const selectedBadges = shuffledBadges.slice(0, badgeCount);

  selectedBadges.forEach(badge => {
      const img = document.createElement("img");
      img.src = `/static/badges/${badge}`;
      img.alt = badge.split(".")[0];
      img.style.height = "18px";
      img.style.verticalAlign = "middle";
      img.style.marginRight = "2px";
      content.appendChild(img);
  });

  // Random color for username
  const usernameColors = [
      "#FF0000", "#0000FF", "#008000", "#B22222", "#FF7F50", "#9ACD32", "#FF4500",
      "#2E8B57", "#DAA520", "#D2691E", "#5F9EA0", "#1E90FF", "#FF69B4", "#8A2BE2", "#00FF7F"
  ];
  const usernameColor = usernameColors[Math.floor(Math.random() * usernameColors.length)];

  // Append full message line
  const message = document.createElement("span");
  message.className = "message";
  message.innerHTML = `<span class="message-username" style="color:${usernameColor}"><strong>${data.username}</strong></span>: ${data.comment}`;

  content.appendChild(message);
  wrapper.appendChild(content);
  messages.appendChild(wrapper);
  chat.scrollTop = chat.scrollHeight;
}