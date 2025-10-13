from flask import Flask, request, send_file
from backend import backend_use_mp3

import tempfile

app = Flask(__name__)#送ってきたファイルはnameに格納されてる

@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_input:
        file.save(tmp_input.name)
        result = backend_use_mp3(tmp_input.name)
        return result  # Flaskは辞書をJSONで返してくれます

if __name__ == '__main__':#デバック用に残してる
    app.run(debug=True)
