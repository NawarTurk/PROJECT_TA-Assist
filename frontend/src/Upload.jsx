import React, { useState } from "react";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Select an audio file first");
    setLoading(true);
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch("http://localhost:5007/transcribe", {
        method: "POST",
        body: fd,
      });
      const data = await res.json();
      setResult(data.text || JSON.stringify(data));
    } catch (err) {
      setResult("Upload failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="audio/*"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <div style={{ marginTop: 8 }}>
        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Uploading..." : "Upload & Transcribe"}
        </button>
      </div>
      {result && (
        <pre style={{ whiteSpace: "pre-wrap", marginTop: 12 }}>{result}</pre>
      )}
    </div>
  );
}
