import { Router } from "express";
import { getSession } from "@auth/express";
import multer from "multer";
import path from "path";
import fs from "fs";

import { authConfig } from "../auth/auth.js";
import { prisma } from "../lib/prisma.js";
import { runPrediction } from "../services/prediction.service.js";
import { recordActivity } from "../services/activity.service.js";
import { ensureImageUploadDirectory, imageUploadDirectory, imagePublicUrl, resolveStoredUpload, hasValidImageSignature } from "../services/upload-storage.service.js";

const router = Router();

/**
 * -------------------------------------------------------
 * Upload configuration
 * -------------------------------------------------------
 */

ensureImageUploadDirectory();

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, imageUploadDirectory);
  },

  filename: (_req, file, cb) => {
    const extension =
      path.extname(file.originalname).toLowerCase();

    const filename = `${Date.now()}-${Math.random()
      .toString(36)
      .substring(2, 10)}${extension}`;

    cb(null, filename);
  },
});

const imageUpload = multer({
  storage,

  limits: {
    fileSize: 10 * 1024 * 1024,
  },

  fileFilter: (_req, file, cb) => {
    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.mimetype)) {
      return cb(
        new Error(
          "Only JPG, PNG, and WEBP images are supported.",
        ),
      );
    }

    cb(null, true);
  },
});

/**
 * -------------------------------------------------------
 * Authentication helper
 * -------------------------------------------------------
 */

async function getAuthenticatedUser(req: any) {
  const session = await getSession(
    req,
    authConfig,
  );

  if (!session?.user?.email) {
    return null;
  }

  const user = await prisma.user.findUnique({
    where: {
      email: session.user.email.toLowerCase(),
    },
  });

  return user;
}

/**
 * =======================================================
 * DASHBOARD STATS
 * =======================================================
 */

router.get("/stats", async (req, res) => {
  try {
    const user = await getAuthenticatedUser(req);
    if (!user) return res.status(401).json({ success: false, message: "Authentication required" });
    const scope = { analysis: { userId: user.id } };
    const [investigations, completed, processing, failed, evidence, analyzedEvidence] = await Promise.all([
      prisma.analysis.count({ where: { userId: user.id } }),
      prisma.analysis.count({ where: { userId: user.id, status: "COMPLETED" } }),
      prisma.analysis.count({ where: { userId: user.id, status: "PROCESSING" } }),
      prisma.analysis.count({ where: { userId: user.id, status: "FAILED" } }),
      prisma.analysisContent.count({ where: scope }),
      prisma.analysisContent.count({ where: { ...scope, predictions: { some: { status: "COMPLETED" } } } }),
    ]);
    return res.json({ success: true, stats: { investigations, completed, processing, failed, evidence, analyzedEvidence, pendingEvidence: evidence - analyzedEvidence } });
  } catch (error) {
    console.error("Dashboard stats query failed", error);
    return res.status(500).json({ success: false, message: "Unable to load dashboard stats" });
  }
});
router.get("/", async (req, res) => {
  try {
    const user = await getAuthenticatedUser(req);

    if (!user) {
      return res.status(401).json({
        success: false,
        message: "Authentication required",
      });
    }

    const analyses =
      await prisma.analysis.findMany({
        where: {
          userId: user.id,
        },

        orderBy: {
          createdAt: "desc",
        },

        include: {
          _count: {
            select: {
              analysisContents: true,
              predictions: true,
            },
          },
        },
      });

    return res.status(200).json({
      success: true,
      analyses,
    });
  } catch (error) {
    console.error(
      "List analyses error:",
      error,
    );

    return res.status(500).json({
      success: false,
      message: "Unable to load analyses",
    });
  }
});

/**
 * =======================================================
 * CREATE ANALYSIS
 * =======================================================
 */

router.post("/", async (req, res) => {
  try {
    const user = await getAuthenticatedUser(req);

    if (!user) {
      return res.status(401).json({
        success: false,
        message: "Authentication required",
      });
    }

    const title =
      typeof req.body?.title === "string"
        ? req.body.title.trim()
        : "";

    if (!title) {
      return res.status(400).json({
        success: false,
        message: "Analysis title is required",
      });
    }

    const analysis =
      await prisma.analysis.create({
        data: {
          userId: user.id,
          title,
          status: "DRAFT",
        },
      });

    await recordActivity({ userId: user.id, analysisId: analysis.id, analysisTitle: analysis.title, event: "INVESTIGATION_CREATED", status: "COMPLETED" });

    return res.status(201).json({
      success: true,
      analysis,
    });
  } catch (error) {
    console.error(
      "Create analysis error:",
      error,
    );

    return res.status(500).json({
      success: false,
      message: "Unable to create analysis",
    });
  }
});

/**
 * =======================================================
 * GET ANALYSIS
 * =======================================================
 */

router.get("/:analysisId", async (req, res) => {
  try {
    const user = await getAuthenticatedUser(req);

    if (!user) {
      return res.status(401).json({
        success: false,
        message: "Authentication required",
      });
    }

    const { analysisId } = req.params;

    const analysis =
      await prisma.analysis.findFirst({
        where: {
          id: analysisId,
          userId: user.id,
        },

        include: {
          analysisContents: {
            orderBy: {
              createdAt: "desc",
            },
          },

          predictions: {
            orderBy: {
              createdAt: "desc",
            },

            include: {
              content: true,
              model: true,
              modelVersion: true,
            },
          },
        },
      });

    if (!analysis) {
      return res.status(404).json({
        success: false,
        message: "Analysis not found",
      });
    }

    return res.status(200).json({
      success: true,
      analysis,
    });
  } catch (error) {
    console.error(
      "Get analysis error:",
      error,
    );

    return res.status(500).json({
      success: false,
      message: "Unable to load analysis",
    });
  }
});

/**
 * =======================================================
 * LIST ANALYSIS CONTENT
 * =======================================================
 */

router.get(
  "/:analysisId/content",
  async (req, res) => {
    try {
      const user =
        await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const { analysisId } = req.params;

      const analysis =
        await prisma.analysis.findFirst({
          where: {
            id: analysisId,
            userId: user.id,
          },
        });

      if (!analysis) {
        return res.status(404).json({
          success: false,
          message: "Analysis not found",
        });
      }

      const contents =
        await prisma.analysisContent.findMany({
          where: {
            analysisId,
          },

          orderBy: {
            createdAt: "desc",
          },
        });

      return res.status(200).json({
        success: true,
        contents,
      });
    } catch (error) {
      console.error(
        "List analysis content error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to load analysis content",
      });
    }
  },
);

/**
 * =======================================================
 * ADD TEXT EVIDENCE
 * =======================================================
 */

router.post(
  "/:analysisId/content/text",
  async (req, res) => {
    try {
      const user =
        await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const { analysisId } = req.params;

      const title =
        typeof req.body?.title === "string"
          ? req.body.title.trim()
          : "";

      const text =
        typeof req.body?.text === "string"
          ? req.body.text.trim()
          : "";

      if (!text) {
        return res.status(400).json({
          success: false,
          message: "Text content is required",
        });
      }

      const analysis =
        await prisma.analysis.findFirst({
          where: {
            id: analysisId,
            userId: user.id,
          },
        });

      if (!analysis) {
        return res.status(404).json({
          success: false,
          message: "Analysis not found",
        });
      }

      const content =
        await prisma.analysisContent.create({
          data: {
            analysisId,
            type: "TEXT",
            title: title || "Text Evidence",
            text,
          },
        });

      await recordActivity({ userId: user.id, analysisId, analysisTitle: analysis.title, contentId: content.id, contentTitle: content.title || content.type, event: "EVIDENCE_ADDED", status: "COMPLETED", details: { type: content.type } });
      return res.status(201).json({
        success: true,
        content,
      });
    } catch (error) {
      console.error(
        "Add text evidence error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to add text evidence",
      });
    }
  },
);

/**
 * =======================================================
 * ADD SOURCE EVIDENCE
 * =======================================================
 */

router.post(
  "/:analysisId/content/source",
  async (req, res) => {
    try {
      const user =
        await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const { analysisId } = req.params;

      const title =
        typeof req.body?.title === "string"
          ? req.body.title.trim()
          : "";

      const sourceUrl =
        typeof req.body?.sourceUrl === "string"
          ? req.body.sourceUrl.trim()
          : "";

      if (!sourceUrl) {
        return res.status(400).json({
          success: false,
          message: "Source URL is required",
        });
      }

      try {
        new URL(sourceUrl);
      } catch {
        return res.status(400).json({
          success: false,
          message: "Invalid source URL",
        });
      }

      const analysis =
        await prisma.analysis.findFirst({
          where: {
            id: analysisId,
            userId: user.id,
          },
        });

      if (!analysis) {
        return res.status(404).json({
          success: false,
          message: "Analysis not found",
        });
      }

      const content =
        await prisma.analysisContent.create({
          data: {
            analysisId,
            type: "SOURCE",
            title: title || "Source",
            sourceUrl,
          },
        });

      await recordActivity({ userId: user.id, analysisId, analysisTitle: analysis.title, contentId: content.id, contentTitle: content.title || content.type, event: "EVIDENCE_ADDED", status: "COMPLETED", details: { type: content.type } });
      return res.status(201).json({
        success: true,
        content,
      });
    } catch (error) {
      console.error(
        "Add source evidence error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to add source evidence",
      });
    }
  },
);

/**
 * =======================================================
 * ADD IMAGE EVIDENCE
 * =======================================================
 */

router.post(
  "/:analysisId/content/image",
  imageUpload.single("image"),
  async (req, res) => {
    try {
      const user =
        await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      // Express can type route params as string | string[].
      // Convert analysisId to a guaranteed string.
      const analysisId = String(
        req.params.analysisId,
      );

      const analysis =
        await prisma.analysis.findFirst({
          where: {
            id: analysisId,
            userId: user.id,
          },
        });

      if (!analysis) {
        return res.status(404).json({
          success: false,
          message: "Analysis not found",
        });
      }

      if (!req.file) {
        return res.status(400).json({
          success: false,
          message: "Image file is required",
        });
      }

      const title =
        typeof req.body?.title === "string"
          ? req.body.title.trim()
          : "";

      const fileUrl =
        imagePublicUrl(req.file.filename);

      const content =
        await prisma.analysisContent.create({
          data: {
            analysisId,
            type: "IMAGE",
            title:
              title || req.file.originalname,
            fileUrl,
            fileName:
              req.file.originalname,
            mimeType:
              req.file.mimetype,
            fileSize:
              req.file.size,
          },
        });

      await recordActivity({ userId: user.id, analysisId, analysisTitle: analysis.title, contentId: content.id, contentTitle: content.title || content.type, event: "EVIDENCE_ADDED", status: "COMPLETED", details: { type: content.type } });
      return res.status(201).json({
        success: true,
        content,
      });
    } catch (error) {
      console.error(
        "Add image evidence error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to add image evidence",
      });
    }
  },
);
 /**
 * =======================================================
 * DELETE CONTENT
 * =======================================================
 */

router.delete(
  "/:analysisId/content/:contentId",
  async (req, res) => {
    try {
      const user =
        await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      /**
       * Convert route parameters to guaranteed strings.
       */
      const analysisId = String(
        req.params.analysisId,
      );

      const contentId = String(
        req.params.contentId,
      );

      /**
       * Verify analysis ownership.
       */
      const analysis =
        await prisma.analysis.findFirst({
          where: {
            id: analysisId,
            userId: user.id,
          },
        });

      if (!analysis) {
        return res.status(404).json({
          success: false,
          message: "Analysis not found",
        });
      }

      /**
       * Verify evidence belongs to this analysis.
       */
      const content =
        await prisma.analysisContent.findFirst({
          where: {
            id: contentId,
            analysisId,
          },
        });

      if (!content) {
        return res.status(404).json({
          success: false,
          message: "Evidence not found",
        });
      }

      /**
       * Remove physical uploaded image
       * when deleting image evidence.
       */
      if (
        content.type === "IMAGE" &&
        content.fileUrl
      ) {
        const absolutePath = resolveStoredUpload(content.fileUrl);
        if (absolutePath && fs.existsSync(absolutePath)) fs.unlinkSync(absolutePath);
      }

      /**
       * Delete database record.
       *
       * Related predictions are automatically
       * removed because AnalysisContent ->
       * Prediction uses onDelete: Cascade.
       */
      await recordActivity({ userId: user.id, analysisId, analysisTitle: analysis.title, contentId, contentTitle: content.title || content.type, event: "EVIDENCE_REMOVED", status: "COMPLETED", details: { type: content.type } });
      await prisma.analysisContent.delete({
        where: {
          id: contentId,
        },
      });

      return res.status(200).json({
        success: true,
        message: "Evidence deleted",
      });
    } catch (error) {
      console.error(
        "Delete content error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to delete evidence",
      });
    }
  },
);
 /**
 * =======================================================
 * UPDATE ANALYSIS
 * =======================================================
 */

router.patch(
  "/:analysisId",
  async (req, res) => {
    try {
      const user =
        await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const { analysisId } = req.params;

      const existing =
        await prisma.analysis.findFirst({
          where: {
            id: analysisId,
            userId: user.id,
          },
        });

      if (!existing) {
        return res.status(404).json({
          success: false,
          message: "Analysis not found",
        });
      }

      const data: {
        title?: string;
        status?:
          | "DRAFT"
          | "QUEUED"
          | "PROCESSING"
          | "COMPLETED"
          | "FAILED";
      } = {};

      if (
        typeof req.body?.title === "string"
      ) {
        const title =
          req.body.title.trim();

        if (title) {
          data.title = title;
        }
      }

      const allowedStatuses = [
        "DRAFT",
        "QUEUED",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
      ] as const;

      if (
        allowedStatuses.includes(
          req.body?.status,
        )
      ) {
        data.status = req.body.status;
      }

      const analysis =
        await prisma.analysis.update({
          where: {
            id: analysisId,
          },
          data,
        });
      if (data.status && data.status !== existing.status) {
        await recordActivity({ userId: user.id, analysisId, analysisTitle: analysis.title, event: "INVESTIGATION_STATUS_CHANGED", status: data.status, details: { previousStatus: existing.status } });
      }

      return res.status(200).json({
        success: true,
        analysis,
      });
    } catch (error) {
      console.error(
        "Update analysis error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to update analysis",
      });
    }
  },
);

/**
 * =======================================================
 * DELETE ANALYSIS
 * =======================================================
 */

router.delete(
  "/:analysisId",
  async (req, res) => {
    try {
      const user =
        await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const { analysisId } = req.params;

      const analysis =
        await prisma.analysis.findFirst({
          where: {
            id: analysisId,
            userId: user.id,
          },
        });

      if (!analysis) {
        return res.status(404).json({
          success: false,
          message: "Analysis not found",
        });
      }

      await prisma.analysis.delete({
        where: {
          id: analysisId,
        },
      });

      return res.status(200).json({
        success: true,
        message: "Analysis deleted",
      });
    } catch (error) {
      console.error(
        "Delete analysis error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to delete analysis",
      });
    }
  },
);

/**
 * =======================================================
 * RUN PREDICTION
 * =======================================================
 */

router.post(
  "/:analysisId/predict/:contentId",
  async (req, res) => {
    try {
      const user =
        await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const {
        analysisId,
        contentId,
      } = req.params;

      /**
       * Verify analysis ownership.
       */

      const analysis =
        await prisma.analysis.findFirst({
          where: {
            id: analysisId,
            userId: user.id,
          },
        });

      if (!analysis) {
        return res.status(404).json({
          success: false,
          message: "Analysis not found",
        });
      }

      /**
       * Verify evidence ownership.
       */

      const content =
        await prisma.analysisContent.findFirst({
          where: {
            id: contentId,
            analysisId,
          },
        });

      if (!content) {
        return res.status(404).json({
          success: false,
          message: "Evidence not found",
        });
      }

      await recordActivity({ userId: user.id, analysisId, analysisTitle: analysis.title, event: "INVESTIGATION_STATUS_CHANGED", status: "PROCESSING", details: { previousStatus: analysis.status } });

      /**
       * Mark analysis as processing.
       */

      await prisma.analysis.update({
        where: {
          id: analysisId,
        },

        data: {
          status: "PROCESSING",
        },
      });

      try {
        /**
         * Run prediction engine.
         */

        const result =
          await runPrediction({
            analysisId,
            contentId,
          });

        /**
         * Create prediction record.
         *
         * JSON values are explicitly cast to
         * Prisma-compatible InputJsonValue.
         */

        const prediction =
          await prisma.prediction.create({
            data: {
              analysisId,
              contentId,

              prediction:
                result.prediction,

              confidence:
                result.confidence,

              signals:
                result.signals as any,

              metadata:
                result.metadata as any,

              status: "COMPLETED",
            },

            include: {
              content: true,
              model: true,
              modelVersion: true,
            },
          });

        await recordActivity({ userId: user.id, analysisId, analysisTitle: analysis.title, contentId, contentTitle: content.title || content.type, predictionId: prediction.id, event: "PREDICTION_EXECUTED", status: prediction.status, details: { prediction: prediction.prediction, confidence: prediction.confidence } });

        await recordActivity({ userId: user.id, analysisId, analysisTitle: analysis.title, event: "INVESTIGATION_STATUS_CHANGED", status: "COMPLETED", details: { previousStatus: "PROCESSING" } });

        /**
         * Mark analysis completed.
         */

        await prisma.analysis.update({
          where: {
            id: analysisId,
          },

          data: {
            status: "COMPLETED",
          },
        });

        return res.status(201).json({
          success: true,
          prediction,
        });
      } catch (predictionError) {
        await recordActivity({ userId: user.id, analysisId, analysisTitle: analysis.title, event: "INVESTIGATION_STATUS_CHANGED", status: "FAILED", details: { previousStatus: "PROCESSING" } });

        /**
         * Prediction failed.
         */

        await prisma.analysis.update({
          where: {
            id: analysisId,
          },

          data: {
            status: "FAILED",
          },
        });

        throw predictionError;
      }
    } catch (error) {
      console.error(
        "Prediction error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message: "Unable to run prediction. Please try again.",
      });
    }
  },
);

/**
 * =======================================================
 * GET PREDICTIONS
 * =======================================================
 */

router.get(
  "/:analysisId/predictions",
  async (req, res) => {
    try {
      const user =
        await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const { analysisId } = req.params;

      /**
       * Verify analysis ownership.
       */

      const analysis =
        await prisma.analysis.findFirst({
          where: {
            id: analysisId,
            userId: user.id,
          },
        });

      if (!analysis) {
        return res.status(404).json({
          success: false,
          message: "Analysis not found",
        });
      }

      /**
       * Load predictions.
       */

      const predictions =
        await prisma.prediction.findMany({
          where: {
            analysisId,
          },

          orderBy: {
            createdAt: "desc",
          },

          include: {
            content: true,
            model: true,
            modelVersion: true,
          },
        });

      return res.status(200).json({
        success: true,
        predictions,
      });
    } catch (error) {
      console.error(
        "Get predictions error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to load predictions",
      });
    }
  },
);

export default router;







