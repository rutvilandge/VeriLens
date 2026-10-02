-- CreateEnum
CREATE TYPE "ContentType" AS ENUM ('TEXT', 'IMAGE', 'SOURCE');

-- CreateTable
CREATE TABLE "AnalysisContent" (
    "id" TEXT NOT NULL,
    "analysisId" TEXT NOT NULL,
    "type" "ContentType" NOT NULL,
    "title" TEXT,
    "text" TEXT,
    "sourceUrl" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "AnalysisContent_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "AnalysisContent_analysisId_idx" ON "AnalysisContent"("analysisId");

-- CreateIndex
CREATE INDEX "AnalysisContent_analysisId_type_idx" ON "AnalysisContent"("analysisId", "type");

-- AddForeignKey
ALTER TABLE "AnalysisContent" ADD CONSTRAINT "AnalysisContent_analysisId_fkey" FOREIGN KEY ("analysisId") REFERENCES "Analysis"("id") ON DELETE CASCADE ON UPDATE CASCADE;
