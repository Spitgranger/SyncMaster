import {io} from "socket.io-client";

// Define the websocket object that will be used across the application
const socket = io(process.env.SOCKET_SERVER || "http://localhost:5001");

export default socket;