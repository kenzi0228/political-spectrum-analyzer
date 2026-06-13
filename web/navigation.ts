import type { ViewKey } from "./types";

const VIEWS: ReadonlySet<string> = new Set([
  "home",
  "input",
  "guide",
  "visualization",
  "analysis",
  "comparison",
  "methodology",
  "atlas",
  "privacy",
  "legal",
  "about",
]);

export interface AppRoute {
  view: ViewKey;
  profileId?: string;
}

export const parseAppRoute = (location: string): AppRoute => {
  const normalized = location.startsWith("#") ? location.slice(1) : location;
  const [path, query = ""] = normalized.split("?");
  const candidate = path.replace(/^\/+/, "");
  const view = VIEWS.has(candidate) ? (candidate as ViewKey) : "home";
  const profileId = new URLSearchParams(query).get("profile")?.trim();
  return { view, profileId: profileId || undefined };
};

export const buildAppRoute = (view: ViewKey, profileId: string): string =>
  `/${view === "home" ? "" : view}?${new URLSearchParams({ profile: profileId }).toString()}`;

export const currentAppLocation = (): string =>
  `${window.location.pathname}${window.location.search}`;
