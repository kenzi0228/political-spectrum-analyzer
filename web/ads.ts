export type AdConsent = "accepted" | "rejected" | null;

const CONSENT_KEY = "psa.adConsent";
const ADSENSE_CLIENT = "ca-pub-8513561134992486";
const ADSENSE_SCRIPT_ID = "psa-adsense";

export const readAdConsent = (): AdConsent => {
  try {
    const value = localStorage.getItem(CONSENT_KEY);
    return value === "accepted" || value === "rejected" ? value : null;
  } catch {
    return null;
  }
};

export const storeAdConsent = (consent: Exclude<AdConsent, null>): void => {
  try {
    localStorage.setItem(CONSENT_KEY, consent);
  } catch {
    // Consent remains effective for the current page even without persistence.
  }
};

export const loadAdsense = (): void => {
  if (document.getElementById(ADSENSE_SCRIPT_ID)) return;
  const script = document.createElement("script");
  script.id = ADSENSE_SCRIPT_ID;
  script.async = true;
  script.crossOrigin = "anonymous";
  script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_CLIENT}`;
  document.head.append(script);
};

export const applyAdConsent = (consent: Exclude<AdConsent, null>): void => {
  storeAdConsent(consent);
  if (consent === "accepted") loadAdsense();
};
