from flask import Flask, request, send_file, jsonify, render_template, url_for
from PIL import Image, ImageOps
import cv2
import numpy as np
import os

app = Flask(__name__)

# Ensure required directories exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("static/output", exist_ok=True)

# Function to create a coloring sheet
def create_coloring_sheet(input_path, output_path, posterize_levels=4):
    try:
        # Step 1: Posterize the image
        img = Image.open(input_path).convert("RGB")
        img = np.array(img)
        img = img // (256 // posterize_levels) * (256 // posterize_levels)
        posterized_img = Image.fromarray(img.astype('uint8'))
        
        # Step 2: Edge detection
        edges = cv2.Canny(np.array(posterized_img.convert("L")), 100, 200)
        edges = Image.fromarray(edges).convert("1")  # Convert to binary image
        
        # Step 3: Combine edges with posterized image
        coloring_sheet = ImageOps.invert(edges).convert("L")  # Invert edges for white background
        coloring_sheet.save(output_path)
        return True
    except Exception as e:
        print(f"Error creating coloring sheet: {e}")
        return False

# Route for the homepage
@app.route('/')
def home():
    # Render the homepage with an optional image_url
    return render_template('index.html', image_url=None)

# Route for file upload and processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save the uploaded file temporarily
        input_path = os.path.join("uploads", file.filename)
        output_path = os.path.join("static/output/coloring_sheet.jpg")
        file.save(input_path)

        # Create the coloring sheet
        if create_coloring_sheet(input_path, output_path):
            # Generate the URL for the image
            image_url = url_for('static', filename='output/coloring_sheet.jpg')
            return render_template('index.html', image_url=image_url)
        else:
            return jsonify({"error": "Failed to create coloring sheet"}), 500
    except Exception as e:
        print(f"Error during upload or processing: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(input_path):
            os.remove(input_path)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
