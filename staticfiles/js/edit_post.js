document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.box');
    const imageInput = document.getElementById('id_image');
    const videoInput = document.getElementById('id_video');
    const previewImage = document.getElementById('preview-image');
    const previewVideo = document.getElementById('preview-video');
    const cropButton = document.getElementById('crop-button');
    const croppedImageInput = document.getElementById('cropped-image'); 
    let cropper = null;

    cropButton.style.display = 'none';

    // Function to initialize cropper on an image
    function initializeCropper(imageElement) {
        cropper = new Cropper(imageElement, {
            aspectRatio: 16 / 9,    
            viewMode: 1,
            autoCropArea: 1,
            responsive: true,
            guides: true,
            center: true,
            highlight: true,
            background: true,
        });
        cropButton.style.display = 'block'; // Show crop button when cropper is initialized
    }

    // Function to reset preview and cropper instance
    function resetPreview() {
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        if (previewImage) previewImage.style.display = 'none';
        if (previewVideo) previewVideo.style.display = 'none';
        cropButton.style.display = 'none';
    }

    // Handle image selection and preview
    if (imageInput) {
        imageInput.addEventListener('change', function () {
            if (videoInput && videoInput.files.length > 0) {
                alert("You can only upload an image or a video, not both.");
                imageInput.value = ""; // Clear image input if video is selected
                return;
            }
            resetPreview(); // Reset any previous preview or cropper
            const file = this.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImage.src = e.target.result;
                    previewImage.style.display = 'block';
                    initializeCropper(previewImage); // Initialize cropper on new image
                };
                reader.readAsDataURL(file);
            } else {
                alert("Please select a valid image file.");
            }
        });
    }

    // Handle video selection and preview
    if (videoInput) {
        videoInput.addEventListener('change', function () {
            if (imageInput && imageInput.files.length > 0) {
                alert("You can only upload an image or a video, not both.");
                videoInput.value = ""; // Clear video input if image is selected
                return;
            }
            resetPreview(); // Reset any previous preview or cropper
            const file = this.files[0];
            if (file && file.type.startsWith('video/')) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    const source = document.createElement('source');
                    source.src = e.target.result;
                    previewVideo.innerHTML = '';
                    previewVideo.appendChild(source);
                    previewVideo.load();
                    previewVideo.style.display = 'block';
                    cropButton.style.display = 'none'; // Hide crop button for video
                };
                reader.readAsDataURL(file);
            } else {
                alert("Please select a valid video file.");
            }
        });
    }

    // Crop button functionality - post cropped image
    if (cropButton) {
        cropButton.addEventListener('click', function () {
            if (cropper) {
                const canvas = cropper.getCroppedCanvas(); // Get the cropped image
                croppedImageInput.value = canvas.toDataURL('image/jpeg');
                form.submit();
            }
        });
    }

    

    // Cancel button functionality - Redirect to profile page
    const cancelButton = document.getElementById('cancel-button');
    if (cancelButton) {
        cancelButton.addEventListener('click', function () {
            window.location.href = cancelButton.getAttribute('data-url');
        });
    }

    // Case 1: If an image is already selected (editing an existing post), initialize cropper
    if (previewImage && previewImage.src) {
        previewImage.style.display = 'block';
        initializeCropper(previewImage); 
        if (videoInput){ videoInput.disabled = true;} 
    }

    // Case 2: If a video is already selected (editing an existing post), show the video and disable crop
    if (previewVideo && previewVideo.src) {
        previewVideo.style.display = 'block';
        cropButton.style.display = 'none';
        if (imageInput){imageInput.disabled = true;}
    }

});
