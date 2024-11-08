import os
from flask import Flask, request, jsonify, send_file, send_from_directory
from PIL import Image
import cv2
import numpy as np
import io

app = Flask(__name__, static_folder='static', static_url_path='')

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB limit

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """
    Check if the file has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cartoonify_image(image):
    """
    Convert the input PIL Image to a cartoon-like image with outlines around color regions.
    Steps:
    1. Convert PIL Image to OpenCV format.
    2. Apply bilateral filter to smooth colors while preserving edges.
    3. Detect edges using adaptive thresholding.
    4. Combine the edge mask with the smoothed color image.
    5. Convert the final image back to PIL format.
    """
    # Convert PIL Image to OpenCV format
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Resize image for faster processing (optional)
    # cv_image = cv2.resize(cv_image, (800, 600))

    # Apply bilateral filter to reduce color palette and preserve edges
    color = cv2.bilateralFilter(cv_image, d=9, sigmaColor=250, sigmaSpace=250)

    # Convert to grayscale
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    # Apply median blur to reduce noise
    gray = cv2.medianBlur(gray, 7)

    # Detect edges using adaptive thresholding
    edges = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        blockSize=9,
        C=2
    )

    # Convert edges to color
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    # Combine color image with edge mask using bitwise AND
    cartoon = cv2.bitwise_and(color, edges_colored)

    # Convert back to PIL Image
    cartoon_pil = Image.fromarray(cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB))

    return cartoon_pil

@app.route('/api/convert', methods=['POST'])
def convert_image():
    """
    API endpoint to convert an uploaded image to a coloring page.
    Expects a file with the key 'image' in the form data.
    Returns the converted image as a PNG file.
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Unsupported file type'}), 400

    try:
        # Open the image file with PIL
        img = Image.open(file.stream).convert('RGB')

        # Convert the image to a cartoon-like coloring page
        coloring_page = cartoonify_image(img)

        # Save the coloring page to a BytesIO object
        img_io = io.BytesIO()
        coloring_page.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name='coloring_page.png'
        )
    except Exception as e:
        return jsonify({'error': f'Image processing failed: {str(e)}'}), 500

@app.route('/')
def serve_frontend():
    """
    Serve the frontend HTML page.
    """
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """
    Serve static files (CSS, JS, images) from the 'static' directory.
    """
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    # Enable debug mode for local development
    app.run(debug=True)
