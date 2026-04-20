import { useState, useEffect, useCallback, useRef } from 'react';
import { io } from 'socket.io-client';

const SOCKET_SERVER_URL = 'http://localhost:4000';

export const useAgentStream = (threadId) => {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [activeAgent, setActiveAgent] = useState('idle');
    const [agentStatus, setAgentStatus] = useState('waiting_for_user');
    const [curatedMenu, setCuratedMenu] = useState(null);
    const [gameState, setGameState] = useState(null);
    const [systemError, setSystemError] = useState(null);

    const socketRef = useRef(null);

    useEffect(() => {
        socketRef.current = io(SOCKET_SERVER_URL);
        const socket = socketRef.current;

        socket.emit('join_session', threadId);

        socket.on('agent_status', (data) => {
            console.log("🛰️ RECEIVED agent_status:", data);
            setActiveAgent(data.active_agent);
            setAgentStatus(data.status);
            
            if (data.active_agent === 'learner_analytics') {
                setCuratedMenu(null);
                setGameState(null);
                setSystemError(null);
            }
        });

        // --- FIXED IMMUTABLE UPDATE ---
        socket.on('message_chunk', (chunk) => {
            setMessages((prevMessages) => {
                const lastMessage = prevMessages[prevMessages.length - 1];

                // Check if we should append to the existing AI message
                if (lastMessage && lastMessage.sender === 'ai') {
                    return prevMessages.map((msg, index) => {
                        if (index === prevMessages.length - 1) {
                            // Return a NEW object for the last message
                            return { ...msg, text: msg.text + chunk };
                        }
                        return msg;
                    });
                } else {
                    // Start a brand new AI message block
                    return [...prevMessages, { sender: 'ai', text: chunk, id: Date.now() }];
                }
            });
        });

        socket.on('game_update', (gameData) => {
            setGameState(gameData);
        });

        socket.on('curated_menu', (options) => {
            setCuratedMenu(options);
        });

        socket.on('system_error', (error) => {
            console.error("❌ SOCKET ERROR:", error);
            setSystemError(error.message);
            setActiveAgent('idle');
            setAgentStatus('error');
        });

        return () => {
            socket.disconnect();
        };
    }, [threadId]);

    const sendMessage = useCallback((textOverride = null) => {
        const textToSend = textOverride || inputValue;
        if (!textToSend.trim()) return;

        console.log("🚀 FRONTEND: Attempting to send message:", textToSend);

        setMessages((prev) => [...prev, { sender: 'user', text: textToSend, id: Date.now() }]);
        setInputValue('');
        setCuratedMenu(null);

        if (socketRef.current) {
            socketRef.current.emit('send_message', {
                threadId: threadId,
                message: textToSend
            });
            console.log("📡 FRONTEND: Socket emit sent!");
        } else {
            console.error("❌ FRONTEND: Socket is NOT connected!");
        }
    }, [inputValue, threadId]);

    return {
        messages,
        inputValue,
        setInputValue,
        sendMessage,
        activeAgent,
        agentStatus,
        curatedMenu,
        gameState,
        systemError
    };
};