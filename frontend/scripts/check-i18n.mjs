import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const frontendRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);
const sourceRoot = path.join(frontendRoot, "src");
const englishMessages = JSON.parse(
  await readFile(
    path.join(sourceRoot, "shared/foundation/i18n/en.json"),
    "utf8",
  ),
);
const keyPattern = /(?:\bt\s*\(|\$t\s*\()\s*['"]([^'"]+)['"]/g;
const missingKeys = [];

async function inspectDirectory(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  for (const entry of entries) {
    const entryPath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      await inspectDirectory(entryPath);
      continue;
    }
    if (!/\.(?:ts|vue)$/.test(entry.name)) continue;

    const source = await readFile(entryPath, "utf8");
    for (const match of source.matchAll(keyPattern)) {
      const key = match[1];
      if (key && !(key in englishMessages)) {
        missingKeys.push(`${path.relative(frontendRoot, entryPath)}: ${key}`);
      }
    }
  }
}

await inspectDirectory(sourceRoot);
if (missingKeys.length > 0) {
  console.error(
    `Missing English i18n keys:\n${missingKeys.map((key) => `- ${key}`).join("\n")}`,
  );
  process.exitCode = 1;
} else {
  console.log("All statically referenced i18n keys exist in en.json.");
}
