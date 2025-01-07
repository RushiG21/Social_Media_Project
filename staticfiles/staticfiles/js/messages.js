// Open a chat with a user
async function openChat(username, profilePicUrl) {
    try {
        document.getElementById('chat-modal').style.display = 'block';
        const chatProfilePic = document.getElementById('chat-profile-pic');
        const chatUsername = document.getElementById('chat-username');

        chatProfilePic.src = profilePicUrl ; // Fallback if no image URL
        chatUsername.textContent = username;
        const response = await fetch(`/chat/${username}/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to open chat.');
        }

        const data = await response.json();
        const chatForm = document.getElementById('chat-form');
        chatForm.dataset.chatId = data.chat_id;
        loadMessages(data.chat_id);
    } catch (error) {
        console.error('Error opening chat:', error);
        alert('Unable to open chat. Please try again.');
    }
}

// Load messages for a chat
async function loadMessages(chatId) {
    try {
        const response = await fetch(`/chat/${chatId}/messages/`);
        if (!response.ok) {
            throw new Error('Failed to load messages.');
        }
        const data = await response.json();
        const chatBox = document.getElementById('chat-box');
        const currentUser = chatBox.getAttribute('data-current-user');
        chatBox.innerHTML = '';
        if (data.messages.length === 0) {
            chatBox.innerHTML = '<p>No messages yet.</p>';
        } else {
            data.messages.forEach((message) => {
                const isSentByCurrentUser = message.sender__username === currentUser;
                console.log(message.sender__username, currentUser, isSentByCurrentUser);
                const messageElement = document.createElement('div');
                messageElement.className = isSentByCurrentUser ? 'message sent' : 'message received';
                messageElement.innerHTML = `
                    <strong>${message.sender__username}</strong> 
                    <p>${message.content}</p>
                    <span class="timestamp">${new Date(message.timestamp).toLocaleString('en-US', {year: 'numeric',month: 'short',day: 'numeric',hour: 'numeric',minute: '2-digit',hour12: true})}</span>
                `;
                chatBox.appendChild(messageElement);
            });
        }
        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
        console.error('Error loading messages:', error);
        alert('Failed to load messages. Please try again.');
    }
}


// Send a message in the chat
async function sendMessage(event) {
    event.preventDefault();
    const chatForm = document.getElementById('chat-form');
    const chatId = chatForm.dataset.chatId;
    const chatInput = document.getElementById('chat-message');
    const messageContent = chatInput.value.trim();
    if (!chatId) {
        console.error('Chat ID is not defined.');
        alert('Chat session not initialized.');
        return;
    }
    if (!messageContent) {
        alert('Message cannot be empty.');
        return;
    }
    try {
        const response = await fetch(`/send_message/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            },
            body: new URLSearchParams({ chat_id: chatId, content: messageContent }),
        });
        if (!response.ok) {
            throw new Error(await response.text());
        }
        const data = await response.json();
        const chatBox = document.getElementById('chat-box');
        const currentUser = chatBox.getAttribute('data-current-user');
        const messageElement = document.createElement('div');
        messageElement.className = 'message sent';
        messageElement.innerHTML = `
            <strong>${data.sender}</strong> ${data.content}
            <span class="timestamp">${new Date(data.timestamp).toLocaleString()}</span>
        `;
        chatBox.appendChild(messageElement);
        chatInput.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
        console.error('Error sending message:', error);
        alert('Failed to send message. Please try again.');
    }
}

// Close the chat modal
function closeChatModal() {
    document.getElementById('chat-modal').style.display = 'none';
    document.getElementById('chat-box').innerHTML = ''; // Clear chat messages
    document.getElementById('chat-form').dataset.chatId = ''; // Reset chat ID
}
