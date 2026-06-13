import { AXES, DEFAULT_SCORES } from "./constants";
import type { AxisKey, Profile, Scores } from "./types";
import { SCORING_MODEL_VERSION } from "./model";

const STORAGE_VERSION = 3;
const PROFILE_SCHEMA = "political_spectrum_profile.v2";

type UnknownRecord = Record<string, unknown>;

const isRecord = (value: unknown): value is UnknownRecord =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const makeId = (): string =>
  globalThis.crypto?.randomUUID?.() ??
  `profile-${Date.now()}-${Math.random().toString(16).slice(2)}`;

const parseScore = (value: unknown, axis: AxisKey): number => {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error(`Le score « ${axis} » doit être un nombre.`);
  }
  if (value < 0 || value > 100) {
    throw new Error(`Le score « ${axis} » doit être compris entre 0 et 100.`);
  }
  return value;
};

export const parseScores = (value: unknown): Scores => {
  if (!isRecord(value)) {
    throw new Error("Le champ « scores » est absent ou invalide.");
  }
  return Object.fromEntries(
    AXES.map((axis) => [axis, parseScore(value[axis], axis)]),
  ) as Scores;
};

const normalizeStoredProfile = (
  value: unknown,
  index: number,
  usedIds: Set<string>,
): Profile => {
  if (!isRecord(value)) throw new Error("Profil local invalide.");
  const rawId =
    typeof value.id === "string" && value.id.trim() ? value.id.trim() : makeId();
  const id = usedIds.has(rawId) ? makeId() : rawId;
  usedIds.add(id);
  const name =
    typeof value.name === "string" && value.name.trim()
      ? value.name.trim().slice(0, 100)
      : `Profil ${index + 1}`;
  return {
    id,
    name,
    scores: parseScores(value.scores),
    modelVersion:
      typeof value.modelVersion === "string"
        ? value.modelVersion
        : SCORING_MODEL_VERSION,
  };
};

export const parseStoredProfiles = (raw: string | null): Profile[] | null => {
  if (!raw) return null;
  try {
    const parsed: unknown = JSON.parse(raw);
    const values =
      isRecord(parsed) &&
      (parsed.version === STORAGE_VERSION || parsed.version === 2)
        ? parsed.profiles
        : parsed;
    if (!Array.isArray(values) || values.length === 0) return null;
    const usedIds = new Set<string>();
    return values.map((profile, index) =>
      normalizeStoredProfile(profile, index, usedIds),
    );
  } catch {
    return null;
  }
};

export const serializeProfiles = (profiles: Profile[]): string =>
  JSON.stringify({ version: STORAGE_VERSION, profiles });

export const parseImportedProfile = (
  raw: string,
  currentProfile: Profile,
): Profile => {
  let payload: unknown;
  try {
    payload = JSON.parse(raw);
  } catch {
    throw new Error("Le fichier sélectionné n’est pas un JSON valide.");
  }
  if (!isRecord(payload)) {
    throw new Error("Le fichier ne contient pas un profil valide.");
  }
  if (
    payload.schema !== undefined &&
    !["political_spectrum_profile.v1", PROFILE_SCHEMA].includes(String(payload.schema))
  ) {
    throw new Error("Le schéma de ce fichier de profil n’est pas reconnu.");
  }
  const name =
    typeof payload.name === "string" && payload.name.trim()
      ? payload.name.trim().slice(0, 100)
      : currentProfile.name;
  return {
    ...currentProfile,
    name,
    scores: parseScores(payload.scores),
    modelVersion: SCORING_MODEL_VERSION,
  };
};

export const createDefaultProfile = (index = 1): Profile => ({
  id: makeId(),
  name: `Profil ${index}`,
  scores: { ...DEFAULT_SCORES },
  modelVersion: SCORING_MODEL_VERSION,
});
