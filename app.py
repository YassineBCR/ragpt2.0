import os
import json
import requests
from flask import Flask, request, render_template, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from extract_content import extract_content  # Importer la fonction d'extraction de contenu

app = Flask(__name__)

# URL de l'endpoint de votre modèle Azure OpenAI Studio
MODEL_ENDPOINT = "https://openaiyass.openai.azure.com/"
API_KEY = "12c576ecdd5e4ae2b23afb49e785896e"  # Remplacez par votre clé API

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'csv', 'html', 'xml'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', message='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', message='No selected file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create directory if it doesn't exist
            file.save(file_path)
            content = extract_content(file_path)
            if content is None:
                return render_template('index.html', message='Failed to extract content from the file.')
            
            # Sauvegarder le contenu dans un fichier JSON
            json_data = {'content': content}
            with open('content.json', 'w', encoding='utf-8') as file:
                json.dump(json_data, file, ensure_ascii=False)
                
            return redirect(url_for('scan_success'))
        else:
            return render_template('index.html', message='Invalid file extension')
    return render_template('index.html', message='')

@app.route('/scan-success', methods=['GET'])
def scan_success():
    return render_template('scan_success.html')

@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    if request.method == 'POST':
        data = request.get_json()
        if 'question' not in data:
            return jsonify({'error': 'No question provided'})
        question = data['question']
        with open('content.json', 'r', encoding='utf-8') as file:
            content = json.load(file)
        context = content['content']
        
        # Envoyer la requête à l'API Azure OpenAI
        headers = {
            'Content-Type': 'application/json',
            'api-key': '12c576ecdd5e4ae2b23afb49e785896e'  # Remplacez par votre clé API
        }
        data = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
            ]
        }

        response = requests.post(MODEL_ENDPOINT, headers=headers, json=data)
        print(f"Response Status Code: {response.status_code}")  # Log status code
        print(f"Response Text: {response.text}")  # Log response text

        if response.status_code == 200:
            answer = response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No response')
        else:
            answer = 'Error: Could not get a response from the model.'

        return jsonify({'answer': answer})
    else:
        return render_template('ask.html')

if __name__ == '__main__':
    app.run(debug=True)
