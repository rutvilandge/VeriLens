import { prisma } from "../lib/prisma.js";

type PredictionInput = {
  analysisId: string;
  contentId: string;
};

type PredictionResult = {
  prediction: string;
  confidence: number;
  signals: Record<string, unknown>;
  metadata: Record<string, unknown>;
};

export async function runPrediction(
  input: PredictionInput,
): Promise<PredictionResult> {
  const content = await prisma.analysisContent.findUnique({
    where: {
      id: input.contentId,
    },
  });

  if (!content) {
    throw new Error("Evidence content not found");
  }

  if (content.analysisId !== input.analysisId) {
    throw new Error(
      "Evidence does not belong to this analysis",
    );
  }

  /*
   * Stage 19 MVP prediction logic.
   *
   * This is intentionally deterministic and local.
   * Later stages can replace this with actual ML models.
   */

  let prediction = "INCONCLUSIVE";
  let confidence = 0.5;

  const signals: Record<string, unknown> = {
    contentType: content.type,
    hasText: Boolean(content.text),
    hasSourceUrl: Boolean(content.sourceUrl),
    hasFile: Boolean(content.fileUrl),
  };

  if (content.type === "TEXT" && content.text) {
    const textLength = content.text.trim().length;

    signals.textLength = textLength;

    if (textLength >= 500) {
      prediction = "TEXT_REQUIRES_ANALYSIS";
      confidence = 0.65;
    } else if (textLength > 0) {
      prediction = "TEXT_REQUIRES_ANALYSIS";
      confidence = 0.55;
    }
  }

  if (content.type === "IMAGE") {
    prediction = "IMAGE_REQUIRES_ANALYSIS";
    confidence = 0.55;
  }

  if (content.type === "SOURCE") {
    prediction = "SOURCE_REQUIRES_ANALYSIS";
    confidence = 0.6;
  }

  return {
    prediction,
    confidence,
    signals,
    metadata: {
      engine: "verilens-prediction-engine",
      version: "0.1.0",
      mode: "deterministic-mvp",
      generatedAt: new Date().toISOString(),
    },
  };
}