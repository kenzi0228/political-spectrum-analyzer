import { mkdir, readFile, writeFile } from "node:fs/promises";

const pages = {
  guide: ["Guide", "Guide d’utilisation de Politiscales Analyser."],
  methodology: ["Méthodologie", "Formule, statut scientifique et limites du modèle de projection."],
  atlas: ["Atlas des références", "Atlas documentaire de 500 personnalités politiques et historiques."],
  privacy: ["Politique de confidentialité", "Stockage local des profils et choix publicitaires."],
  legal: ["Mentions légales", "Informations légales de Politiscales Analyser."],
  about: ["À propos", "Positionnement éditorial et gouvernance du projet."],
};

const source = await readFile("dist/index.html", "utf8");
for (const [route, [title, description]] of Object.entries(pages)) {
  const canonical = `https://politiscales-analyser.vercel.app/${route}`;
  const html = source
    .replace("<title>Politiscales Analyser</title>", `<title>${title} · Politiscales Analyser</title>`)
    .replace(
      /<meta\s+name="description"\s+content="[^"]*"\s*\/>/,
      `<meta name="description" content="${description}" />`,
    )
    .replace(
      /<meta\s+property="og:title"\s+content="[^"]*"\s*\/>/,
      `<meta property="og:title" content="${title} · Politiscales Analyser" />`,
    )
    .replace(
      /<meta\s+property="og:url"\s+content="[^"]*"\s*\/>/,
      `<meta property="og:url" content="${canonical}" />`,
    )
    .replace(
      /<link\s+rel="canonical"\s+href="[^"]*"\s*\/>/,
      `<link rel="canonical" href="${canonical}" />`,
    );
  await mkdir(`dist/${route}`, { recursive: true });
  await writeFile(`dist/${route}/index.html`, html, "utf8");
}
