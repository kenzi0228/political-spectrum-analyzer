import type { ReactNode } from "react";
import type { Language, ViewKey } from "../types";

export function PageHeading({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="page-heading">
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
  );
}

export function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export function AnalysisBlock({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="analysis-block">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

export function SiteFooter({
  language,
  onNavigate,
  onPrivacyChoices,
}: {
  language: Language;
  onNavigate: (view: ViewKey) => void;
  onPrivacyChoices: () => void;
}) {
  const link = (view: ViewKey, fr: string, en: string) => (
    <button type="button" onClick={() => onNavigate(view)}>
      {language === "fr" ? fr : en}
    </button>
  );
  return (
    <footer className="site-footer">
      <span>Politiscales Analyser</span>
      <nav aria-label={language === "fr" ? "Informations légales" : "Legal information"}>
        {link("about", "À propos", "About")}
        {link("privacy", "Confidentialité", "Privacy")}
        {link("legal", "Mentions légales", "Legal notice")}
        <button type="button" onClick={onPrivacyChoices}>
          {language === "fr" ? "Choix publicitaires" : "Ad choices"}
        </button>
      </nav>
    </footer>
  );
}
