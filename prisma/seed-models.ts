import { prisma } from "../src/backend/lib/prisma.js";

const models = [
  {
    name: "Text Authenticity Model",
    slug: "text-authenticity",
    description:
      "Analyzes written content for authenticity signals, linguistic patterns, and potential manipulation.",
    type: "TEXT_AUTHENTICITY" as const,
    provider: "VeriLens",
    task: "Text authenticity analysis",
  },
  {
    name: "AI-Generated Text Model",
    slug: "ai-generated-text",
    description:
      "Analyzes text for patterns associated with AI-generated content.",
    type: "AI_GENERATED_TEXT" as const,
    provider: "VeriLens",
    task: "AI-generated text detection",
  },
  {
    name: "Image Authenticity Model",
    slug: "image-authenticity",
    description:
      "Analyzes images for visual authenticity signals, manipulation indicators, and synthetic-content patterns.",
    type: "IMAGE_AUTHENTICITY" as const,
    provider: "VeriLens",
    task: "Image authenticity analysis",
  },
  {
    name: "Multimodal Model",
    slug: "multimodal",
    description:
      "Combines text and image evidence to produce cross-modal authenticity insights.",
    type: "MULTIMODAL" as const,
    provider: "VeriLens",
    task: "Multimodal evidence analysis",
  },
];

async function main() {
  console.log("🚀 Seeding VeriLens Model Registry...\n");

  for (const model of models) {
    const result = await prisma.aIModel.upsert({
      where: {
        slug: model.slug,
      },
      update: {
        name: model.name,
        description: model.description,
        type: model.type,
        provider: model.provider,
        task: model.task,
      },
      create: model,
    });

    console.log(`✅ ${result.name}`);
  }

  console.log("\n🎉 Model Registry seeded successfully.");
}

main()
  .catch((error) => {
    console.error("❌ Model seeding failed:", error);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });

