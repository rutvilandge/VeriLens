<script setup lang="ts">
import LandingNavbar from "../components/landing/LandingNavbar.vue"
import HeroSection from "../components/landing/HeroSection.vue"
import AnalysisFlow from "../components/landing/AnalysisFlow.vue"
import IntelligenceSection from "../components/landing/IntelligenceSection.vue"
import EvidenceSection from "../components/landing/EvidenceSection.vue"
import GraphPreview from "../components/landing/GraphPreview.vue"
import ExplainabilitySection from "../components/landing/ExplainabilitySection.vue"
import ModelLabSection from "../components/landing/ModelLabSection.vue"
import MLOpsSection from "../components/landing/MLOpsSection.vue"
import LandingCTA from "../components/landing/LandingCTA.vue"
import LandingFooter from "../components/landing/LandingFooter.vue"
</script>

<template>
  <main>
    <!-- Navigation -->
    <LandingNavbar />

    <!-- Landing story -->
    <HeroSection />

    <!-- How VeriLens processes content -->
    <AnalysisFlow />

    <!-- Multimodal intelligence -->
    <IntelligenceSection />

    <!-- Evidence retrieval and relationships -->
    <EvidenceSection />

    <!-- Knowledge graph -->
    <GraphPreview />

    <!-- Explainable AI -->
    <ExplainabilitySection />

    <!-- Model experimentation -->
    <ModelLabSection />

    <!-- Production monitoring -->
    <MLOpsSection />

    <!-- Final conversion -->
    <LandingCTA />

    <!-- Portfolio / contact -->
    <LandingFooter />
  </main>
</template>
