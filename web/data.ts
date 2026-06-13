import Papa from "papaparse";
import type { ReferenceProfile } from "./types";

let cache: ReferenceProfile[] | null = null;

const REQUIRED_COLUMNS = [
  "name",
  "period",
  "display_group",
  "country",
  "ideology_family",
  "x",
  "y",
  "confidence",
  "century",
  "role_category",
  "gender",
  "notes",
  "source",
  "is_estimated",
] as const;

export const parseReferenceProfiles = (csv: string): ReferenceProfile[] => {
  const parsed = Papa.parse<Record<string, string>>(csv, {
    header: true,
    skipEmptyLines: true,
  });
  if (parsed.errors.length > 0) {
    throw new Error(
      `Dataset CSV invalide : ${parsed.errors[0].message} (ligne ${parsed.errors[0].row ?? "inconnue"}).`,
    );
  }
  const fields = new Set(parsed.meta.fields ?? []);
  const missing = REQUIRED_COLUMNS.filter((column) => !fields.has(column));
  if (missing.length > 0) {
    throw new Error(`Colonnes CSV manquantes : ${missing.join(", ")}.`);
  }

  return parsed.data.map((row, index) => {
    const x = Number(row.x);
    const y = Number(row.y);
    const line = index + 2;
    if (!row.name?.trim()) {
      throw new Error(`Nom manquant dans le dataset à la ligne ${line}.`);
    }
    if (!Number.isFinite(x) || !Number.isFinite(y) || Math.abs(x) > 4 || Math.abs(y) > 4) {
      throw new Error(
        `Coordonnées invalides pour ${row.name} à la ligne ${line}.`,
      );
    }
    if (!["male", "female"].includes(row.gender)) {
      throw new Error(
        `Genre invalide pour ${row.name} à la ligne ${line}.`,
      );
    }
    for (const column of [
      "display_group",
      "country",
      "ideology_family",
      "confidence",
      "century",
      "role_category",
    ] as const) {
      if (!row[column]?.trim()) {
        throw new Error(
          `Valeur ${column} manquante pour ${row.name} à la ligne ${line}.`,
        );
      }
    }
    return {
      name: row.name.trim(),
      period: row.period.trim(),
      display_group: row.display_group.trim(),
      country: row.country.trim(),
      ideology_family: row.ideology_family.trim(),
      x,
      y,
      confidence: row.confidence.trim(),
      century: row.century.trim(),
      role_category: row.role_category.trim(),
      gender: row.gender,
      notes: row.notes?.trim() ?? "",
      source: row.source?.trim() ?? "",
      is_estimated: row.is_estimated?.trim().toLowerCase() === "true",
      provenanceStatus: row.source?.trim() ? "sourced" : "unsourced",
    };
  });
};

export const loadReferenceProfiles = async (): Promise<ReferenceProfile[]> => {
  if (cache) return cache;
  const { default: personalitiesCsv } = await import(
    "../data/reference/personalities.csv?raw"
  );
  cache = parseReferenceProfiles(personalitiesCsv);
  return cache;
};
