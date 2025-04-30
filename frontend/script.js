document.getElementById('upload-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const fileInput = document.getElementById('audio-file');
    const file = fileInput.files[0];
  
    if (!file) {
      alert('ファイルを選択してください');
      return;
    }
  
    const formData = new FormData();
    formData.append('file', file);
  
    fetch('', {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        document.getElementById('result').textContent = JSON.stringify(data, null, 2);
      })
      .catch((error) => {
        console.error('エラー:', error);
      });
  });
  