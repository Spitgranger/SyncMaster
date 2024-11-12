import express, { Express, Request, Response } from "express";
import dotenv from "dotenv";
import http, {IncomingMessage} from "http";
import bodyParser from "body-parser";
import userRoutes from "./routes/users";
import { Server, Socket } from "socket.io";
import session, {SessionData} from "express-session";

declare module 'express-session' {
    interface SessionData {
        chatId: string | Uint8Array
    }
}

dotenv.config();

const app: Express = express();
const port = process.env.PORT || 3000;
var sessionIds: string[] | Uint8Array[] = [];

const server = new http.Server(app);
const io = new Server(server, {
    cors: {
        origin: "*",
    },
});
io.on("connection", (socket: Socket) => {
    console.log("Socket connected: ", socket.id);
    socket.on("join_room", (data) => {
        socket.join(data);
        console.log("User joined room: ", data);
    });
    socket.on("disconnect", () => {
        console.log("A user disconnected");
    });
});

app.use(bodyParser.json({limit: "30mb"}));
app.use(bodyParser.urlencoded({limit: "30mb", extended: true}));

app.use("/api/users", userRoutes);

app.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
});
