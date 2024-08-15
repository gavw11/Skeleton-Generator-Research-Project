from flask import Flask, request, jsonify
import tempfile
from skeleton_generation.multiple_overlay import skeletonize
import os

app = Flask(__name__)

@app.route('/upload', methods=["POST"])
def upload():
    if request.method == 'POST':

        file = request.files['file']

        if not file:
            return jsonify({"msg": "File Not Accessible!"}), 400

        file_name, _ = os.path.splitext(file.filename)

        with tempfile.NamedTemporaryFile(delete=False) as input_file:
            input_path = input_file.name
            file.save(input_path)

        output_path = r"backend\output_path"
        
        skeletonize(input_path, output_path, file_name)

        os.remove(input_path)
    
        return jsonify({"msg": "Video Uploaded Succesfully!"}), 200
    
if __name__ == "__main__":
    app.run(debug=True)