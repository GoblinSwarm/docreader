// Mostrar la cámara en el video
function startCamera(videoElementId) {
    navigator.mediaDevices.getUserMedia({ video: true })
    .then(function(stream) {
        let video = document.getElementById(videoElementId);
        video.srcObject = stream;
        video.play();
    })
    .catch(function(err) {
        console.error("Error al acceder a la cámara: " + err);
        alert("No se pudo acceder a la cámara");
    });
}

// Capturar foto desde el video
function capturePhoto() {
    let video = document.getElementById('videoElement');
    let canvas = document.getElementById('canvasElement');
    let context = canvas.getContext('2d');

    // Dibuja el frame del video en el canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convierte la imagen del canvas en un dataURL (base64)
    let imageData = canvas.toDataURL('image/png');

    // Muestra la imagen capturada
    let imgElement = document.getElementById('capturedImage');
    imgElement.src = imageData;
    imgElement.style.display = 'block';

    // Guarda la imagen capturada en el input oculto para enviarla por POST
    document.getElementById('capturedImageInput').value = imageData;
}