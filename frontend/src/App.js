import React from 'react';
import AgentChat from './components/AgentChat';

function App() {
  // In a production app, this would come from a user login or URL parameter.
  // For local testing, we hardcode a session ID.
  const testThreadId = "ram_local_session_001";

  return (
    <div className="min-h-screen py-8">
      <AgentChat threadId={testThreadId} />
    </div>
  );
}

export default App;