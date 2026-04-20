const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const setupChatSockets = require('./sockets/chatSocket');

// Initialize Express App
const app = express();
app.use(cors());
app.use(express.json());

// Create HTTP Server and Socket.io Instance
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "http://localhost:3000", // React Frontend URL
        methods: ["GET", "POST"]
    }
});

// Basic Health Check Route
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'Gateway is running', ai_connected: true });
});

// Initialize Socket listeners
setupChatSockets(io);

const PORT = process.env.PORT || 4000;
server.listen(PORT, () => {
    console.log(`🚀 API Gateway running on http://localhost:${PORT}`);
});