import React, { useState } from "react";
import AskForm from "./components/AskForm";
import SummaryViewer from "./components/SummaryViewer";
import { askQuestion, getSummary, getTTS, generateImage } from "./utils/api";

function App() {
  const [chatResponse, setChatResponse] = useState("");
  const [summary, setSummary] = useState("");
  const [chatAudioUrl, setChatAudioUrl] = useState(null);
  const [summaryAudioUrl, setSummaryAudioUrl] = useState(null);
  const [chatImageUrl, setChatImageUrl] = useState(null);
  const [summaryImageUrl, setSummaryImageUrl] = useState(null);
  const [alertMessage, setAlertMessage] = useState("");
  const [loading, setLoading] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-tr from-purple-400 to-purple-600 text-white p-6">
      <div className="flex flex-row items-center justify-center mt-4 space-x-4">
        <img
          src="./brainLight64.png"
          className="w-16 h-16 rounded-full aura-pulse mb-4 bg-gradient-to-tr from-purple-800 to-purple-400 p-1 border border-white transform-gpu origin-center hover:scale-105 transition duration-200 ease-in-out"
          alt="Smart Librarian"
        />
        <h1 className="text-4xl text-shadow-xs font-extrabold text-center leading-tight text-white mb-4">
          Smart Librarian – AI Book Chatbot
        </h1>
      </div>

      <div className="max-w-3xl mx-auto space-y-6">
        <AskForm setChatResponse={setChatResponse} />

        {chatResponse && (
          <div className="bg-white/30 backdrop-blur-md shadow-2xl rounded-3xl p-6">
            <h2 className="text-2xl text-shadow-xs font-bold mb-3">
              Chatbot Recommendation:
            </h2>
            <p className="text-shadow-md leading-relaxed font-semibold">
              {chatResponse}
            </p>
            <div className="mt-4">
              <button
                onClick={async () => {
                  const url = await getTTS(chatResponse);
                  setChatAudioUrl(url);
                }}
                className="bg-purple-700 hover:bg-gradient-to-tr from-purple-700 to-white/30 text-white py-2 px-4 rounded-3xl transform-gpu origin-center hover:scale-105
    transition duration-200 ease-in-out

    shadow-md hover:shadow-2xl

    antialiased

    will-change-transform
    [backface-visibility:hidden]
    [transform:translateZ(0)]"
              >
                🔊 Generate Chat Audio
              </button>

              {chatAudioUrl && (
                <audio
                  controls
                  src={`http://localhost:8000${chatAudioUrl}`}
                  className="w-full rounded-2xl shadow-inner mt-4"
                />
              )}
            </div>
          </div>
        )}

        <SummaryViewer setSummary={setSummary} />

        {summary && (
          <div className="bg-white/30 backdrop-blur-md shadow-2xl rounded-3xl p-6">
            <h2 className="text-2xl text-shadow-xs font-bold mb-3">
              Full Book Summary:
            </h2>
            <p className="text-shadow-md leading-relaxed font-semibold">
              {summary}
            </p>
            <button
              onClick={async () => {
                const url = await getTTS(summary);
                setSummaryAudioUrl(url);
              }}
              className="bg-purple-700 hover:bg-gradient-to-tr from-purple-700 to-white/30 text-white py-2 px-4 rounded-3xl mt-4 transform-gpu origin-center hover:scale-105
    transition duration-200 ease-in-out

    shadow-md hover:shadow-2xl

    antialiased

    will-change-transform
    [backface-visibility:hidden]
    [transform:translateZ(0)]"
            >
              🔊 Generate Summary Audio
            </button>

            {summaryAudioUrl && (
              <audio
                controls
                src={`http://localhost:8000${summaryAudioUrl}`}
                className="w-full rounded-2xl shadow-inner mt-4"
              />
            )}
          </div>
        )}
      </div>
      {alertMessage && (
        <div className="px-4 py-6 bg-white/80 rounded-2xl flex items-center justify-between w-full border border-l-transparent border-gray-200 mt-4">
          {/* Left icon */}
          <div className="flex items-center">
            <img
              src="/errorAlert.png"
              alt="Error Alert"
              className="w-8 h-8 mr-3"
            />
            <span className="text-gray-800/80 font-bold">{alertMessage}</span>
          </div>

          {/* Close button */}
          <button onClick={() => setAlertMessage("")}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="fill-current text-gray-700"
              viewBox="0 0 16 16"
              width="25"
              height="25"
            >
              <path
                fillRule="evenodd"
                d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"
              />
            </svg>
          </button>
        </div>
      )}
      <div className="mt-6 max-w-xl mx-auto bg-gradient-to-tr from-white/50 to-purple-700/60 backdrop-blur-lg shadow-lg rounded-3xl p-6">
        {/* Button stays above images */}
        <div className="flex justify-center mb-6">
          <button
            onClick={async () => {
              if (!chatResponse && !summary) {
                setAlertMessage(
                  "Please get a recommendation or summary first."
                );
                setTimeout(() => setAlertMessage(""), 6000);
                return;
              }

              setLoading(true); // Show overlay

              if (chatResponse) {
                const url = await generateImage(chatResponse);
                setChatImageUrl(url);
              }

              if (summary) {
                const url = await generateImage(summary);
                setSummaryImageUrl(url);
              }

              setLoading(false); // Hide overlay
            }}
            disabled={loading}
            className="bg-purple-700 hover:bg-gradient-to-tr from-purple-700 to-white/30 text-white py-2 px-4 rounded-3xl mt-6 transform-gpu origin-center hover:scale-105
    transition duration-200 ease-in-out

    shadow-md hover:shadow-2xl

    antialiased

    will-change-transform
    [backface-visibility:hidden]
    [transform:translateZ(0)]"
          >
            🎨 Generate Image
          </button>
        </div>

        {/* Images stack vertically below the button */}
        <div className="flex flex-col gap-6 items-center">
          {chatImageUrl && (
            <div className="text-center w-full">
              <h3 className="text-shadow-xs leading-relaxed font-semibold mb-2">
                Chatbot Recommendation Image:
              </h3>
              <img
                src={chatImageUrl}
                alt="Chat Recommendation"
                className="rounded-3xl border border-white shadow-lg w-full h-[400px] object-cover"
              />
            </div>
          )}

          {summaryImageUrl && (
            <div className="text-center w-full">
              <h3 className="text-shadow-xs leading-relaxed font-semibold mb-2">
                Book Summary Image:
              </h3>
              <img
                src={summaryImageUrl}
                alt="Summary"
                className="rounded-3xl border border-white shadow-lg w-full h-[400px] object-cover"
              />
            </div>
          )}
        </div>
      </div>
      {loading && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-white"></div>
        </div>
      )}
    </div>
  );
}

export default App;
