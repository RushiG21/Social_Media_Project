function previewImage(event) {
    const output = document.getElementById('currentProfilePic');
    if (event.target.files && event.target.files[0]) {
        // Create a URL for the new image and set it as the src for the preview
        output.src = URL.createObjectURL(event.target.files[0]);
    }
}