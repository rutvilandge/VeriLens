import { Router } from "express";
import { getSession } from "@auth/express";
import { authConfig } from "../auth/auth.js";
import { prisma } from "../lib/prisma.js";
import { resolveStoredUpload } from "../services/upload-storage.service.js";

const router = Router();

router.get("/images/:filename", async (req, res) => {
  try {
    const session = await getSession(req, authConfig);
    const email = session?.user?.email?.toLowerCase();
    if (!email) return res.status(401).json({ success: false, message: "Authentication required" });
    const filename = String(req.params.filename || "");
    if (!/^[a-zA-Z0-9_-]+\.(jpg|jpeg|png|webp)$/i.test(filename)) return res.status(404).json({ success: false, message: "Image not found" });
    const content = await prisma.analysisContent.findFirst({
      where: { fileUrl: `/uploads/images/${filename}`, analysis: { user: { email } } },
      select: { fileUrl: true },
    });
    if (!content?.fileUrl) return res.status(404).json({ success: false, message: "Image not found" });
    const filePath = resolveStoredUpload(content.fileUrl);
    if (!filePath) return res.status(404).json({ success: false, message: "Image not found" });
    return res.sendFile(filePath, { headers: { "Cache-Control": "private, no-store" } }, (error) => {
      if (error && !res.headersSent) res.status(404).json({ success: false, message: "Image not found" });
    });
  } catch {
    return res.status(500).json({ success: false, message: "Unable to load image" });
  }
});

export default router;

