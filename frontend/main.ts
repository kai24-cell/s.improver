<script>
    document.getElementById('optimize-form').addEventListener('submit', function(e) {
      e.preventDefault();
      const urlInput = document.getElementById('url').value;
      const fileInput = document.getElementById('file').files[0];
      const result = document.getElementById('result');
      const preview = document.getElementById('link-preview');

      preview.style.display = 'block';
      if (fileInput) {
        preview.innerHTML = `<strong>選択されたファイル:</strong><br>${fileInput.name}`;
      } else if (urlInput) {
        preview.innerHTML = `<strong>入力されたURL:</strong><br><a href="${urlInput}" target="_blank" style="color:#4caf50;">${urlInput}</a>`;
      } else {
        preview.innerHTML = `<p style="color: red;">URLかファイルのどちらかを入力・選択してください。</p>`;
        result.style.display = 'none';
        return;
      }

      result.style.display = 'block';
      result.innerHTML = '<p>解析中...しばらくお待ちください。</p>';

      // フェイク処理（実際はここでAPIにリクエスト）
      setTimeout(() => {
        result.innerHTML = '<p>AIによる分析により，最適なEQが適用され，音質が向上しました．</p>';
      }, 2000);
    });
  </script>