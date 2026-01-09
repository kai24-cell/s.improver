"use strict";

const optimizeForm = document.getElementById('optimize-form');
const result = document.getElementById('result');
const preview = document.getElementById('link-preview');
const submitButton = document.getElementById('length');

function base64ToBlob(base64, mimeType) {
    const bin = atob(base64); // Base64をデコード
    const len = bin.length;
    const arr = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        arr[i] = bin.charCodeAt(i);
    }
    return new Blob([arr], { type: mimeType });
}

if (optimizeForm) {
    optimizeForm.addEventListener('submit', async function (e) {
        e.preventDefault();


        const urlInput = document.getElementById('url').value;
        const fileInput = document.getElementById('file').files?.[0];

        preview.style.display = 'block';
        if (!fileInput && !urlInput) {
            preview.innerHTML = `<p style="color: red;">URLかファイルのどちらかを入力・選択してください。</p>`;
            result.style.display = 'none';
            return;
        }

        const formData = new FormData();
        if (fileInput) {
            preview.innerHTML = `<strong>選択されたファイル:</strong><br>${fileInput.name}`;
            formData.append('file', fileInput);
        } else if (urlInput) {
            preview.innerHTML = `<strong>入力されたURL:</strong><br><a href="${urlInput}" target="_blank" style="color:#4caf50;">${urlInput}</a>`;
            formData.append('url', urlInput);
        }

        result.style.display = 'block';
        result.innerHTML = '<p>解析中...サーバーに送信しています。(1〜2分かかる場合があります)</p>';
        submitButton.disabled = true;
        submitButton.innerText = '処理中...';

        try {
            const response = await fetch('http://127.0.0.1:5000/process', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();

                let htmlContent = '<h3>処理完了</h3>';

                if (data.transcript) {
                    htmlContent += `
                        <div style="background: #333; padding: 15px; margin: 10px 0; border-radius: 5px; text-align: left;">
                            <strong style="color: #4caf50;">文字起こし:</strong>
                            <p style="color: #fff; margin-top: 5px;">${data.transcript}</p>
                        </div>`;
                }

                if (data.tags && data.tags.length > 0) {
                    const tagsHtml = data.tags.map(tag => 
                        `<span style="background: #4caf50; color: white; padding: 2px 8px; border-radius: 10px; margin-right: 5px; font-size: 0.9em;">${tag}</span>`
                    ).join('');
                    
                    htmlContent += `
                        <div style="background: #333; padding: 15px; margin: 10px 0; border-radius: 5px; text-align: left;">
                            <strong style="color: #4caf50;">抽出タグ:</strong>
                            <div style="margin-top: 10px;">${tagsHtml}</div>
                        </div>`;
                }

                result.innerHTML = htmlContent;

                if (data.audio_data) {
                    // Base64をBlobに変換
                    const blob = base64ToBlob(data.audio_data, 'audio/mpeg');
                    const downloadUrl = window.URL.createObjectURL(blob);
                    
                    // ダウンロードボタンを作成して表示
                    const downloadBtn = document.createElement('a');
                    downloadBtn.href = downloadUrl;
                    downloadBtn.download = data.filename || 'processed_audio.mp3';
                    downloadBtn.innerText = '音声をダウンロード';
                    downloadBtn.style.cssText = "display: inline-block; background: #4caf50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; font-weight: bold;";
                    
                    result.appendChild(downloadBtn);
                }

            } else {
                const errorText = await response.text();
                console.error('Server Error:', errorText);
                result.innerHTML = `<p style="color: red;">エラー: ${errorText}</p>`;
            }

        } catch (error) {
            console.error('Fetch Error:', error);
            result.innerHTML = `<p style="color: red;">通信エラー。コンソールを確認してください。</p>`;
        } finally {
            submitButton.disabled = false;
            submitButton.innerText = '最適化開始';
        }
    });
}