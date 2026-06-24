# apple-dev-skills

> 一份**為 AI 編碼代理打造的精選技能目錄**（[Claude Code](https://code.claude.com)）——
> 由一位開發者親身的實戰出貨經驗建構與蒐集而成。涵蓋第一方的 **Apple/Swift**
> 與 **AI 代理協作**技能，再加上以**引用方式**聚合的同類最佳**外部**技能 plugin
> （完整標註原作者，絕不複製）。
>
> English：[`README.md`](README.md)

本 repo 是單一 **marketplace**，託管兩個第一方 plugin 與數個聚合的外部 plugin。

## 安裝

> Claude Code 透過 **plugin** 系統來發現共享技能。本 repo 既是一個
> marketplace，也是兩個第一方 plugin 的所在地。

### A — marketplace（最簡單）

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 20 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 10 agent-collaboration skills
```

任選其一或兩者皆裝。外部 plugin 的安裝方式相同，例如 `/plugin install swiftui-expert@apple-dev-skills`。

### B — repo 層級（vendored submodule，釘選版本）

將其 vendor 並釘選進單一 repo，接著註冊一個 project-scope 的本機路徑 marketplace，
讓 plugin 從釘選的 submodule 載入（協作者會被提示信任此 workspace）：

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v1.0.0 && cd -
```

`.claude/settings.json`（已提交版控）：

```json
{
  "extraKnownMarketplaces": {
    "apple-dev-skills": { "source": { "source": "directory", "path": "./.claude/skills/apple-dev-skills" } }
  },
  "enabledPlugins": {
    "apple-dev-skills@apple-dev-skills": true,
    "collaboration-skills@apple-dev-skills": true
  }
}
```

單純一個 submodule **不會**被發現——真正載入技能的是 marketplace 註冊。

### C — `npx skills`（扁平，無 plugin）

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

## 目錄

### apple-dev-skills (20) — Apple/Swift

| Skill | 一句話說明 |
|---|---|
| `swift6-concurrency` | Swift 6 語言模式 + 完整並行檢查；Sendable 為預設 |
| `apple-platform-targets` | 預設 iOS 18 / macOS 15、Xcode 16+；僅在需要最新 OS 專屬 API 時才升到 26 |
| `swiftpm-modularization` | 單一 Package、多 target、薄 App、DI composition root、測試一對一 |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot；protocol fake；嚴格/寬容的 snapshot gate |
| `xcode-cloud-single-track-ci` | 單軌 Xcode Cloud；PR / Main / Release / Periodic；merge 前的 PR CI |
| `mise-tool-management` | mise 管理二進位 CLI 工具；dev 與 CI 共用 `.mise.toml`；macOS-only 的 `os` 守門 |
| `oslog-logger-defaults` | `os.Logger`（不用第三方）；subsystem = bundle ID；`.private` 為預設 |
| `apple-three-piece-analytics` | ASC Analytics + MetricKit + Game Center；不用第三方追蹤；PrivacyInfo 為必備 |
| `telemetry-facade-pattern` | 單一 `Telemetry` target、fan-out facade；OSLog / NoOp / MetricKit / GameCenter sink |
| `ai-translated-localization` | 預設 7 個語系；AI 翻譯流程；`Localizable.xcstrings`；完整性 gate |
| `ios-accessibility-engineering` | SwiftUI 與 UIKit 的 VoiceOver / Dynamic Type / 觸控目標 / Reduce Motion；WCAG 2.2 |
| `swift-dependency-injection` | Protocol 注入 + composition root；environment vs constructor；`@TaskLocal`；Sendable |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch 預算 / 啟動 / 記憶體 / 二進位大小 / MetricKit |
| `apple-public-repo-security` | 公開 iOS/macOS repo 的三道防線 + 先輪替的洩漏 SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`，把 ID 出貨進二進位但留在 diff 之外 |
| `monetization-sdk-integration` | 新增/升級/稽核變現 SDK；把 `import` 隔離在單一橋接檔 |
| `app-store-review-rejections` | 針對 free + ads + IAP + CloudKit + GC 診斷並預先化解 App Review 退件類型 |
| `swiftui-interaction-footguns` | 純程式碼審查會漏掉的已知 SwiftUI 互動 bug |
| `app-icon-rasterize` | 透過 `qlmanage` 把 1024 的 SVG icon 點陣化成 asset catalog PNG——不用 Homebrew |
| `ios-design-mockup` | 由規格產生單檔 HTML 的 iOS 設計 mockup——iPhone 框架 + tokens |

### collaboration-skills (10) — AI 代理流程

| Skill | 一句話說明 |
|---|---|
| `spec-phase-orchestration` | 實作前的文件流水線；逐節核准 |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer 三人組；第一輪外觀問題就地處理；limit(N) |
| `leader-developer-handoff-contract` | 派發 sub-agent 時的 5 個必備要素 |
| `agent-impl-notes-log` | sub-agent 任務進行中的 impl-notes——決策、偏離、待解問題 |
| `subagent-conflict-detection` | 檢查新 sub-agent 的目標不會與進行中的 worktree 重疊 |
| `methodology-pattern-extractor` | 從會議記錄中萃取重複出現 ≥3 次的模式 |
| `session-to-meeting-log` | 將一次 Claude Code session 整理成會議記錄；摘要而非逐字 |
| `pr-diff-verification` | push/PR 前，驗證 `git show --stat HEAD` 與 commit 宣稱相符 |
| `backlog-routing-by-topic` | 依主題把零散想法路由到對應 spec 檔的 §Backlog |
| `claude-skill-plugin-packaging` | 散布/安裝 Claude Code 技能——depth-1 規則、plugin + marketplace、聚合 |

### 聚合的外部技能 (5) — 以引用方式，標註原作者

此處列出但**並非在此撰寫**；它們從原作者自己的 repo 安裝（你拿到的是
他們的最新版），並完整標註。**聚合，而非佔用**：只列出與 MIT 相容、
非重複的 plugin——第一方技能僅針對真正的缺口才撰寫。

| Plugin | 作者 | 涵蓋範圍 |
|---|---|---|
| [`apple-skills`](https://github.com/vabole/apple-skills) | vabole (MIT) | 廣泛的 Apple 框架——SwiftUI、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit … |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI 模式、Swift Charts、Liquid Glass、Instruments 工具鏈 |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI 陷阱、已棄用 API 觀察清單、iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | 超壓縮溝通模式——削減約 75% 的 token（通用 agent 行為） |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | 「懶散資深開發者」模式——強制採用最簡、最短的解法（通用 agent 行為） |

## 來源出處

第一方技能是從 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的
`.claude/skills/` 提煉並通用化而來——一個 spec-first、由 AI-Leader/Developer 建構、
出貨中的 Apple 平台遊戲作品集——再加上對公開的 Apple / WCAG / Swift 標準的原創撰寫。
聚合的外部技能仍屬其作者的作品，僅以引用方式呈現。MIT——見 [LICENSE](LICENSE)。

<!-- src-sha: 010c540106cd90092baa4873f0bd0a14905dbc67 -->
