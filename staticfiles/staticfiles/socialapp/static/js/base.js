document.addEventListener("DOMContentLoaded", () => {

    // Confirm before deleting a post
    document.querySelectorAll('a[href*="/delete_post/"]').forEach(link => {
        link.addEventListener('click', (event) => {
            if (!confirm("Are you sure you want to delete this post?")) {
                event.preventDefault();
            }
        });
    });
});

// Function to toggle follow/unfollow a user
async function toggleFollowUser(username) {
    const csrftoken = getCookie('csrftoken');
    const url = `/toggle-follow/${username}/`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: username }) // Send the username in the body
        });

        if (!response.ok) {
            throw new Error(`Failed to toggle follow status for ${username}`);
        }

        const data = await response.json();
        const followButton = document.querySelector(`button[onclick*="toggleFollowUser('${username}')"]`);
        if (data.following_status) {
            followButton.textContent = 'Unfollow';
        } else {
            followButton.textContent = 'Follow';
        }

        // Update followers count
        const followersCountElement = document.getElementById('followers-count');
        if (followersCountElement) {
            followersCountElement.textContent = `Followers: ${data.followers_count}`;
        }
    } catch (error) {
        console.error('Error following/unfollowing the user.', error);
    }
}

// Function to toggle like/unlike for a post
async function toggleLikePost(postId) {
    const csrftoken = getCookie('csrftoken');
    const url = `/post/${postId}/like/`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to toggle like status for post ${postId}`);
        }

        const data = await response.json();
        const likeButton = document.getElementById(`like-button-${postId}`);
        const likeCountElement = document.getElementById(`like-count-${postId}`);
        if (likeCountElement) {
            likeCountElement.textContent = data.like_count;
        } else {
            console.error(`Like count element not found for post ${postId}`);
        }

        if (likeButton) {
            likeButton.innerHTML = data.liked ? '❤️' : '🤍';
        } else {
            console.error(`Like button element not found for post ${postId}`);
        }
    } catch (error) {
        console.error('Error liking/unliking the post.', error);
    }
}

// Toggle the visibility of the comments section for a specific post
function toggleComments(postId) {
    const commentSection = document.getElementById(`comments-${postId}`);
    commentSection.classList.toggle('hidden');
    if (commentSection.style.display === 'none' || commentSection.style.display === '') {
        commentSection.style.display = 'block';
    } else {
        commentSection.style.display = 'none';
    }
}

// Add a comment to a post
async function addComment(event, postId) {
    event.preventDefault(); 

    const form = event.target;
    const formData = new FormData(form);
    const csrftoken = getCookie('csrftoken'); // Get CSRF token

    try {
        const response = await fetch(`/post/${postId}/comment/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: formData // Send the form data
        });

        if (!response.ok) {
            throw new Error('Failed to add comment');
        }

        const data = await response.json();
        const commentsContainer = document.getElementById(`comments-${postId}`);
        const commentList = commentsContainer.querySelector('.comments-list');

        const newCommentItem = document.createElement('li');
        newCommentItem.classList.add('comment-item');
        newCommentItem.innerHTML = `<strong>${data.username}:</strong> ${data.text}
        <p class="comment-date">${data.created_at}</p>`;
        commentList.appendChild(newCommentItem);

        form.reset();
    } catch (error) {
        console.error('Error adding comment:', error);
    }
}

// Helper function to retrieve CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
