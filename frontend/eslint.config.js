import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import eslintConfigPrettier from "eslint-config-prettier/flat";
import pluginVue from "eslint-plugin-vue";
import vuejsAccessibility from "eslint-plugin-vuejs-accessibility";
import globals from "globals";
import tseslint from "typescript-eslint";

const sourceMarker = "/src/";

// The allowed domain DAG generates the domain-to-domain boundary check.
const domainDependencies = {
  decisions: ["value-types", "sources"],
  proposals: ["value-types", "sources"],
  tasks: ["documents", "budget"],
  approvals: ["sources"],
};

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
  return {
    ImportDeclaration: inspect,
    ExportNamedDeclaration: inspect,
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
          const allowedDependencies = domainDependencies[importer.name] ?? [];
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

export default tseslint.config(
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
