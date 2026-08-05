# apple-dev-skills

> 一份**為 AI coding agents 精選的 skills 目錄**（[Claude Code](https://code.claude.com)）——
> 由一位開發者親身出貨經驗打造與收集而成。包含第一方 **Apple/Swift**
> 與 **AI-agent 協作** skills，並以**引用方式**彙整精選的**外部** skill plugins
> （完整標註原作者出處，絕不複製）。
>
> 語言：[English](README.md) · [繁體中文](README.zh-Hant.md)

本 repo 是一個 **marketplace**，內含兩個第一方 plugins 與數個以引用方式彙整的外部 plugins。

## 安裝

> Claude Code 透過 **plugin** 系統探索共享的 skills。本 repo 既是一個
> marketplace，也是兩個第一方 plugins 的所在地。

### A — marketplace（最簡單）

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 25 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 12 agent-collaboration skills
```

可擇一安裝或兩者都裝。外部 plugins 的安裝方式相同，例如 `/plugin install swiftui-expert@apple-dev-skills`。

### B — repo 層級（vendored submodule，釘選版本）

Vendor 並釘選到某個 repo 中，接著註冊一個 project-scope 的 local-path marketplace，
讓 plugins 從釘選的 submodule 載入（協作者會被提示信任該 workspace）：

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v1.6.0 && cd -
```

`.claude/settings.json`（提交到版本庫）：

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

僅有 submodule 本身**不會**被探索到——是 marketplace 註冊讓 skills 得以載入。

### C — `npx skills`（扁平安裝，不經 plugin）

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

> **路徑 C 不包含彙整的外部 plugins。** `npx skills` 只掃描本
> repo 中的 `SKILL.md` 資料夾，從不讀取 `marketplace.json`，因此上述命令
> 只能取得 37 個第一方 skills——6 個外部 plugins 會被靜默略過。
> 若要扁平安裝完整目錄（含外部 plugins，直接從其作者的 repo 拉取）：

```bash
scripts/install-flat.sh -g          # user 層級；拿掉 -g 則為 project 層級
scripts/install-flat.sh --dry-run   # 預覽將執行的 `npx skills add` 命令
```

## 目錄

### apple-dev-skills（25）— Apple/Swift

| Skill | 一句話簡介 |
|---|---|
| `swift6-concurrency` | Swift 6 language mode + 完整並行檢查；預設 Sendable |
| `apple-platform-targets` | 預設 iOS 18 / macOS 15、Xcode 16+；只為 latest-OS-only API 才升到 26 |
| `swiftpm-modularization` | 單一 Package、多 target、瘦 App、DI composition root、測試一對一 |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot；protocol fakes；strict/tolerant snapshot 關卡 |
| `xcode-cloud-single-track-ci` | 單軌 Xcode Cloud；PR / Main / Release / Periodic；pre-merge PR CI |
| `mise-tool-management` | mise 管理 binary CLI 工具；dev 與 CI 共用 `.mise.toml`；macOS-only `os` guard |
| `oslog-logger-defaults` | `os.Logger`（不用第三方）；subsystem = bundle ID；預設 `.private` |
| `apple-three-piece-analytics` | ASC Analytics + MetricKit + Game Center；不用第三方追蹤；PrivacyInfo 必備 |
| `telemetry-facade-pattern` | 單一 `Telemetry` target、fan-out facade；OSLog / NoOp / MetricKit / GameCenter sinks |
| `ai-translated-localization` | 預設 7 個 locales；AI 翻譯流程；`Localizable.xcstrings`；完整度關卡 |
| `ios-accessibility-engineering` | SwiftUI 與 UIKit 的 VoiceOver / Dynamic Type / 觸控目標 / Reduce Motion；WCAG 2.2 |
| `swift-dependency-injection` | Protocol 注入 + composition root；environment vs constructor；`@TaskLocal`；Sendable |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch 預算 / 啟動 / 記憶體 / binary 大小 / MetricKit |
| `apple-public-repo-security` | 公開 iOS/macOS repo 的三道防線 + rotate-first 洩漏 SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`，讓識別碼「進 binary 但不進 diff」 |
| `monetization-sdk-integration` | 新增/升級/稽核變現 SDK；把 `import` 隔離在單一 bridge 檔 |
| `app-store-review-rejections` | 診斷並預防免費 + 廣告 + IAP + CloudKit + GC 的 App Review 拒絕類型 |
| `asc-api-automation` | 用 `.p8` 產 ES256 JWT + curl 打 ASC REST API——TestFlight、metadata、送審、報表；不用 fastlane |
| `swiftui-interaction-footguns` | 純代碼審查抓不到的已知 SwiftUI 互動 bug |
| `swiftui-navigation-architecture` | 型別化 `Route` enum + `@Observable` router；value-based `NavigationStack`；逐轉場的呈現語義與 macOS fallback；深層連結；分 tab paths |
| `app-icon-rasterize` | 用 `qlmanage` 把 1024 SVG icon 點陣化成 asset-catalog PNG——不用 Homebrew |
| `ios-design-mockup` | 從 spec 產生單檔 HTML iOS 設計 mockup——iPhone 外框 + tokens |
| `interactive-simulator-ux-audit` | 用 `idb`（tap/describe/screenshot）驅動已開機的 Simulator，抓 snapshot 抓不到的導航/modal/safe-area bug |
| `host-driven-xcuitest-e2e` | 透過 Tuist 的啟動式 XCUITest E2E——專用 scheme 接線 + macOS 視窗座標點擊驅動 |
| `cloudkit-schema-source-of-truth` | 提交入庫的 `.ckdb` + `cktool` export/validate/deploy 到 Development；Production 是使用者掌控、僅限 Console 的關卡 |

### collaboration-skills（12）— AI-agent 流程

| Skill | 一句話簡介 |
|---|---|
| `spec-phase-orchestration` | 實作前文件 pipeline；逐節核准 |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer 三角；第一輪 cosmetic 直接 inline 處理；limit(N) |
| `leader-developer-handoff-contract` | 派工 sub-agent 時的 5 個必備要素 |
| `agent-impl-notes-log` | Sub-agent 任務期間的即時 impl-notes——決策、偏離、待決問題 |
| `subagent-conflict-detection` | 檢查新 sub-agent 的目標不與進行中的 worktree 重疊 |
| `methodology-pattern-extractor` | 從會議記錄萃取出現 ≥3 次的模式 |
| `session-to-meeting-log` | 把 Claude Code session 整併成會議記錄；摘要而非逐字稿 |
| `pr-diff-verification` | Push/PR 前，驗證 `git show --stat HEAD` 與 commit 宣稱相符 |
| `backlog-routing-by-topic` | 把零散想法依主題導向對應 spec 檔的 §Backlog |
| `claude-skill-plugin-packaging` | 發布/安裝 Claude Code skills——depth-1 規則、plugin + marketplace、彙整 |
| `skill-authoring-patterns` | 在 `superpowers:writing-skills` 之上的 Apple/Swift 目錄層——router descriptions、bookend sections、two-tier references、evidence-based CR |
| `github-contribution-workflow` | gh-CLI 貢獻迴圈——PR、issue、GitHub 檔案操作、secrets、貢獻流程 repo 設定；慣例 + CLEAN-before-merge |

### 彙整的外部 plugins（6）— 引用方式，標註出處

在此列出但**非本 repo 所作**；它們從各自作者的 repo 安裝（你拿到的是
其最新版本），完整標註出處。**彙整而不據為己有**：只列 MIT 相容、
不重複的 plugins——第一方 skills 只為真正的缺口而寫。
外部 plugins 是廣度型**參考**（「API 長這樣 / X 要怎麼做」）；
第一方 skills 位於其下一層，是**有立場的預設值與出貨實戰記錄**
（用 iOS 18、單一 Package、swift-testing + snapshot、OSLog 不用第三方、
審查漏掉的 runtime bug）。主題重疊處，差異在高度而非重複。

| Plugin | 作者 | 涵蓋範圍 |
|---|---|---|
| [`apple-skills`](https://github.com/vabole/apple-skills) | vabole (MIT) | 廣泛 Apple frameworks——SwiftUI、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit… |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI patterns、Swift Charts、Liquid Glass、Instruments 工具鏈 |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI 陷阱、已棄用 API 觀察清單、iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | 超壓縮溝通模式——省下約 75% tokens（通用 agent 行為） |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | 「懶惰資深工程師」模式——強制最簡、最短的解法（通用 agent 行為） |
| [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) | Ayoub G. (MIT) | 常駐 ADHD 友善輸出模式——行動優先、編號步驟、每回合重述狀態；相對於 `caveman`（token 壓縮）與 `ponytail`（解法簡潔），本 plugin 塑造的是結構（通用 agent 行為） |

## 來源

第一方 skills 由 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的
`.claude/skills/` 蒸餾並通用化而來——那是一個 spec-first、以 AI-Leader/Developer 模式打造、
已出貨的 Apple 平台遊戲作品集——再加上對公開 Apple / WCAG / Swift 標準的原創整理。
彙整的外部 plugins 仍屬其作者的作品，僅以引用方式呈現。MIT——見 [LICENSE](LICENSE)。

<!-- src-sha: 7d385704d713ec6bce7a0196ebfd113ef71622f6 -->
