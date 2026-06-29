import {
  ChevronDown,
  Download,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  RotateCcw,
  Search,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { toPng } from "html-to-image";
import { useEffect, useMemo, useRef, useState } from "react";
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

export type Filters = Record<
  "country" | "ideology_family" | "role_category" | "gender" | "century" | "confidence",
  string[]
>;

export const ANY_FILTER = "__ANY__";
const FILTER_STORAGE_KEY = "psa.referenceFilters.v2";

export const EMPTY_FILTERS: Filters = {
  country: [],
  ideology_family: [],
  role_category: [],
  gender: [],
  century: [],
  confidence: [],
};

const readStoredFilters = (): Filters => {
  try {
    const parsed: unknown = JSON.parse(
      localStorage.getItem(FILTER_STORAGE_KEY) ?? "{}",
    );
    if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
      return EMPTY_FILTERS;
    }
    return Object.fromEntries(
      (Object.keys(EMPTY_FILTERS) as (keyof Filters)[]).map((key) => {
        const value = (parsed as Record<string, unknown>)[key];
        return [
          key,
          Array.isArray(value)
            ? value.filter((item): item is string => typeof item === "string")
            : [],
        ];
      }),
    ) as Filters;
  } catch {
    return EMPTY_FILTERS;
  }
};

export interface NearestReference {
  reference: ReferenceProfile;
  distance: number;
}

export const findNearestReferences = (
  references: ReferenceProfile[],
  profile: Profile,
  limit = 3,
): NearestReference[] => {
  const projection = computeProjection(profile.scores);
  return references
    .map((reference) => ({
      reference,
      distance: Math.hypot(reference.x - projection.x, reference.y - projection.y),
    }))
    .sort(
      (left, right) =>
        left.distance - right.distance ||
        left.reference.name.localeCompare(right.reference.name),
    )
    .slice(0, limit);
};

export const filterReferenceProfiles = (
  references: ReferenceProfile[],
  filters: Filters,
): ReferenceProfile[] => {
  const hasSelection = Object.values(filters).some((values) => values.length > 0);
  if (!hasSelection) return [];

  return references.filter((reference) =>
    Object.entries(filters).every(([key, values]) => {
      if (values.length === 0 || values.includes(ANY_FILTER)) return true;
      const raw = reference[key as keyof Filters] as string;
      return values.some((value) =>
        raw.split(";").map((item) => item.trim()).includes(value),
      );
    }),
  );
};

const safeFilename = (value: string): string =>
  value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .toLowerCase() || "profile";

export default function VisualizationView({
  language,
  profiles,
  activeProfile,
}: {
  language: Language;
  profiles: Profile[];
  activeProfile: Profile;
}) {
  const [references, setReferences] = useState<ReferenceProfile[]>([]);
  const [loadError, setLoadError] = useState("");
  const [exportError, setExportError] = useState("");
  const [exporting, setExporting] = useState(false);
  const [filters, setFilters] = useState<Filters>(readStoredFilters);
  const [openFilter, setOpenFilter] = useState<keyof Filters | null>(null);
  const [showReferenceLabels, setShowReferenceLabels] = useState(
    () => localStorage.getItem("psa.showReferenceLabels") !== "false",
  );
  const [referenceQuery, setReferenceQuery] = useState("");
  const [selectedReference, setSelectedReference] = useState<ReferenceProfile | null>(null);
  const [xDomain, setXDomain] = useState<[number, number]>([-4, 4]);
  const [yDomain, setYDomain] = useState<[number, number]>([-4, 4]);
  const filtersRef = useRef<HTMLElement>(null);
  const exportRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let mounted = true;
    void loadReferenceProfiles()
      .then((items) => {
        if (mounted) {
          setReferences(items);
          setLoadError("");
        }
      })
      .catch((error) => {
        if (mounted) {
          setReferences([]);
          setLoadError(
            error instanceof Error
              ? error.message
              : "Impossible de charger le dataset de référence.",
          );
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(filters));
  }, [filters]);

  useEffect(() => {
    localStorage.setItem("psa.showReferenceLabels", String(showReferenceLabels));
  }, [showReferenceLabels]);

  useEffect(() => {
    if (!openFilter) return;
    const closeOnOutsideClick = (event: PointerEvent) => {
      const target = event.target;
      if (!(target instanceof Node)) return;
      const activeFilter = filtersRef.current?.querySelector(
        `details[data-filter="${openFilter}"]`,
      );
      if (activeFilter && !activeFilter.contains(target)) {
        setOpenFilter(null);
      }
    };
    document.addEventListener("pointerdown", closeOnOutsideClick);
    return () => document.removeEventListener("pointerdown", closeOnOutsideClick);
  }, [openFilter]);

  const filtered = useMemo(
    () => filterReferenceProfiles(references, filters),
    [filters, references],
  );
  const nearest = useMemo(
    () => findNearestReferences(filtered, activeProfile),
    [activeProfile, filtered],
  );
  const activeFilterLabels = Object.entries(filters)
    .filter(([, values]) => values.length > 0 && !values.includes(ANY_FILTER))
    .map(([key, values]) => `${key}: ${values.join(", ")}`);
  const filterSummary =
    activeFilterLabels.length > 0
      ? activeFilterLabels.join(" · ")
      : Object.values(filters).some((values) => values.includes(ANY_FILTER))
        ? language === "fr"
          ? "Toutes les références"
          : "All references"
        : language === "fr"
          ? "Aucune référence sélectionnée"
          : "No references selected";
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
  const inspectReference = () => {
    const normalized = referenceQuery.trim().toLocaleLowerCase();
    const match = references.find(
      (reference) => reference.name.toLocaleLowerCase() === normalized,
    );
    setSelectedReference(match ?? null);
    if (match) {
      const radius = Math.max(0.75, (xDomain[1] - xDomain[0]) / 4);
      const xCenter = Math.max(-4 + radius, Math.min(4 - radius, match.x));
      const yCenter = Math.max(-4 + radius, Math.min(4 - radius, match.y));
      setXDomain([xCenter - radius, xCenter + radius]);
      setYDomain([yCenter - radius, yCenter + radius]);
    }
  };
  const zoom = (factor: number) => {
    const resize = ([minimum, maximum]: [number, number]): [number, number] => {
      const center = (minimum + maximum) / 2;
      const radius = Math.max(0.5, Math.min(4, ((maximum - minimum) / 2) * factor));
      return [Math.max(-4, center - radius), Math.min(4, center + radius)];
    };
    setXDomain(resize);
    setYDomain(resize);
  };
  const pan = (xDirection: number, yDirection: number) => {
    const shift = (xDomain[1] - xDomain[0]) * 0.2;
    const move = ([minimum, maximum]: [number, number], direction: number): [number, number] => {
      const delta = shift * direction;
      if (minimum + delta < -4 || maximum + delta > 4) return [minimum, maximum];
      return [minimum + delta, maximum + delta];
    };
    setXDomain((value) => move(value, xDirection));
    setYDomain((value) => move(value, yDirection));
  };
  const exportVisualization = async () => {
    if (!exportRef.current || exporting) return;
    setExporting(true);
    setExportError("");
    try {
      const backgroundColor =
        document.documentElement.dataset.theme === "light" ? "#f5f7fb" : "#0e1117";
      const dataUrl = await toPng(exportRef.current, {
        backgroundColor,
        cacheBust: true,
        pixelRatio: 2,
      });
      const link = document.createElement("a");
      link.download = `political-map-${safeFilename(activeProfile.name)}.png`;
      link.href = dataUrl;
      link.click();
    } catch {
      setExportError(
        language === "fr"
          ? "L’export PNG a échoué. Réessayez après le chargement complet de la carte."
          : "PNG export failed. Try again after the map has fully loaded.",
      );
    } finally {
      setExporting(false);
    }
  };

  return (
    <>
      <div className="page-heading">
        <h1>{language === "fr" ? "Carte politique" : "Political map"}</h1>
        <p>
          {language === "fr"
            ? "Les références restent masquées tant qu’aucun filtre n’est choisi. Sélectionnez Any pour toutes les afficher."
            : "References remain hidden until a filter is selected. Select Any to display them all."}
        </p>
      </div>
      <section className="filter-bar" ref={filtersRef}>
        {(Object.keys(filters) as (keyof Filters)[]).map((key) => (
          <MultiFilter
            key={key}
            filterKey={key}
            label={
              {
                country: language === "fr" ? "Pays" : "Countries",
                ideology_family: language === "fr" ? "Familles idéologiques" : "Ideology families",
                role_category: language === "fr" ? "Catégories de rôle" : "Role categories",
                gender: language === "fr" ? "Genre" : "Gender",
                century: language === "fr" ? "Siècles" : "Centuries",
                confidence: language === "fr" ? "Confiance" : "Confidence",
              }[key]
            }
            options={key === "gender" ? ["male", "female"] : options(key)}
            selected={filters[key]}
            open={openFilter === key}
            language={language}
            onOpenChange={(isOpen) => setOpenFilter(isOpen ? key : null)}
            onChange={(selected) => setFilters({ ...filters, [key]: selected })}
          />
        ))}
        <button
          className="icon-button"
          onClick={() => setFilters(EMPTY_FILTERS)}
          title={language === "fr" ? "Réinitialiser les filtres" : "Clear filters"}
        >
          <RotateCcw size={18} />
        </button>
      </section>
      {loadError && (
        <div className="inline-alert" role="alert">
          {loadError}
        </div>
      )}
      {exportError && (
        <div className="inline-alert" role="alert">
          {exportError}
        </div>
      )}
      <div className="reference-count" aria-live="polite">
        <div>
          <strong>{filtered.length} / {references.length || 500}</strong>{" "}
          {language === "fr" ? "profils de référence affichés" : "reference profiles displayed"}
        </div>
        <div className="visualization-actions">
          <label className="reference-label-toggle">
            <input
              type="checkbox"
              checked={showReferenceLabels}
              onChange={(event) => setShowReferenceLabels(event.target.checked)}
            />
            <span>
              {language === "fr"
                ? "Afficher les noms sur la carte"
                : "Show names on the map"}
            </span>
          </label>
          <button
            className="secondary-button"
            disabled={exporting || references.length === 0}
            onClick={() => void exportVisualization()}
          >
            <Download size={16} />
            {exporting
              ? language === "fr" ? "Export..." : "Exporting..."
              : language === "fr" ? "Exporter en PNG" : "Export PNG"}
          </button>
        </div>
      </div>
      <section className="map-tools" aria-label={language === "fr" ? "Outils de carte" : "Map tools"}>
        <label>
          <Search size={17} aria-hidden="true" />
          <span className="sr-only">{language === "fr" ? "Rechercher une personnalité" : "Search a personality"}</span>
          <input
            type="search"
            list="reference-names"
            value={referenceQuery}
            placeholder={language === "fr" ? "Rechercher une personnalité" : "Search a personality"}
            onChange={(event) => setReferenceQuery(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") inspectReference();
            }}
          />
          <datalist id="reference-names">
            {references.map((reference) => <option key={`${reference.name}-${reference.period}`} value={reference.name} />)}
          </datalist>
        </label>
        <button className="icon-button" type="button" onClick={inspectReference} title={language === "fr" ? "Afficher la référence" : "Show reference"}><Search size={17} /></button>
        <button className="icon-button" type="button" onClick={() => zoom(0.65)} title={language === "fr" ? "Zoom avant" : "Zoom in"}><ZoomIn size={17} /></button>
        <button className="icon-button" type="button" onClick={() => zoom(1.55)} title={language === "fr" ? "Zoom arrière" : "Zoom out"}><ZoomOut size={17} /></button>
        <button className="icon-button" type="button" onClick={() => pan(-1, 0)} title={language === "fr" ? "Déplacer à gauche" : "Pan left"}><ArrowLeft size={17} /></button>
        <button className="icon-button" type="button" onClick={() => pan(1, 0)} title={language === "fr" ? "Déplacer à droite" : "Pan right"}><ArrowRight size={17} /></button>
        <button className="icon-button" type="button" onClick={() => pan(0, 1)} title={language === "fr" ? "Déplacer vers le haut" : "Pan up"}><ArrowUp size={17} /></button>
        <button className="icon-button" type="button" onClick={() => pan(0, -1)} title={language === "fr" ? "Déplacer vers le bas" : "Pan down"}><ArrowDown size={17} /></button>
        <button className="icon-button" type="button" onClick={() => { setXDomain([-4, 4]); setYDomain([-4, 4]); }} title={language === "fr" ? "Réinitialiser le zoom" : "Reset zoom"}><RotateCcw size={17} /></button>
      </section>
      {selectedReference && (
        <section className="reference-inspector">
          <div>
            <span className={`provenance-badge ${selectedReference.provenanceStatus}`}>
              {selectedReference.provenanceStatus === "sourced"
                ? language === "fr" ? "Source déclarée" : "Declared source"
                : language === "fr" ? "Non sourcé" : "Unsourced"}
            </span>
            <h2>{selectedReference.name}</h2>
            <p>{selectedReference.country} · {selectedReference.period} · {selectedReference.ideology_family}</p>
          </div>
          <dl><div><dt>x / y</dt><dd>{selectedReference.x.toFixed(2)} / {selectedReference.y.toFixed(2)}</dd></div><div><dt>{language === "fr" ? "Confiance éditoriale" : "Editorial confidence"}</dt><dd>{selectedReference.confidence}</dd></div></dl>
          <p>{selectedReference.notes || (language === "fr" ? "Justification détaillée indisponible." : "Detailed rationale unavailable.")}</p>
        </section>
      )}
      <div className="visualization-export-surface" ref={exportRef}>
        <div className="export-context">
          <div>
            <span>{language === "fr" ? "Profil analysé" : "Analyzed profile"}</span>
            <strong>{activeProfile.name}</strong>
          </div>
          <div>
            <span>{language === "fr" ? "Références incluses" : "Included references"}</span>
            <strong>{filtered.length} / {references.length || 500}</strong>
          </div>
          <p>{filterSummary}</p>
        </div>
        <section
          className="chart-panel"
          role="img"
          aria-label={
            language === "fr"
              ? `Carte politique avec ${profiles.length} profils et ${filtered.length} références`
              : `Political map with ${profiles.length} profiles and ${filtered.length} references`
          }
        >
          <ResponsiveContainer width="100%" height={600}>
            <ScatterChart margin={{ top: 24, right: 24, bottom: 24, left: 8 }}>
              <CartesianGrid stroke="var(--chart-grid)" strokeDasharray="3 3" />
              <ReferenceArea x1={-4} x2={0} y1={-4} y2={0} fill="#166534" fillOpacity={0.17} />
              <ReferenceArea x1={0} x2={4} y1={-4} y2={0} fill="#1e40af" fillOpacity={0.17} />
              <ReferenceArea x1={-4} x2={0} y1={0} y2={4} fill="#92400e" fillOpacity={0.16} />
              <ReferenceArea x1={0} x2={4} y1={0} y2={4} fill="#991b1b" fillOpacity={0.15} />
              <ReferenceLine x={0} stroke="var(--chart-zero)" />
              <ReferenceLine y={0} stroke="var(--chart-zero)" />
              <XAxis type="number" dataKey="x" domain={xDomain} tickCount={9} stroke="var(--chart-axis)" allowDataOverflow />
              <YAxis type="number" dataKey="y" domain={yDomain} tickCount={9} stroke="var(--chart-axis)" allowDataOverflow />
              <Tooltip content={<ChartTooltip />} />
              <Scatter
                name="References"
                data={filtered}
                fill="var(--chart-reference)"
                opacity={0.62}
                label={
                  showReferenceLabels
                    ? {
                        dataKey: "name",
                        position: "top",
                        className: "reference-point-label",
                      }
                    : false
                }
              />
              <Scatter name="Profiles" data={profilePoints} shape="diamond" />
            </ScatterChart>
          </ResponsiveContainer>
        </section>
        <NearestReferences
          language={language}
          profile={activeProfile}
          nearest={nearest}
          filteredCount={filtered.length}
        />
        <details className="accessible-data-table">
          <summary>{language === "fr" ? "Alternative tabulaire accessible de la carte" : "Accessible tabular map alternative"}</summary>
          <div>
            <table>
              <thead><tr><th>{language === "fr" ? "Nom" : "Name"}</th><th>{language === "fr" ? "Pays" : "Country"}</th><th>x</th><th>y</th><th>{language === "fr" ? "Provenance" : "Provenance"}</th></tr></thead>
              <tbody>{filtered.slice(0, 100).map((reference) => <tr key={`${reference.name}-${reference.period}`}><td>{reference.name}</td><td>{reference.country}</td><td>{reference.x.toFixed(2)}</td><td>{reference.y.toFixed(2)}</td><td>{reference.provenanceStatus === "sourced" ? language === "fr" ? "Sourcée" : "Sourced" : language === "fr" ? "À vérifier" : "Review required"}</td></tr>)}</tbody>
            </table>
            {filtered.length > 100 && <p>{language === "fr" ? "Le tableau est limité aux 100 premières lignes ; utilisez les filtres pour réduire la sélection." : "The table is limited to the first 100 rows; use filters to narrow the selection."}</p>}
          </div>
        </details>
      </div>
    </>
  );
}

export function MultiFilter({
  filterKey,
  label,
  options,
  selected,
  open,
  language,
  onOpenChange,
  onChange,
}: {
  filterKey: string;
  label: string;
  options: string[];
  selected: string[];
  open: boolean;
  language: Language;
  onOpenChange: (open: boolean) => void;
  onChange: (selected: string[]) => void;
}) {
  const [search, setSearch] = useState("");
  const normalizedSearch = search.trim().toLocaleLowerCase();
  const visibleOptions = options.filter((option) =>
    option.toLocaleLowerCase().includes(normalizedSearch),
  );

  useEffect(() => {
    if (!open) setSearch("");
  }, [open]);

  return (
    <details
      className="multi-filter"
      data-filter={filterKey}
      open={open}
      onToggle={(event) => onOpenChange(event.currentTarget.open)}
    >
      <summary>
        <span>{label}</span>
        <small>
          {selected.includes(ANY_FILTER)
            ? "Any"
            : selected.length || "None"}
        </small>
        <ChevronDown size={15} />
      </summary>
      <div className="filter-menu" role="group" aria-label={label}>
        <label className="filter-search">
          <span className="sr-only">
            {language === "fr" ? `Rechercher dans ${label}` : `Search ${label}`}
          </span>
          <input
            type="search"
            value={search}
            placeholder={
              language === "fr"
                ? `Rechercher dans ${label.toLocaleLowerCase()}`
                : `Search ${label.toLocaleLowerCase()}`
            }
            aria-label={
              language === "fr" ? `Rechercher dans ${label}` : `Search ${label}`
            }
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <label className="filter-any">
          <input
            type="checkbox"
            checked={selected.includes(ANY_FILTER)}
            onChange={() =>
              onChange(selected.includes(ANY_FILTER) ? [] : [ANY_FILTER])
            }
          />
          <span>Any</span>
        </label>
        {visibleOptions.map((option) => (
          <label key={option}>
            <input
              type="checkbox"
              checked={selected.includes(option)}
              onChange={() =>
                onChange(
                  selected.includes(option)
                    ? selected.filter((item) => item !== option)
                    : [
                        ...selected.filter((item) => item !== ANY_FILTER),
                        option,
                      ],
                )
              }
            />
            <span>{option}</span>
          </label>
        ))}
        {!visibleOptions.length && (
          <p className="filter-empty">
            {language === "fr" ? "Aucune option correspondante" : "No matching option"}
          </p>
        )}
      </div>
    </details>
  );
}

function NearestReferences({
  language,
  profile,
  nearest,
  filteredCount,
}: {
  language: Language;
  profile: Profile;
  nearest: NearestReference[];
  filteredCount: number;
}) {
  return (
    <section className="nearest-references" aria-labelledby="nearest-title">
      <div className="nearest-heading">
        <div>
          <span>{language === "fr" ? "Proximité cartographique" : "Map proximity"}</span>
          <h2 id="nearest-title">
            {language === "fr"
              ? `Les 3 références les plus proches de ${profile.name}`
              : `3 references closest to ${profile.name}`}
          </h2>
        </div>
        <small>
          {language === "fr"
            ? `Calculées parmi ${filteredCount} références affichées`
            : `Calculated from ${filteredCount} displayed references`}
        </small>
      </div>
      {nearest.length > 0 ? (
        <div className="nearest-grid">
          {nearest.map(({ reference, distance }, index) => (
            <article key={`${reference.name}-${index}`}>
              <span className="nearest-rank">#{index + 1}</span>
              <div>
                <strong>{reference.name}</strong>
                <p>{reference.ideology_family} · {reference.country}</p>
              </div>
              <dl>
                <div><dt>x / y</dt><dd>{reference.x.toFixed(2)} / {reference.y.toFixed(2)}</dd></div>
                <div>
                  <dt>{language === "fr" ? "Distance" : "Distance"}</dt>
                  <dd>{distance.toFixed(3)}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      ) : (
        <p className="muted-empty">
          {language === "fr"
            ? "Aucune référence ne correspond à cette combinaison de filtres."
            : "No reference matches this filter combination."}
        </p>
      )}
    </section>
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
