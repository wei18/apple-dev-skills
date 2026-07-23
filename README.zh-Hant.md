# apple-dev-skills

> 一份**為 AI 編程代理精選的技能目錄**（[Claude Code](https://code.claude.com)）——
> 由一位開發者的實際出貨經驗打造與收集而成。第一方的 **Apple/Swift** 與
> **AI 代理協作**技能，外加以**引用方式**匯集的同類最佳**外部**技能外掛
> （完整歸功於原作者，絕不複製）。
>
> 語言：[English](README.md) · [繁體中文](README.zh-Hant.md)

本 repo 是一個**市集（marketplace）**，托管兩個第一方外掛與數個匯集的外部外掛。

## 安裝

> Claude Code 透過**外掛（plugin）**系統來發現共享技能。本 repo 既是一個
> 市集，也是兩個第一方外掛的家。

### A — 市集（最簡單）

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 25 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 12 agent-collaboration skills
```

安裝其中一個或兩個都裝。外部外掛以相同方式安裝，例如 `/plugin install swiftui-expert@apple-dev-skills`。

### B — repo 層級（vendored 子模組，釘選版本）

將其 vendor 並釘選進單一 repo，再註冊一個 project-scope 的 local-path 市集，讓
外掛從釘選的子模組載入（協作者會被提示信任該工作區）：

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v1.5.0 && cd -
```

`.claude/settings.json`（納入版控）：

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

僅有一個裸子模組**不會**被發現——真正載入技能的是市集註冊。

### C — `npx skills`（扁平式，無外掛）

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

## 目錄

### apple-dev-skills (25) — Apple/Swift

| Skill | 一句話說明 |
|---|---|
| `swift6-concurrency` | Swift 6 語言模式 + 完整並行檢查；預設 Sendable |
| `apple-platform-targets` | 預設 iOS 18 / macOS 15、Xcode 16+；僅在需要 latest-OS-only API 時才升到 26 |
| `swiftpm-modularization` | 單一 Package、多 target、精簡 App、DI composition root、一對一測試 |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot；protocol fake；嚴格/寬容 snapshot 閘門 |
| `xcode-cloud-single-track-ci` | 單軌 Xcode Cloud；PR / Main / Release / Periodic；合併前的 PR CI |
| `mise-tool-management` | mise 管理二進位 CLI 工具；dev 與 CI 共用 `.mise.toml`；macOS-only 的 `os` 防護 |
| `oslog-logger-defaults` | `os.Logger`（不用第三方）；subsystem = bundle ID；預設 `.private` |
| `apple-three-piece-analytics` | ASC Analytics + MetricKit + Game Center；不用第三方追蹤；PrivacyInfo 必備 |
| `telemetry-facade-pattern` | 單一 `Telemetry` target、fan-out facade；OSLog / NoOp / MetricKit / GameCenter sink |
| `ai-translated-localization` | 預設 7 個 locale；AI 翻譯流程；`Localizable.xcstrings`；完整度閘門 |
| `ios-accessibility-engineering` | 為 SwiftUI 與 UIKit 做 VoiceOver / Dynamic Type / 觸控目標 / Reduce Motion；WCAG 2.2 |
| `swift-dependency-injection` | Protocol 注入 + composition root；environment vs constructor；`@TaskLocal`；Sendable |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch 預算 / 啟動 / 記憶體 / 二進位大小 / MetricKit |
| `apple-public-repo-security` | 公開 iOS/macOS repo 的三道防線 + 洩漏優先輪替 SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`，用於「隨二進位出貨但不進 diff」的 ID |
| `monetization-sdk-integration` | 新增/升級/稽核變現 SDK；將 `import` 隔離到單一 bridge 檔 |
| `app-store-review-rejections` | 診斷並預先化解 free + ads + IAP + CloudKit + GC 的 App Review 拒審類別 |
| `asc-api-automation` | 以 `.p8` 產生 ES256 JWT + curl 呼叫 ASC REST API——TestFlight、metadata、送審、報表；不用 fastlane |
| `swiftui-interaction-footguns` | 純程式碼審查漏掉的已知 SwiftUI 互動 bug |
| `swiftui-navigation-architecture` | 型別化 `Route` enum + `@Observable` router；value-based `NavigationStack`；每次轉場的呈現語意含 macOS fallback；deep link；每個 tab 各自的 path |
| `app-icon-rasterize` | 用 `qlmanage` 將 1024 SVG 圖示點陣化為 asset-catalog PNG——不用 Homebrew |
| `ios-design-mockup` | 從規格產生單檔 HTML iOS 設計 mockup——iPhone 框架 + tokens |
| `interactive-simulator-ux-audit` | 用 `idb` 驅動已啟動的 Simulator（tap/describe/screenshot）以捕捉 snapshot 抓不到的 nav/modal/safe-area bug |
| `host-driven-xcuitest-e2e` | 透過 Tuist 的啟動 App XCUITest E2E——專屬 scheme 接線 + macOS 視窗框架點擊驅動 |
| `cloudkit-schema-source-of-truth` | 納入版控的 `.ckdb` + `cktool` 匯出/驗證/部署到 Development；Production 是使用者自持、僅限 Console 的閘門 |

### collaboration-skills (12) — AI 代理流程

| Skill | 一句話說明 |
|---|---|
| `spec-phase-orchestration` | 實作前的文件流水線；逐節逐節核准 |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer 三方；第一輪外觀性 inline；limit(N) |
| `leader-developer-handoff-contract` | 派工子代理時的 5 個必要元素 |
| `agent-impl-notes-log` | 子代理任務進行中的即時 impl-notes——決策、偏離、待解問題 |
| `subagent-conflict-detection` | 檢查新子代理的目標不與進行中的 worktree 重疊 |
| `methodology-pattern-extractor` | 從會議記錄中萃取重複出現 ≥3 次的模式 |
| `session-to-meeting-log` | 將一個 Claude Code session 整併成會議記錄；摘要，非逐字 |
| `pr-diff-verification` | push/PR 前，驗證 `git show --stat HEAD` 與 commit 宣稱相符 |
| `backlog-routing-by-topic` | 依主題將零散想法路由到對應 spec 檔的 §Backlog |
| `claude-skill-plugin-packaging` | 發布/安裝 Claude Code 技能——depth-1 規則、plugin + marketplace、匯集 |
| `skill-authoring-patterns` | 在 `superpowers:writing-skills` 之上的 Apple/Swift 目錄層——router 描述、bookend 章節、兩層式引用、以證據為本的 CR |
| `github-contribution-workflow` | gh-CLI 貢獻循環——PR、issue、GitHub 檔案操作、secrets、contribution-flow repo 設定；慣例 + 合併前 CLEAN |

### 匯集的外部技能 (6) — 以引用方式，完整歸功

於此列出但**非在此撰寫**；它們從原作者自己的 repo 安裝（你取得的是
其最新版本），並完整歸功。**匯集，不據為己有**：僅列出 MIT 相容、
非重複的外掛——第一方技能只為真正的缺口而寫。
外部技能是廣泛的**參考**（「這是 API／這是怎麼建 X」）；第一方技能
位於其下一層，作為**有主張的預設值與已出貨的實戰故事**
（用 iOS 18、單一 Package、swift-testing + snapshot、OSLog 不用第三方、審查漏掉的
執行期 bug）。當主題重疊時，它們差在高度，而非重複。

| Plugin | 作者 | 涵蓋 |
|---|---|---|
| [`apple-skills`](https://github.com/vabole/apple-skills) | vabole (MIT) | 廣泛的 Apple 框架——SwiftUI、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit … |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI 模式、Swift Charts、Liquid Glass、Instruments 工具鏈 |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI 陷阱、已棄用 API 觀察清單、iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | 超壓縮溝通模式——削減約 75% token（通用代理行為） |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | 「懶惰資深開發者」模式——強制最簡最短的解法（通用代理行為） |
| [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) | Ayoub G. (MIT) | 常駐的 ADHD 友善輸出模式——行動優先、編號步驟、每回合重述狀態；相對於 `caveman`（token 壓縮）與 `ponytail`（解法簡化），本項塑造的是結構（通用代理行為） |

## 出處

第一方技能是從 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的
`.claude/skills/` 蒸餾與泛化而來——一個 spec-first、由 AI-Leader/Developer 打造、
已出貨的 Apple 平台遊戲作品集——再加上對公開 Apple / WCAG / Swift 標準的原創撰述。
匯集的外部技能仍是其作者的作品，僅以引用方式呈現。MIT——見 [LICENSE](LICENSE)。

<!-- src-sha: 8b04d1d1cfa8cda2fbd6eabdabaeaec1f1d82343 -->
