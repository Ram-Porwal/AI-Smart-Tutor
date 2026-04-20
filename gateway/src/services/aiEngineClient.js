const axios = require('axios');

const PYTHON_ENGINE_URL = process.env.PYTHON_ENGINE_URL || 'http://localhost:8000';

class AIEngineClient {
    /**
     * Sends a message to the LangGraph Engine and streams the response.
     * @param {string} threadId - The LangGraph checkpointer ID (User Session)
     * @param {string} message - The user's input
     * @param {function} onEvent - Callback to emit data to the React frontend
     */
    static async streamTutorResponse(threadId, message, onEvent) {
        try {
            const response = await axios({
                method: 'post',
                url: `${PYTHON_ENGINE_URL}/stream_chat`, // We will build this FastAPI route later
                data: {
                    thread_id: threadId,
                    message: message
                },
                responseType: 'stream' // Crucial for real-time streaming
            });

            const stream = response.data;

            // Listen to the data chunks coming from Python
            stream.on('data', (chunk) => {
                const lines = chunk.toString().split('\n').filter(line => line.trim() !== '');
                
                for (const line of lines) {
                    try {
                        // LangGraph typically streams JSON events
                        const eventData = JSON.parse(line);
                        
                        // Pass the event (Agent Handoffs, Tokens, or Final State) back to the socket
                        onEvent(eventData);
                    } catch (e) {
                        console.warn('Could not parse chunk as JSON:', line);
                    }
                }
            });

            return new Promise((resolve, reject) => {
                stream.on('end', resolve);
                stream.on('error', reject);
            });

        } catch (error) {
            console.error('Error connecting to AI Engine:', error.message);
            throw error;
        }
    }
}

module.exports = AIEngineClient;