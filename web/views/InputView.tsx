import { useRef, useState } from "react";
import {
  ArrowRight,
  BarChart3,
  Download,
  RotateCcw,
  Trash2,
  Upload,
} from "lucide-react";
import { AXIS_PAIRS, DEFAULT_SCORES, axisLabel } from "../constants";
import { computeProjection, quadrant } from "../scoring";
import { parseImportedProfile } from "../profile-data";
import type { AxisKey, Language, Profile, ViewKey } from "../types";
import { Metric, PageHeading } from "../components/Common";

interface InputViewProps {
  language: Language;
  profile: Profile;
  preciseInput: boolean;
  canDelete: boolean;
  onChange: (profile: Profile) => void;
  onDelete: () => void;
  onNavigate: (view: ViewKey) => void;
}

export function InputView({
  language,
  profile,
  preciseInput,
  canDelete,
  onChange,
  onDelete,
  onNavigate,
}: InputViewProps) {
  const fileInput = useRef<HTMLInputElement>(null);
  const [importError, setImportError] = useState("");
  const projection = computeProjection(profile.scores);
  const updateScore = (axis: AxisKey, value: number) =>
    onChange({ ...profile, scores: { ...profile.scores, [axis]: value } });
  const reset = () => onChange({ ...profile, scores: { ...DEFAULT_SCORES } });

  const exportProfile = () => {
    const content = JSON.stringify({
      schema: "political_spectrum_profile.v2",
      saved_at: new Date().toISOString(),
      name: profile.name,
      modelVersion: profile.modelVersion,
      scores: profile.scores,
    }, null, 2);
    const url = URL.createObjectURL(new Blob([content], { type: "application/json" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${slug(profile.name)}.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const importProfile = async (file: File) => {
    try {
      onChange(parseImportedProfile(await file.text(), profile));
      setImportError("");
    } catch (error) {
      setImportError(error instanceof Error ? error.message : language === "fr" ? "Import impossible." : "Import failed.");
    }
  };

  return (
    <>
      <PageHeading
        title={language === "fr" ? "Saisie du profil" : "Profile input"}
        description={language === "fr" ? "Ajustez les 16 scores. Chaque modification reste enregistrée dans ce navigateur." : "Adjust all 16 scores. Each change remains stored in this browser."}
      />
      <section className="toolbar">
        <label className="name-field">
          <span>{language === "fr" ? "Nom du profil" : "Profile name"}</span>
          <input value={profile.name} onChange={(event) => onChange({ ...profile, name: event.target.value })} />
        </label>
        <div className="toolbar-actions">
          <input hidden ref={fileInput} type="file" accept=".json,application/json" onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void importProfile(file);
            event.target.value = "";
          }} />
          <button className="secondary-button" onClick={() => fileInput.current?.click()}><Upload size={17} />{language === "fr" ? "Importer" : "Import"}</button>
          <button className="secondary-button" onClick={exportProfile}><Download size={17} />{language === "fr" ? "Exporter" : "Export"}</button>
          <button className="icon-button" onClick={reset} title={language === "fr" ? "Réinitialiser" : "Reset"}><RotateCcw size={18} /></button>
          <button className="icon-button danger" disabled={!canDelete} onClick={onDelete} title={language === "fr" ? "Supprimer" : "Delete"}><Trash2 size={18} /></button>
        </div>
      </section>
      {importError && <div className="inline-alert" role="alert">{importError}</div>}
      <div className="metric-strip">
        <Metric label="X" value={projection.x.toFixed(2)} />
        <Metric label="Y" value={projection.y.toFixed(2)} />
        <Metric label="Quadrant" value={quadrant(projection.x, projection.y, language)} />
        <Metric label={language === "fr" ? "Distance au centre" : "Distance to center"} value={Math.hypot(projection.x, projection.y).toFixed(2)} />
      </div>
      <div className="score-sections">
        {(["society", "economy", "strategy"] as const).map((group) => (
          <section className="score-section" key={group}>
            <h2>{group === "society" ? language === "fr" ? "Société et autorité" : "Society and authority" : group === "economy" ? language === "fr" ? "Économie" : "Economy" : language === "fr" ? "Stratégie de changement" : "Change strategy"}</h2>
            <div className="score-grid">
              {AXIS_PAIRS.filter((pair) => pair.group === group).flatMap(({ left, right }) =>
                [left, right].map((axis) => (
                  <ScoreControl key={axis} axis={axis} language={language} value={profile.scores[axis]} precise={preciseInput} onChange={(value) => updateScore(axis, value)} />
                )),
              )}
            </div>
          </section>
        ))}
      </div>
      <section className="input-next-actions">
        <div><strong>{language === "fr" ? "Votre profil est prêt" : "Your profile is ready"}</strong><p>{language === "fr" ? "Examinez sa position ou ouvrez la lecture détaillée." : "Inspect its position or open the detailed reading."}</p></div>
        <div>
          <button className="ghost-action" onClick={() => onNavigate("visualization")}><BarChart3 size={18} />{language === "fr" ? "Se rendre à la visualisation" : "Go to visualization"}</button>
          <button className="primary-action" onClick={() => onNavigate("analysis")}>{language === "fr" ? "Se rendre à l’analyse" : "Go to analysis"}<ArrowRight size={18} /></button>
        </div>
      </section>
    </>
  );
}

function ScoreControl({
  axis,
  language,
  value,
  precise,
  onChange,
}: {
  axis: AxisKey;
  language: Language;
  value: number;
  precise: boolean;
  onChange: (value: number) => void;
}) {
  const id = `score-${axis}`;
  return (
    <div className="score-control">
      <label htmlFor={id}>{axisLabel(axis, language)}</label>
      <output htmlFor={id}>{value}</output>
      <input
        id={id}
        aria-label={axisLabel(axis, language)}
        className={precise ? "score-number" : undefined}
        type={precise ? "number" : "range"}
        min="0"
        max="100"
        value={value}
        onChange={(event) => onChange(Math.max(0, Math.min(100, Number(event.target.value))))}
      />
    </div>
  );
}

const slug = (value: string) =>
  value.trim().toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "profile";
