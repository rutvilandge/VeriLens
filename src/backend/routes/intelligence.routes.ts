import { Router } from "express";
import { getSession } from "@auth/express";
import { authConfig } from "../auth/auth.js";
import { prisma } from "../lib/prisma.js";

const router = Router();

async function currentUser(req: Parameters<typeof getSession>[0]) {
  const session = await getSession(req, authConfig);
  if (!session?.user?.email) return null;
  return prisma.user.findUnique({ where: { email: session.user.email.toLowerCase() }, select: { id: true } });
}

router.get("/graph", async (req, res) => {
  try {
    const user = await currentUser(req);
    if (!user) return res.status(401).json({ success: false, message: "Authentication required" });
    const analyses = await prisma.analysis.findMany({ where: { userId: user.id }, orderBy: { createdAt: "desc" }, include: { analysisContents: { orderBy: { createdAt: "asc" } }, predictions: { include: { model: true, modelVersion: true } } } });
    return res.json({ success: true, analyses });
  } catch {
    return res.status(500).json({ success: false, message: "Unable to load investigation graph" });
  }
});

export default router;
