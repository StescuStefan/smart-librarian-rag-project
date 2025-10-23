export const askQuestion = async (question) => {
  try {
    const res = await fetch('http://localhost:8000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    return data.response;
  } catch (error) {
    console.error('Error asking question:', error);
    return 'Error fetching response';
  }
};

export const getSummary = async (title) => {
  try {
    const res = await fetch('http://localhost:8000/summary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    const data = await res.json();
    return data.summary || data.error;
  } catch (error) {
    console.error('Error fetching summary:', error);
    return 'Error fetching summary';
  }
};

export const getTTS = async (text) => {
  try {
    const res = await fetch('http://localhost:8000/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    return data.audio_url;
  } catch (error) {
    console.error('Error fetching TTS audio:', error);
    return null;
  }
};

export const generateImage = async (prompt) => {
  try {
    const res = await fetch("http://localhost:8000/generate-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();
    return data.image_url;
  } catch (error) {
    console.error("Image generation failed:", error);
    return null;
  }
};

// utils/api.js (add this)
export async function sttTranscribe(file, language = "en-US") {
  const fd = new FormData();
  fd.append("file", file);         // Blob/File
  fd.append("language", language); // "en-US" or "ro-RO"

  const res = await fetch("http://localhost:8000/stt", {
    method: "POST",
    body: fd,
  });
  return await res.json(); // { text, seconds_counted, quota_seconds_used } or { error }
}
