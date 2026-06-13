import { useEffect, useMemo, useState } from "react";
import { GitCompareArrows } from "lucide-react";
import { AXES, PROFILE_COLORS, axisLabel } from "../constants";
import { computeProjection, quadrant } from "../scoring";
import type { Language, Profile } from "../types";
import { Metric, PageHeading } from "../components/Common";

export const computeProjectionDispersion = (points: Array<{ x: number; y: number }>): number => {
  if (points.length < 2) return 0;
  const center = points.reduce((sum, point) => ({ x: sum.x + point.x, y: sum.y + point.y }), { x: 0, y: 0 });
  center.x /= points.length;
  center.y /= points.length;
  return Math.sqrt(points.reduce((sum, point) => sum + (point.x - center.x) ** 2 + (point.y - center.y) ** 2, 0) / points.length);
};

export function ComparisonView({ language, profiles }: { language: Language; profiles: Profile[] }) {
  const [leftId, setLeftId] = useState(profiles[0]?.id ?? "");
  const [rightId, setRightId] = useState(profiles[1]?.id ?? profiles[0]?.id ?? "");
  useEffect(() => {
    if (!profiles.some((profile) => profile.id === leftId)) setLeftId(profiles[0]?.id ?? "");
    if (!profiles.some((profile) => profile.id === rightId)) setRightId(profiles[1]?.id ?? profiles[0]?.id ?? "");
  }, [leftId, profiles, rightId]);
  const left = profiles.find((profile) => profile.id === leftId) ?? profiles[0];
  const right = profiles.find((profile) => profile.id === rightId) ?? profiles[1] ?? profiles[0];
  const ranked = useMemo(() => !left || !right ? [] : AXES.map((axis) => ({ axis, delta: Math.abs(left.scores[axis] - right.scores[axis]) })).sort((a, b) => b.delta - a.delta), [left, right]);
  const projections = profiles.map((profile) => ({ profile, projection: computeProjection(profile.scores) }));
  const spread = computeProjectionDispersion(projections.map(({ projection }) => projection));

  if (profiles.length < 2) return <><PageHeading title={language === "fr" ? "Comparaison" : "Comparison"} description={language === "fr" ? "Ajoutez au moins deux profils." : "Add at least two profiles."} /><section className="empty-state"><GitCompareArrows size={28} /><p>{language === "fr" ? "Ajoutez un second profil depuis la barre supérieure." : "Add a second profile from the top bar."}</p></section></>;

  return (
    <>
      <PageHeading title={language === "fr" ? "Comparaison des profils" : "Profile comparison"} description={language === "fr" ? "Sélectionnez une paire, puis examinez ses désaccords et convergences." : "Select a pair, then inspect disagreements and common ground."} />
      <section className="comparison-selector">
        <label>{language === "fr" ? "Profil A" : "Profile A"}<select value={leftId} onChange={(event) => setLeftId(event.target.value)}>{profiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.name}</option>)}</select></label>
        <label>{language === "fr" ? "Profil B" : "Profile B"}<select value={rightId} onChange={(event) => setRightId(event.target.value)}>{profiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.name}</option>)}</select></label>
      </section>
      <div className="comparison-summary">
        <section className="analysis-block"><h2>{language === "fr" ? "Désaccords principaux" : "Largest differences"}</h2><ul>{ranked.slice(0, 4).map(({ axis, delta }) => <li key={axis}>{axisLabel(axis, language)} · {delta} {language === "fr" ? "points" : "points"}</li>)}</ul></section>
        <section className="analysis-block"><h2>{language === "fr" ? "Terrain commun" : "Common ground"}</h2><ul>{[...ranked].reverse().slice(0, 4).map(({ axis, delta }) => <li key={axis}>{axisLabel(axis, language)} · {delta} {language === "fr" ? "point(s) d’écart" : "point(s) apart"}</li>)}</ul></section>
      </div>
      <div className="metric-strip comparison-metrics">
        {projections.map(({ profile, projection }, index) => <div className="metric" key={profile.id}><span><i className="color-dot" style={{ background: PROFILE_COLORS[index % PROFILE_COLORS.length] }} />{profile.name}</span><strong>{projection.x.toFixed(2)}, {projection.y.toFixed(2)}</strong><small>{quadrant(projection.x, projection.y, language)}</small></div>)}
        <Metric label={language === "fr" ? "Dispersion spatiale (RMS)" : "Spatial dispersion (RMS)"} value={spread.toFixed(2)} />
      </div>
      <section className="comparison-table-wrap"><table className="comparison-table"><thead><tr><th>{language === "fr" ? "Axe" : "Axis"}</th>{profiles.map((profile) => <th key={profile.id}>{profile.name}</th>)}<th>{language === "fr" ? "Écart" : "Range"}</th></tr></thead><tbody>{AXES.map((axis) => { const values = profiles.map((profile) => profile.scores[axis]); return <tr key={axis}><td>{axisLabel(axis, language)}</td>{values.map((value, index) => <td key={profiles[index].id}>{value}</td>)}<td>{Math.max(...values) - Math.min(...values)}</td></tr>; })}</tbody></table></section>
    </>
  );
}
