// Vercel's Express runtime loads a default-exported app from src/server.ts.
// Keep src/backend/server.ts as the local development entry point.
import express from "express";
import app from "./backend/app.js";

// Vercel detects the framework from this entry point's direct Express import.
void express;

export default app;
