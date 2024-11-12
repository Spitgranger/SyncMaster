import express, { Express, Request, Response } from "express";
import dotenv from "dotenv";

dotenv.config();

const app: Express = express();
const port = process.env.PORT || 3000;
app.set("view engine","ejs")


app.get("/", (req: Request, res: Response) => {
  res.send("Express + TypeScript Server");
});

app.get("/portal", (req: Request, res: Response) => {
  res.send("<h1>Contractor Portal</h1> \n<h2>Station HC001</h2> \n<h2>Work Order Number</h2>\n <h2>Entry Exit Procedures</h2>");
 
})

app.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
});
