// Toggle follow/unfollow for profile page
async function toggleFollow(event, username, isFollowing, followBack) {
    event.preventDefault();
    const button = document.getElementById('follow-button');
    const messageButton = document.getElementById('message-button');
    button.classList.add('loading');  // Add loading state

    try {
        const response = await fetch(`/toggle-follow/${username}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.following_status) {
                button.textContent = 'Unfollow';
            } else {
                button.textContent = followBack ? 'Follow Back' : 'Follow';
            }
            toggleMessageButton(data.following_status);
            updateFollowCounts(data);
            
        } else {
            alert('There was an issue with following/unfollowing the user. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('There was an issue with following/unfollowing the user. Please try again.');
    } finally {
        button.classList.remove('loading');  // Remove loading state
    }
}

// Toggle the visibility of the following list modal
function toggleFollowingList(event) {
    event.preventDefault();
    toggleModal('following-modal');
}

// Toggle the visibility of the followers list modal
function toggleFollowersList(event) {
    event.preventDefault();
    toggleModal('followers-modal');
}

// General function to toggle modals
function toggleModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal.style.display === 'block') {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Enable scrolling
    } else {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Disable scrolling
    }
}

// Update follower count display
function updateFollowCounts(data) {
    document.getElementById('followers-count').textContent = `Followers: ${data.followers_count}`;
    document.getElementById('following-count').textContent = `Following: ${data.following_count}`;
}

// Function to toggle the visibility of the "Message" button based on follow status
function toggleMessageButton(isFollowing) {
    const messageButton = document.getElementById('message-button');
    if (messageButton) {
        messageButton.style.display = isFollowing ? 'inline-block' : 'none';
    }
}

// Open a chat with a user
async function openChat(username) {
    try {
        document.getElementById('chat-modal').style.display = 'block';
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
                    <span class="timestamp">${new Date(message.timestamp).toLocaleString('en-US',{year: 'numeric',month: 'short',day: 'numeric',hour: 'numeric',minute: '2-digit',hour12: true})}</span>
                `;
                chatBox.appendChild(messageElement);
            });
        }
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
            body: new URLSearchParams({chat_id: chatId, content: messageContent }),
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
        chatInput.value = ''; // Clear input
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