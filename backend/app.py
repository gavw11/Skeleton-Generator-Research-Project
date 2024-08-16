from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import tempfile
from skeleton_generation.skel import skeletonize
import os
import uuid

app = Flask(__name__)
CORS(app)

file_dict = {}

# Determine the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))
# Set the result folder relative to the base directory
app.config['RESULT_FOLDER'] = os.path.join(base_dir, 'output_path')


@app.route('/upload', methods=["POST"])
def upload():
    if request.method == 'POST':

        file = request.files['file']

        file_unique_id = str(uuid.uuid4())

        if not file:
            return jsonify({"msg": "File Not Accessible!"}), 400

        file_name, file_ext = os.path.splitext(file.filename)
        skeleton_fil_name = f"{file_name}-skeleton{file_ext}"

        with tempfile.NamedTemporaryFile(delete=False) as input_file:
            input_path = input_file.name
            file.save(input_path)
        
        skeletonize(input_path, app.config['RESULT_FOLDER'], skeleton_fil_name)

        file_dict[file_unique_id] = {"skeleton": skeleton_fil_name}

        os.remove(input_path)
    
        return jsonify({"msg": "Video Uploaded Succesfully!", "id": file_unique_id}), 200


@app.route('/download/<unique_id>', methods=["GET"])
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