import { ChevronDown, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { PROFILE_COLORS } from "../constants";
import { loadReferenceProfiles } from "../data";
import { computeProjection } from "../scoring";
import type { Language, Profile, ReferenceProfile } from "../types";

type Filters = Record<
  "country" | "ideology_family" | "role_category" | "gender" | "century" | "confidence",
  string[]
>;

const EMPTY_FILTERS: Filters = {
  country: [],
  ideology_family: [],
  role_category: [],
  gender: [],
  century: [],
  confidence: [],
};

export default function VisualizationView({
  language,
  profiles,
}: {
  language: Language;
  profiles: Profile[];
}) {
  const [references, setReferences] = useState<ReferenceProfile[]>([]);
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);

  useEffect(() => {
    let mounted = true;
    void loadReferenceProfiles().then((items) => {
      if (mounted) setReferences(items);
    });
    return () => {
      mounted = false;
    };
  }, []);

  const anyFilter = Object.values(filters).some((values) => values.length > 0);
  const filtered = useMemo(
    () =>
      anyFilter
        ? references.filter((reference) =>
            Object.entries(filters).every(([key, values]) => {
              if (values.length === 0) return true;
              const raw = reference[key as keyof Filters] as string;
              return values.some((value) =>
                raw.split(";").map((item) => item.trim()).includes(value),
              );
            }),
          )
        : [],
    [anyFilter, filters, references],
  );
  const options = (key: keyof Filters) =>
    Array.from(
      new Set(
        references.flatMap((reference) =>
          String(reference[key]).split(";").map((value) => value.trim()).filter(Boolean),
        ),
      ),
    ).sort();
  const profilePoints = profiles.map((profile, index) => ({
    ...computeProjection(profile.scores),
    name: profile.name,
    fill: PROFILE_COLORS[index % PROFILE_COLORS.length],
  }));

  return (
    <>
      <div className="page-heading">
        <h1>{language === "fr" ? "Carte politique" : "Political map"}</h1>
        <p>
          {language === "fr"
            ? "Les references restent masquees tant qu'aucun filtre n'est selectionne."
            : "Reference profiles remain hidden until a filter is selected."}
        </p>
      </div>
      <section className="filter-bar">
        {(Object.keys(filters) as (keyof Filters)[]).map((key) => (
          <MultiFilter
            key={key}
            label={
              {
                country: language === "fr" ? "Pays" : "Countries",
                ideology_family: language === "fr" ? "Familles ideologiques" : "Ideology families",
                role_category: language === "fr" ? "Categories de role" : "Role categories",
                gender: "Gender",
                century: language === "fr" ? "Siecles" : "Centuries",
                confidence: "Confidence",
              }[key]
            }
            options={key === "gender" ? ["male", "female"] : options(key)}
            selected={filters[key]}
            onChange={(selected) => setFilters({ ...filters, [key]: selected })}
          />
        ))}
        <button
          className="icon-button"
          onClick={() => setFilters(EMPTY_FILTERS)}
          title={language === "fr" ? "Vider les filtres" : "Clear filters"}
        >
          <RotateCcw size={18} />
        </button>
      </section>
      <div className="reference-count">
        <strong>{filtered.length} / {references.length || 500}</strong>{" "}
        {language === "fr" ? "profils de reference affiches" : "reference profiles displayed"}
      </div>
      <section className="chart-panel">
        <ResponsiveContainer width="100%" height={600}>
          <ScatterChart margin={{ top: 24, right: 24, bottom: 24, left: 8 }}>
            <CartesianGrid stroke="#d8dee8" strokeDasharray="3 3" />
            <ReferenceArea x1={-4} x2={0} y1={-4} y2={0} fill="#b9e4dc" fillOpacity={0.28} />
            <ReferenceArea x1={0} x2={4} y1={-4} y2={0} fill="#bcd8f4" fillOpacity={0.25} />
            <ReferenceArea x1={-4} x2={0} y1={0} y2={4} fill="#f2d6a2" fillOpacity={0.25} />
            <ReferenceArea x1={0} x2={4} y1={0} y2={4} fill="#efb5ad" fillOpacity={0.22} />
            <ReferenceLine x={0} stroke="#6e7887" />
            <ReferenceLine y={0} stroke="#6e7887" />
            <XAxis type="number" dataKey="x" domain={[-4, 4]} tickCount={9} />
            <YAxis type="number" dataKey="y" domain={[-4, 4]} tickCount={9} />
            <Tooltip content={<ChartTooltip />} />
            <Scatter name="References" data={filtered} fill="#8793a5" opacity={0.58} />
            <Scatter name="Profiles" data={profilePoints} shape="diamond" />
          </ScatterChart>
        </ResponsiveContainer>
      </section>
    </>
  );
}

function MultiFilter({
  label,
  options,
  selected,
  onChange,
}: {
  label: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}) {
  return (
    <details className="multi-filter">
      <summary>
        <span>{label}</span>
        <small>{selected.length || "Any"}</small>
        <ChevronDown size={15} />
      </summary>
      <div className="filter-menu">
        <button onClick={() => onChange([])}>Any / None</button>
        {options.map((option) => (
          <label key={option}>
            <input
              type="checkbox"
              checked={selected.includes(option)}
              onChange={() =>
                onChange(
                  selected.includes(option)
                    ? selected.filter((item) => item !== option)
                    : [...selected, option],
                )
              }
            />
            <span>{option}</span>
          </label>
        ))}
      </div>
    </details>
  );
}

function ChartTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: ReferenceProfile & { fill?: string } }>;
}) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <strong>{point.name}</strong>
      <span>x {Number(point.x).toFixed(2)} · y {Number(point.y).toFixed(2)}</span>
      {point.ideology_family && <span>{point.ideology_family}</span>}
      {point.country && <span>{point.country}</span>}
      {point.role_category && <span>Role: {point.role_category}</span>}
    </div>
  );
}
