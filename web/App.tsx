import {
  Activity,
  BarChart3,
  BookOpen,
  Download,
  GitCompareArrows,
  Languages,
  Plus,
  RotateCcw,
  SlidersHorizontal,
  Trash2,
  Upload,
} from "lucide-react";
import { lazy, Suspense, useRef, useState } from "react";
import { analyzeProfile } from "./analysis";
import {
  AXES,
  AXIS_PAIRS,
  DEFAULT_SCORES,
  PROFILE_COLORS,
  axisLabel,
} from "./constants";
import { computeProjection, quadrant } from "./scoring";
import type {
  AxisKey,
  Language,
  Profile,
  ViewKey,
} from "./types";

const VisualizationView = lazy(() => import("./views/VisualizationView"));

const makeProfile = (index = 1): Profile => ({
  id: crypto.randomUUID(),
  name: `Profil ${index}`,
  scores: { ...DEFAULT_SCORES },
});

const readStoredProfiles = (): Profile[] => {
  try {
    const value = localStorage.getItem("psa.profiles");
    return value ? (JSON.parse(value) as Profile[]) : [makeProfile()];
  } catch {
    return [makeProfile()];
  }
};

const text = {
  fr: {
    input: "Saisie",
    visualization: "Visualisation",
    analysis: "Analyse",
    comparison: "Comparaison",
    methodology: "Methodologie",
    title: "Political Spectrum Analyzer",
    subtitle: "Lecture detaillee de profils Politiscales",
  },
  en: {
    input: "Input",
    visualization: "Visualization",
    analysis: "Analysis",
    comparison: "Comparison",
    methodology: "Methodology",
    title: "Political Spectrum Analyzer",
    subtitle: "Detailed reading of Politiscales profiles",
  },
};

const viewIcons = {
  input: SlidersHorizontal,
  visualization: BarChart3,
  analysis: Activity,
  comparison: GitCompareArrows,
  methodology: BookOpen,
};

function App() {
  const [language, setLanguage] = useState<Language>("fr");
  const [view, setView] = useState<ViewKey>("input");
  const [profiles, setProfilesState] = useState<Profile[]>(readStoredProfiles);
  const [activeId, setActiveId] = useState(profiles[0].id);
  const copy = text[language];

  const setProfiles = (next: Profile[]) => {
    setProfilesState(next);
    localStorage.setItem("psa.profiles", JSON.stringify(next));
  };
  const activeProfile =
    profiles.find((profile) => profile.id === activeId) ?? profiles[0];

  const addProfile = () => {
    const profile = makeProfile(profiles.length + 1);
    setProfiles([...profiles, profile]);
    setActiveId(profile.id);
  };
  const removeProfile = (id: string) => {
    if (profiles.length === 1) return;
    const next = profiles.filter((profile) => profile.id !== id);
    setProfiles(next);
    if (id === activeId) setActiveId(next[0].id);
  };
  const updateProfile = (next: Profile) =>
    setProfiles(
      profiles.map((profile) => (profile.id === next.id ? next : profile)),
    );

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">PS</div>
          <div>
            <strong>{copy.title}</strong>
            <span>{copy.subtitle}</span>
          </div>
        </div>
        <nav aria-label={language === "fr" ? "Vues" : "Views"}>
          {(Object.keys(viewIcons) as ViewKey[]).map((key) => {
            const Icon = viewIcons[key];
            return (
              <button
                className={view === key ? "nav-button active" : "nav-button"}
                key={key}
                onClick={() => setView(key)}
              >
                <Icon size={18} />
                {copy[key]}
              </button>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <button
            className="language-button"
            onClick={() => setLanguage(language === "fr" ? "en" : "fr")}
          >
            <Languages size={17} />
            {language === "fr" ? "English" : "Francais"}
          </button>
          <span>Scoring model V2</span>
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div className="profile-tabs">
            {profiles.map((profile, index) => (
              <button
                className={profile.id === activeId ? "profile-tab active" : "profile-tab"}
                key={profile.id}
                onClick={() => setActiveId(profile.id)}
              >
                <span
                  className="color-dot"
                  style={{ background: PROFILE_COLORS[index % PROFILE_COLORS.length] }}
                />
                {profile.name}
              </button>
            ))}
          </div>
          <button className="icon-button" onClick={addProfile} title={language === "fr" ? "Ajouter un profil" : "Add profile"}>
            <Plus size={19} />
          </button>
        </header>

        <div className="page">
          {view === "input" && (
            <InputView
              language={language}
              profile={activeProfile}
              canDelete={profiles.length > 1}
              onChange={updateProfile}
              onDelete={() => removeProfile(activeProfile.id)}
            />
          )}
          {view === "visualization" && (
            <Suspense fallback={<div className="loading-view">Chargement de la visualisation...</div>}>
              <VisualizationView language={language} profiles={profiles} />
            </Suspense>
          )}
          {view === "analysis" && (
            <AnalysisView language={language} profile={activeProfile} />
          )}
          {view === "comparison" && (
            <ComparisonView language={language} profiles={profiles} />
          )}
          {view === "methodology" && <MethodologyView language={language} />}
        </div>
      </main>
    </div>
  );
}

function PageHeading({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="page-heading">
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
  );
}

function InputView({
  language,
  profile,
  canDelete,
  onChange,
  onDelete,
}: {
  language: Language;
  profile: Profile;
  canDelete: boolean;
  onChange: (profile: Profile) => void;
  onDelete: () => void;
}) {
  const fileInput = useRef<HTMLInputElement>(null);
  const projection = computeProjection(profile.scores);
  const updateScore = (axis: AxisKey, value: number) =>
    onChange({
      ...profile,
      scores: { ...profile.scores, [axis]: value },
    });
  const reset = () => onChange({ ...profile, scores: { ...DEFAULT_SCORES } });
  const exportProfile = () => {
    const payload = {
      schema: "political_spectrum_profile.v1",
      saved_at: new Date().toISOString(),
      name: profile.name,
      scores: profile.scores,
    };
    download(
      JSON.stringify(payload, null, 2),
      `${slug(profile.name)}.json`,
      "application/json",
    );
  };
  const importProfile = async (file: File) => {
    const payload = JSON.parse(await file.text()) as {
      name?: string;
      scores?: Partial<Profile["scores"]>;
    };
    if (!payload.scores) return;
    onChange({
      ...profile,
      name: payload.name || profile.name,
      scores: { ...DEFAULT_SCORES, ...payload.scores },
    });
  };

  return (
    <>
      <PageHeading
        title={language === "fr" ? "Saisie du profil" : "Profile input"}
        description={
          language === "fr"
            ? "Ajustez les 16 scores. Les donnees restent dans votre navigateur."
            : "Adjust the 16 scores. Data remains in your browser."
        }
      />
      <section className="toolbar">
        <label className="name-field">
          <span>{language === "fr" ? "Nom du profil" : "Profile name"}</span>
          <input
            value={profile.name}
            onChange={(event) => onChange({ ...profile, name: event.target.value })}
          />
        </label>
        <div className="toolbar-actions">
          <input
            hidden
            ref={fileInput}
            type="file"
            accept=".json,application/json"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) void importProfile(file);
            }}
          />
          <button className="secondary-button" onClick={() => fileInput.current?.click()}>
            <Upload size={17} /> {language === "fr" ? "Importer" : "Import"}
          </button>
          <button className="secondary-button" onClick={exportProfile}>
            <Download size={17} /> {language === "fr" ? "Exporter" : "Export"}
          </button>
          <button className="icon-button" onClick={reset} title={language === "fr" ? "Reinitialiser" : "Reset"}>
            <RotateCcw size={18} />
          </button>
          <button className="icon-button danger" disabled={!canDelete} onClick={onDelete} title={language === "fr" ? "Supprimer" : "Delete"}>
            <Trash2 size={18} />
          </button>
        </div>
      </section>

      <div className="metric-strip">
        <Metric label="X" value={projection.x.toFixed(2)} />
        <Metric label="Y" value={projection.y.toFixed(2)} />
        <Metric label={language === "fr" ? "Quadrant" : "Quadrant"} value={quadrant(projection.x, projection.y, language)} />
        <Metric label={language === "fr" ? "Distance au centre" : "Distance to center"} value={Math.hypot(projection.x, projection.y).toFixed(2)} />
      </div>

      <div className="score-sections">
        {(["society", "economy", "strategy"] as const).map((group) => (
          <section className="score-section" key={group}>
            <h2>
              {group === "society"
                ? language === "fr" ? "Societe et autorite" : "Society and authority"
                : group === "economy"
                  ? language === "fr" ? "Economie" : "Economy"
                  : language === "fr" ? "Strategie de changement" : "Change strategy"}
            </h2>
            <div className="score-grid">
              {AXIS_PAIRS.filter((pair) => pair.group === group).flatMap(({ left, right }) =>
                [left, right].map((axis) => (
                  <ScoreControl
                    axis={axis}
                    key={axis}
                    language={language}
                    value={profile.scores[axis]}
                    onChange={(value) => updateScore(axis, value)}
                  />
                )),
              )}
            </div>
          </section>
        ))}
      </div>
    </>
  );
}

function ScoreControl({
  axis,
  language,
  value,
  onChange,
}: {
  axis: AxisKey;
  language: Language;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="score-control">
      <span>{axisLabel(axis, language)}</span>
      <output>{value}</output>
      <input
        type="range"
        min="0"
        max="100"
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function AnalysisView({
  language,
  profile,
}: {
  language: Language;
  profile: Profile;
}) {
  const result = analyzeProfile(profile, language);
  return (
    <>
      <PageHeading
        title={language === "fr" ? `Analyse de ${profile.name}` : `${profile.name} analysis`}
        description={language === "fr" ? "Lecture personnalisee des 16 axes et de leurs interactions." : "Personalized reading of all 16 axes and their interactions."}
      />
      <section className="analysis-lead">
        <h2>{language === "fr" ? "Lecture personnalisee" : "Personalized profile reading"}</h2>
        <p>{result.summary}</p>
      </section>
      <div className="analysis-grid">
        <AnalysisBlock title={language === "fr" ? "Points saillants" : "Profile highlights"}>
          <ul>{result.highlights.map((item) => <li key={item}>{item}</li>)}</ul>
        </AnalysisBlock>
        <AnalysisBlock title={language === "fr" ? "Axes dominants" : "Dominant axes"}>
          <AxisList axes={result.dominant} profile={profile} language={language} />
        </AnalysisBlock>
        <AnalysisBlock title={language === "fr" ? "Axes les plus faibles" : "Weakest axes"}>
          <AxisList axes={result.weakest} profile={profile} language={language} />
        </AnalysisBlock>
        <AnalysisBlock title={language === "fr" ? "Tensions internes" : "Internal tensions"}>
          {result.tensions.length ? (
            <ul>{result.tensions.map((item) => <li key={item}>{item}</li>)}</ul>
          ) : (
            <p>{language === "fr" ? "Aucune tension forte detectee selon les seuils du modele." : "No strong tension detected under the model thresholds."}</p>
          )}
        </AnalysisBlock>
      </div>
      <AnalysisBlock title={language === "fr" ? "Equilibre axe par axe" : "Axis-by-axis balance"}>
        <div className="balance-list">
          {result.balances.map((balance) => (
            <div className="balance-row" key={balance.left}>
              <span>{axisLabel(balance.left, language)}</span>
              <div className="balance-track">
                <div style={{ width: `${profile.scores[balance.left]}%` }} />
                <i style={{ left: `${profile.scores[balance.left]}%` }} />
              </div>
              <span>{axisLabel(balance.right, language)}</span>
              <strong>{balance.delta > 0 ? "+" : ""}{balance.delta}</strong>
            </div>
          ))}
        </div>
      </AnalysisBlock>
      <AnalysisBlock title={language === "fr" ? "Lecture score par score" : "Score-by-score reading"}>
        <div className="score-notes">
          {result.scoreNotes.map(({ axis, score, note }) => (
            <div key={axis}><strong>{axisLabel(axis, language)}</strong><span>{score}/100 · {note}</span></div>
          ))}
        </div>
      </AnalysisBlock>
    </>
  );
}

function AnalysisBlock({ title, children }: { title: string; children: React.ReactNode }) {
  return <section className="analysis-block"><h2>{title}</h2>{children}</section>;
}

function AxisList({ axes, profile, language }: { axes: AxisKey[]; profile: Profile; language: Language }) {
  return <div className="axis-list">{axes.map((axis) => <div key={axis}><span>{axisLabel(axis, language)}</span><strong>{profile.scores[axis]}</strong></div>)}</div>;
}

function ComparisonView({ language, profiles }: { language: Language; profiles: Profile[] }) {
  const projections = profiles.map((profile) => ({ profile, projection: computeProjection(profile.scores) }));
  const spread = profiles.length > 1
    ? Math.max(...projections.flatMap(({ projection }) => [projection.x, projection.y])) -
      Math.min(...projections.flatMap(({ projection }) => [projection.x, projection.y]))
    : 0;
  return (
    <>
      <PageHeading
        title={language === "fr" ? "Comparaison des profils" : "Profile comparison"}
        description={language === "fr" ? "Compare les positions globales et les ecarts sur chaque axe." : "Compare global positions and per-axis differences."}
      />
      {profiles.length < 2 ? (
        <section className="empty-state"><GitCompareArrows size={28} /><p>{language === "fr" ? "Ajoutez un second profil depuis la barre superieure." : "Add a second profile from the top bar."}</p></section>
      ) : (
        <>
          <div className="metric-strip comparison-metrics">
            {projections.map(({ profile, projection }, index) => (
              <div className="metric" key={profile.id}>
                <span><i className="color-dot" style={{ background: PROFILE_COLORS[index % PROFILE_COLORS.length] }} />{profile.name}</span>
                <strong>{projection.x.toFixed(2)}, {projection.y.toFixed(2)}</strong>
                <small>{quadrant(projection.x, projection.y, language)}</small>
              </div>
            ))}
            <Metric label={language === "fr" ? "Dispersion globale" : "Overall spread"} value={spread.toFixed(2)} />
          </div>
          <section className="comparison-table-wrap">
            <table className="comparison-table">
              <thead><tr><th>{language === "fr" ? "Axe" : "Axis"}</th>{profiles.map((profile) => <th key={profile.id}>{profile.name}</th>)}<th>{language === "fr" ? "Ecart" : "Range"}</th></tr></thead>
              <tbody>{AXES.map((axis) => {
                const values = profiles.map((profile) => profile.scores[axis]);
                return <tr key={axis}><td>{axisLabel(axis, language)}</td>{values.map((value, index) => <td key={profiles[index].id}>{value}</td>)}<td>{Math.max(...values) - Math.min(...values)}</td></tr>;
              })}</tbody>
            </table>
          </section>
        </>
      )}
    </>
  );
}

function MethodologyView({ language }: { language: Language }) {
  return (
    <>
      <PageHeading
        title={language === "fr" ? "Methodologie" : "Methodology"}
        description={language === "fr" ? "Formule V2 actuellement utilisee pour la projection x/y." : "Current V2 formula used for the x/y projection."}
      />
      <section className="methodology">
        <h2>{language === "fr" ? "Principe" : "Principle"}</h2>
        <p>{language === "fr" ? "La carte est une projection synthetique. L'analyse detaillee conserve les 16 scores et ne doit pas etre reduite au quadrant." : "The map is a synthetic projection. Detailed analysis retains all 16 scores and should not be reduced to the quadrant."}</p>
        <div className="formula-grid">
          <pre>{`economic_left =
  0.90 * communisme
  + 0.70 * regulation
  + 0.35 * ecologie
  + 0.25 * revolution`}</pre>
          <pre>{`economic_right =
  0.90 * capitalisme
  + 0.75 * laissez_faire
  + 0.25 * productivisme
  + 0.20 * reformisme`}</pre>
          <pre>{`social_libertarian =
  0.70 * constructivisme
  + 0.65 * justice_rehabilitative
  + 0.70 * progressisme
  + 0.50 * internationalisme`}</pre>
          <pre>{`social_authoritarian =
  0.60 * essentialisme
  + 0.70 * justice_punitive
  + 0.70 * conservatisme
  + 0.50 * nationalisme`}</pre>
        </div>
        <pre>{`economic_raw = economic_right - economic_left
  + 0.12 * (productivisme - ecologie)

social_raw = social_authoritarian - social_libertarian
  + 0.10 * (nationalisme - internationalisme)
  + 0.08 * (revolution - reformisme)

x = 4 * sigmoid_scaled(economic_raw / 120)
y = 4 * sigmoid_scaled(social_raw / 120)`}</pre>
        <h2>{language === "fr" ? "Limites" : "Limitations"}</h2>
        <p>{language === "fr" ? "Les coordonnees des personnalites sont des estimations documentaires, non des mesures scientifiques. Les filtres exposent le champ role_category du dataset, jamais display_group." : "Reference coordinates are documented estimates, not scientific measurements. Filters expose the dataset's role_category field, never display_group."}</p>
      </section>
    </>
  );
}

const slug = (value: string) =>
  value.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "profile";

const download = (content: string, filename: string, type: string) => {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
};

export default App;
