import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { ESLint } from "eslint";

const frontendRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../..",
);
const eslint = new ESLint({
  cwd: frontendRoot,
  overrideConfigFile: path.join(frontendRoot, "eslint.config.js"),
});

async function lintSource(source: string, sourcePath: string) {
  const [result] = await eslint.lintText(source, { filePath: sourcePath });
  return result?.messages ?? [];
}

describe("architecture dependency rule", () => {
  it("rejects dynamic cross-feature imports", async () => {
    const diagnostics = await lintSource(
      "export const loadOtherFeature = () => import('@/features/plots/PlotPage.vue')",
      path.join(frontendRoot, "src/features/home/loader.ts"),
    );

    expect(diagnostics).toHaveLength(1);
    expect(diagnostics[0]?.ruleId).toBe("architecture/enforce-layer-order");
    expect(diagnostics[0]?.message).toContain(
      "features may depend on shared modules",
    );
  });

  it("enforces the domain dependency DAG declared in the structure document", async () => {
    const allowedDependency = await lintSource(
      "export type { ValueType } from '@/shared/domains/value-types'",
      path.join(frontendRoot, "src/shared/domains/decisions/decision.ts"),
    );
    const undeclaredDependency = await lintSource(
      "export type { Budget } from '@/shared/domains/budget'",
      path.join(frontendRoot, "src/shared/domains/decisions/decision.ts"),
    );

    expect(allowedDependency).toEqual([]);
    expect(undeclaredDependency).toHaveLength(1);
    expect(undeclaredDependency[0]?.ruleId).toBe(
      "architecture/enforce-layer-order",
    );
  });
});
