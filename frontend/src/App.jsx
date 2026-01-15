import React from "react";
import Upload from "./Upload";

// gateway URL comes from Vite env var `VITE_GATEWAY_URL`, fallback to localhost:5555
export const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL;

export default function App() {
  return (
    <div style={{ padding: 20, fontFamily: 'Arial' }}>
      <h2>Audio Transcription</h2>
      <Upload />
    </div>
  );
}
