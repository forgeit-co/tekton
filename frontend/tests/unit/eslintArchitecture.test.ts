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

const architectureRuleFixtures = [
  {
    ruleId: "architecture/enforce-layer-order",
    shouldFlag: {
      source:
        "import PlotPage from '@/features/plots/PlotPage.vue'; export { PlotPage }",
      path: "src/features/home/loader.ts",
    },
    shouldPass: {
      source:
        "import { apiClient } from '@/shared/foundation/api/client'; export { apiClient }",
      path: "src/features/home/loader.ts",
    },
  },
  {
    ruleId: "architecture/no-feature-api-in-pages",
    shouldFlag: {
      source:
        "<script setup>import { getHome } from '@/features/home/api/homeApi'</script>",
      path: "src/features/home/HomePage.vue",
    },
    shouldPass: {
      source:
        "<script setup>import { useHome } from '@/features/home/composables/useHome'</script>",
      path: "src/features/home/HomePage.vue",
    },
  },
  {
    ruleId: "architecture/no-router-or-stores-in-presenters",
    shouldFlag: {
      source: '<script setup>import { useRouter } from "vue-router"</script>',
      path: "src/features/home/HomePresenter.vue",
    },
    shouldPass: {
      source: '<script setup>import { ref } from "vue"</script>',
      path: "src/features/home/HomePresenter.vue",
    },
  },
] as const;

async function lintSource(source: string, sourcePath: string) {
  const [result] = await eslint.lintText(source, {
    filePath: path.join(frontendRoot, sourcePath),
  });
  return result?.messages ?? [];
}

describe("frontend architecture rules", () => {
  it("covers every configured custom rule with passing and failing fixtures", async () => {
    const fixtureRuleIds = architectureRuleFixtures.map(
      (fixture) => fixture.ruleId,
    );
    const sourceConfiguration = await eslint.calculateConfigForFile(
      path.join(frontendRoot, "src/features/home/HomePage.vue"),
    );
    const architecturePlugin = sourceConfiguration?.plugins.architecture;
    const configuredRuleIds = Object.keys(architecturePlugin?.rules ?? {}).map(
      (ruleName) => `architecture/${ruleName}`,
    );

    expect([...fixtureRuleIds].sort()).toEqual(configuredRuleIds.sort());

    for (const fixture of architectureRuleFixtures) {
      const flaggedDiagnostics = await lintSource(
        fixture.shouldFlag.source,
        fixture.shouldFlag.path,
      );
      const passingDiagnostics = await lintSource(
        fixture.shouldPass.source,
        fixture.shouldPass.path,
      );

      expect(
        flaggedDiagnostics.map((diagnostic) => diagnostic.ruleId),
        `${fixture.ruleId} should_flag fixture`,
      ).toContain(fixture.ruleId);
      expect(
        passingDiagnostics.map((diagnostic) => diagnostic.ruleId),
        `${fixture.ruleId} should_pass fixture`,
      ).not.toContain(fixture.ruleId);
    }
  });

  for (const fixture of architectureRuleFixtures) {
    it(`${fixture.ruleId} flags its should_flag fixture`, async () => {
      const diagnostics = await lintSource(
        fixture.shouldFlag.source,
        fixture.shouldFlag.path,
      );

      expect(diagnostics.map((diagnostic) => diagnostic.ruleId)).toContain(
        fixture.ruleId,
      );
    });

    it(`${fixture.ruleId} passes its should_pass fixture`, async () => {
      const diagnostics = await lintSource(
        fixture.shouldPass.source,
        fixture.shouldPass.path,
      );

      expect(diagnostics.map((diagnostic) => diagnostic.ruleId)).not.toContain(
        fixture.ruleId,
      );
    });
  }
});
