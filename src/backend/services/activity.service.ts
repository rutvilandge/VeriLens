import { prisma } from "../lib/prisma.js";

type ActivityInput = {
  userId: string;
  analysisId?: string;
  analysisTitle?: string;
  contentId?: string;
  contentTitle?: string;
  predictionId?: string;
  event: string;
  status: string;
  details?: Record<string, unknown>;
};

export async function recordActivity(input: ActivityInput) {
  return prisma.activityEvent.create({
    data: {
      ...input,
      details: input.details as any,
    },
  });
}
