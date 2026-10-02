<script setup lang="ts">
import {
  onBeforeUnmount,
  onMounted,
  computed,
  ref,
} from "vue";

import {
  Activity,
  BarChart3,
  Bell,
  BrainCircuit,
  ChevronDown,
  FileSearch,
  GitBranch,
  LayoutDashboard,
  LogOut,
  Menu,
  Network,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-vue-next";

/* -------------------------------------------------------------------------- */
/* Session                                                                    */
/* -------------------------------------------------------------------------- */

const { logout } = useVeriLensAuth();
const {
  user,
  loading: sessionLoading,
  fetchSession,
} = useVeriLensSession();

await fetchSession();

/* -------------------------------------------------------------------------- */
/* Navigation                                                                 */
/* -------------------------------------------------------------------------- */

const navigation = [
  {
    label: "Overview",
    icon: LayoutDashboard,
    to: "/dashboard",
  },
  {
    label: "Analyses",
    icon: FileSearch,
    to: "/dashboard/analyses",
  },
  {
    label: "Evidence",
    icon: ShieldCheck,
    to: "/dashboard/evidence",
  },
  {
    label: "Knowledge Graph",
    icon: Network,
    to: "/dashboard/knowledge-graph",
  },
];

const intelligenceNavigation = [
  {
    label: "Model Lab",
    icon: BrainCircuit,
    to:"/dashboard/model-lab",
  },
  {
    label: "AI Pipeline",
    icon: GitBranch,
    to: "/dashboard/ai-pipeline",
  },
  {
    label: "Reports",
    icon: BarChart3,
    to: "/dashboard/reports",
  },
];

const systemNavigation = [
  {
    label: "Activity",
    icon: Activity,
    to: "/dashboard/activity",
  },
  {
    label: "Settings",
    icon: Settings,
    to: "/dashboard/settings",
  },
];

/* -------------------------------------------------------------------------- */
/* Sidebar                                                                    */
/* -------------------------------------------------------------------------- */

const sidebarCollapsed = ref(false);
const mobileMenuOpen = ref(false);

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};

const closeMobileMenu = () => {
  mobileMenuOpen.value = false;
};

/* -------------------------------------------------------------------------- */
/* Search                                                                     */
/* -------------------------------------------------------------------------- */

const searchOpen = ref(false);
const globalSearchQuery = ref("");
const searchResults = computed(() => { const query = globalSearchQuery.value.trim().toLowerCase(); return query ? analyses.value.filter((item) => item.title.toLowerCase().includes(query)).slice(0, 8) : []; });

const toggleSearch = () => {
  searchOpen.value = !searchOpen.value;
};

const closeSearch = () => {
  searchOpen.value = false;
};

//* -------------------------------------------------------------------------- */
/* Dashboard                                                                  */
/* -------------------------------------------------------------------------- */

const {
  stats,
  analyses,
  loading: analysesLoading,
  refreshDashboard,
} = useVeriLensAnalyses();

await refreshDashboard();

type DashboardActivity = { id: string; event: string; analysisId: string | null; analysisTitle: string | null; createdAt: string };
const recentActivity = ref<DashboardActivity[]>([]);
const activityLoading = ref(true);
const activityError = ref(false);
const activityApiBase = String(useRuntimeConfig().public.apiBase || "");
const activityLabels: Record<string, string> = { INVESTIGATION_CREATED: "Investigation created", EVIDENCE_ADDED: "Evidence added", EVIDENCE_REMOVED: "Evidence removed", PREDICTION_EXECUTED: "Prediction executed", INVESTIGATION_STATUS_CHANGED: "Investigation status changed" };
onMounted(async () => {
  try { const response = await $fetch<{ events: DashboardActivity[] }>(`${activityApiBase}/api/activity`, { credentials: "include" }); recentActivity.value = (response.events || []).slice(0, 5); }
  catch { activityError.value = true; }
  finally { activityLoading.value = false; }
});

const dashboardStats = computed(() => [
  {
    label: "Investigations",
    value: String(stats.value.investigations),
    caption:
      stats.value.investigations === 0
        ? "No analyses yet"
        : `${stats.value.investigations} total analyses`,
    to: "/dashboard/analyses",
  },

  {
    label: "Completed",
    value: String(stats.value.completed),
    caption:
      stats.value.completed === 0
        ? "Awaiting first result"
        : `${stats.value.completed} completed`,
    to: "/dashboard/analyses?status=COMPLETED",
  },

  {
    label: "Processing",
    value: String(stats.value.processing),
    caption:
      stats.value.processing === 0
        ? "No active pipelines"
        : `${stats.value.processing} active`,
    to: "/dashboard/analyses?status=PROCESSING",
  },

  {
    label: "Failed",
    value: String(stats.value.failed),
    caption: "Failed investigations",
    to: "/dashboard/analyses?status=FAILED",
  },
  {
    label: "Analyzed evidence",
    value: String(stats.value.analyzedEvidence),
    caption: "Evidence with a completed prediction",
    to: "/dashboard/knowledge-graph",
  },
  {
    label: "Pending evidence",
    value: String(stats.value.pendingEvidence),
    caption: "Evidence without completed predictions",
    to: "/dashboard/analyses",
  },
  {
    label: "Evidence",
    value: String(stats.value.evidence),
    caption:
      stats.value.evidence === 0
        ? "No evidence collected"
        : `${stats.value.evidence} evidence items`,
    to: "/dashboard/evidence",
  },
]);
/* -------------------------------------------------------------------------- */
/* Keyboard shortcuts                                                         */
/* -------------------------------------------------------------------------- */

const handleKeydown = (event: KeyboardEvent) => {
  if (
    (event.metaKey || event.ctrlKey) &&
    event.key.toLowerCase() === "k"
  ) {
    event.preventDefault();

    searchOpen.value = true;
  }

  if (event.key === "Escape") {
    searchOpen.value = false;
    mobileMenuOpen.value = false;
  }
};

if (import.meta.client) {
  window.addEventListener("keydown", handleKeydown);

  onBeforeUnmount(() => {
    window.removeEventListener(
      "keydown",
      handleKeydown,
    );
  });
}
</script>

<template>
  <div
    class="dashboard-shell"
    :class="{
      'sidebar-is-collapsed': sidebarCollapsed,
    }"
  >
    <!-- Mobile backdrop -->
    <Transition name="fade">
      <button
        v-if="mobileMenuOpen"
        class="mobile-backdrop"
        aria-label="Close navigation"
        @click="closeMobileMenu"
      />
    </Transition>

    <!-- Sidebar -->
    <aside
      class="dashboard-sidebar"
      :class="{
        'is-collapsed': sidebarCollapsed,
        'is-mobile-open': mobileMenuOpen,
      }"
    >
      <!-- Brand -->
      <div class="sidebar-brand">
        <NuxtLink
          to="/dashboard"
          class="brand-link"
          @click="closeMobileMenu"
        >
          <div class="brand-mark">
            <ShieldCheck :size="20" />
          </div>

          <div
            v-if="!sidebarCollapsed"
            class="brand-copy"
          >
            <span class="brand-name">
              VeriLens
            </span>

            <span class="brand-caption">
              Evidence Intelligence
            </span>
          </div>
        </NuxtLink>

        <button
          class="mobile-close"
          aria-label="Close navigation"
          @click="closeMobileMenu"
        >
          <X :size="19" />
        </button>
      </div>

      <!-- New Analysis -->
      <div class="sidebar-action">
        <NuxtLink
          to="/dashboard/analyses/new"
          class="new-analysis-button"
          @click="closeMobileMenu"
        >
          <Plus :size="18" />

          <span v-if="!sidebarCollapsed">
            New Analysis
          </span>
        </NuxtLink>
      </div>

      <!-- Workspace -->
      <nav class="sidebar-nav">
        <div
          v-if="!sidebarCollapsed"
          class="nav-section-label"
        >
          Workspace
        </div>

        <NuxtLink
          v-for="item in navigation"
          :key="item.label"
          :to="item.to"
          class="sidebar-nav-item"
          active-class="is-active"
          @click="closeMobileMenu"
        >
          <component
            :is="item.icon"
            :size="18"
          />

          <span v-if="!sidebarCollapsed">
            {{ item.label }}
          </span>
        </NuxtLink>

        <div
          v-if="!sidebarCollapsed"
          class="nav-section-label nav-section-spaced"
        >
          Intelligence
        </div>

        <NuxtLink
          v-for="item in intelligenceNavigation"
          :key="item.label"
          :to="item.to"
          class="sidebar-nav-item"
          active-class="is-active"
          @click="closeMobileMenu"
        >
          <component
            :is="item.icon"
            :size="18"
          />

          <span v-if="!sidebarCollapsed">
            {{ item.label }}
          </span>
        </NuxtLink>

        <div
          v-if="!sidebarCollapsed"
          class="nav-section-label nav-section-spaced"
        >
          System
        </div>

        <NuxtLink
          v-for="item in systemNavigation"
          :key="item.label"
          :to="item.to"
          class="sidebar-nav-item"
          active-class="is-active"
          @click="closeMobileMenu"
        >
          <component
            :is="item.icon"
            :size="18"
          />

          <span v-if="!sidebarCollapsed">
            {{ item.label }}
          </span>
        </NuxtLink>
      </nav>

      <!-- Sidebar footer -->
      <div class="sidebar-footer">
        <div class="system-status">
          <span class="status-indicator" />

          <div v-if="!sidebarCollapsed">
            <span class="status-title">
              System operational
            </span>

            <span class="status-caption">
              All core services available
            </span>
          </div>
        </div>

        <button
          class="sidebar-collapse-button"
          :aria-label="
            sidebarCollapsed
              ? 'Expand sidebar'
              : 'Collapse sidebar'
          "
          @click="toggleSidebar"
        >
          <PanelLeftOpen
            v-if="sidebarCollapsed"
            :size="18"
          />

          <PanelLeftClose
            v-else
            :size="18"
          />

          <span v-if="!sidebarCollapsed">
            Collapse
          </span>
        </button>
      </div>
    </aside>

    <!-- Main -->
    <div class="dashboard-main">
      <!-- Topbar -->
      <header class="dashboard-topbar">
        <div class="topbar-left">
          <button
            class="mobile-menu-button"
            aria-label="Open navigation"
            @click="mobileMenuOpen = true"
          >
            <Menu :size="21" />
          </button>

          <button
            class="search-trigger"
            @click="toggleSearch"
          >
            <Search :size="17" />

            <span>
              Search VeriLens...
            </span>

            <kbd>⌘ K</kbd>
          </button>
        </div>

        <div class="topbar-right">
          <NuxtLink to="/dashboard/activity" class="topbar-icon-button" aria-label="Activity history">
            <Bell :size="18" />
          </NuxtLink>

          <div class="topbar-divider" />

          <NuxtLink to="/dashboard/settings" class="user-menu">
            <div class="user-avatar">
              {{
                user?.name
                  ?.charAt(0)
                  .toUpperCase() || "U"
              }}
            </div>

            <div class="user-details">
              <span>
                {{ user?.name || "User" }}
              </span>

              <small>
                {{
                  user?.email ||
                  "Personal workspace"
                }}
              </small>
            </div>

            <ChevronDown :size="15" />
          </NuxtLink>
          <button class="topbar-icon-button" aria-label="Sign out" title="Sign out" @click="logout"><LogOut :size="17" /></button>
        </div>
      </header>

      <!-- Page content -->
      <main class="dashboard-content">
        <!-- Welcome -->
        <section class="welcome-section">
          <div>
            <div class="eyebrow">
              <Sparkles :size="13" />
              Intelligence workspace
            </div>

            <h1>
              Welcome back,
              <span>
                {{ user?.name || "there" }}.
              </span>
            </h1>

            <p>
              Investigate content, connect evidence,
              and understand what the models see.
            </p>
          </div>

          <NuxtLink
            to="/dashboard/analyses/new"
            class="primary-action"
          >
            <Plus :size="18" />
            Start Analysis
          </NuxtLink>
        </section>

        <!-- Statistics -->
        <section class="stats-grid">
          <NuxtLink
            v-for="stat in dashboardStats"
            :key="stat.label"
            :to="stat.to"
            class="stat-card vl-glass"
          >
            <div class="stat-card-top">
              <span class="stat-label">
                {{ stat.label }}
              </span>

              <div class="stat-icon">
                <Activity :size="16" />
              </div>
            </div>

            <div class="stat-value">
              {{ stat.value }}
            </div>

            <div class="stat-caption">
              {{ stat.caption }}
            </div>
          </NuxtLink>
        </section>

        <!-- Empty workspace -->
        <section class="workspace-section">
          <div class="workspace-heading">
            <div>
              <div class="vl-eyebrow">
                Investigation workspace
              </div>

              <h2>
                Your intelligence workspace
              </h2>

              <p>
                Start an investigation to turn content
                into claims, evidence, model insights,
                and an explainable verdict.
              </p>
            </div>

            <NuxtLink
              to="/dashboard/analyses/new"
              class="secondary-action"
            >
              <Plus :size="17" />
              New Analysis
            </NuxtLink>
          </div>

          <div class="workspace-grid">
            <!-- Analysis card -->
            <article
              class="workspace-card workspace-card-large vl-glass"
            >
              <div class="card-visual analysis-visual">
                <div class="visual-orbit orbit-one" />
                <div class="visual-orbit orbit-two" />

                <div class="visual-core">
                  <FileSearch :size="27" />
                </div>

                <div class="visual-node node-one">
                  <span />
                </div>

                <div class="visual-node node-two">
                  <span />
                </div>

                <div class="visual-node node-three">
                  <span />
                </div>
              </div>

              <div class="workspace-card-content">
                <div class="workspace-card-eyebrow">
                  Analysis
                </div>

                <h3>
                  Investigate a new piece of content
                </h3>

                <p>
                  Bring text, images, or other evidence
                  into a structured investigation.
                </p>

                <NuxtLink
                  to="/dashboard/analyses/new"
                  class="card-link"
                >
                  Start investigation
                  <span>→</span>
                </NuxtLink>
              </div>
            </article>

            <!-- Evidence card -->
<NuxtLink
  to="/dashboard/evidence"
  class="workspace-card vl-glass group block cursor-pointer"
>
  <div class="mini-card-icon">
    <ShieldCheck :size="20" />
  </div>

  <div class="workspace-card-eyebrow">
    Evidence intelligence
  </div>

  <h3>
    Evidence Graph
  </h3>

  <p>
    Connect claims, sources, relationships,
    and supporting or contradicting evidence.
  </p>

  <div class="card-link">
    Explore evidence
    <span class="transition-transform duration-200 group-hover:translate-x-1">
      →
    </span>
  </div>
</NuxtLink>
            <!-- Model card -->
            <article
              class="workspace-card vl-glass"
            >
              <div class="mini-card-icon">
                <BrainCircuit :size="20" />
              </div>

              <div class="workspace-card-eyebrow">
                Model intelligence
              </div>

              <h3>
                Model Lab
              </h3>

              <p>
                Inspect model metrics, predictions,
                explanations, and inference behavior.
              </p>

              <NuxtLink
                to="/dashboard/model-lab"
                class="card-link"
              >
                Open Model Lab
                <span>→</span>
              </NuxtLink>
            </article>
          </div>
        </section>

        <!-- Recent activity placeholder -->
        <section class="recent-section">
          <div class="section-heading">
            <div>
              <div class="vl-eyebrow">
                Recent activity
              </div>

              <h2>
                Investigation history
              </h2>
            </div>

            <NuxtLink
              to="/dashboard/activity"
              class="text-link"
            >
              View activity
              <span>→</span>
            </NuxtLink>
          </div>

          <div v-if="activityLoading" class="empty-activity vl-glass">Loading recent activity?</div>
          <div v-else-if="activityError" class="empty-activity vl-glass">Activity history is temporarily unavailable. <NuxtLink to="/dashboard/activity" class="text-link">Open activity</NuxtLink></div>
          <div v-else-if="!recentActivity.length" class="empty-activity vl-glass">No recorded activity yet. Events will appear here after you create an investigation or add evidence.</div>
          <div v-else class="recent-events">
            <article v-for="event in recentActivity" :key="event.id" class="recent-event vl-glass">
              <NuxtLink v-if="event.analysisId" :to="`/dashboard/analyses/${event.analysisId}`" class="font-semibold">{{ activityLabels[event.event] || event.event }} ? {{ event.analysisTitle || "Investigation" }}</NuxtLink>
              <p v-else class="font-semibold">{{ activityLabels[event.event] || event.event }}</p>
              <time class="text-xs text-[var(--vl-muted)]">{{ new Date(event.createdAt).toLocaleString() }}</time>
            </article>
          </div>
        </section>
      </main>
    </div>

    <!-- Search overlay -->
    <Transition name="search">
      <div
        v-if="searchOpen"
        class="search-overlay"
        @click.self="closeSearch"
      >
        <div class="search-modal vl-glass">
          <div class="search-modal-header">
            <div class="search-input-wrapper">
              <Search :size="18" />

              <input
                v-model="globalSearchQuery"
                autofocus
                type="search"
                placeholder="Search investigation titles..."
              />
            </div>

            <button
              class="search-close"
              @click="closeSearch"
            >
              ESC
            </button>
          </div>

          <div class="search-results">
            <p v-if="!globalSearchQuery.trim()" class="search-empty">Enter an investigation title to search your workspace.</p>
            <p v-else-if="!searchResults.length" class="search-empty">No matching investigations.</p>
            <NuxtLink v-for="item in searchResults" :key="item.id" :to="`/dashboard/analyses/${item.id}`" class="search-result" @click="closeSearch">{{ item.title }} <span>{{ item.status }}</span></NuxtLink>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* -------------------------------------------------------------------------- */
/* Layout                                                                      */
/* -------------------------------------------------------------------------- */

.dashboard-shell {
  min-height: 100vh;
  background: var(--vl-bg);
}

.dashboard-main {
  min-height: 100vh;
  margin-left: 272px;
  transition: margin-left 220ms ease;
}

.sidebar-is-collapsed .dashboard-main {
  margin-left: 82px;
}

/* -------------------------------------------------------------------------- */
/* Sidebar                                                                     */
/* -------------------------------------------------------------------------- */

.dashboard-sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 50;

  display: flex;
  width: 272px;
  flex-direction: column;

  padding: 22px 16px 16px;

  background:
    linear-gradient(
      180deg,
      rgba(250, 248, 242, 0.96),
      rgba(244, 241, 232, 0.94)
    );

  border-right: 1px solid var(--vl-border);

  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);

  transition:
    width 220ms ease,
    transform 220ms ease;
}

.dashboard-sidebar.is-collapsed {
  width: 82px;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  justify-content: space-between;

  min-height: 44px;
  margin-bottom: 22px;
}

.brand-link {
  display: flex;
  align-items: center;
  min-width: 0;

  color: inherit;
  text-decoration: none;
}

.brand-mark {
  display: grid;
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  place-items: center;

  color: var(--vl-surface);

  background: var(--vl-sage-dark);
  border-radius: 13px;

  box-shadow:
    0 10px 26px rgba(77, 93, 74, 0.2);
}

.brand-copy {
  display: flex;
  flex-direction: column;
  margin-left: 11px;
}

.brand-name {
  font-size: 0.98rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.brand-caption {
  margin-top: 2px;

  color: var(--vl-muted);
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.mobile-close {
  display: none;

  width: 36px;
  height: 36px;

  place-items: center;

  color: var(--vl-muted);

  background: transparent;
  border: 0;
}

/* -------------------------------------------------------------------------- */
/* Sidebar action                                                              */
/* -------------------------------------------------------------------------- */

.sidebar-action {
  margin-bottom: 22px;
}

.new-analysis-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 9px;

  width: 100%;
  min-height: 44px;

  color: var(--vl-surface);
  background: var(--vl-sage-dark);

  border-radius: 12px;

  font-size: 0.83rem;
  font-weight: 700;
  text-decoration: none;

  box-shadow:
    0 12px 24px rgba(77, 93, 74, 0.15);

  transition:
    transform 180ms ease,
    box-shadow 180ms ease;
}

.new-analysis-button:hover {
  transform: translateY(-1px);

  box-shadow:
    0 15px 28px rgba(77, 93, 74, 0.2);
}

.is-collapsed .new-analysis-button {
  width: 44px;
  margin-inline: auto;
}

/* -------------------------------------------------------------------------- */
/* Navigation                                                                  */
/* -------------------------------------------------------------------------- */

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
}

.nav-section-label {
  padding: 0 11px;
  margin-bottom: 7px;

  color: var(--vl-muted);

  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.nav-section-spaced {
  margin-top: 22px;
}

.sidebar-nav-item {
  display: flex;
  align-items: center;
  gap: 11px;

  min-height: 42px;
  padding: 0 11px;
  margin-bottom: 4px;

  color: #686e66;

  border-radius: 11px;

  font-size: 0.82rem;
  font-weight: 600;

  text-decoration: none;

  transition:
    color 160ms ease,
    background 160ms ease,
    transform 160ms ease;
}

.sidebar-nav-item:hover {
  color: var(--vl-ink);
  background: rgba(113, 129, 107, 0.08);
}

.sidebar-nav-item.is-active {
  color: var(--vl-sage-dark);
  background: rgba(113, 129, 107, 0.13);
}

.is-collapsed .sidebar-nav-item {
  justify-content: center;
  padding-inline: 0;
}

/* -------------------------------------------------------------------------- */
/* Sidebar footer                                                             */
/* -------------------------------------------------------------------------- */

.sidebar-footer {
  padding-top: 14px;
  border-top: 1px solid var(--vl-border);
}

.system-status {
  display: flex;
  align-items: center;
  gap: 10px;

  min-height: 42px;
  padding: 7px 9px;
  margin-bottom: 8px;

  border-radius: 11px;
  background: rgba(255, 255, 255, 0.3);
}

.status-indicator {
  width: 8px;
  height: 8px;
  flex: 0 0 8px;

  background: #668568;
  border-radius: 999px;

  box-shadow:
    0 0 0 4px rgba(102, 133, 104, 0.1);
}

.status-title,
.status-caption {
  display: block;
}

.status-title {
  font-size: 0.72rem;
  font-weight: 700;
}

.status-caption {
  margin-top: 2px;

  color: var(--vl-muted);
  font-size: 0.62rem;
}

.sidebar-collapse-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  width: 100%;
  min-height: 38px;

  color: var(--vl-muted);

  background: transparent;
  border: 0;
  border-radius: 10px;

  font-size: 0.73rem;
  font-weight: 600;
}

.sidebar-collapse-button:hover {
  color: var(--vl-ink);
  background: rgba(113, 129, 107, 0.07);
}

/* -------------------------------------------------------------------------- */
/* Topbar                                                                      */
/* -------------------------------------------------------------------------- */

.dashboard-topbar {
  position: sticky;
  top: 0;
  z-index: 30;

  display: flex;
  align-items: center;
  justify-content: space-between;

  min-height: 76px;
  padding: 0 34px;

  background: rgba(244, 241, 232, 0.78);

  border-bottom: 1px solid rgba(32, 35, 31, 0.08);

  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.topbar-left,
.topbar-right {
  display: flex;
  align-items: center;
}

.search-trigger {
  display: flex;
  align-items: center;
  gap: 10px;

  min-width: 290px;
  min-height: 40px;
  padding: 0 12px;

  color: var(--vl-muted);

  background: rgba(250, 248, 242, 0.72);
  border: 1px solid var(--vl-border);
  border-radius: 11px;

  font-size: 0.76rem;
  font-weight: 600;

  text-align: left;
}

.search-trigger:hover {
  color: var(--vl-ink);
  border-color: rgba(77, 93, 74, 0.22);
}

.search-trigger kbd {
  margin-left: auto;

  padding: 3px 7px;

  color: var(--vl-muted);

  background: var(--vl-surface-soft);
  border: 1px solid var(--vl-border);
  border-radius: 6px;

  font-size: 0.62rem;
}

.mobile-menu-button {
  display: none;

  width: 40px;
  height: 40px;

  place-items: center;

  color: var(--vl-ink);

  background: transparent;
  border: 0;
}

.topbar-right {
  gap: 12px;
}

.topbar-icon-button {
  position: relative;

  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;

  color: var(--vl-muted);

  background: transparent;
  border: 0;
  border-radius: 10px;
}

.topbar-icon-button:hover {
  color: var(--vl-ink);
  background: rgba(113, 129, 107, 0.08);
}

.notification-dot {
  position: absolute;
  top: 8px;
  right: 8px;

  width: 6px;
  height: 6px;

  background: var(--vl-terracotta);
  border: 2px solid var(--vl-bg);
  border-radius: 999px;
}

.topbar-divider {
  width: 1px;
  height: 26px;
  margin-inline: 4px;

  background: var(--vl-border);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 10px;

  padding: 5px 8px 5px 5px;

  color: var(--vl-ink);

  background: transparent;
  border: 0;
  border-radius: 11px;

  text-align: left;
}

.user-menu:hover {
  background: rgba(113, 129, 107, 0.07);
}

.user-avatar {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;

  color: var(--vl-surface);

  background: var(--vl-sage-dark);
  border-radius: 10px;

  font-size: 0.75rem;
  font-weight: 800;
}

.user-details {
  display: flex;
  min-width: 130px;
  flex-direction: column;
}

.user-details span {
  overflow: hidden;

  font-size: 0.76rem;
  font-weight: 750;

  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-details small {
  overflow: hidden;

  margin-top: 2px;

  color: var(--vl-muted);

  font-size: 0.61rem;

  text-overflow: ellipsis;
  white-space: nowrap;
}

/* -------------------------------------------------------------------------- */
/* Content                                                                     */
/* -------------------------------------------------------------------------- */

.dashboard-content {
  width: min(1380px, calc(100% - 68px));
  margin-inline: auto;
  padding: 46px 0 80px;
}

.welcome-section {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 28px;

  margin-bottom: 38px;
}

.eyebrow {
  display: flex;
  align-items: center;
  gap: 7px;

  margin-bottom: 12px;

  color: var(--vl-sage-dark);

  font-size: 0.69rem;
  font-weight: 800;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.welcome-section h1 {
  max-width: 780px;

  margin: 0;

  font-size: clamp(2rem, 4vw, 3.65rem);
  font-weight: 750;
  letter-spacing: -0.055em;
  line-height: 0.98;
}

.welcome-section h1 span {
  color: var(--vl-sage-dark);
}

.welcome-section p {
  max-width: 610px;

  margin: 17px 0 0;

  color: var(--vl-muted);

  font-size: 0.96rem;
  line-height: 1.7;
}

.primary-action,
.secondary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;

  min-height: 45px;
  padding: 0 17px;

  border-radius: 11px;

  font-size: 0.76rem;
  font-weight: 750;

  text-decoration: none;
  white-space: nowrap;
}

.primary-action {
  color: var(--vl-surface);
  background: var(--vl-sage-dark);

  box-shadow:
    0 12px 25px rgba(77, 93, 74, 0.16);
}

.primary-action:hover {
  transform: translateY(-1px);
}

.secondary-action {
  color: var(--vl-sage-dark);

  background: rgba(250, 248, 242, 0.7);
  border: 1px solid var(--vl-border);
}

/* -------------------------------------------------------------------------- */
/* Stats                                                                       */
/* -------------------------------------------------------------------------- */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;

  margin-bottom: 34px;
}

.stat-card {
  min-height: 142px;
  padding: 19px;

  border-radius: 16px;
}

.stat-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-label {
  color: var(--vl-muted);

  font-size: 0.69rem;
  font-weight: 750;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.stat-icon,
.mini-card-icon {
  display: grid;

  place-items: center;

  color: var(--vl-sage-dark);

  background: rgba(113, 129, 107, 0.09);
  border-radius: 9px;
}

.stat-icon {
  width: 31px;
  height: 31px;
}

.stat-value {
  margin-top: 18px;

  font-size: 2rem;
  font-weight: 750;
  letter-spacing: -0.04em;
}

.stat-caption {
  margin-top: 4px;

  color: var(--vl-muted);

  font-size: 0.68rem;
}

/* -------------------------------------------------------------------------- */
/* Workspace                                                                   */
/* -------------------------------------------------------------------------- */

.workspace-section,
.recent-section {
  margin-top: 38px;
}

.workspace-heading,
.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;

  margin-bottom: 18px;
}

.workspace-heading h2,
.section-heading h2 {
  margin: 7px 0 0;

  font-size: 1.4rem;
  font-weight: 760;
  letter-spacing: -0.035em;
}

.workspace-heading p {
  max-width: 620px;

  margin: 8px 0 0;

  color: var(--vl-muted);

  font-size: 0.78rem;
  line-height: 1.65;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  gap: 14px;
}

.workspace-card {
  min-height: 315px;
  padding: 22px;

  border-radius: 18px;
}

.workspace-card-large {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  overflow: hidden;
}

.card-visual {
  position: relative;

  min-height: 145px;
  overflow: hidden;

  border-radius: 13px;

  background:
    radial-gradient(
      circle at 50% 50%,
      rgba(113, 129, 107, 0.17),
      transparent 36%
    ),
    rgba(238, 236, 227, 0.56);
}

.visual-core {
  position: absolute;
  top: 50%;
  left: 50%;

  display: grid;
  width: 56px;
  height: 56px;
  place-items: center;

  color: var(--vl-sage-dark);

  background: rgba(250, 248, 242, 0.88);
  border: 1px solid var(--vl-border);
  border-radius: 16px;

  transform: translate(-50%, -50%);

  box-shadow:
    0 12px 30px rgba(32, 35, 31, 0.08);
}

.visual-orbit {
  position: absolute;
  top: 50%;
  left: 50%;

  border: 1px solid rgba(113, 129, 107, 0.2);
  border-radius: 50%;

  transform: translate(-50%, -50%);
}

.orbit-one {
  width: 150px;
  height: 86px;
  transform:
    translate(-50%, -50%)
    rotate(-12deg);
}

.orbit-two {
  width: 205px;
  height: 112px;
  transform:
    translate(-50%, -50%)
    rotate(18deg);
}

.visual-node {
  position: absolute;

  display: grid;
  width: 12px;
  height: 12px;
  place-items: center;

  background: var(--vl-terracotta);
  border: 3px solid var(--vl-surface);

  border-radius: 50%;
}

.visual-node span {
  display: block;
  width: 4px;
  height: 4px;

  background: var(--vl-surface);
  border-radius: 50%;
}

.node-one {
  top: 26%;
  left: 31%;
}

.node-two {
  top: 62%;
  right: 24%;
}

.node-three {
  right: 29%;
  bottom: 22%;
}

.workspace-card-content {
  padding-top: 18px;
}

.workspace-card-eyebrow {
  color: var(--vl-sage-dark);

  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.13em;
  text-transform: uppercase;
}

.workspace-card h3 {
  margin: 8px 0 0;

  font-size: 1.1rem;
  font-weight: 750;
  letter-spacing: -0.025em;
}

.workspace-card p {
  margin: 9px 0 0;

  color: var(--vl-muted);

  font-size: 0.76rem;
  line-height: 1.65;
}

.mini-card-icon {
  width: 42px;
  height: 42px;
  margin-bottom: 28px;
}

.card-link,
.text-link {
  display: inline-flex;
  align-items: center;
  gap: 7px;

  margin-top: 19px;

  color: var(--vl-sage-dark);

  font-size: 0.72rem;
  font-weight: 750;

  text-decoration: none;
}

.card-link:hover,
.text-link:hover {
  text-decoration: underline;
}

.card-link span,
.text-link span {
  transition: transform 160ms ease;
}

.card-link:hover span,
.text-link:hover span {
  transform: translateX(3px);
}

/* -------------------------------------------------------------------------- */
/* Activity                                                                    */
/* -------------------------------------------------------------------------- */

.section-heading {
  align-items: center;
}

.empty-activity {
  display: flex;
  align-items: center;
  gap: 16px;

  min-height: 115px;
  padding: 22px;

  border-radius: 16px;
}

.empty-activity-icon {
  display: grid;
  width: 44px;
  height: 44px;
  flex: 0 0 44px;
  place-items: center;

  color: var(--vl-sage-dark);

  background: rgba(113, 129, 107, 0.09);
  border-radius: 12px;
}

.empty-activity h3 {
  margin: 0;

  font-size: 0.88rem;
  font-weight: 750;
}

.empty-activity p {
  max-width: 560px;

  margin: 5px 0 0;

  color: var(--vl-muted);

  font-size: 0.72rem;
  line-height: 1.55;
}

/* -------------------------------------------------------------------------- */
/* Search modal                                                                */
/* -------------------------------------------------------------------------- */

.search-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;

  display: grid;
  place-items: start center;

  padding: 100px 20px 30px;

  background: rgba(32, 35, 31, 0.18);

  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.search-modal {
  width: min(680px, 100%);

  overflow: hidden;

  border-radius: 18px;
}

.search-modal-header {
  display: flex;
  align-items: center;
  gap: 10px;

  padding: 10px;

  border-bottom: 1px solid var(--vl-border);
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 10px;

  padding: 0 10px;

  color: var(--vl-muted);
}

.search-input-wrapper input {
  width: 100%;
  min-height: 45px;

  color: var(--vl-ink);

  background: transparent;
  border: 0;
  outline: 0;

  font-size: 0.82rem;
}

.search-input-wrapper input::placeholder {
  color: #969b93;
}

.search-close {
  min-height: 34px;
  padding: 0 9px;

  color: var(--vl-muted);

  background: var(--vl-surface-soft);
  border: 1px solid var(--vl-border);
  border-radius: 7px;

  font-size: 0.62rem;
  font-weight: 750;
}

.search-empty {
  display: flex;
  flex-direction: column;
  align-items: center;

  padding: 55px 30px;

  text-align: center;
}

.search-empty-icon {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;

  color: var(--vl-sage-dark);

  background: rgba(113, 129, 107, 0.1);
  border-radius: 14px;
}

.search-empty h3 {
  margin: 15px 0 0;

  font-size: 0.95rem;
}

.search-empty p {
  margin: 6px 0 0;

  color: var(--vl-muted);

  font-size: 0.72rem;
}

/* -------------------------------------------------------------------------- */
/* Transitions                                                                 */
/* -------------------------------------------------------------------------- */

.fade-enter-active,
.fade-leave-active {
  transition: opacity 180ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.search-enter-active,
.search-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.search-enter-from,
.search-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* -------------------------------------------------------------------------- */
/* Responsive                                                                  */
/* -------------------------------------------------------------------------- */

@media (max-width: 1100px) {
  .dashboard-content {
    width: min(100% - 44px, 1380px);
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .workspace-grid {
    grid-template-columns: 1fr 1fr;
  }

  .workspace-card-large {
    grid-column: 1 / -1;
  }
}

@media (max-width: 820px) {
  .dashboard-sidebar {
    width: 272px;

    transform: translateX(-100%);

    box-shadow:
      20px 0 70px rgba(32, 35, 31, 0.12);
  }

  .dashboard-sidebar.is-mobile-open {
    transform: translateX(0);
  }

  .dashboard-sidebar.is-collapsed {
    width: 272px;
  }

  .dashboard-sidebar.is-collapsed .brand-copy,
  .dashboard-sidebar.is-collapsed .new-analysis-button span,
  .dashboard-sidebar.is-collapsed .sidebar-nav-item span,
  .dashboard-sidebar.is-collapsed .nav-section-label,
  .dashboard-sidebar.is-collapsed .system-status div,
  .dashboard-sidebar.is-collapsed
    .sidebar-collapse-button span {
    display: block;
  }

  .dashboard-sidebar.is-collapsed
    .sidebar-nav-item {
    justify-content: flex-start;
    padding-inline: 11px;
  }

  .dashboard-sidebar.is-collapsed
    .new-analysis-button {
    width: 100%;
  }

  .mobile-close {
    display: grid;
  }

  .dashboard-main,
  .sidebar-is-collapsed .dashboard-main {
    margin-left: 0;
  }

  .mobile-menu-button {
    display: grid;
  }

  .search-trigger {
    min-width: 0;
  }

  .search-trigger span {
    display: none;
  }

  .search-trigger kbd {
    display: none;
  }

  .dashboard-topbar {
    padding-inline: 18px;
  }

  .user-details {
    display: none;
  }

  .topbar-divider {
    display: none;
  }
}

@media (max-width: 680px) {
  .dashboard-content {
    width: min(100% - 28px, 1380px);
    padding-top: 32px;
  }

  .welcome-section {
    align-items: flex-start;
    flex-direction: column;
    margin-bottom: 28px;
  }

  .welcome-section h1 {
    font-size: 2.25rem;
  }

  .primary-action {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: 1fr 1fr;
    gap: 9px;
  }

  .stat-card {
    min-height: 125px;
    padding: 15px;
  }

  .stat-value {
    font-size: 1.65rem;
  }

  .workspace-heading,
  .section-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .workspace-card-large {
    grid-column: auto;
  }

  .secondary-action {
    width: 100%;
  }

  .empty-activity {
    align-items: flex-start;
  }
}

@media (max-width: 440px) {
  .topbar-right {
    gap: 4px;
  }

  .search-trigger {
    width: 40px;
    padding: 0;

    justify-content: center;

    border: 0;
    background: transparent;
  }

  .dashboard-topbar {
    min-height: 66px;
    padding-inline: 10px;
  }

  .dashboard-content {
    width: min(100% - 22px, 1380px);
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .welcome-section h1 {
    font-size: 2rem;
  }

  .workspace-card {
    min-height: 285px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .dashboard-sidebar,
  .dashboard-main,
  .new-analysis-button,
  .card-link span,
  .text-link span {
    transition: none !important;
  }
}
.recent-events { display: grid; gap: 10px; }
.recent-event { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 16px 18px; border: 1px solid var(--vl-border); border-radius: 14px; }
.search-results { display: grid; gap: 8px; padding: 18px; }
.search-empty { color: var(--vl-muted); font-size: 0.875rem; padding: 16px; }
.search-result { display: flex; justify-content: space-between; gap: 12px; padding: 13px 15px; border-radius: 12px; background: rgba(113,129,107,.08); color: var(--vl-ink); font-size: .9rem; }
.search-result span { color: var(--vl-muted); font-size: .75rem; }</style>
