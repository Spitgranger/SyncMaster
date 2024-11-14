import express, {Express} from "express";
import dotenv from "dotenv";
import http from "http";
import bodyParser from "body-parser";
import userRoutes from "./routes/users";
import dashboardRoutes from "./routes/dashboard";
import {DefaultEventsMap, Server, Socket} from "socket.io";
import cors from "cors";
import {sessionIds} from "./controllers/users";

declare module 'express-session' {
    interface SessionData {
        sessionId: string | Uint8Array
    }
}

dotenv.config();

const app: Express = express();
const port: number = parseInt(process.env.PORT || "5001");

app.use(cors({
    origin: "*",
    credentials: true,
}));

const server: http.Server = new http.Server(app);
export const io: Server<DefaultEventsMap, DefaultEventsMap, DefaultEventsMap, any> = new Server(server, {
    cors: {
        origin: "*",
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
app.use("/api/dashboard", dashboardRoutes);

server.listen(port, () => {
    console.log(`[server]: Server is running at http://localhost:${port}`);
});
