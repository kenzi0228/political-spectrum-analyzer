import {
  Activity,
  BarChart3,
  BookOpen,
  CircleHelp,
  Copy,
  GitCompareArrows,
  Home,
  Languages,
  Library,
  Moon,
  Plus,
  SlidersHorizontal,
  Sun,
  Undo2,
} from "lucide-react";
import { lazy, Suspense, useEffect, useState } from "react";
import { applyAdConsent, loadAdsense, readAdConsent, type AdConsent } from "./ads";
import { CookieConsent } from "./components/CookieConsent";
import { SiteFooter } from "./components/Common";
import { messages } from "./i18n";
import { SCORING_MODEL_VERSION } from "./model";
import { buildAppRoute, currentAppLocation, parseAppRoute } from "./navigation";
import {
  createDefaultProfile,
  parseStoredProfiles,
  serializeProfiles,
} from "./profile-data";
import { PROFILE_COLORS } from "./constants";
import type { Language, Profile, ViewKey } from "./types";
import { AnalysisView } from "./views/AnalysisView";
import { ComparisonView } from "./views/ComparisonView";
import { InputView } from "./views/InputView";
import {
  AboutView,
  GuideView,
  HomeView,
  LegalView,
  MethodologyView,
  PrivacyView,
} from "./views/StaticViews";

const VisualizationView = lazy(() => import("./views/VisualizationView"));
const AtlasView = lazy(() => import("./views/AtlasView"));

const NAV_VIEWS = [
  "home",
  "input",
  "guide",
  "visualization",
  "analysis",
  "comparison",
  "methodology",
  "atlas",
] as const satisfies readonly ViewKey[];

const viewIcons = {
  home: Home,
  input: SlidersHorizontal,
  guide: CircleHelp,
  visualization: BarChart3,
  analysis: Activity,
  comparison: GitCompareArrows,
  methodology: BookOpen,
  atlas: Library,
} as const;

const readStoredProfiles = (): Profile[] => {
  try {
    return parseStoredProfiles(localStorage.getItem("psa.profiles")) ?? [createDefaultProfile()];
  } catch {
    return [createDefaultProfile()];
  }
};

export default function App() {
  const [profiles, setProfilesState] = useState<Profile[]>(readStoredProfiles);
  const [language, setLanguage] = useState<Language>("fr");
  const [view, setView] = useState<ViewKey>(() => parseAppRoute(currentAppLocation()).view);
  const [theme, setTheme] = useState<"dark" | "light">(() => localStorage.getItem("psa.theme") === "light" ? "light" : "dark");
  const [preciseInput, setPreciseInput] = useState(() => localStorage.getItem("psa.preciseInput") !== "false");
  const [activeId, setActiveId] = useState(() => {
    const requested = parseAppRoute(currentAppLocation()).profileId;
    return profiles.some((profile) => profile.id === requested) ? requested! : profiles[0].id;
  });
  const [undoSnapshot, setUndoSnapshot] = useState<Profile[] | null>(null);
  const [adConsent, setAdConsent] = useState<AdConsent>(readAdConsent);
  const [storageAvailable, setStorageAvailable] = useState(true);
  const copy = messages[language];
  const activeProfile = profiles.find((profile) => profile.id === activeId) ?? profiles[0];

  const persistProfiles = (next: Profile[], remember = true) => {
    if (remember) setUndoSnapshot(profiles);
    setProfilesState(next);
    try {
      localStorage.setItem("psa.profiles", serializeProfiles(next));
    } catch {
      setStorageAvailable(false);
    }
  };

  const navigate = (nextView: ViewKey, profileId = activeId, replace = false) => {
    setView(nextView);
    setActiveId(profileId);
    const route = buildAppRoute(nextView, profileId);
    if (currentAppLocation() === route) return;
    window.history[replace ? "replaceState" : "pushState"](null, "", route);
  };

  useEffect(() => {
    const canonical = buildAppRoute(view, activeId);
    if (currentAppLocation() !== canonical) window.history.replaceState(null, "", canonical);
    try {
      localStorage.setItem("psa.profiles", serializeProfiles(profiles));
    } catch {
      setStorageAvailable(false);
    }
    if (adConsent === "accepted") loadAdsense();
  }, []);

  useEffect(() => {
    const syncRoute = () => {
      const route = parseAppRoute(currentAppLocation());
      setView(route.view);
      if (route.profileId && profiles.some((profile) => profile.id === route.profileId)) {
        setActiveId(route.profileId);
      }
    };
    window.addEventListener("popstate", syncRoute);
    return () => window.removeEventListener("popstate", syncRoute);
  }, [profiles]);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("psa.theme", theme);
    } catch {
      setStorageAvailable(false);
    }
  }, [theme]);

  useEffect(() => {
    try {
      localStorage.setItem("psa.preciseInput", String(preciseInput));
    } catch {
      setStorageAvailable(false);
    }
  }, [preciseInput]);

  useEffect(() => {
    document.documentElement.lang = language;
    document.title = `${copy.views[NAV_VIEWS.includes(view as typeof NAV_VIEWS[number]) ? view as typeof NAV_VIEWS[number] : "home"]} · Politiscales Analyser`;
  }, [copy, language, view]);

  const addProfile = () => {
    const profile = createDefaultProfile(profiles.length + 1);
    persistProfiles([...profiles, profile]);
    navigate(view, profile.id);
  };

  const duplicateProfile = () => {
    const profile = {
      ...createDefaultProfile(profiles.length + 1),
      name: `${activeProfile.name} ${language === "fr" ? "copie" : "copy"}`,
      scores: { ...activeProfile.scores },
    };
    persistProfiles([...profiles, profile]);
    navigate(view, profile.id);
  };

  const removeProfile = (id: string) => {
    if (profiles.length === 1) return;
    const next = profiles.filter((profile) => profile.id !== id);
    persistProfiles(next);
    if (id === activeId) navigate(view, next[0].id, true);
  };

  const updateProfile = (next: Profile) =>
    persistProfiles(profiles.map((profile) => profile.id === next.id ? next : profile));

  const undo = () => {
    if (!undoSnapshot?.length) return;
    const current = profiles;
    persistProfiles(undoSnapshot, false);
    setUndoSnapshot(current);
    if (!undoSnapshot.some((profile) => profile.id === activeId)) navigate(view, undoSnapshot[0].id, true);
  };

  const renderView = () => {
    switch (view) {
      case "home": return <HomeView language={language} onNavigate={navigate} />;
      case "input": return <InputView language={language} profile={activeProfile} preciseInput={preciseInput} canDelete={profiles.length > 1} onChange={updateProfile} onDelete={() => removeProfile(activeProfile.id)} onNavigate={navigate} />;
      case "guide": return <GuideView language={language} />;
      case "visualization": return <Suspense fallback={<div className="loading-view">{copy.loadingVisualization}</div>}><VisualizationView language={language} profiles={profiles} activeProfile={activeProfile} /></Suspense>;
      case "analysis": return <AnalysisView language={language} profile={activeProfile} />;
      case "comparison": return <ComparisonView language={language} profiles={profiles} />;
      case "methodology": return <MethodologyView language={language} />;
      case "atlas": return <Suspense fallback={<div className="loading-view">{copy.loadingAtlas}</div>}><AtlasView language={language} /></Suspense>;
      case "privacy": return <PrivacyView language={language} />;
      case "legal": return <LegalView language={language} />;
      case "about": return <AboutView language={language} />;
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">PS</div><div><strong>Politiscales Analyser</strong><span>{copy.brandSubtitle}</span></div></div>
        <nav aria-label={language === "fr" ? "Vues" : "Views"}>
          {NAV_VIEWS.map((key) => {
            const Icon = viewIcons[key];
            return <button className={view === key ? "nav-button active" : "nav-button"} key={key} onClick={() => navigate(key)} title={copy.views[key]} aria-current={view === key ? "page" : undefined}><Icon size={18} />{copy.views[key]}</button>;
          })}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-settings"><span>{copy.appearance}</span><div className="segmented-control" aria-label={copy.theme}><button className={theme === "dark" ? "active" : ""} onClick={() => setTheme("dark")} title={copy.darkTheme} aria-pressed={theme === "dark"}><Moon size={16} /></button><button className={theme === "light" ? "active" : ""} onClick={() => setTheme("light")} title={copy.lightTheme} aria-pressed={theme === "light"}><Sun size={16} /></button></div></div>
          {view === "input" && <label className="sidebar-toggle"><span><strong>{copy.preciseInput}</strong><small>{copy.preciseInputDetail}</small></span><input type="checkbox" checked={preciseInput} onChange={(event) => setPreciseInput(event.target.checked)} /></label>}
          <button className="language-button" onClick={() => setLanguage(language === "fr" ? "en" : "fr")}><Languages size={17} />{language === "fr" ? "English" : "Français"}</button>
          <span>{SCORING_MODEL_VERSION}</span>
        </div>
      </aside>
      <main>
        <header className="topbar">
          <div className="profile-tabs">{profiles.map((profile, index) => <button className={profile.id === activeId ? "profile-tab active" : "profile-tab"} key={profile.id} onClick={() => navigate(view, profile.id)}><span className="color-dot" style={{ background: PROFILE_COLORS[index % PROFILE_COLORS.length] }} />{profile.name}</button>)}</div>
          <div className="topbar-actions">
            <span className={storageAvailable ? "save-indicator" : "save-indicator error"}>
              {storageAvailable
                ? language === "fr" ? "Enregistré localement" : "Saved locally"
                : language === "fr" ? "Session non persistée" : "Session not persisted"}
            </span>
            <button className="icon-button" onClick={addProfile} title={copy.addProfile}><Plus size={19} /></button>
            <button className="icon-button" onClick={duplicateProfile} title={copy.duplicateProfile}><Copy size={18} /></button>
            <button className="icon-button" disabled={!undoSnapshot} onClick={undo} title={copy.undo}><Undo2 size={18} /></button>
          </div>
        </header>
        <div className="page">
          {renderView()}
          <SiteFooter language={language} onNavigate={navigate} onPrivacyChoices={() => setAdConsent(null)} />
        </div>
      </main>
      {adConsent === null && <CookieConsent language={language} onAccept={() => { applyAdConsent("accepted"); setAdConsent("accepted"); }} onReject={() => { applyAdConsent("rejected"); setAdConsent("rejected"); }} />}
    </div>
  );
}
