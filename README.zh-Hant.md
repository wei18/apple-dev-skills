# apple-dev-skills

> 一份**為 AI 編程代理（[Claude Code](https://code.claude.com)）整理的技能目錄** —
> 由一位開發者根據自身的實際出貨經驗打造與蒐集。第一方的 **Apple/Swift**
> 與 **AI 代理協作**技能，外加以**引用方式**彙整的同類最佳**外部**技能外掛
> （完整標註原作者，絕不複製）。
>
> 繁體中文：[`README.zh-Hant.md`](README.zh-Hant.md)

本倉庫是一個**市集（marketplace）**，托管兩個第一方外掛與數個彙整的外部外掛。

## 安裝

> Claude Code 透過**外掛**系統來發現共享技能。本倉庫既是市集，
> 也是兩個第一方外掛的所在地。

### A — 市集（最簡單）

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 20 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 10 agent-collaboration skills
```

任選其一或兩者皆裝。外部外掛的安裝方式相同，例如 `/plugin install swiftui-expert@apple-dev-skills`。

### B — 倉庫層級（vendored submodule，已釘選版本）

將其 vendor 並釘選到單一倉庫中，接著註冊一個專案範圍的本機路徑市集，使
外掛從釘選的 submodule 載入（協作者會被提示信任此工作區）：

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v1.2.0 && cd -
```

`.claude/settings.json`（已提交）：

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

光有裸 submodule **無法**被發現 — 是市集註冊在載入這些技能。

### C — `npx skills`（扁平、無外掛）

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

## 目錄

### apple-dev-skills (20) — Apple/Swift

| Skill | 一句話說明 |
|---|---|
| `swift6-concurrency` | Swift 6 語言模式 + 完整並行檢查；預設 Sendable |
| `apple-platform-targets` | 預設 iOS 18 / macOS 15、Xcode 16+；僅在使用最新版 OS 專屬 API 時才升至 26 |
| `swiftpm-modularization` | 單一 Package、多 target、薄 App、DI 組裝根（composition root）、測試一對一 |
| `swift-testing-baseline` | swift-testing + pointfreeco 快照；協定 fake；嚴格／寬鬆快照閘門 |
| `xcode-cloud-single-track-ci` | 單軌 Xcode Cloud；PR / Main / Release / Periodic；合併前 PR CI |
| `mise-tool-management` | mise 管理二進位 CLI 工具；開發與 CI 共用 `.mise.toml`；macOS-only `os` 守衛 |
| `oslog-logger-defaults` | `os.Logger`（不用第三方）；subsystem = bundle ID；預設 `.private` |
| `apple-three-piece-analytics` | ASC Analytics + MetricKit + Game Center；不用第三方追蹤；PrivacyInfo 為必要項 |
| `telemetry-facade-pattern` | 單一 `Telemetry` target、扇出 facade；OSLog / NoOp / MetricKit / GameCenter sink |
| `ai-translated-localization` | 預設 7 種語系；AI 翻譯流程；`Localizable.xcstrings`；完整度閘門 |
| `ios-accessibility-engineering` | 為 SwiftUI 與 UIKit 提供 VoiceOver / Dynamic Type / 觸控目標 / Reduce Motion；WCAG 2.2 |
| `swift-dependency-injection` | 協定注入 + 組裝根；environment 對比建構子；`@TaskLocal`；Sendable |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch 預算 / 啟動 / 記憶體 / 二進位大小 / MetricKit |
| `apple-public-repo-security` | 公開 iOS/macOS 倉庫的三道防線 + 洩漏優先輪替 SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`，用於隨二進位出貨但不進 diff 的 ID |
| `monetization-sdk-integration` | 新增／升級／稽核變現 SDK；將 `import` 隔離到單一橋接檔 |
| `app-store-review-rejections` | 診斷並預先化解免費 + 廣告 + IAP + CloudKit + GC 的 App 審查駁回類型 |
| `swiftui-interaction-footguns` | 會躲過純程式碼審查的已知 SwiftUI 互動 bug |
| `app-icon-rasterize` | 透過 `qlmanage` 將 1024 SVG 圖示點陣化為 asset-catalog PNG — 不用 Homebrew |
| `ios-design-mockup` | 從規格產生單檔 HTML iOS 設計樣稿 — iPhone 外框 + tokens |

### collaboration-skills (11) — AI 代理流程

| Skill | 一句話說明 |
|---|---|
| `spec-phase-orchestration` | 實作前的文件流水線；逐節核可 |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer 三方；第一輪外觀問題以 inline 處理；limit(N) |
| `leader-developer-handoff-contract` | 派遣 sub-agent 時的 5 項必備要素 |
| `agent-impl-notes-log` | sub-agent 任務進行中的即時 impl-notes — 決策、偏離、待解問題 |
| `subagent-conflict-detection` | 檢查新 sub-agent 的目標不與進行中的 worktree 重疊 |
| `methodology-pattern-extractor` | 從會議記錄中萃取重複出現 ≥3 次的模式 |
| `session-to-meeting-log` | 將一次 Claude Code session 整理成會議記錄；摘要而非逐字 |
| `pr-diff-verification` | 在 push/PR 前，驗證 `git show --stat HEAD` 與該 commit 的宣稱相符 |
| `backlog-routing-by-topic` | 依主題將零散想法路由到對應規格檔的 §Backlog |
| `claude-skill-plugin-packaging` | 散布／安裝 Claude Code 技能 — depth-1 規則、外掛 + 市集、彙整 |
| `skill-authoring-patterns` | 在 `superpowers:writing-skills` 之上的 Apple/Swift 目錄層 — 路由式描述、首尾呼應段落、兩層式 references、以證據為本的 CR |

### 彙整的外部外掛 (5) — 以引用方式，標註出處

此處僅列出但**非於此處撰寫**；它們從各自作者的倉庫安裝（你取得的是
其最新版本），並完整標註出處。**彙整，而非佔為己有**：僅列出 MIT 相容、
非重複的外掛 — 第一方技能只為真正的缺口而寫。

| Plugin | 作者 | 涵蓋範圍 |
|---|---|---|
| [`apple-skills`](https://github.com/vabole/apple-skills) | vabole (MIT) | 廣泛的 Apple 框架 — SwiftUI、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit … |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI 模式、Swift Charts、Liquid Glass、Instruments 工具鏈 |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI 陷阱、棄用 API 觀察清單、iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | 超壓縮溝通模式 — 削減約 75% 的 token（通用代理行為） |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | 「懶散資深開發者」模式 — 強制採用最簡單、最短的解法（通用代理行為） |

## 出處

第一方技能是從 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的
`.claude/skills/` 中提煉並通用化而來 — 那是一個規格優先、由 AI-Leader/Developer
打造的出貨級 Apple 平台遊戲作品集 — 外加對公開 Apple / WCAG / Swift 標準的原創整理。
彙整的外部外掛仍屬其作者的作品，僅以引用方式呈現。MIT — 見 [LICENSE](LICENSE)。

<!-- src-sha: 52a8e48e14caa462bce61b83e70c200d5cc9a1d5 -->
