document.addEventListener("DOMContentLoaded", function() {
    const chatForm = document.getElementById("status-form");
    const messageForm = document.getElementById("message-form");
    const messageInput = document.getElementById("message-input");
    const messagesContainer = document.getElementById("messages");
    
    let otherUserId = "";
    
    chatForm.addEventListener("submit", function(e) {
        e.preventDefault();
        const statusText = chatForm.elements["status_text"].value;
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/post_status");
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                window.location.reload();
            }
        };
        xhr.send("status_text=" + encodeURIComponent(statusText));
    });

    const discussButtons = document.getElementsByClassName("btn-discuss");
    for (let i = 0; i < discussButtons.length; i++) {
        const discussButton = discussButtons[i];
        discussButton.addEventListener("click", function(e) {
            otherUserId = discussButton.getAttribute("data-user-id");
            loadChat();
        });
    }

    messageForm.addEventListener("submit", function(e) {
        e.preventDefault();
        const message = messageInput.value;
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/send_message");
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                messageInput.value = "";
                loadChat();
            }
        };
        xhr.send("other_user_id=" + encodeURIComponent(otherUserId) + "&message=" + encodeURIComponent(message));
    });

    function loadChat() {
        const xhr = new XMLHttpRequest();
        xhr.open("GET", "/get_chat/" + encodeURIComponent(otherUserId));
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                messagesContainer.innerHTML = "";
                for (let i = 0; i < response.length; i++) {
                    const message = response[i];
                    const p = document.createElement("p");
                    p.textContent = message.sender + ": " + message.message;
                    messagesContainer.appendChild(p);
                }
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        };
        xhr.send();
    }
});
