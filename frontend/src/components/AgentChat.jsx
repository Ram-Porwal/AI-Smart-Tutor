import React, { useEffect, useRef } from 'react';
import { useAgentStream } from '../hooks/useAgentStream';

// ---------------------------------------------------------
// 1. The Persona Dictionary (Visual Mapping)
// ---------------------------------------------------------
const AGENT_PERSONAS = {
  learner_analytics: { name: 'Analytics', icon: '🧠', color: 'bg-blue-500', text: 'text-blue-500', ring: 'ring-blue-300' },
  path_planner: { name: 'Planner', icon: '🗺️', color: 'bg-purple-500', text: 'text-purple-500', ring: 'ring-purple-300' },
  content_creator: { name: 'Engine', icon: '⚙️', color: 'bg-orange-500', text: 'text-orange-500', ring: 'ring-orange-300' },
  referee: { name: 'Referee', icon: '⚖️', color: 'bg-slate-700', text: 'text-slate-700', ring: 'ring-slate-400' },
  coach: { name: 'Coach', icon: '🗣️', color: 'bg-emerald-500', text: 'text-emerald-500', ring: 'ring-emerald-300' },
  idle: { name: 'System', icon: '✨', color: 'bg-gray-300', text: 'text-gray-400', ring: 'ring-transparent' }
};

export default function AgentChat({ threadId }) {
  // 2. Consume the Nervous System Hook
  const {
    messages,
    inputValue,
    setInputValue,
    sendMessage,
    activeAgent,
    agentStatus,
    curatedMenu,
    gameState,
    systemError
  } = useAgentStream(threadId);

  const endOfMessagesRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, activeAgent]);

  // 1. Create a dedicated submit handler
  const handleSubmit = (e) => {
    e.preventDefault(); // Prevents the page from refreshing
    console.log("🖱️ UI: Form submit triggered");
    sendMessage();
  };

  // Get current active persona styling
  const currentPersona = AGENT_PERSONAS[activeAgent] || AGENT_PERSONAS['idle'];

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-50 shadow-2xl rounded-lg overflow-hidden">
      
      {/* --------------------------------------------------------- */}
      {/* HEADER: Dynamic Persona Indicator                         */}
      {/* --------------------------------------------------------- */}
      <div className={`p-4 transition-colors duration-500 text-white flex items-center justify-between ${currentPersona.color}`}>
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{currentPersona.icon}</span>
          <div>
            <h1 className="font-bold text-lg">AI Smart Tutor</h1>
            <p className="text-sm opacity-90 transition-opacity">
              {agentStatus === 'waiting_for_user' ? 'Ready' : `${currentPersona.name} is ${agentStatus}...`}
            </p>
          </div>
        </div>
      </div>

      {/* --------------------------------------------------------- */}
      {/* MAIN CONTENT AREA: Messages & Generative UI             */}
      {/* --------------------------------------------------------- */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {/* Error Banner */}
        {systemError && (
          <div className="p-4 bg-red-100 text-red-700 rounded-lg border border-red-300">
            ⚠️ {systemError}
          </div>
        )}

        {/* Message History */}
        {messages.map((msg, idx) => (
          <div key={msg.id || idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] rounded-2xl p-4 shadow-sm ${
              msg.sender === 'user' 
                ? 'bg-blue-600 text-white rounded-br-none' 
                : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none'
            }`}>
              {msg.sender === 'ai' && <span className="mr-2 text-emerald-500 font-bold">Coach:</span>}
              <span className="whitespace-pre-wrap leading-relaxed">{msg.text}</span>
            </div>
          </div>
        ))}

        {/* The "Thinking" Bubble (Only shows when internal agents are passing the baton) */}
        {activeAgent !== 'idle' && activeAgent !== 'coach' && (
          <div className="flex justify-start items-center space-x-3 animate-pulse text-sm font-medium">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white shadow-md ${currentPersona.color}`}>
              {currentPersona.icon}
            </div>
            <span className={`${currentPersona.text}`}>
              {currentPersona.name} is evaluating...
            </span>
          </div>
        )}

        {/* Generative UI: Curated Menu (Human-in-the-Loop) */}
        {curatedMenu && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 animate-fade-in-up">
            {curatedMenu.map((option) => (
              <button 
                key={option.path_id}
                onClick={() => sendMessage(`[Selected Path]: ${option.label}`)}
                className="flex items-center space-x-4 p-4 bg-white border-2 border-emerald-100 hover:border-emerald-400 rounded-xl shadow-sm transition-all hover:shadow-md text-left"
              >
                <span className="text-3xl">{option.icon}</span>
                <span className="font-semibold text-gray-700">{option.label}</span>
              </button>
            ))}
          </div>
        )}

        {/* Generative UI: Game Canvas (Placeholder for interactive JSON) */}
        {gameState && (
          <div className="p-6 bg-slate-800 text-white rounded-xl shadow-inner mt-6 animate-fade-in">
             <h3 className="font-bold text-orange-400 mb-2 border-b border-slate-600 pb-2">
               Interactive Challenge: {gameState.game_type}
             </h3>
             <p className="mb-4 text-slate-300">{gameState.instructions}</p>
             {/* Imagine a dedicated <GameRenderer /> component goes here */}
             <div className="p-4 bg-slate-900 rounded font-mono text-sm text-green-400 border border-slate-700">
               {'// Interactive workspace active...'}
             </div>
          </div>
        )}

        <div ref={endOfMessagesRef} />
      </div>

      {/* --------------------------------------------------------- */}
      {/* INPUT AREA                                                */}
      {/* --------------------------------------------------------- */}
      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSubmit} className="flex space-x-4 relative">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            // Ensure this is only disabled if an agent is actually "thinking"
            disabled={activeAgent !== 'idle' && activeAgent !== 'coach'} 
            placeholder={activeAgent === 'idle' ? "Type your response..." : "Processing..."}
            className={`flex-1 p-4 bg-gray-100 rounded-full focus:outline-none focus:ring-2 transition-all ${currentPersona.ring}`}
          />
          <button
            type="submit"
            // Disable button only if input is empty or agents are in a non-interruptible state
            disabled={!inputValue.trim() || (activeAgent !== 'idle' && activeAgent !== 'coach')}
            className={`px-8 rounded-full font-bold text-white transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed ${currentPersona.color}`}
          >
            Send
          </button>
        </form>
      </div>

    </div>
  );
}