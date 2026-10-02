import type { ErrorRequestHandler } from "express";

export const errorMiddleware: ErrorRequestHandler = (error, _req, res, _next) => {
  const inferredStatus = error?.code === "LIMIT_FILE_SIZE" ? 413 : error?.message?.startsWith("Only JPG, PNG, and WEBP") ? 400 : error?.status;
  const statusCode = typeof inferredStatus === "number" ? inferredStatus : 500;
  const safeStatus = statusCode >= 400 && statusCode < 500 ? statusCode : 500;
  const message = safeStatus === 413
    ? "The uploaded file exceeds the 10 MB limit."
    : safeStatus === 400
      ? "Only valid JPG, PNG, and WEBP images are supported."
      : "An unexpected server error occurred.";
  console.error(JSON.stringify({ level: "error", message: "Request failed", status: safeStatus, name: error?.name || "Error" }));
  res.status(safeStatus).json({ success: false, message });
};
