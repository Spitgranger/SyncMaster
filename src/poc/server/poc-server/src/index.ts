import express, { Express } from "express";
import dotenv from "dotenv";
import http from "http";
import bodyParser from "body-parser";
import userRoutes from "./routes/users";
import { Server, Socket } from "socket.io";
import cors from "cors";
import {sessionIds} from "./controllers/users";

declare module 'express-session' {
    interface SessionData {
        sessionId: string | Uint8Array
    }
}

dotenv.config();

const app: Express = express();
const port = process.env.PORT || 5001;

app.use(cors({
    origin: "http://localhost:3001",
    credentials: true,
}));

const server = new http.Server(app);
export const io = new Server(server, {
    cors: {
        origin: ["http://localhost:3001"],
    },
});
io.on("connection", (socket: Socket) => {
    console.log("Socket connected: ", socket.id);
    socket.on("join_session", (data) => {
        socket.join(data);
        console.log("User started session: ", data);
        console.log(sessionIds);
    });
    socket.on("disconnect", () => {
        console.log("A user disconnected");
    });
});

app.use(bodyParser.json({limit: "30mb"}));
app.use(bodyParser.urlencoded({limit: "30mb", extended: true}));

app.use("/api/users", userRoutes);

server.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
});
