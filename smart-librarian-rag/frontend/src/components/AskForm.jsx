import React, { useState } from "react";
import { askQuestion } from "../utils/api";
import { startListening } from "../utils/speech";

const AskForm = ({ setChatResponse }) => {
  const [question, setQuestion] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await askQuestion(question);
    setChatResponse(response);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-gradient-to-tr from-white/50 to-purple-700/60 backdrop-blur-lg shadow-lg rounded-3xl p-6"
    >
      <label className="block text-white text-lg text-shadow-xs font-semibold mb-2">
        Ask a book-related question:
      </label>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        className="w-full p-4 mb-6 rounded-2xl bg-white/20 backdrop-blur-sm border border-white/40 font-semibold text-violet-900/70 placeholder-violet-900/70 focus:outline-none focus:ring-2 focus:ring-purple-200 transition duration-150 ease-in-out"
        placeholder="e.g., Recommend a book about adventure"
      />

      <div className="flex gap-4">
        <button
          type="submit"
          className="w-1/2 bg-white hover:bg-gray-100 text-purple-800 font-medium px-4 py-2 rounded-3xl transition-transform transform hover:scale-105 shadow-md"
        >
          Ask
        </button>

        <button
          type="button"
          onClick={() => startListening(setQuestion)}
          className="w-1/2 bg-purple-700 hover:bg-gradient-to-tr from-purple-700 to-white/30 text-white py-2 px-4 rounded-3xl transition-transform transform hover:scale-105 shadow-md"
        >
          🎤 Speak
        </button>
      </div>
    </form>
  );
};

export default AskForm;
