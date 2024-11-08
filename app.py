import os
from flask import Flask, request, jsonify, send_file, send_from_directory
from PIL import Image, ImageFilter, ImageOps
import io
import numpy as np

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

def dodge(front, back):
    """
    Dodge blend function to lighten the image by blending front and back images.
    """
    result = front * 255 / (255 - back + 1)
    result[result > 255] = 255
    result[back == 255] = 255
    return result.astype('uint8')

def convert_to_coloring_page(image):
    """
    Convert the input PIL Image to a coloring page version with outlines of different shades.
    """
    # Convert to grayscale
    gray = image.convert('L')
    
    # Invert the grayscale image
    inverted = ImageOps.invert(gray)
    
    # Apply Gaussian blur
    blurred = inverted.filter(ImageFilter.GaussianBlur(radius=5))
    
    # Convert images to numpy arrays
    gray_np = np.array(gray)
    blurred_np = np.array(blurred)
    
    # Apply dodge blend
    try:
        final_np = dodge(blurred_np, gray_np)
    except ZeroDivisionError:
        final_np = gray_np
    
    # Convert back to PIL Image
    final = Image.fromarray(final_np)
    
    # Enhance edges by increasing contrast
    final = final.point(lambda x: x if x > 200 else 255)
    
    return final

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
        # Open the image file
        img = Image.open(file.stream)
        
        # Convert the image to a coloring page
        coloring_page = convert_to_coloring_page(img)
        
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
