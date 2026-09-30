import { execFile } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";
import openapiTS, { astToString } from "openapi-typescript";
import { format } from "prettier";

const frontendRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);
const repositoryRoot = path.resolve(frontendRoot, "..");
const outputPath = path.join(
  frontendRoot,
  "src/shared/foundation/api/schema.d.ts",
);
const executeFile = promisify(execFile);
const backendCommand = process.platform === "win32" ? "uv.exe" : "uv";
const { stdout: backendExport } = await executeFile(
  backendCommand,
  [
    "run",
    "--directory",
    path.join(repositoryRoot, "backend"),
    "python",
    "-m",
    "tekton.entrypoints.openapi",
  ],
  { maxBuffer: 10 * 1024 * 1024 },
);

const schema = JSON.parse(backendExport);
schema.paths = Object.fromEntries(
  Object.entries(schema.paths).map(([pathName, pathItem]) => [
    pathName.startsWith("/api/") ? pathName.slice("/api".length) : pathName,
    pathItem,
  ]),
);
const generatedTypes = await openapiTS(schema);
const declaration = await format(astToString(generatedTypes), {
  filepath: outputPath,
});
const isCheckMode = process.argv.includes("--check");
if (isCheckMode) {
  let existingDeclaration;
  try {
    existingDeclaration = await readFile(outputPath, "utf8");
  } catch (error) {
    if (!(
      error instanceof Error &&
      "code" in error &&
      error.code === "ENOENT"
    )) {
      throw error;
    }
  }
  if (existingDeclaration !== declaration) {
    console.error("Generated API types are out of date. Run pnpm api-types.");
    process.exitCode = 1;
  } else {
    console.log("Generated API types are up to date.");
  }
} else {
  await mkdir(path.dirname(outputPath), { recursive: true });
  await writeFile(outputPath, declaration);
  console.log(
    `Generated API types at ${path.relative(frontendRoot, outputPath)}.`,
  );
}
