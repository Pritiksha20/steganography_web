from flask import Flask, render_template, request
import os
from PIL import Image
import numpy as np
import webbrowser
from threading import Timer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def encode_image(image_path, text):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = np.array(img)

    binary_text = ''.join(format(ord(char), '08b') for char in text) + '1111111111111110'
    flat_pixels = pixels.flatten()

    for i in range(len(binary_text)):
        flat_pixels[i] = (flat_pixels[i] & 0xFE) | int(binary_text[i])

    encoded_pixels = flat_pixels.reshape(pixels.shape)
    encoded_img = Image.fromarray(encoded_pixels.astype(np.uint8))
    encoded_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_image.png')
    encoded_img.save(encoded_image_path)
    return encoded_image_path

def decode_image(image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = np.array(img).flatten()

    binary_text = ''
    for value in pixels:
        binary_text += str(value & 1)

    text = ''
    i = 0
    while i < len(binary_text):
        byte = binary_text[i:i+8]
        if byte == '11111111':
            next_byte = binary_text[i+8:i+16]
            if next_byte == '11111110':
                break
            else:
                text += chr(int(byte, 2))
                i += 8
        else:
            text += chr(int(byte, 2))
            i += 8

    return text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        choice = request.form.get('choice')
        if choice == '1':
            image = request.files['image']
            message = request.form.get('message')
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
            encoded_image_path = encode_image(image_path, message)
            return render_template('index.html', encoded_image=encoded_image_path)
        elif choice == '2':
            image = request.files['image']
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
            decoded_message = decode_image(image_path)
            return render_template('index.html', decoded_message=decoded_message)
    return render_template('index.html')

def open_browser():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(debug=False)