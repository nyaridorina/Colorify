# app.py
from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
import io
from PIL import Image

app = Flask(__name__)

def convert_to_coloring_page(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Invert the grayscale image
    inverted_image = cv2.bitwise_not(gray_image)
    # Apply a Gaussian blur to the inverted image
    blurred_image = cv2.GaussianBlur(inverted_image, (21, 21), 0)
    # Invert the blurred image
    inverted_blur = cv2.bitwise_not(blurred_image)
    # Create the final "pencil sketch" effect
    sketch_image = cv2.divide(gray_image, inverted_blur, scale=256.0)
    return sketch_image

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    # Convert uploaded image to an OpenCV image
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)
    in_memory_file.seek(0)
    file_bytes = np.frombuffer(in_memory_file.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # Process the image
    coloring_page = convert_to_coloring_page(image)
    
    # Save the output image to a byte stream to send back as a file
    _, buffer = cv2.imencode('.png', coloring_page)
    byte_io = io.BytesIO(buffer)
    byte_io.seek(0)
    
    return send_file(byte_io, mimetype='image/png', as_attachment=True, download_name='coloring_page.png')

if __name__ == "__main__":
    app.run(debug=True)
