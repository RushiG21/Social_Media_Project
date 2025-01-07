let cropper;
function handleFileSelect(event) {
    const previewBox = document.getElementById('preview-box');
    const cropButton = document.getElementById('crop-button');
    const files = event.target.files; // Get selected files
    
    if (cropper) {
        cropper.destroy();
        cropper = null; // Reset cropper instance
    }
    
    previewBox.innerHTML = ''; // Clear previous previews
    cropButton.style.display = 'none';

    if (files.length > 0) {
        const file = files[0];
        const fileType = file.type;
        console.log("Selected file type:", fileType); 

        if (fileType.startsWith('image/')) {
            const fileURL = URL.createObjectURL(file);
            const imgElement = document.createElement('img');
            imgElement.src = fileURL;
            previewBox.appendChild(imgElement);// Append the image to the preview box

            // Initialize the cropper on the image once it is loaded
            imgElement.onload = function() {
                cropper = new Cropper(imgElement, {
                    aspectRatio: 16 / 9,
                    viewMode: 2,
                    autoCropArea: 1,
                    dragMode: 'crop',
                    responsive: true,
                    restore: true,
                    guides: true,
                    center: true,
                    highlight: true,
                    cropBoxMovable: true, 
                    cropBoxResizable: true,
                    toggleDragModeOnDblclick: false, 
                    background: false,
                    modal: true, 
                    minCropBoxWidth: 150,
                    minCropBoxHeight: 150,
                    scalable: false,
                    zoomOnWheel: true,
                    zoomOnTouch: true, 
                    checkOrientation: true,
                    checkCrossOrigin: true,
                });
                cropButton.style.display = 'block'; // Show crop button for image
            };
        } 
        else if (fileType.startsWith('video/')) {
            const fileURL = URL.createObjectURL(file);
            const videoElement = document.createElement('video');
            videoElement.src = fileURL;
            videoElement.controls = true; 
            videoElement.autoplay = true;
            videoElement.loop = true;
            videoElement.style.width = '100%';
            videoElement.style.height = 'auto';
        
            // Append error handling
            videoElement.onerror = function() {
                alert('Error loading video. Please try another file.');
                console.log("Failed to load video:", fileURL);
                window.location.href = '/add_post/';
            };
        
            previewBox.appendChild(videoElement); // Show the video directly in the preview box
            cropButton.style.display = 'none'; // Hide crop button for video
        }else {
            console.log("Not a supported file type");
        }
    }
}

// Attach event listeners to file inputs
document.addEventListener('DOMContentLoaded', function () {
    const imageInput = document.getElementById('id_image');
    const videoInput = document.getElementById('id_video');
    const cropButton = document.getElementById('crop-button');
    const form = document.querySelector('.box');  // Form element
    const croppedImageInput = document.getElementById('cropped-image');

    if (imageInput) {
        imageInput.addEventListener('change', handleFileSelect);
    }
    if (videoInput) {
        videoInput.addEventListener('change', handleFileSelect);
    }

    // Crop button functionality
    cropButton.addEventListener('click', function () {
        if (cropper) {
            const canvas = cropper.getCroppedCanvas();
            if (canvas) {
                const croppedImageDataURL = canvas.toDataURL('image/jpeg'); // Convert to Data URL (JPEG format)
                croppedImageInput.value = croppedImageDataURL;
                form.submit();
            } else {
                alert('Error cropping image. Please try again.');
            }
        } else {
            alert('No image selected for cropping.');
        }
    });

    // Cancel button functionality
    const cancelButton = document.getElementById('cancel-button');
    cancelButton.addEventListener('click', function() {
        const form = document.querySelector('.box');
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        form.reset();
        document.getElementById('preview-box').innerHTML = '';
        const cropButton = document.getElementById('crop-button');
        cropButton.style.display = 'none';
    });
    
});

