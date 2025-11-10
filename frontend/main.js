"use strict";
// フォーム要素を取得
const optimizeForm = document.getElementById('optimize-form');

// 結果表示用の要素をあらかじめ取得
const result = document.getElementById('result');
const preview = document.getElementById('link-preview');

// フォームが存在する場合のみイベントリスナーを追加 (nullチェック)
if (optimizeForm) {
    // submit イベントは非同期処理 (async) にします
    optimizeForm.addEventListener('submit', async function (e) {
        var _a;
        e.preventDefault();

        // --- フォームデータを取得 ---
        const urlInput = document.getElementById('url').value;
        const fileInput = (_a = document.getElementById('file').files) === null || _a === void 0 ? void 0 : _a[0];

        // --- 入力チェックとプレビュー表示 ---
        preview.style.display = 'block';

        if (!fileInput && !urlInput) {
            preview.innerHTML = `<p style="color: red;">URLかファイルのどちらかを入力・選択してください。</p>`;
            result.style.display = 'none';
            return;
        }

        // FormDataオブジェクトを作成 (ファイルをサーバーに送信するために必要)
        const formData = new FormData();

        if (fileInput) { 
            preview.innerHTML = `<strong>選択されたファイル:</strong><br>${fileInput.name}`;
            // Python側が 'file' というキーで待っているので、'file' というキーで追加
            formData.append('file', fileInput); 
        }
        else if (urlInput) {
            preview.innerHTML = `<strong>入力されたURL:</strong><br><a href="${urlInput}" target="_blank" style="color:#4caf50;">${urlInput}</a>`;
            // (注: 現在のPython APIはURL処理に対応していません。ここではファイルのみを想定します)
            // もしURLも送る場合は、formData.append('url', urlInput); のようにします
            
            // 現状、ファイル入力のみを優先する場合
            if (!fileInput) {
                 preview.innerHTML = `<p style="color: red;">（現在はファイルアップロードのみ対応しています）</p>`;
                 return;
            }
        }

        // --- サーバーへの送信処理 (ここが重要) ---
        result.style.display = 'block';
        result.innerHTML = '<p>解析中...サーバーに送信しています。</p>';

        try {
            // fetch API を使って /process エンドポイントに POST リクエストを送信
            const response = await fetch('/process', {
                method: 'POST',
                body: formData, // FormData オブジェクトを body に設定
            });

            if (response.ok) {
                // サーバーからファイルが正常に返ってきた場合
                result.innerHTML = '<p>処理が完了しました。ダウンロードを開始します。</p>';

                // レスポンスからファイルデータを取得 (Blobオブジェクトとして)
                const blob = await response.blob();
                
                // ダウンロード用のリンクを動的に作成
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = downloadUrl;
                // Python側で指定した download_name があればそれが使われますが、
                // 万が一のためにフロント側でもファイル名を指定できます
                a.download = 'processed_audio.mp3'; 
                document.body.appendChild(a);
                
                // リンクをクリックしてダウンロードを実行
                a.click();
                
                // 後片付け
                window.URL.revokeObjectURL(downloadUrl);
                a.remove();

            } else {
                // サーバーがエラーを返した場合
                result.innerHTML = `<p style="color: red;">エラーが発生しました。サーバー側で問題が起きた可能性があります。</p>`;
            }

        } catch (error) {
            // ネットワークエラーなど
            console.error('Fetch Error:', error);
            result.innerHTML = `<p style="color: red;">送信エラー。サーバーに接続できませんでした。</p>`;
        }
    });
}