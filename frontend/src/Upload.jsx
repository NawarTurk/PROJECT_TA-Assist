import React, { useState } from "react";
import { GATEWAY_URL } from "./App";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const handleUpload = async () => {
    if (!file) return alert("Select an audio file first");
    setLoading(true);
    setResult(null);
    setAnalysis(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${GATEWAY_URL}/transcribe`, {
        method: "POST",
        body: fd,
      });
      const data = await res.json();
      setResult(data.text || "");
      setAnalysis(data.analysis || null);
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
        <div style={{ marginTop: 12 }}>
          <h4>Transcription</h4>
          <pre style={{ whiteSpace: "pre-wrap" }}>{result}</pre>
        </div>
      )}
      {analysis && (
        <div style={{ marginTop: 12 }}>
          <h4>Analysis</h4>
          <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(analysis, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
