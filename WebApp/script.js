async function uploadImage() {
    const input = document.getElementById('imageInput');
    const resultDiv = document.getElementById('result');

    if (!input.files[0]) {
        resultDiv.innerText = "Please select an image first.";
        return;
    }

    const file = input.files[0];
    const formData = new FormData();
    formData.append("file", file);

    resultDiv.innerText = "Processing...";

    try {
        // Remplace cette URL par l'URL de ton HTTP Trigger UploadImage
        const response = await fetch("https://<YOUR_FUNCTION_APP>.azurewebsites.net/api/UploadImage", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.Emotions && data.Emotions.length > 0) {
            resultDiv.innerHTML = `
                <strong>Image:</strong> ${data.ImageName}<br>
                <strong>Faces detected:</strong> ${data.FacesCount}<br>
                <strong>Emotions:</strong> ${data.Emotions.join(", ")}
            `;
        } else {
            resultDiv.innerText = "No faces detected.";
        }

    } catch (err) {
        console.error(err);
        resultDiv.innerText = `Error: ${err.message}`;
    }
}
