import path from "node:path";
import { readFileSync, readdirSync } from "node:fs";
import { defineConfig } from "eslint/config";
import js from "@eslint/js";
import eslintConfigPrettier from "eslint-config-prettier/flat";
import pluginVue from "eslint-plugin-vue";
import vuejsAccessibility from "eslint-plugin-vuejs-accessibility";
import globals from "globals";
import tseslint from "typescript-eslint";

const sourceMarker = "/src/";
const domainRoot = new URL("./src/shared/domains/", import.meta.url);

const structureDocument = readFileSync(
  new URL("./project_structure.md", import.meta.url),
  "utf8",
);

function readDomainDependencies(document) {
  const documentLines = document.split("\n");
  const tableStart = documentLines.findIndex((line) =>
    /^\|\s*Domain\s*\|\s*Allowed domain dependencies\s*\|$/.test(line),
  );
  if (tableStart === -1) {
    throw new Error(
      "project_structure.md must declare the shared-domain DAG table.",
    );
  }

  const table = documentLines.slice(tableStart + 2);
  const dependencies = new Map();
  for (const row of table) {
    if (!row.startsWith("|")) break;
    const columns = row
      .split("|")
      .slice(1, -1)
      .map((column) => column.trim().replaceAll("`", ""));
    if (columns.length !== 2) {
      throw new Error(
        `Malformed domain dependency row in project_structure.md: ${row}`,
      );
    }
    const [domainName, dependencyNames] = columns;
    const domain = domainName === "Every other domain" ? "*" : domainName;
    if (!domain || !dependencyNames || dependencies.has(domain)) {
      throw new Error(`Invalid or duplicate domain dependency row: ${row}`);
    }
    const allowedDependencies =
      dependencyNames === "None (foundation only)"
        ? []
        : dependencyNames
            .split(", ")
            .map((dependency) => dependency.replaceAll("`", ""));
    dependencies.set(domain, allowedDependencies);
  }

  if (!dependencies.has("*")) {
    throw new Error(
      "project_structure.md must declare the default domain dependency row.",
    );
  }
  const domains = readdirSync(domainRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);
  for (const domain of domains) {
    if (!dependencies.has(domain) && !dependencies.has("*")) {
      throw new Error(
        `Domain '${domain}' is missing from the project_structure.md DAG.`,
      );
    }
    for (const dependency of dependencies.get(domain) ??
      dependencies.get("*")) {
      if (!domains.includes(dependency)) {
        throw new Error(
          `Domain '${domain}' depends on unknown domain '${dependency}'.`,
        );
      }
    }
  }
  for (const domain of dependencies.keys()) {
    if (domain !== "*" && !domains.includes(domain)) {
      throw new Error(
        `Unknown domain '${domain}' is declared in project_structure.md.`,
      );
    }
  }
  return dependencies;
}

const domainDependencies = readDomainDependencies(structureDocument);

function sourceModulePath(filename) {
  const normalized = filename.split(path.sep).join("/");
  return normalized.includes(sourceMarker)
    ? (normalized.split(sourceMarker).pop() ?? null)
    : null;
}

function resolveSourceImport(filename, source) {
  if (typeof source !== "string") return null;
  if (source.startsWith("@/")) return source.slice(2);
  if (!source.startsWith("./") && !source.startsWith("../")) return null;
  const currentModule = sourceModulePath(filename);
  if (!currentModule) return null;
  const resolved = path.posix.normalize(
    path.posix.join(path.posix.dirname(currentModule), source),
  );
  return resolved.startsWith("..") ? null : resolved;
}

function layerOf(modulePath) {
  if (!modulePath) return null;
  if (modulePath.startsWith("features/"))
    return { type: "feature", name: modulePath.split("/")[1] };
  if (modulePath.startsWith("shared/domains/")) {
    return { type: "domain", name: modulePath.split("/")[2] };
  }
  if (modulePath.startsWith("shared/foundation/"))
    return { type: "foundation", name: null };
  if (modulePath.startsWith("app/")) return { type: "app", name: null };
  return null;
}

function sourceVisitor(check) {
  function inspect(node) {
    if (node.source && typeof node.source.value === "string")
      check(node, node.source.value);
  }

  function inspectExport(node) {
    if (node.source && typeof node.source.value === "string") {
      check(node, node.source.value);
    } else if (node.exportKind === "type" && node.declaration?.source) {
      inspect(node.declaration);
    }
  }
  return {
    ImportDeclaration: inspect,
    TSImportType(node) {
      const importSource = node.source?.value;
      if (typeof importSource === "string") {
        check(node, importSource);
      }
    },
    ImportExpression(node) {
      if (
        node.source.type === "Literal" &&
        typeof node.source.value === "string"
      ) {
        check(node, node.source.value);
      } else if (
        node.source.type === "TemplateLiteral" &&
        node.source.expressions.length === 0
      ) {
        check(node, node.source.quasis[0]?.value.cooked ?? null);
      }
    },
    ExportNamedDeclaration: inspectExport,
    ExportAllDeclaration: inspect,
  };
}

const enforceLayerOrder = {
  meta: {
    type: "problem",
    docs: {
      description:
        "Enforce app → features → shared domains → foundation dependencies.",
    },
    messages: {
      forbidden: "'{{ filename }}' cannot import '{{ source }}': {{ reason }}",
    },
  },
  create(context) {
    const filename = path.basename(context.filename);
    const importer = layerOf(sourceModulePath(context.filename));
    if (!importer) return {};

    return sourceVisitor((node, source) => {
      const target = layerOf(resolveSourceImport(context.filename, source));
      if (!target) return;

      let reason = null;
      if (importer.type === "foundation" && target.type !== "foundation") {
        reason = "shared foundation may import only other foundation modules";
      } else if (importer.type === "domain") {
        if (target.type === "app" || target.type === "feature") {
          reason = "shared domains cannot depend on app or feature modules";
        } else if (target.type === "domain" && target.name !== importer.name) {
          const allowedDependencies =
            domainDependencies.get(importer.name) ??
            domainDependencies.get("*");
          if (!allowedDependencies.includes(target.name)) {
            reason = `domain dependency is not declared; allowed domains: ${allowedDependencies.join(", ") || "none"}`;
          }
        }
      } else if (importer.type === "feature") {
        if (
          target.type === "app" ||
          (target.type === "feature" && target.name !== importer.name)
        ) {
          reason =
            "features may depend on shared modules, not app or other features";
        }
      }

      if (reason) {
        context.report({
          node,
          messageId: "forbidden",
          data: { filename, source, reason },
        });
      }
    });
  },
};

const noFeatureApiInPages = {
  meta: {
    type: "problem",
    docs: { description: "Route pages must access APIs through composables." },
    messages: {
      forbidden:
        "'{{ filename }}' must not import its feature API ('{{ source }}'). Use a composable.",
    },
  },
  create(context) {
    const modulePath = sourceModulePath(context.filename);
    const featureName = modulePath?.match(/^features\/([^/]+)\//)?.[1];
    if (!featureName || !path.basename(context.filename).endsWith("Page.vue"))
      return {};
    return {
      ImportDeclaration(node) {
        const source = node.source.value;
        if (
          typeof source === "string" &&
          (source.startsWith(`@/features/${featureName}/api/`) ||
            source === `@/features/${featureName}/api` ||
            source.startsWith("../api/") ||
            source === "../api")
        ) {
          context.report({
            node,
            messageId: "forbidden",
            data: { filename: path.basename(context.filename), source },
          });
        }
      },
    };
  },
};

const noRouterOrStoresInPresenters = {
  meta: {
    type: "problem",
    docs: {
      description:
        "Presenters receive navigation and state through props and emits.",
    },
    messages: {
      forbidden:
        "'{{ filename }}' must not import '{{ source }}'; keep routing and store wiring in containers.",
    },
  },
  create(context) {
    if (!path.basename(context.filename).endsWith("Presenter.vue")) return {};
    return {
      ImportDeclaration(node) {
        const source = node.source.value;
        if (typeof source !== "string" || node.importKind === "type") return;
        if (
          source === "vue-router" ||
          source.startsWith("@/shared/stores") ||
          (source.startsWith("@/features/") && source.includes("/stores/"))
        ) {
          context.report({
            node,
            messageId: "forbidden",
            data: { filename: path.basename(context.filename), source },
          });
        }
      },
    };
  },
};

const architecture = {
  meta: { name: "architecture" },
  rules: {
    "enforce-layer-order": enforceLayerOrder,
    "no-feature-api-in-pages": noFeatureApiInPages,
    "no-router-or-stores-in-presenters": noRouterOrStoresInPresenters,
  },
};

const accessibilityRules = vuejsAccessibility.configs?.recommended?.rules ?? {};

export default defineConfig(
  { ignores: ["dist/**", "coverage/**", "node_modules/**"] },
  {
    files: ["src/**/*.{ts,vue}"],
    extends: [
      js.configs.recommended,
      ...tseslint.configs.recommended,
      ...pluginVue.configs["flat/recommended"],
    ],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: globals.browser,
      parserOptions: { parser: tseslint.parser },
    },
    plugins: {
      architecture,
      "vuejs-accessibility": vuejsAccessibility,
    },
    rules: {
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
      "architecture/enforce-layer-order": "error",
      "architecture/no-feature-api-in-pages": "error",
      "architecture/no-router-or-stores-in-presenters": "error",
      "vue/no-v-html": "error",
      ...accessibilityRules,
    },
  },
  {
    files: ["tests/**/*.{ts,vue}"],
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: { ...globals.browser, ...globals.node },
    },
    rules: {
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_" },
      ],
    },
  },
  {
    files: [
      "*.config.js",
      "*.config.ts",
      "eslint.config.js",
      "scripts/**/*.mjs",
    ],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: globals.node,
    },
    rules: {
      "architecture/enforce-layer-order": "off",
      "architecture/no-feature-api-in-pages": "off",
      "architecture/no-router-or-stores-in-presenters": "off",
    },
  },
  eslintConfigPrettier,
);
