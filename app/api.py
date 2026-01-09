from flask import Flask, request, jsonify
from backend import backend_call
import io
import tempfile
import os
import traceback
import base64  
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/process', methods=['POST'])
def process():
    input_file = None
    output_path = None
    try:
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            print("ファイルアップロードを処理します。")
            temporary_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            file.save(temporary_file.name)
            temporary_file.close()
            input_file = temporary_file.name
        elif 'url' in request.form and request.form['url'].strip() != '':
            url = request.form['url'].strip()
            print(f"URLを処理します: {url}")
            try:
                response = requests.get(url)
                response.raise_for_status()
                temporary_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                temporary_file.write(response.content)
                temporary_file.close()
                input_file = temporary_file.name
            except requests.exceptions.RequestException:
                return "urlのダウンロードに失敗した", 400
        else:
            return "入力を受け取らなかった", 400

        output_path, ai_data = backend_call(input_file)
    
        with open(output_path, 'rb') as f:
            audio_content = f.read()
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            # レスポンスデータの構築
        response_data = {
            "status": "success",
            "audio_data": audio_base64,       # 音声データ本体
            "filename": "processed_audio.mp3",
            "transcript": "",                 # デフォルトは空文字
            "tags": []                        # デフォルトは空リスト
        }
        if ai_data:
            response_data["transcript"] = ai_data.get("text", "")
            response_data["tags"] = ai_data.get("tags", [])
        return jsonify(response_data)
        
    except Exception as e:
        print("エラーが発生しました！詳細:")
        print(traceback.format_exc())
        return f"サーバー内部エラー: {str(e)}", 500
        
    finally:
        if input_file and os.path.exists(input_file):
            try:
                os.remove(input_file)
            except:
                pass
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass

if __name__ == '__main__':
    app.run(debug=True)