import { ShieldCheck } from "lucide-react";
import type { Language } from "../types";

export function CookieConsent({
  language,
  onAccept,
  onReject,
}: {
  language: Language;
  onAccept: () => void;
  onReject: () => void;
}) {
  return (
    <section className="consent-banner" aria-labelledby="consent-title">
      <ShieldCheck size={24} aria-hidden="true" />
      <div>
        <strong id="consent-title">
          {language === "fr" ? "Vos choix publicitaires" : "Your advertising choices"}
        </strong>
        <p>
          {language === "fr"
            ? "Les profils politiques restent dans votre navigateur. Avec votre accord, Google AdSense peut charger des cookies ou identifiants publicitaires tiers. Refuser n’empêche pas d’utiliser l’application."
            : "Political profiles remain in your browser. With your permission, Google AdSense may load third-party advertising cookies or identifiers. Rejecting does not prevent use of the application."}
        </p>
      </div>
      <div className="consent-actions">
        <button className="ghost-action" type="button" onClick={onReject}>
          {language === "fr" ? "Refuser" : "Reject"}
        </button>
        <button className="primary-action" type="button" onClick={onAccept}>
          {language === "fr" ? "Accepter les publicités" : "Accept ads"}
        </button>
      </div>
    </section>
  );
}
