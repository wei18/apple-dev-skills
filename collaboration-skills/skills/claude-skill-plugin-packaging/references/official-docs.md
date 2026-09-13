Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Create plugins | https://code.claude.com/docs/en/plugins | Native mechanism section; Packaging (`plugin.json` name = namespace) |
| Create and distribute a plugin marketplace | https://code.claude.com/docs/en/plugin-marketplaces#plugin-sources | Aggregating: accepted plugin source schema and version gates (`pluginRoot` >=2.1.239, `archive` >=2.1.224, `command` >=2.1.229); marketplace source takes `ref` but not `sha` |
| Create and distribute a plugin marketplace | https://code.claude.com/docs/en/plugin-marketplaces#relative-paths | Gotcha: relative paths fail only for direct-URL marketplaces; "external" means any plugin source other than a relative path |
| Discover and install prebuilt plugins through marketplaces | https://code.claude.com/docs/en/discover-plugins#configure-team-marketplaces | "As of Claude Code v2.1.195, adding the marketplace doesn't install plugins that come from an external source..." |
| All settings | https://code.claude.com/docs/en/settings-reference#extraknownmarketplaces | `extraKnownMarketplaces` JSON shape; "`directory` ... for development only" |
| Plugins reference | https://code.claude.com/docs/en/plugins-reference#skills-directory-plugins | Depth-1 exception; Model D (`<name>@skills-dir`, trust, primary working directory, MCP/LSP/monitor limits); verification via `claude plugin details` / `claude plugin list` |
| Error reference | https://code.claude.com/docs/en/errors#marketplace-is-registered-from-an-untrusted-source | Gotcha on reserved marketplace names: an already-registered marketplace reports an error, it doesn't stop silently |
| Extend Claude with skills | https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short | Gotcha "Token cost": listing budget; "Plugin skills are not affected by `skillOverrides`" |
| vercel-labs/skills README (upstream of `npx skills`) | https://github.com/vercel-labs/skills#plugin-manifest-discovery | `npx skills` does read `marketplace.json` / `plugin.json` but only follows declared local skill paths, so externals are skipped |
| Agent Skills | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | Gotcha "name containing claude": reserved words "anthropic", "claude" on the platform upload path |
