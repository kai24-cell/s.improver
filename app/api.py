from flask import Flask, request, send_file, after_this_request
from backend import backend_call

import tempfile
import os

app = Flask(__name__)#送ってきたファイルはnameに格納されてる
#メモ:フロントエンドのファイルキーはfileらしい
@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        print("ファイルがない")
        return 1
    file = request.files['file']

    if file.filename == '':
        print("ファイルが選択されていません")#url方式を一旦考えない前提のエラーチェック 
        return 1
    
    temporary_file =tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    file.save(temporary_file.name)
    temporary_file.close()
    input_file = temporary_file.name
    output_path = None#初期化

    try:
        output_path = backend_call(input_file)
       
        @after_this_request#処理終わりのアノテーションreturnを返し終わったら動く 
        def clean_up(response):
            if os.path.exists(input_file):
                os.remove(input_file)
            if output_path and os.path.exists(output_path):
                os.remove(output_path)
            return response

        return send_file(output_path,as_attachment=True,download_name = "processed_audio.mp3")     

    except Exception:
        if os.path.exists(input_file):
            os.remove(input_file)
        return 2

if __name__ == '__main__':
    app.run(debug=True)
