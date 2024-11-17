from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageOps
import cv2
import numpy as np
import os

app = Flask(__name__)

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
        print(f"Error creating Painting Base: {e}")
        return False

# Define the route for the homepage
@app.route('/')
def home():
    return """
    <h1>Painting Base from Image</h1>
    <p>Upload a photo to convert it into a Painting Base!</p>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" />
        <input type="submit" value="Upload" />
    </form>
    """

# Define the route for file upload and processing
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
        output_path = os.path.join("output", "coloring_sheet.jpg")
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        file.save(input_path)

        # Create the Painting Base
        if create_coloring_sheet(input_path, output_path):
            return send_file(output_path, as_attachment=True, download_name="coloring_sheet.jpg")
        else:
            return jsonify({"error": "Failed to create coloring sheet"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up uploaded file
        if os.path.exists(input_path):
            os.remove(input_path)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
