import { useState } from "react";
import { analyzeProfile } from "../analysis";
import { AXES, axisLabel } from "../constants";
import { computeAxisContributions, computeProjection } from "../scoring";
import type { AxisKey, Language, Profile } from "../types";
import { AnalysisBlock, Metric, PageHeading } from "../components/Common";

export function AnalysisView({ language, profile }: { language: Language; profile: Profile }) {
  const result = analyzeProfile(profile, language);
  const contributions = computeAxisContributions(profile.scores);
  const [simulatedAxis, setSimulatedAxis] = useState<AxisKey>("capitalisme");
  const [simulatedValue, setSimulatedValue] = useState(profile.scores.capitalisme);
  const currentProjection = computeProjection(profile.scores);
  const simulatedProjection = computeProjection({
    ...profile.scores,
    [simulatedAxis]: simulatedValue,
  });
  return (
    <>
      <PageHeading title={language === "fr" ? `Analyse de ${profile.name}` : `${profile.name} analysis`} description={language === "fr" ? "Lecture heuristique explicable des 16 axes, de leurs interactions et de leurs limites." : "Explainable heuristic reading of all 16 axes, their interactions, and limitations."} />
      <section className="analysis-lead">
        <span className="analysis-archetype">{result.archetype}</span>
        <h2>{language === "fr" ? "Lecture personnalisée du profil" : "Personalized profile reading"}</h2>
        <p>{result.summary}</p>
        <div className="interpretation-confidence">
          <strong>{result.interpretabilityLabel} · {result.interpretabilityScore.toFixed(1)}/100</strong>
          <span>{language === "fr" ? "Cette lecture est heuristique. Cet indicateur mesure la lisibilité des scores, pas une confiance statistique ni une certitude politique." : "This reading is heuristic. The indicator measures score readability, not statistical confidence or political certainty."}</span>
        </div>
      </section>
      <div className="metric-strip analysis-diagnostics">
        <Metric label={language === "fr" ? "Intensité" : "Intensity"} value={`${result.intensityScore.toFixed(1)}/100`} />
        <Metric label={language === "fr" ? "Clarté directionnelle" : "Directional clarity"} value={`${result.coherenceScore.toFixed(1)}/100`} />
        <div className="metric metric-wide"><span>{language === "fr" ? "Centre de gravité" : "Center of gravity"}</span><strong>{result.centerOfGravity}</strong></div>
      </div>
      <details className="analysis-disclosure" open>
        <summary>{language === "fr" ? "Lectures économique, sociétale et stratégique" : "Economic, societal, and strategic readings"}</summary>
        <div className="analysis-reading-grid">
          <AnalysisBlock title={language === "fr" ? "Économie" : "Economy"}><p>{result.economicReading}</p></AnalysisBlock>
          <AnalysisBlock title={language === "fr" ? "Société" : "Society"}><p>{result.societalReading}</p></AnalysisBlock>
          <AnalysisBlock title={language === "fr" ? "Stratégie" : "Strategy"}><p>{result.strategicReading}</p></AnalysisBlock>
        </div>
      </details>
      <details className="analysis-disclosure">
        <summary>{language === "fr" ? "Diagnostics, moteurs et contre-signaux" : "Diagnostics, drivers, and counter-signals"}</summary>
        <div className="analysis-grid">
          <AnalysisBlock title={language === "fr" ? "Diagnostics" : "Diagnostics"}><ul>{result.diagnosticNotes.map((item) => <li key={item}>{item}</li>)}</ul></AnalysisBlock>
          <AnalysisBlock title={language === "fr" ? "Points saillants" : "Highlights"}><ul>{result.highlights.map((item) => <li key={item}>{item}</li>)}</ul></AnalysisBlock>
          <AnalysisBlock title={language === "fr" ? "Axes dominants" : "Dominant axes"}><AxisList axes={result.dominant} profile={profile} language={language} emptyText={language === "fr" ? "Aucun axe au-dessus de 60/100." : "No axis above 60/100."} /></AnalysisBlock>
          <AnalysisBlock title={language === "fr" ? "Contre-signaux faibles" : "Weak counter-signals"}><AxisList axes={result.weakest} profile={profile} language={language} emptyText={language === "fr" ? "Aucun axe sous 35/100." : "No axis below 35/100."} /></AnalysisBlock>
          <AnalysisBlock title={language === "fr" ? "Tensions internes" : "Internal tensions"}>{result.tensions.length ? <ul>{result.tensions.map((item) => <li key={item}>{item}</li>)}</ul> : <p>{language === "fr" ? "Aucune tension forte selon les seuils du modèle." : "No strong tension under the model thresholds."}</p>}</AnalysisBlock>
        </div>
      </details>
      <details className="analysis-disclosure">
        <summary>{language === "fr" ? "Pourquoi cette position x/y ?" : "Why this x/y position?"}</summary>
        <PositionExplanation profile={profile} contributions={contributions} language={language} />
      </details>
      <details className="analysis-disclosure">
        <summary>{language === "fr" ? "Simulateur de sensibilité" : "Sensitivity simulator"}</summary>
        <section className="analysis-block disclosure-block sensitivity-tool">
          <p>{language === "fr" ? "Modifiez virtuellement un score pour voir son effet isolé. Le profil enregistré n’est pas modifié." : "Virtually change one score to inspect its isolated effect. The saved profile is not modified."}</p>
          <label>
            <span>{language === "fr" ? "Axe simulé" : "Simulated axis"}</span>
            <select value={simulatedAxis} onChange={(event) => {
              const axis = event.target.value as AxisKey;
              setSimulatedAxis(axis);
              setSimulatedValue(profile.scores[axis]);
            }}>
              {AXES.map((axis) => <option key={axis} value={axis}>{axisLabel(axis, language)}</option>)}
            </select>
          </label>
          <label>
            <span>{axisLabel(simulatedAxis, language)} · {simulatedValue}/100</span>
            <input type="range" min="0" max="100" value={simulatedValue} onChange={(event) => setSimulatedValue(Number(event.target.value))} />
          </label>
          <div className="sensitivity-results">
            <Metric label="Δ x" value={(simulatedProjection.x - currentProjection.x).toFixed(3)} />
            <Metric label="Δ y" value={(simulatedProjection.y - currentProjection.y).toFixed(3)} />
          </div>
        </section>
      </details>
      <details className="analysis-disclosure">
        <summary>{language === "fr" ? "Équilibre axe par axe" : "Axis-by-axis balance"}</summary>
        <section className="analysis-block disclosure-block"><div className="balance-list">{result.balances.map((balance) => <div className="balance-entry" key={balance.left}><div className="balance-row"><span>{axisLabel(balance.left, language)}</span><div className="balance-track"><div style={{ width: `${profile.scores[balance.left]}%` }} /><i style={{ left: `${profile.scores[balance.left]}%` }} /></div><span>{axisLabel(balance.right, language)}</span><strong>{balance.delta > 0 ? "+" : ""}{balance.delta}</strong></div><p><strong>{balance.leadingSide}</strong> · {balance.reading}</p></div>)}</div></section>
      </details>
      <details className="analysis-disclosure">
        <summary>{language === "fr" ? "Lecture score par score" : "Score-by-score reading"}</summary>
        <section className="analysis-block disclosure-block"><div className="score-notes">{result.scoreNotes.map(({ axis, score, level, note }) => <div key={axis}><strong>{axisLabel(axis, language)}</strong><span>{score}/100 · {level}</span><p>{note}</p></div>)}</div></section>
      </details>
    </>
  );
}

function AxisList({ axes, profile, language, emptyText }: { axes: AxisKey[]; profile: Profile; language: Language; emptyText: string }) {
  if (!axes.length) return <p className="muted-empty">{emptyText}</p>;
  return <div className="axis-list">{axes.map((axis) => <div key={axis}><span>{axisLabel(axis, language)}</span><strong>{profile.scores[axis]}</strong></div>)}</div>;
}

function PositionExplanation({ profile, contributions, language }: { profile: Profile; contributions: ReturnType<typeof computeAxisContributions>; language: Language }) {
  const relevant = contributions.filter(({ xWeight, yWeight }) => xWeight !== 0 || yWeight !== 0);
  return (
    <section className="analysis-block disclosure-block">
      <p>{language === "fr" ? "Contributions brutes exactes avant normalisation sigmoïde. Les poids proviennent de la configuration versionnée du modèle." : "Exact raw contributions before sigmoid normalization. Weights come from the versioned model configuration."}</p>
      <div className="contribution-table-wrap"><table className="contribution-table"><thead><tr><th>{language === "fr" ? "Axe" : "Axis"}</th><th>Score</th><th>{language === "fr" ? "Poids x" : "x weight"}</th><th>{language === "fr" ? "Contribution x" : "x contribution"}</th><th>{language === "fr" ? "Poids y" : "y weight"}</th><th>{language === "fr" ? "Contribution y" : "y contribution"}</th></tr></thead><tbody>{relevant.map((row) => <tr key={row.axis}><td>{axisLabel(row.axis, language)}</td><td>{profile.scores[row.axis]}</td><td>{row.xWeight ? row.xWeight.toFixed(2) : "—"}</td><td className={row.xContribution > 0 ? "positive" : row.xContribution < 0 ? "negative" : ""}>{row.xContribution ? row.xContribution.toFixed(2) : "—"}</td><td>{row.yWeight ? row.yWeight.toFixed(2) : "—"}</td><td className={row.yContribution > 0 ? "positive" : row.yContribution < 0 ? "negative" : ""}>{row.yContribution ? row.yContribution.toFixed(2) : "—"}</td></tr>)}</tbody></table></div>
    </section>
  );
}
