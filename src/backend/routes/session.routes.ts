import { Router } from "express";
import { getSession } from "@auth/express";

import { authConfig } from "../auth/auth.js";
import { prisma } from "../lib/prisma.js";

const router = Router();

router.get("/me", async (req, res) => {
  try {
    const session = await getSession(req, authConfig);

    if (!session?.user?.email) {
      return res.status(401).json({
        success: false,
        message: "Authentication required",
      });
    }

    const user = await prisma.user.findUnique({
      where: {
        email: session.user.email.toLowerCase(),
      },
      select: {
        id: true,
        name: true,
        email: true,
        createdAt: true,
      },
    });

    if (!user) {
      return res.status(401).json({
        success: false,
        message: "User account not found",
      });
    }

    return res.status(200).json({
      success: true,
      user,
    });
  } catch (error) {
    console.error("Session verification error:", error);

    return res.status(500).json({
      success: false,
      message: "Unable to verify session",
    });
  }
});

export default router;