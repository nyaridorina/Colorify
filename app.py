from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageFilter, ImageOps
import io

app = Flask(__name__)

def convert_to_coloring_page(image):
    # Convert to grayscale
    gray = image.convert('L')
    # Invert the image
    inverted = ImageOps.invert(gray)
    # Apply edge enhancement
    edges = inverted.filter(ImageFilter.FIND_EDGES)
    # Convert back to white background
    final = ImageOps.invert(edges)
    return final

@app.route('/api/convert', methods=['POST'])
def convert_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    file = request.files['image']
    try:
        img = Image.open(file.stream)
        coloring_page = convert_to_coloring_page(img)
        img_io = io.BytesIO()
        coloring_page.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return "Photo to Coloring Page API"

if __name__ == '__main__':
    app.run(debug=True)
