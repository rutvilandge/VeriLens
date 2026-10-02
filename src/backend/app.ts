import express from "express";
import cors from "cors";
import helmet from "helmet";
import cookieParser from "cookie-parser";
import rateLimit from "express-rate-limit";
import uploadsRoutes from "./routes/uploads.routes.js";

import { authHandler } from "./auth/auth.js";
import authRoutes from "./routes/auth.routes.js";
import sessionRoutes from "./routes/session.routes.js";
import analysisRoutes from "./routes/analysis.routes.js";
import modelsRoutes from "./routes/models.routes.js";
import activityRoutes from "./routes/activity.routes.js";
import intelligenceRoutes from "./routes/intelligence.routes.js";
import { errorMiddleware } from "./middleware/error.middleware.js";

const app = express();

/**
 * ---------------------------------------------------------
 * Proxy / Auth.js configuration
 * ---------------------------------------------------------
 *
 * Auth.js needs Express to trust the proxy when determining
 * the request protocol and generating secure session cookies.
 *
 */
app.set("trust proxy", true);

/**
 * ---------------------------------------------------------
 * Security
 * ---------------------------------------------------------
 */

app.use(
  helmet({
    crossOriginResourcePolicy: false,
  }),
);

/**
 * ---------------------------------------------------------
 * CORS
 * ---------------------------------------------------------
 */

app.use(
  cors({
    origin: (origin, callback) => {
      const allowed = (process.env.FRONTEND_URL || (process.env.NODE_ENV === "production" ? "" : "http://localhost:3000"))
        .split(",").map((value) => value.trim()).filter(Boolean);
      if (!origin || allowed.includes(origin)) return callback(null, true);
      return callback(new Error("Origin is not allowed by CORS"));
    },
    credentials: true,
  }),
);

/**
 * ---------------------------------------------------------
 * Body parsing
 * ---------------------------------------------------------
 */

app.use(express.json({ limit: "10mb" }));
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

/**
 * ---------------------------------------------------------
 * Static uploads
 * ---------------------------------------------------------
 *
 * Uploaded images are stored inside:
 *
 * uploads/images/
 *
 * They are available through:
 *
 * /uploads/images/<filename>
 *
 * Example:
 * /uploads/images/example.png
 *
 */

app.use("/uploads", uploadsRoutes);

/**
 * ---------------------------------------------------------
 * API rate limiting
 * ---------------------------------------------------------
 */

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  limit: 200,
  standardHeaders: "draft-7",
  legacyHeaders: false,
});

app.use("/api", apiLimiter);

/**
 * ---------------------------------------------------------
 * Authentication API
 * ---------------------------------------------------------
 */

app.use("/api/auth", authRoutes);

/**
 * ---------------------------------------------------------
 * Session API
 * ---------------------------------------------------------
 */

app.use("/api/session", sessionRoutes);

/**
 * ---------------------------------------------------------
 * Analysis API
 * ---------------------------------------------------------
 *
 * GET    /api/analyses/stats
 * GET    /api/analyses
 * POST   /api/analyses
 * GET    /api/analyses/:id
 * PATCH  /api/analyses/:id
 * DELETE /api/analyses/:id
 *
 * Content:
 *
 * GET    /api/analyses/:id/content
 * POST   /api/analyses/:id/content/text
 * POST   /api/analyses/:id/content/image
 * POST   /api/analyses/:id/content/source
 * DELETE /api/analyses/:id/content/:contentId
 *
 */

app.use("/api/analyses", analysisRoutes);

/**
 * ---------------------------------------------------------
 * Model Lab API
 * ---------------------------------------------------------
 *
 * GET    /api/models
 * POST   /api/models
 * GET    /api/models/:id
 * POST   /api/models/:id/versions
 * POST   /api/models/:id/versions/:versionId/evaluations
 * POST   /api/models/:id/experiments
 * GET    /api/models/:id/experiments
 *
 */

app.use("/api/models", modelsRoutes);
app.use("/api/activity", activityRoutes);
app.use("/api/intelligence", intelligenceRoutes);

/**
 * ---------------------------------------------------------
 * Auth.js
 * ---------------------------------------------------------
 */

app.use("/auth", authHandler);

/**
 * ---------------------------------------------------------
 * Health check
 * ---------------------------------------------------------
 */

app.get("/api/health", (_req, res) => {
  res.status(200).json({
    success: true,
    service: "VeriLens API",
    status: "healthy",
    timestamp: new Date().toISOString(),
  });
});

/**
 * ---------------------------------------------------------
 * API root
 * ---------------------------------------------------------
 */

app.get("/api", (_req, res) => {
  res.status(200).json({
    success: true,
    service: "VeriLens API",
    version: "1.0.0",
    status: "running",
  });
});

/**
 * ---------------------------------------------------------
 * 404 API fallback
 * ---------------------------------------------------------
 */

app.use("/api", (_req, res) => {
  res.status(404).json({
    success: false,
    message: "API route not found",
  });
});

/**
 * ---------------------------------------------------------
 * Export
 * ---------------------------------------------------------
 */

app.use(errorMiddleware);

export default app;





