from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import tempfile
from skeleton_generation.skel import skeletonize_video, skeletonize_img
import os
import uuid
import json

app = Flask(__name__)
CORS(app)

frontend_folder = os.path.join(os.getcwd(), "..", "frontend")
dist_folder = os.path.join(frontend_folder, "dist")


@app.route('/', defaults={"filename":""})
@app.route('/<path:filename>')
def index(filename):
    if not filename:
        filename = "index.html"
    return send_from_directory(dist_folder, filename)

#API Routes
file_dict = {}

# Determine the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))
# Set the result folder relative to the base directory
app.config['RESULT_FOLDER'] = os.path.join(base_dir, 'output_path')

@app.route('/api/upload', methods=["POST"])
def upload():
    if request.method == 'POST':

        file = request.files['file']

        generation_settings = request.form.get('generationSettings')
        if generation_settings:
            generation_settings = json.loads(generation_settings)
            print(generation_settings)

        file_unique_id = str(uuid.uuid4())

        if not file:
            return jsonify({"msg": "File Not Accessible!"}), 400
        

        with tempfile.NamedTemporaryFile(delete=False) as input_file:
            input_path = input_file.name
            file.save(input_path)
        
        
        file_name, ext = os.path.splitext(file.filename)

        # Define image and video extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']

        if ext.lower() in image_extensions:
            skeleton_fil_name = f"{file_name}-skeleton.png"
            skeletonize_img(input_path, app.config['RESULT_FOLDER'], skeleton_fil_name, generation_settings)
        elif ext.lower() in video_extensions:
            skeleton_fil_name = f"{file_name}-skeleton.mp4"
            skeletonize_video(input_path, app.config['RESULT_FOLDER'], skeleton_fil_name, generation_settings)

        file_dict[file_unique_id] = {"skeleton": skeleton_fil_name}

        os.remove(input_path)
    
        return jsonify({"msg": "Video Uploaded Succesfully!", "id": file_unique_id}), 200

@app.route('/api/view/<unique_id>', methods=['GET'])
def view(unique_id):
    if unique_id in file_dict:
        file_name = file_dict[unique_id]["skeleton"]
        file_path = os.path.join(app.config['RESULT_FOLDER'], file_name)

        if os.path.exists(file_path):
            return send_from_directory(app.config['RESULT_FOLDER'], file_name, mimetype='video/mp4')
        else:
            return jsonify({"msg": "Video Not Found!"}), 404
    else:
        return jsonify({"msg": "ID Not Found!"}), 404

@app.route('/api/download/<unique_id>', methods=["GET"])
def download(unique_id):

    print(f"Received unique_id: {unique_id}")

    if unique_id in file_dict:
        file_name = file_dict[unique_id]["skeleton"]
        file_path = os.path.join(app.config['RESULT_FOLDER'], file_name)

        print(f"Looking for file: {file_path}")

        if os.path.exists(file_path):
            print("hi")
            return send_from_directory(app.config['RESULT_FOLDER'], file_name, as_attachment=True, mimetype='video/mp4')
        else:
            return jsonify({"msg": "Video Not Found!"}), 404      
    else:
        return jsonify({"msg": "ID Not Found!"}), 404
    
    
if __name__ == "__main__":
    app.run(debug=True)