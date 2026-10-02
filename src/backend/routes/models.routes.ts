import { Router } from "express";
import { getSession } from "@auth/express";
import { z } from "zod";

import { authConfig } from "../auth/auth.js";
import { prisma } from "../lib/prisma.js";

const router = Router();

/* =========================================================
   AUTHENTICATED USER
========================================================= */

const getAuthenticatedUser = async (req: any) => {
  const session = await getSession(req, authConfig);

  if (!session?.user?.email) {
    return null;
  }

  return prisma.user.findUnique({
    where: {
      email: session.user.email,
    },
  });
};

/* =========================================================
   VALIDATION
========================================================= */

const createModelSchema = z.object({
  name: z.string().min(2).max(200),
  slug: z
    .string()
    .min(2)
    .max(100)
    .regex(
      /^[a-z0-9-]+$/,
      "Slug can contain only lowercase letters, numbers and hyphens",
    ),
  description: z.string().max(1000).optional(),
  type: z.enum([
    "TEXT_AUTHENTICITY",
    "AI_GENERATED_TEXT",
    "IMAGE_AUTHENTICITY",
    "MULTIMODAL",
  ]),
  provider: z.string().max(100).optional(),
  task: z.string().max(200).optional(),
});

const createVersionSchema = z.object({
  version: z.string().min(1).max(50),
  description: z.string().max(1000).optional(),
  status: z
    .enum([
      "DEVELOPMENT",
      "READY",
      "DEPLOYED",
      "ARCHIVED",
    ])
    .optional(),
  framework: z.string().max(100).optional(),
  modelPath: z.string().max(500).optional(),
  parameters: z.record(z.string(), z.any()).optional(),
});

const createEvaluationSchema = z.object({
  datasetName: z.string().max(200).optional(),
  accuracy: z.number().min(0).max(1).optional(),
  precision: z.number().min(0).max(1).optional(),
  recall: z.number().min(0).max(1).optional(),
  f1Score: z.number().min(0).max(1).optional(),
  sampleCount: z.number().int().nonnegative().optional(),
});

const createExperimentSchema = z.object({
  name: z.string().min(2).max(200),
  description: z.string().max(1000).optional(),
  configuration: z.record(z.string(), z.any()).optional(),
});

/* =========================================================
   GET ALL MODELS
   GET /api/models
========================================================= */

router.get("/", async (req, res) => {
  try {
    const user = await getAuthenticatedUser(req);

    if (!user) {
      return res.status(401).json({
        success: false,
        message: "Authentication required",
      });
    }

    const models = await prisma.aIModel.findMany({
      include: {
        versions: {
          orderBy: {
            createdAt: "desc",
          },
        },
        _count: {
          select: {
            experiments: true,
          },
        },
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    return res.status(200).json({
      success: true,
      models,
    });
  } catch (error) {
    console.error(
      "Model listing error:",
      error,
    );

    return res.status(500).json({
      success: false,
      message: "Unable to fetch models",
    });
  }
});

/* =========================================================
   CREATE MODEL
   POST /api/models
========================================================= */

router.post("/", async (req, res) => {
  try {
    const user = await getAuthenticatedUser(req);

    if (!user) {
      return res.status(401).json({
        success: false,
        message: "Authentication required",
      });
    }

    const result =
      createModelSchema.safeParse(req.body);

    if (!result.success) {
      return res.status(400).json({
        success: false,
        message: "Invalid model details",
        errors:
          result.error.flatten().fieldErrors,
      });
    }

    const existing =
      await prisma.aIModel.findUnique({
        where: {
          slug: result.data.slug,
        },
      });

    if (existing) {
      return res.status(409).json({
        success: false,
        message:
          "A model with this slug already exists",
      });
    }

    const model =
      await prisma.aIModel.create({
        data: {
          name: result.data.name,
          slug: result.data.slug,
          description:
            result.data.description || null,
          type: result.data.type,
          provider:
            result.data.provider || null,
          task:
            result.data.task || null,
        },
      });

    return res.status(201).json({
      success: true,
      message: "Model created successfully",
      model,
    });
  } catch (error) {
    console.error(
      "Model creation error:",
      error,
    );

    return res.status(500).json({
      success: false,
      message: "Unable to create model",
    });
  }
});

/* =========================================================
   GET MODEL BY ID
   GET /api/models/:id
========================================================= */

router.get("/:id", async (req, res) => {
  try {
    const user = await getAuthenticatedUser(req);

    if (!user) {
      return res.status(401).json({
        success: false,
        message: "Authentication required",
      });
    }

    const model =
      await prisma.aIModel.findUnique({
        where: {
          id: req.params.id,
        },
        include: {
          versions: {
            include: {
              evaluations: {
                orderBy: {
                  createdAt: "desc",
                },
              },
            },
            orderBy: {
              createdAt: "desc",
            },
          },
          experiments: {
            orderBy: {
              createdAt: "desc",
            },
          },
        },
      });

    if (!model) {
      return res.status(404).json({
        success: false,
        message: "Model not found",
      });
    }

    return res.status(200).json({
      success: true,
      model,
    });
  } catch (error) {
    console.error(
      "Model fetch error:",
      error,
    );

    return res.status(500).json({
      success: false,
      message: "Unable to fetch model",
    });
  }
});

/* =========================================================
   ADD MODEL VERSION
   POST /api/models/:id/versions
========================================================= */

router.post(
  "/:id/versions",
  async (req, res) => {
    try {
      const user = await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const result =
        createVersionSchema.safeParse(
          req.body,
        );

      if (!result.success) {
        return res.status(400).json({
          success: false,
          message: "Invalid model version",
          errors:
            result.error.flatten().fieldErrors,
        });
      }

      const model =
        await prisma.aIModel.findUnique({
          where: {
            id: req.params.id,
          },
          select: {
            id: true,
          },
        });

      if (!model) {
        return res.status(404).json({
          success: false,
          message: "Model not found",
        });
      }

      const existing =
        await prisma.modelVersion.findUnique({
          where: {
            modelId_version: {
              modelId: model.id,
              version: result.data.version,
            },
          },
        });

      if (existing) {
        return res.status(409).json({
          success: false,
          message:
            "This model version already exists",
        });
      }

      const version =
        await prisma.modelVersion.create({
          data: {
            modelId: model.id,
            version: result.data.version,
            description:
              result.data.description || null,
            status:
              result.data.status ||
              "DEVELOPMENT",
            framework:
              result.data.framework || null,
            modelPath:
              result.data.modelPath || null,
            parameters:
              result.data.parameters || undefined,
          },
        });

      return res.status(201).json({
        success: true,
        message:
          "Model version created successfully",
        version,
      });
    } catch (error) {
      console.error(
        "Model version creation error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to create model version",
      });
    }
  },
);

/* =========================================================
   ADD EVALUATION
   POST /api/models/:id/versions/:versionId/evaluations
========================================================= */

router.post(
  "/:id/versions/:versionId/evaluations",
  async (req, res) => {
    try {
      const user = await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const result =
        createEvaluationSchema.safeParse(
          req.body,
        );

      if (!result.success) {
        return res.status(400).json({
          success: false,
          message: "Invalid evaluation details",
          errors:
            result.error.flatten().fieldErrors,
        });
      }

      const version =
        await prisma.modelVersion.findFirst({
          where: {
            id: req.params.versionId,
            modelId: req.params.id,
          },
          select: {
            id: true,
          },
        });

      if (!version) {
        return res.status(404).json({
          success: false,
          message: "Model version not found",
        });
      }

      const evaluation =
        await prisma.modelEvaluation.create({
          data: {
            modelVersionId: version.id,
            datasetName:
              result.data.datasetName || null,
            accuracy:
              result.data.accuracy ?? null,
            precision:
              result.data.precision ?? null,
            recall:
              result.data.recall ?? null,
            f1Score:
              result.data.f1Score ?? null,
            sampleCount:
              result.data.sampleCount ?? null,
          },
        });

      return res.status(201).json({
        success: true,
        message:
          "Model evaluation added successfully",
        evaluation,
      });
    } catch (error) {
      console.error(
        "Model evaluation error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to add model evaluation",
      });
    }
  },
);

/* =========================================================
   CREATE EXPERIMENT
   POST /api/models/:id/experiments
========================================================= */

router.post(
  "/:id/experiments",
  async (req, res) => {
    try {
      const user = await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const result =
        createExperimentSchema.safeParse(
          req.body,
        );

      if (!result.success) {
        return res.status(400).json({
          success: false,
          message: "Invalid experiment details",
          errors:
            result.error.flatten().fieldErrors,
        });
      }

      const model =
        await prisma.aIModel.findUnique({
          where: {
            id: req.params.id,
          },
          select: {
            id: true,
          },
        });

      if (!model) {
        return res.status(404).json({
          success: false,
          message: "Model not found",
        });
      }

      const experiment =
        await prisma.experiment.create({
          data: {
            modelId: model.id,
            name: result.data.name,
            description:
              result.data.description || null,
            configuration:
              result.data.configuration ||
              undefined,
          },
        });

      return res.status(201).json({
        success: true,
        message:
          "Experiment created successfully",
        experiment,
      });
    } catch (error) {
      console.error(
        "Experiment creation error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to create experiment",
      });
    }
  },
);

/* =========================================================
   GET MODEL EXPERIMENTS
   GET /api/models/:id/experiments
========================================================= */

router.get(
  "/:id/experiments",
  async (req, res) => {
    try {
      const user = await getAuthenticatedUser(req);

      if (!user) {
        return res.status(401).json({
          success: false,
          message: "Authentication required",
        });
      }

      const model =
        await prisma.aIModel.findUnique({
          where: {
            id: req.params.id,
          },
          select: {
            id: true,
          },
        });

      if (!model) {
        return res.status(404).json({
          success: false,
          message: "Model not found",
        });
      }

      const experiments =
        await prisma.experiment.findMany({
          where: {
            modelId: model.id,
          },
          orderBy: {
            createdAt: "desc",
          },
        });

      return res.status(200).json({
        success: true,
        experiments,
      });
    } catch (error) {
      console.error(
        "Experiment listing error:",
        error,
      );

      return res.status(500).json({
        success: false,
        message:
          "Unable to fetch experiments",
      });
    }
  },
);

export default router;