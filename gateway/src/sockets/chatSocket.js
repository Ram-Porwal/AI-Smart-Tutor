const AIEngineClient = require('../services/aiEngineClient');

const setupChatSockets = (io) => {
    io.on('connection', (socket) => {
        console.log(`🟢 New Client Connected: ${socket.id}`);

        // The React frontend joins a specific "room" based on their thread ID
        socket.on('join_session', (threadId) => {
            socket.join(threadId);
            console.log(`Client ${socket.id} joined session: ${threadId}`);
        });

        // Listen for user messages from React
        socket.on('send_message', async (data) => {
            console.log("📩 BACKEND: Received 'send_message' event!");
            console.log("📦 BACKEND: Data received:", data);

            const { threadId, message } = data;

            // Notify React the AI is thinking
            io.to(threadId).emit('agent_status', { active_agent: 'learner_analytics', status: 'thinking' });
            
            try {
                console.log("🤖 BACKEND: Calling Python Engine...");

                // Call the Python Engine and pass a callback for the stream
                await AIEngineClient.streamTutorResponse(threadId, message, (eventPayload) => {
                    
                    // Route the LangGraph events to specific React listeners
                    if (eventPayload.type === 'agent_handoff') {
                        // e.g., "Baton passed to Path Planner"
                        io.to(threadId).emit('agent_status', { 
                            active_agent: eventPayload.active_agent,
                            status: 'processing'
                        });
                    } 
                    else if (eventPayload.type === 'content_token') {
                        // Streaming the actual text of the Coach's message
                        io.to(threadId).emit('message_chunk', eventPayload.chunk);
                    } 
                    else if (eventPayload.type === 'game_state_update') {
                        // Pushing the generated JSON puzzle to the React canvas
                        io.to(threadId).emit('game_update', eventPayload.game_data);
                    }
                    else if (eventPayload.type === 'curated_options') {
                        // Pushing the Path Planner's menu to React
                        io.to(threadId).emit('curated_menu', eventPayload.options);
                    }
                });

                // Notify React the execution graph is complete
                io.to(threadId).emit('agent_status', { active_agent: 'idle', status: 'waiting_for_user' });

            } catch (error) {
                console.error("❌ BACKEND: Error in send_message loop:", err);
                
                io.to(threadId).emit('system_error', { message: 'AI Engine is currently unreachable.' });
            }
        });

        socket.on('disconnect', () => {
            console.log(`🔴 Client Disconnected: ${socket.id}`);
        });
    });
};

module.exports = setupChatSockets;