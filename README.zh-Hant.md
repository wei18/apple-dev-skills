# apple-dev-skills

> 一份**為 AI 編程代理打造的精選技能目錄**（[Claude Code](https://code.claude.com)）——
> 源自一位開發者自身的實戰出貨經驗，建構並彙整而成。涵蓋第一方的 **Apple/Swift**
> 與 **AI-代理協作**技能，再加上**以引用方式**彙整的同類最佳**外部**技能外掛
>（完整標註原作者，絕不複製）。
>
> English：[`README.md`](README.md)

本 repo 是一個托管兩個第一方外掛與數個彙整外部外掛的**市集（marketplace）**。

## 安裝

> Claude Code 透過**外掛（plugin）**系統來探索共享技能。本 repo 既是市集，
> 也是兩個第一方外掛的所在地。

### A — 市集（最簡單）

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 20 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 10 agent-collaboration skills
```

可任選其一或兩者皆裝。外部外掛安裝方式相同，例如 `/plugin install swiftui-expert@apple-dev-skills`。

### B — repo 層級（內嵌 submodule，釘選版本）

將其內嵌並釘選進單一 repo，接著註冊一個 project-scope 的本機路徑市集，
讓外掛從釘選的 submodule 載入（協作者會被提示信任此 workspace）：

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v1.2.0 && cd -
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

單靠一個裸 submodule **不會**被探索到——是市集的註冊動作才載入這些技能。

### C — `npx skills`（扁平化，不走外掛）

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

## 目錄

### apple-dev-skills（20）— Apple/Swift

| Skill | 一句話說明 |
|---|---|
| `swift6-concurrency` | Swift 6 語言模式 + 完整並行檢查；Sendable 預設啟用 |
| `apple-platform-targets` | 預設 iOS 18 / macOS 15、Xcode 16+；僅在使用最新 OS 專屬 API 時才升至 26 |
| `swiftpm-modularization` | 單一 Package、多 target、薄 App、DI composition root、測試一對一 |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot；protocol fakes；嚴格/容忍式 snapshot gate |
| `xcode-cloud-single-track-ci` | 單軌 Xcode Cloud；PR / Main / Release / Periodic；合併前 PR CI |
| `mise-tool-management` | 由 mise 管理二進位 CLI 工具；開發與 CI 共用 `.mise.toml`；macOS-only `os` guard |
| `oslog-logger-defaults` | `os.Logger`（不用第三方）；subsystem = bundle ID；`.private` 預設 |
| `apple-three-piece-analytics` | ASC Analytics + MetricKit + Game Center；不用第三方追蹤；PrivacyInfo 必備 |
| `telemetry-facade-pattern` | 單一 `Telemetry` target、fan-out facade；OSLog / NoOp / MetricKit / GameCenter sinks |
| `ai-translated-localization` | 預設 7 種語系；AI 翻譯流程；`Localizable.xcstrings`；完整性 gate |
| `ios-accessibility-engineering` | 為 SwiftUI 與 UIKit 提供 VoiceOver / Dynamic Type / 觸控目標 / Reduce Motion；WCAG 2.2 |
| `swift-dependency-injection` | Protocol 注入 + composition root；environment 對比 constructor；`@TaskLocal`；Sendable |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch 預算 / 啟動 / 記憶體 / 二進位大小 / MetricKit |
| `apple-public-repo-security` | 公開 iOS/macOS repo 的三道防線 + 外洩優先輪替 SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`，達成隨二進位出貨但不入 diff 的 ID |
| `monetization-sdk-integration` | 新增/升級/稽核變現 SDK；將 `import` 隔離到單一 bridge 檔 |
| `app-store-review-rejections` | 為免費 + 廣告 + IAP + CloudKit + GC 診斷並預先化解 App Review 退件類別 |
| `swiftui-interaction-footguns` | 會躲過純程式碼審查的已知 SwiftUI 互動 bug |
| `app-icon-rasterize` | 透過 `qlmanage` 將 1024 SVG 圖示點陣化為 asset-catalog PNG——免 Homebrew |
| `ios-design-mockup` | 由規格產出單檔 HTML iOS 設計 mockup——iPhone 外框 + tokens |

### collaboration-skills（12）— AI 代理流程

| Skill | 一句話說明 |
|---|---|
| `spec-phase-orchestration` | 實作前的文件管線；逐段審核 |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer 三角；第 1 輪外觀問題行內處理；limit(N) |
| `leader-developer-handoff-contract` | 派發 sub-agent 時的 5 個必備要素 |
| `agent-impl-notes-log` | sub-agent 任務進行中的 impl-notes——決策、偏離、待解問題 |
| `subagent-conflict-detection` | 檢查新 sub-agent 的目標不與進行中的 worktree 重疊 |
| `methodology-pattern-extractor` | 從會議紀錄中萃取重複出現 ≥3 次的模式 |
| `session-to-meeting-log` | 將一段 Claude Code session 整併為會議紀錄；摘要而非逐字 |
| `pr-diff-verification` | 在 push/PR 前，驗證 `git show --stat HEAD` 與 commit 宣稱相符 |
| `backlog-routing-by-topic` | 依主題將零散點子導向對應 spec 檔的 §Backlog |
| `claude-skill-plugin-packaging` | 散布/安裝 Claude Code 技能——depth-1 規則、外掛 + 市集、彙整 |
| `skill-authoring-patterns` | 在 `superpowers:writing-skills` 之上的 Apple/Swift 目錄層——router 描述、bookend 區段、兩層 references、以證據為本的 CR |
| `github-contribution-workflow` | gh-CLI 貢獻迴圈——PR、issue、GitHub 檔案操作、secrets、contribution-flow repo 設定；慣例 + 合併前 CLEAN |

### 彙整外部（5）— 以引用方式列出，已標註原作者

此處列出但**非於此撰寫**；它們從各原作者自己的 repo 安裝（你會取得
其最新版），並完整標註出處。**彙整，而非占用**：僅列出與 MIT 相容、
無重複的外掛——第一方技能只為真正的空缺而撰寫。

| Plugin | 作者 | 涵蓋範圍 |
|---|---|---|
| [`apple-skills`](https://github.com/vabole/apple-skills) | vabole (MIT) | 廣泛的 Apple 框架——SwiftUI、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit … |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI 模式、Swift Charts、Liquid Glass、Instruments 工具鏈 |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI 陷阱、已棄用 API 觀察清單、iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | 超壓縮溝通模式——削減約 75% token（通用代理行為） |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | 「懶惰資深開發者」模式——強制採用最簡、最短的解法（通用代理行為） |

## 出處

第一方技能是從 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的
`.claude/skills/` 中提煉並泛化而來——一個 spec-first、由 AI-Leader/Developer 建構的
出貨型 Apple 平台遊戲作品集——再加上對公開 Apple / WCAG / Swift 標準的原創整理。
彙整的外部外掛仍屬其各自作者的作品，僅以引用方式呈現。MIT——詳見 [LICENSE](LICENSE)。

<!-- src-sha: 0a79ccfebb996986a982f1087becf65f996f157e -->
