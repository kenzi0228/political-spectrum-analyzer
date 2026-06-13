import { useEffect, useMemo, useState } from "react";
import { Search } from "lucide-react";
import { loadReferenceProfiles } from "../data";
import type { Language, ReferenceProfile } from "../types";
import { PageHeading } from "../components/Common";

export default function AtlasView({ language }: { language: Language }) {
  const [references, setReferences] = useState<ReferenceProfile[]>([]);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<ReferenceProfile | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    void loadReferenceProfiles()
      .then((items) => mounted && setReferences(items))
      .catch((reason) => mounted && setError(reason instanceof Error ? reason.message : "Dataset error"));
    return () => { mounted = false; };
  }, []);

  const matches = useMemo(() => {
    const needle = query.trim().toLocaleLowerCase();
    if (!needle) return references;
    return references.filter((reference) =>
      [reference.name, reference.country, reference.ideology_family, reference.role_category]
        .some((value) => value.toLocaleLowerCase().includes(needle)),
    );
  }, [query, references]);

  return (
    <>
      <PageHeading
        title={language === "fr" ? "Atlas des références" : "Reference atlas"}
        description={language === "fr" ? "Explorez les 500 estimations documentaires et vérifiez leur état de provenance." : "Explore 500 documentary estimates and inspect their provenance status."}
      />
      <label className="atlas-search">
        <Search size={18} aria-hidden="true" />
        <span className="sr-only">{language === "fr" ? "Rechercher une référence" : "Search references"}</span>
        <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder={language === "fr" ? "Nom, pays, famille ou rôle" : "Name, country, family, or role"} />
      </label>
      {error && <div className="inline-alert" role="alert">{error}</div>}
      <div className="atlas-layout">
        <section className="atlas-list" aria-label={language === "fr" ? "Références" : "References"}>
          <p>{matches.length} / {references.length || 500}</p>
          {matches.slice(0, 100).map((reference) => (
            <button key={`${reference.name}-${reference.period}`} className={selected === reference ? "active" : ""} onClick={() => setSelected(reference)}>
              <span><strong>{reference.name}</strong><small>{reference.country} · {reference.period}</small></span>
              <i className={`provenance-dot ${reference.provenanceStatus}`} title={reference.provenanceStatus} />
            </button>
          ))}
          {matches.length > 100 && <small>{language === "fr" ? "Affinez la recherche pour afficher les autres résultats." : "Refine the search to display more results."}</small>}
        </section>
        <section className="atlas-detail">
          {selected ? (
            <>
              <span className={`provenance-badge ${selected.provenanceStatus}`}>
                {selected.provenanceStatus === "sourced"
                  ? language === "fr" ? "Source déclarée" : "Declared source"
                  : language === "fr" ? "Non sourcé · à vérifier" : "Unsourced · review required"}
              </span>
              <h2>{selected.name}</h2>
              <dl>
                <div><dt>{language === "fr" ? "Période" : "Period"}</dt><dd>{selected.period}</dd></div>
                <div><dt>{language === "fr" ? "Pays" : "Country"}</dt><dd>{selected.country}</dd></div>
                <div><dt>{language === "fr" ? "Famille" : "Family"}</dt><dd>{selected.ideology_family}</dd></div>
                <div><dt>{language === "fr" ? "Rôle" : "Role"}</dt><dd>{selected.role_category}</dd></div>
                <div><dt>x / y</dt><dd>{selected.x.toFixed(2)} / {selected.y.toFixed(2)}</dd></div>
                <div><dt>{language === "fr" ? "Confiance éditoriale" : "Editorial confidence"}</dt><dd>{selected.confidence}</dd></div>
              </dl>
              <p>{selected.notes || (language === "fr" ? "Aucune justification détaillée disponible." : "No detailed rationale available.")}</p>
              {selected.source ? <a href={selected.source} target="_blank" rel="noreferrer">{language === "fr" ? "Consulter la source" : "Open source"}</a> : <p className="dataset-warning">{language === "fr" ? "Cette estimation ne possède pas encore de source vérifiable. Elle ne doit pas être présentée comme un fait établi." : "This estimate does not yet have a verifiable source and must not be presented as established fact."}</p>}
            </>
          ) : (
            <p>{language === "fr" ? "Sélectionnez une référence pour examiner sa fiche." : "Select a reference to inspect its record."}</p>
          )}
        </section>
      </div>
    </>
  );
}
