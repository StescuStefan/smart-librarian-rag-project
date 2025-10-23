// Text to Speech Synthesis
export function speak(text) {
  const synth = window.speechSynthesis;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US"; // Change to "ro-RO" for Romanian
  utterance.rate = 1;
  utterance.pitch = 1;

  const loadVoicesAndSpeak = () => {
    const voices = synth.getVoices();
    const googleVoice = voices.find(v => v.name.includes("Google")) || voices[0];
    utterance.voice = googleVoice;
    synth.speak(utterance);
  };

  if (synth.getVoices().length === 0) {
    synth.onvoiceschanged = loadVoicesAndSpeak;
  } else {
    loadVoicesAndSpeak();
  }
}


// Speech-to-Text Transcription
export function startListening(setText, language = "en-US") {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = language;  // defaults to English
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = (event) => {
    const spokenText = event.results[0][0].transcript;
    setText(spokenText);
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
  };

  recognition.start();
}