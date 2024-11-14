import socket from "../../utils/socket.ts";
import {useEffect} from "react";

const useSocket = () => {
    useEffect(() => {
        socket.connect();
        const connected = () => {
            console.log("Session Established");
        };

        const authSuccess = (token: string) => {
            console.log(token);
            // Handle the events here.
            alert("Auth success");
        }

        const eventTest = (userId: string) => {
            console.log(userId);
            alert(`Event Received from socket to uuid ${userId}`);
        }

        socket.on("connect", connected);
        socket.on("authSuccess", authSuccess);
        socket.on("event", eventTest);

        return () => {
            socket.off("connect", connected);
            socket.off("authSuccess", authSuccess);
            socket.off("event", eventTest);
            socket.disconnect();
        }
    }, []);
}

export default useSocket;