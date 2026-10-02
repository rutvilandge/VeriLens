import "dotenv/config";
import app from "./app.js";

const PORT = Number(process.env.API_PORT) || 5000;

app.listen(PORT, () => {
  console.info(JSON.stringify({ level: "info", service: "VeriLens API", status: "running", port: PORT, healthPath: "/api/health" }));
});
