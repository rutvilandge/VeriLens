import { Router } from "express";
import { getSession } from "@auth/express";
import { authConfig } from "../auth/auth.js";
import { prisma } from "../lib/prisma.js";

const router = Router();

router.get("/", async (req, res) => {
  try {
    const session = await getSession(req, authConfig);
    if (!session?.user?.email) return res.status(401).json({ success: false, message: "Authentication required" });
    const user = await prisma.user.findUnique({ where: { email: session.user.email.toLowerCase() }, select: { id: true } });
    if (!user) return res.status(401).json({ success: false, message: "Authentication required" });
    const events = await prisma.activityEvent.findMany({ where: { userId: user.id }, orderBy: { createdAt: "desc" }, take: 100 });
    return res.json({ success: true, events });
  } catch {
    return res.status(500).json({ success: false, message: "Unable to load activity" });
  }
});

export default router;
