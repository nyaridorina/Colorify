async function uploadImage() {
    const input = document.getElementById('imageInput');
    const resultDiv = document.getElementById('result');
    
    // Clear previous results
    resultDiv.innerHTML = '';

    if (input.files.length === 0) {
        alert('Please select an image to convert.');
        return;
    }

    const file = input.files[0];
    const formData = new FormData();
    formData.append('image', file);

    // Show a loading message
    resultDiv.innerHTML = '<p>Processing your image...</p>';

    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            resultDiv.innerHTML = `
                <h2>Your Coloring Page:</h2>
                <img src="${url}" alt="Coloring Page">
                <br>
                <a href="${url}" download="coloring_page.png">Download Coloring Page</a>
            `;
        } else {
            const errorData = await response.json();
            resultDiv.innerHTML = `<p style="color:red;">Error: ${errorData.error}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p style="color:red;">An unexpected error occurred.</p>`;
        console.error('Error:', error);
    }
}
