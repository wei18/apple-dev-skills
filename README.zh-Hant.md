# apple-dev-skills

> 一份**為 AI 編碼代理打造的精選技能目錄**（[Claude Code](https://code.claude.com)）——
> 由一位開發者自身的出貨經驗所建立與蒐集。第一方的 **Apple/Swift**
> 與 **AI 代理協作**技能，外加**以引用方式**彙整的同類最佳**外部**技能外掛
> （歸功於原作者，絕不複製）。
>
> 語言：[English](README.md) · [繁體中文](README.zh-Hant.md)

本倉庫是一個**市集（marketplace）**，內含兩個第一方外掛，並彙整數個外部來源。

## 安裝

> Claude Code 透過**外掛（plugin）**系統來發現共享技能。本倉庫既是
> 市集，也是兩個第一方外掛的所在地。

### A — 市集（最簡單）

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 22 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 12 agent-collaboration skills
```

兩者擇一或全裝皆可。外部來源以相同方式安裝，例如 `/plugin install swiftui-expert@apple-dev-skills`。

### B — 倉庫層級（vendored submodule，已釘選版本）

將其 vendor 並釘選進單一倉庫，接著註冊一個 project-scope 的本機路徑市集，讓
外掛從釘選的 submodule 載入（協作者會被提示信任此工作區）：

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v1.4.0 && cd -
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

單憑一個裸 submodule 是**不會**被發現的——真正載入技能的是市集註冊。

### C — `npx skills`（扁平，無外掛）

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

## 目錄

### apple-dev-skills (22) — Apple/Swift

| Skill | 一句話說明 |
|---|---|
| `swift6-concurrency` | Swift 6 語言模式 + 完整並行檢查；Sendable 為預設 |
| `apple-platform-targets` | 預設 iOS 18 / macOS 15、Xcode 16+；僅在使用最新 OS 限定 API 時才升到 26 |
| `swiftpm-modularization` | 單一 Package、多 target、薄 App、DI composition root、一對一測試 |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot；protocol fake；嚴格／寬容 snapshot 閘門 |
| `xcode-cloud-single-track-ci` | 單軌 Xcode Cloud；PR / Main / Release / Periodic；合併前 PR CI |
| `mise-tool-management` | mise 管理二進位 CLI 工具；dev + CI 共用 `.mise.toml`；macOS 限定 `os` 防護 |
| `oslog-logger-defaults` | `os.Logger`（不用第三方）；subsystem = bundle ID；`.private` 預設 |
| `apple-three-piece-analytics` | ASC Analytics + MetricKit + Game Center；無第三方追蹤；PrivacyInfo 必備 |
| `telemetry-facade-pattern` | 單一 `Telemetry` target、扇出 facade；OSLog / NoOp / MetricKit / GameCenter sink |
| `ai-translated-localization` | 預設 7 種語系；AI 翻譯流程；`Localizable.xcstrings`；完整度閘門 |
| `ios-accessibility-engineering` | SwiftUI 與 UIKit 的 VoiceOver / Dynamic Type / 觸控目標 / Reduce Motion；WCAG 2.2 |
| `swift-dependency-injection` | Protocol 注入 + composition root；environment vs constructor；`@TaskLocal`；Sendable |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch 預算 / 啟動 / 記憶體 / 二進位大小 / MetricKit |
| `apple-public-repo-security` | 公開 iOS/macOS 倉庫的三道防線 + rotate-first 洩漏 SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`，用於隨二進位出貨但不進 diff 的 ID |
| `monetization-sdk-integration` | 新增／升級／稽核變現 SDK；將 `import` 隔離到單一橋接檔 |
| `app-store-review-rejections` | 診斷並預先化解免費 + 廣告 + IAP + CloudKit + GC 的 App Review 退件類型 |
| `asc-api-automation` | 以 `.p8` 簽 ES256 JWT + curl 直呼 ASC REST API — TestFlight、metadata、送審、報表；不用 fastlane |
| `swiftui-interaction-footguns` | 會躲過純程式碼審查的已知 SwiftUI 互動 bug |
| `swiftui-navigation-architecture` | 型別化 `Route` enum + `@Observable` router；value-based `NavigationStack`；每個 transition 的呈現語意（含 macOS fallback）；deep link；分頁各自 path |
| `app-icon-rasterize` | 透過 `qlmanage` 將 1024 SVG 圖示點陣化為 asset-catalog PNG——無需 Homebrew |
| `ios-design-mockup` | 從規格產生單檔 HTML iOS 設計稿——iPhone 外框 + token |

### collaboration-skills (12) — AI 代理流程

| Skill | 一句話說明 |
|---|---|
| `spec-phase-orchestration` | 實作前文件管線；逐節核准 |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer 三角；第一輪外觀問題 inline；limit(N) |
| `leader-developer-handoff-contract` | 派發 sub-agent 時的 5 個必要元素 |
| `agent-impl-notes-log` | sub-agent 任務中持續記錄 impl-notes——決策、偏離、待解問題 |
| `subagent-conflict-detection` | 檢查新 sub-agent 的目標不與進行中的 worktree 重疊 |
| `methodology-pattern-extractor` | 從會議記錄中萃取重複出現 ≥3 次的模式 |
| `session-to-meeting-log` | 將一段 Claude Code session 整併成會議記錄；摘要而非逐字 |
| `pr-diff-verification` | push/PR 前，驗證 `git show --stat HEAD` 與 commit 宣稱一致 |
| `backlog-routing-by-topic` | 依主題將零散點子導向對應 spec 檔的 §Backlog |
| `claude-skill-plugin-packaging` | 散布／安裝 Claude Code 技能——depth-1 規則、plugin + marketplace、彙整 |
| `skill-authoring-patterns` | 疊在 `superpowers:writing-skills` 之上的 Apple/Swift 目錄層——router 描述、首尾段落、兩層引用、基於證據的 CR |
| `github-contribution-workflow` | gh-CLI 貢獻迴圈——PR、issue、GitHub 檔案操作、secret、contribution-flow 倉庫設定；慣例 + 合併前 CLEAN |

### 彙整的外部來源 (5) — 以引用方式，已歸功

此處列出但**並非在此撰寫**；它們從原作者自己的倉庫安裝（你拿到的是
其最新版），並完整歸功。**彙整，不據為己有**：僅列出 MIT 相容、
非重複的外掛——第一方技能只為真正的缺口而寫。
外部來源屬於廣泛的**參考**（「這是 API／這是怎麼建 X」）；第一方
技能位於其下一層，作為**有主見的預設值與出貨實戰故事**
（用 iOS 18、單一 Package、swift-testing + snapshot、OSLog 不用第三方、躲過審查的執行期 bug）。
凡主題重疊處，它們是高度不同，而非重複。

| Plugin | 作者 | 涵蓋範圍 |
|---|---|---|
| [`apple-skills`](https://github.com/vabole/apple-skills) | vabole (MIT) | 廣泛的 Apple 框架——SwiftUI、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit … |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI 模式、Swift Charts、Liquid Glass、Instruments 工具鏈 |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI 陷阱、deprecated-API 觀察清單、iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | 超壓縮溝通模式——削減約 75% token（通用代理行為） |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | 「懶惰資深開發者」模式——強制採用最簡單、最短的解法（通用代理行為） |

## 出處

第一方技能是從 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的
`.claude/skills/` 提煉並通用化而來——一個 spec-first、由 AI-Leader/Developer 打造的
出貨 Apple 平台遊戲作品集——再加上對公開的 Apple / WCAG / Swift 標準的原創撰述。
彙整的外部來源仍屬其作者所有，僅以引用方式呈現。MIT——見 [LICENSE](LICENSE)。

<!-- src-sha: 611aaa20d1e272335606fced5259044b18925f1d -->
