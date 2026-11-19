// ESLint, flat config, for the plain JavaScript the app owns.
//
// The rule that matters here is `no-undef`: the finder's star click used a
// variable that did not exist, threw, and silently did nothing for a session.
// A page's own <script> is checked by `astro check` (TypeScript), which reads
// the .astro file; this file checks the shared modules, the page scripts and
// the check scripts.
//
//   npx eslint src/lib src/scripts tests scripts
//
// Only the rules that name a fault this project has had are errors. Warnings
// are the tidy-up that should not block a commit.

const browser = {
  document: "readonly",
  window: "readonly",
  location: "readonly",
  localStorage: "readonly",
  fetch: "readonly",
  Blob: "readonly",
  URL: "readonly",
  URLSearchParams: "readonly",
  Response: "readonly",
  setTimeout: "readonly",
  clearTimeout: "readonly",
  console: "readonly",
};
const node = { process: "readonly", console: "readonly", URL: "readonly", Buffer: "readonly" };

const rules = {
  "no-undef": "error",
  "no-redeclare": "error",
  "no-dupe-keys": "error",
  "no-unreachable": "error",
  "no-unused-vars": ["warn", { args: "none", varsIgnorePattern: "^_" }],
};

export default [
  {
    files: ["src/lib/**/*.js", "src/scripts/**/*.js"],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: "module",
      // PlateMath is loaded as a plain script by the lab page before its own
      // module runs; it is a deliberate global, not a missing import.
      globals: { ...browser, ...node, PlateMath: "readonly" },
    },
    rules,
  },
  {
    // The check scripts run inside page.evaluate(), so both worlds are present.
    files: ["scripts/**/*.mjs", "tests/**/*.mjs"],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: "module",
      globals: { ...browser, ...node },
    },
    rules,
  },
];
