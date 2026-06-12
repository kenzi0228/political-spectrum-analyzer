import Papa from "papaparse";
import type { ReferenceProfile } from "./types";

let cache: ReferenceProfile[] | null = null;

export const loadReferenceProfiles = async (): Promise<ReferenceProfile[]> => {
  if (cache) return cache;
  const { default: personalitiesCsv } = await import(
    "../data/reference/personalities.csv?raw"
  );
  const parsed = Papa.parse<Record<string, string>>(personalitiesCsv, {
    header: true,
    skipEmptyLines: true,
  });
  cache = parsed.data.map((row) => ({
    name: row.name,
    display_group: row.display_group,
    country: row.country,
    ideology_family: row.ideology_family,
    x: Number(row.x),
    y: Number(row.y),
    confidence: row.confidence,
    century: row.century,
    role_category: row.role_category,
    gender: row.gender,
    notes: row.notes,
  }));
  return cache;
};
