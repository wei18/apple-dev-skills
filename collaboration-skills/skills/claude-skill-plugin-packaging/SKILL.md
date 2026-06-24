---
name: claude-skill-plugin-packaging
description: How to distribute a set of Claude Code skills for reuse across repos/projects, and how to install (consume) them into a project — as a plugin via a marketplace, vendored as a pinned git submodule with committed project-scope settings, or installed globally. Covers the depth-1 discovery rule (why a bare folder/submodule of skills is NOT found), the exact settings.json schema, aggregating other skill repos, and the gotchas. Invoke when sharing skills across projects, wiring a skill plugin into a repo, deciding flat-skills vs plugin, or when asked "why aren't my submodule'd skills showing up / how do I install project skills".
---

# Claude Code Skill Plugin Packaging

## When to invoke

- You have skills in one repo and want them reusable across other repos/projects.
- Wiring an existing skill plugin (e.g. `apple-dev-skills`) into a new project.
- Deciding **flat project skills** vs a **plugin**.
- A submodule/nested folder of skills "isn't being discovered" and you don't know why.
- Aggregating *other people's* skill repos without copy-pasting.
- User asks "how do I share/install skills", "why is my `.claude/skills/<lib>/...` not found".

## The one rule that explains everything: discovery is depth-1

Claude Code discovers **plain project skills only at depth 1**:
`.claude/skills/<skill>/SKILL.md`. It does **not** recurse into subdirectories.

Consequences (each has burned someone):
- A **git submodule** of skills at `.claude/skills/<lib>/` puts SKILL.md at
  `.claude/skills/<lib>/skills/<skill>/SKILL.md` (depth ≥ 2) → **NOT discovered**.
- A bare folder of skills nested one level down → **NOT discovered**.
- An in-repo submodule of a plugin you *also* installed via a marketplace is
  **vestigial** — the marketplace-installed copy is what loads, the submodule does
  nothing for discovery. (This is why a repo can carry `.claude/skills/superpowers`
  yet superpowers actually loads from the plugin cache.)

So: **to share skills across repos, package them as a plugin and distribute via a
marketplace.** A bare submodule alone never works.

## Packaging: make your skills a plugin + marketplace

A repo becomes a Claude Code **plugin** with a manifest, and a **marketplace**
(catalog) with a second manifest. One repo can be both (single-repo model):

```
your-skills-repo/
├── .claude-plugin/
│   ├── plugin.json        # makes it a plugin; "name" becomes the namespace
│   └── marketplace.json   # makes it a marketplace; lists plugins
└── skills/
    └── <skill>/SKILL.md   # one dir per skill
```

`plugin.json` (the `name` is the **plugin** namespace prefix — skills surface as `plugin-name:<skill>`; this is independent of the marketplace name):
```json
{ "name": "your-skills", "version": "0.1.0", "description": "…", "license": "MIT" }
```

The **marketplace** `name` is the catalog identifier used in `/plugin install plugin-name@marketplace-name`. These are two distinct names that happen to be the same string in the single-repo model — that identity is a coincidence, not a requirement. A real-world example where they differ: `"code-formatter@company-tools"` (plugin name = `code-formatter`, marketplace name = `company-tools`).

`marketplace.json` — lists this plugin (and can list MANY plugins from other sources):
```json
{
  "name": "your-skills",
  "owner": { "name": "you" },
  "plugins": [
    { "name": "your-skills", "source": "./", "description": "…", "version": "0.1.0" }
  ]
}
```
`"source": "./"` = the plugin is at the marketplace repo root.

## Installing (consuming) into a project — three models

### A. Global marketplace (simplest, latest)
```
/plugin marketplace add owner/your-skills-repo
/plugin install your-skills@your-skills
```
Loads globally (every project), namespaced. Not pinned per repo.

### B. Vendored submodule + project-scope committed settings (pinned, git-tracked, "comes with the project")

This is the recipe when a specific repo must depend on a **pinned version**,
reproducibly, with **no manual install** for collaborators.

1. Vendor + pin:
   ```
   git submodule add https://github.com/owner/your-skills-repo.git .claude/skills/your-skills
   cd .claude/skills/your-skills && git checkout v0.1.0 && cd -
   ```
2. Commit this to the project's `.claude/settings.json` (the **shared, committed**
   file — not `.claude/settings.local.json`, which is personal/gitignored):
   ```json
   {
     "extraKnownMarketplaces": {
       "your-skills": {
         "source": { "source": "directory", "path": "./.claude/skills/your-skills" }
       }
     },
     "enabledPlugins": { "<plugin-name>@<marketplace-name>": true }
   }
   ```
   Replace `<plugin-name>` with the `name` from the plugin's `plugin.json` and `<marketplace-name>` with the `name` from the marketplace's `marketplace.json`. In the single-repo model these happen to be the same string (e.g. `"your-skills@your-skills": true`), but they are conceptually distinct — the plugin namespace and the catalog identifier.
   - The marketplace `source` for a local dir is an **object** `{"source":"directory","path":"./relative"}` — a **relative** path (resolves against the repo's main checkout). A relative path only resolves because the submodule is itself a git repo.
3. On `git clone --recurse-submodules` + workspace-trust, Claude Code
   auto-registers the marketplace and enables the plugin. Skills load as
   `your-skills:<skill>`. **No `/plugin install` step.**

Why both pieces: the **submodule** pins the exact version (a commit SHA); the
**committed settings.json** is what actually makes Claude Code load it. Either alone
is insufficient (submodule-only = not discovered; settings-only = nothing to point at).

### C. npm — a packaging path some skill sets use (`npx …`); out of scope here.

## Aggregating other skill repos (don't reinvent)

A marketplace is a catalog of plugins from **many sources** — that is the native
aggregation mechanism, no submodule required. Add more entries to `plugins[]`,
each with its own source:

```json
"plugins": [
  { "name": "your-skills",        "source": "./" },
  { "name": "someones-testing",   "source": { "source": "github", "repo": "them/testing-skills" } },
  { "name": "vendored-thing",     "source": { "source": "git-subdir", "url": "https://…", "path": "tools/plugin" } }
]
```
Accepted plugin sources: relative `"./path"` (within the marketplace repo, must
start with `./`), `github` (`repo`,`ref?`,`sha?`), `url` (git URL), `git-subdir`
(`url`,`path`), `npm` (`package`,`version?`). Use a submodule only when you need to
**vendor + pin** another repo's content into yours.

## Gotchas (verified)

- **Bare submodule of skills ≠ discovered** (depth-1 rule). Always pair with a plugin manifest + marketplace registration.
- **`@skills-dir` auto-load** (a plugin folder under `.claude/skills/` loading without registration) is documented but not reliably in use — don't depend on it; register a marketplace.
- **`git commit -a` skips new files** — `plugin.json`/`marketplace.json` are new; `-a` will silently omit them. Use explicit `git add` and verify with `git show --stat`.
- **Marketplace state is per-user** (`~/.claude/plugins/known_marketplaces.json`), but the **committed project `.claude/settings.json` declaration** is what makes it reproducible for everyone on trust.
- **Token cost**: every enabled skill's description is always-on context. ~25 skills ≈ a few thousand tokens per session. Keep the set curated.
- **Relative marketplace paths** only resolve when the marketplace is a git repo (a submodule qualifies); a direct-URL marketplace can't resolve relative plugin sources.

## Verification

- `/reload-plugins` then check the skills list shows `your-skills:<skill>` entries.
- `claude plugin details your-skills@your-skills` lists the bundled skills + scope.
- For model B: `git ls-files .claude/settings.json` (it's committed) and the submodule
  gitlink point at the intended version.
