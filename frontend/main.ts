// フォーム要素を取得
const optimizeForm = document.getElementById('optimize-form');

// フォームが存在する場合のみイベントリスナーを追加 (nullチェック)
if (optimizeForm) {
  optimizeForm.addEventListener('submit', function(e: SubmitEvent) { // イベントの型を 'SubmitEvent' と明記
    e.preventDefault();

    // --- 型アサーションを使用して要素を取得 ---
    // 元のJSコードは、これらの要素が存在することを前提としているため、
    // TypeScriptでも (as HTMLInputElement) のように型アサーションを使い、
    // 「この要素はこの型である」とコンパイラに伝えます。

    const urlInput = (document.getElementById('url') as HTMLInputElement).value;

    // .files は null の可能性があるため、オプショナルチェーン (?.) を使用します
    const fileInput = (document.getElementById('file') as HTMLInputElement).files?.[0];

    const result = document.getElementById('result') as HTMLElement;
    const preview = document.getElementById('link-preview') as HTMLElement;

    // --- ここからは元のロジKックと全く同じ ---

    preview.style.display = 'block';

    if (fileInput) { // fileInput は File | undefined 型になります
      preview.innerHTML = `<strong>選択されたファイル:</strong><br>${fileInput.name}`;
    } else if (urlInput) { // urlInput は string 型
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
}