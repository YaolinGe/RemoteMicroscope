document.addEventListener('DOMContentLoaded', function () {
    var cameraFeed = document.getElementById('camera-feed');
    var loadingSpinner = document.getElementById('loading-spinner');

    // Show the loading spinner when the page first loads
    loadingSpinner.style.display = 'block';
    cameraFeed.style.display = 'none';

    // Wait for the camera feed to load
    cameraFeed.onload = function () {
        // Hide the loading spinner and show the camera feed
        loadingSpinner.style.display = 'none';
        cameraFeed.style.display = 'block';
    };

    cameraFeed.onerror = function () {
        // Handle error (e.g., camera feed not available)
        loadingSpinner.style.display = 'none';
        alert('Error loading camera feed. Please try again.');
    };
});

document.getElementById('camera-select').addEventListener('change', function () {
    var cameraIndex = document.getElementById('camera-select').value;
    var cameraFeed = document.getElementById('camera-feed');
    var loadingSpinner = document.getElementById('loading-spinner');

    // Show the loading spinner when switching cameras
    loadingSpinner.style.display = 'block';
    cameraFeed.style.display = 'none';

    // Update the camera feed source
    cameraFeed.src = "/video_feed/" + cameraIndex;

    // Wait for the new feed to load
    cameraFeed.onload = function () {
        // Hide the loading spinner and show the camera feed
        loadingSpinner.style.display = 'none';
        cameraFeed.style.display = 'block';
    };

    cameraFeed.onerror = function () {
        // Handle error (e.g., camera feed not available)
        loadingSpinner.style.display = 'none';
        alert('Error loading camera feed. Please try again.');
    };
});
