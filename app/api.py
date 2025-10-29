from flask import Flask, request, send_file
from backend import backend_call

import tempfile
import os

app = Flask(__name__)#送ってきたファイルはnameに格納されてる

@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_input:
        file.save(tmp_input.name)
        input_file =tmp_input.name

    try:
        output_path = backend_call(input_file.name)
        return send_file(output_path,as_attachment=True)
    finally:
        if os.path.exists(input_file):
            os.remove(input_file)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':#デバック用に残してる
    app.run(debug=True)
