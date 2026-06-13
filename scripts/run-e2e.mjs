import { spawn } from "node:child_process";

const node = process.execPath;
const preview = spawn(
  node,
  ["node_modules/vite/bin/vite.js", "preview", "--host", "127.0.0.1", "--port", "4173"],
  { stdio: "inherit" },
);

const waitForServer = async () => {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      const response = await fetch("http://127.0.0.1:4173");
      if (response.ok) return;
    } catch {
      // The preview server is still starting.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("Vite preview did not start on port 4173.");
};

let exitCode = 1;
try {
  await waitForServer();
  exitCode = await new Promise((resolve) => {
    const runner = spawn(
      node,
      ["node_modules/@playwright/test/cli.js", "test", ...process.argv.slice(2)],
      { stdio: "inherit" },
    );
    runner.on("exit", (code) => resolve(code ?? 1));
  });
} finally {
  preview.kill();
}

process.exit(exitCode);
