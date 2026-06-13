import type { Language, ViewKey } from "./types";

interface Messages {
  brandSubtitle: string;
  appearance: string;
  theme: string;
  darkTheme: string;
  lightTheme: string;
  preciseInput: string;
  preciseInputDetail: string;
  addProfile: string;
  duplicateProfile: string;
  undo: string;
  loadingVisualization: string;
  loadingAtlas: string;
  views: Record<Exclude<ViewKey, "privacy" | "legal" | "about">, string>;
}

export const messages: Record<Language, Messages> = {
  fr: {
    brandSubtitle: "Analyse politique multidimensionnelle",
    appearance: "Apparence",
    theme: "Thème",
    darkTheme: "Thème sombre",
    lightTheme: "Thème clair",
    preciseInput: "Saisie précise",
    preciseInputDetail: "Valeurs numériques exactes",
    addProfile: "Ajouter un profil",
    duplicateProfile: "Dupliquer le profil",
    undo: "Annuler la dernière modification",
    loadingVisualization: "Chargement de la visualisation…",
    loadingAtlas: "Chargement de l’atlas…",
    views: {
      home: "Accueil",
      input: "Saisie",
      guide: "Guide",
      visualization: "Visualisation",
      analysis: "Analyse",
      comparison: "Comparaison",
      methodology: "Méthodologie",
      atlas: "Atlas",
    },
  },
  en: {
    brandSubtitle: "Multidimensional political analysis",
    appearance: "Appearance",
    theme: "Theme",
    darkTheme: "Dark theme",
    lightTheme: "Light theme",
    preciseInput: "Precise input",
    preciseInputDetail: "Exact numeric values",
    addProfile: "Add profile",
    duplicateProfile: "Duplicate profile",
    undo: "Undo last change",
    loadingVisualization: "Loading visualization…",
    loadingAtlas: "Loading atlas…",
    views: {
      home: "Home",
      input: "Input",
      guide: "Guide",
      visualization: "Visualization",
      analysis: "Analysis",
      comparison: "Comparison",
      methodology: "Methodology",
      atlas: "Atlas",
    },
  },
};
