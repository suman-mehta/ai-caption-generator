import requests
from flask import Flask, request, render_template

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)

API_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/microsoft/git-base-coco"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return render_template('error.html', error_message="No file part in the request.")
    
    file = request.files['image']
    if file.filename == '':
        return render_template('error.html', error_message="No image selected.")

    if file and allowed_file(file.filename):
        image_data = file.read()
        try:
            response = requests.post(API_URL, headers=headers, data=image_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result and isinstance(result, list) and 'generated_text' in result[0]:
                    caption = result[0]['generated_text']
                    return render_template('result.html', caption=caption)
                else:
                    return render_template('error.html', error_message="API returned an unexpected response.")
            else:
                return render_template('error.html', error_message=f"API Error ({response.status_code}): {response.text}")
        except requests.exceptions.Timeout:
            return render_template('error.html', error_message="The request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            return render_template('error.html', error_message=f"A network error occurred: {e}")
    else:
        return render_template('error.html', error_message="Invalid file type. Please upload a valid image (png, jpg, jpeg).")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
