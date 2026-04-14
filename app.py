import os
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Пути внутри контейнера
DATA_DIR = '/app/data'
FILE_PATH = os.path.join(DATA_DIR, 'document.md')
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')

# Создаем директории, если их нет
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

if not os.path.exists(FILE_PATH):
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write('# Добро пожаловать\n\nТеперь тут есть картинки, эмодзи и сохранение!')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/file', methods=['GET'])
def get_file():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        return jsonify({'content': f.read()})

@app.route('/api/file', methods=['POST'])
def save_file():
    data = request.json
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(data.get('content', ''))
    return jsonify({'status': 'success'})

# --- НОВЫЕ МАРШРУТЫ ДЛЯ КАРТИНОК ---

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Пустое имя файла'}), 400

    # Генерируем уникальное имя, чтобы файлы не перезаписывали друг друга
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
    filename = f"{uuid.uuid4().hex}.{ext}"
    
    file.save(os.path.join(UPLOAD_DIR, filename))
    
    # Возвращаем URL загруженной картинки
    return jsonify({'url': f'/uploads/{filename}'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)