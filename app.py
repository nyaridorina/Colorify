import os
from flask import Flask, request, jsonify, send_file, send_from_directory
from PIL import Image, ImageFilter, ImageOps
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

def convert_to_coloring_page(image):
    """
    Convert the input PIL Image to a coloring page version.
    Steps:
    1. Convert to grayscale.
    2. Invert the image colors.
    3. Apply edge detection.
    4. Invert the edges to get black lines on white background.
    """
    # Convert to grayscale
    gray = image.convert('L')
    
    # Invert the grayscale image
    inverted = ImageOps.invert(gray)
    
    # Apply edge detection
    edges = inverted.filter(ImageFilter.FIND_EDGES)
    
    # Further enhance edges by increasing contrast
    enhanced_edges = edges.point(lambda x: 0 if x < 128 else 255, '1')
    
    return enhanced_edges.convert('L')

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
