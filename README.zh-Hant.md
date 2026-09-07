# apple-dev-skills

> 一份**用 AI coding agent（[Claude Code](https://code.claude.com)）vibe coding iOS（與 Apple 生態系）App 的技能目錄**
> —— 為獨立開發者與小型團隊而寫，把一個點子帶到 App Store 上架。第一方技能分兩半：**Apple/Swift**
> 管你在做什麼，**harness engineering** 管你怎麼駕馭那個在做事的 agent —— 派工、審查、出貨。
> 兩者都是帶立場的預設值與實際上架的戰場故事，並受一道一致性把關。另以**引用方式**彙整
> 同類最佳的**外部**技能 plugin（完整標註原作者，絕不複製）。
>
> 語言：[English](README.md) · [繁體中文](README.zh-Hant.md)

本 repo 是單一 **marketplace**，收錄兩個第一方 plugin 與數個彙整而來的外部 plugin。

## 安裝

> 技能會依其 `description:` 自行觸發——裝好之後，直接描述你的任務即可。

### A —— marketplace（最簡單）

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 25 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 12 agent-collaboration skills
```

裝其中一個或兩個都裝皆可。外部 plugin 的安裝方式相同，例如 `/plugin install swiftui-expert@apple-dev-skills`。

### B —— repo 層級（vendored submodule，鎖定版本）

在單一 repo 內 vendor 並鎖版，接著註冊一個 project-scope 的 local-path marketplace，
讓 plugin 從鎖定的 submodule 載入（協作者會被提示信任該 workspace）：

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v1.6.0 && cd -
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

單靠一個 submodule **不會**被探索到——真正載入技能的是 marketplace 註冊。

### C —— `npx skills`（平鋪，不走 plugin）

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

> **路徑 C 不包含彙整而來的外部 plugin。** `npx skills` 確實會讀取本 repo 的
> `marketplace.json` / `plugin.json`，但只跟隨本地宣告的技能路徑——它不會抓取外部
> plugin 的遠端 `github` / `git-subdir` 來源，因此上述指令只涵蓋 37 個第一方技能；
> 6 個外部 plugin 會被靜默略過。若要平鋪安裝整份目錄（含外部 plugin，從原作者的 repo 拉取）：

```bash
scripts/install-flat.sh -g          # user-level; drop -g for project-level
scripts/install-flat.sh --dry-run   # preview the `npx skills add` commands
```

> 新安裝的技能最容易第一個失去描述：Claude Code 的技能清單有 context 預算，
> 溢出時會從最少被呼叫的技能開始丟棄描述。執行 `/doctor` 檢查清單的成本；
> 若太吃緊，可在 settings 調整 `skillListingBudgetFraction` / `skillOverrides`。

## 目錄

- **Spec** 流程 → `spec-phase-orchestration`
- **Bootstrap** 專案 → `apple-platform-targets`
- **Build** UI → `swiftui-navigation-architecture`
- **Test** 測試 → `swift-testing-baseline`
- **Ship** 上架 → `asc-api-automation`
- **Operate** 營運 → `apple-three-piece-analytics`

完整索引見下方表格。

### apple-dev-skills（25）—— Apple/Swift

| Skill | 一句話說明 |
|---|---|
| `swift6-concurrency` | Swift 6 語言模式 + 完整 concurrency 檢查；預設 Sendable |
| `apple-platform-targets` | 預設 iOS 18 / macOS 15、Xcode 16+；只有為了 latest-OS-only API 才升到 26 |
| `swiftpm-modularization` | 單一 Package、多 target、薄 App、DI composition root、測試一對一 |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot；protocol fake；嚴格/寬鬆 snapshot 把關 |
| `xcode-cloud-single-track-ci` | 單軌 Xcode Cloud；PR / Main / Release / Periodic；merge 前的 PR CI |
| `mise-tool-management` | 以 mise 管理二進位 CLI 工具；開發與 CI 共用 `.mise.toml`；macOS-only `os` guard |
| `oslog-logger-defaults` | `os.Logger`（不用第三方）；subsystem = bundle ID；預設 `.private` |
| `apple-three-piece-analytics` | ASC Analytics + MetricKit + Game Center；不用第三方追蹤；PrivacyInfo 必備 |
| `telemetry-facade-pattern` | 單一 `Telemetry` target、fan-out facade；OSLog / NoOp / MetricKit / GameCenter sink |
| `ai-translated-localization` | 預設 7 個語系；AI 翻譯流程；`Localizable.xcstrings`；完整度把關 |
| `ios-accessibility-engineering` | SwiftUI 與 UIKit 的 VoiceOver / Dynamic Type / 觸控目標 / Reduce Motion；WCAG 2.2 |
| `swift-dependency-injection` | Protocol 注入 + composition root；environment vs constructor；`@TaskLocal`；Sendable |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch 預算 / 啟動 / 記憶體 / 二進位大小 / MetricKit |
| `apple-public-repo-security` | 公開 iOS/macOS repo 的三道防線 + rotate-first 洩漏處理 SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`，讓識別碼進得了二進位、出不了 diff |
| `monetization-sdk-integration` | 新增／升級／稽核變現 SDK；把 `import` 隔離在單一 bridge 檔 |
| `app-store-review-rejections` | 診斷並預先化解 free + 廣告 + IAP + CloudKit + GC 的 App Review 退件類型 |
| `asc-api-automation` | 用 `.p8` 產 ES256 JWT + curl 打 ASC REST API —— TestFlight、metadata、送審、報表；不用 fastlane |
| `swiftui-interaction-footguns` | 純程式碼審查抓不到的已知 SwiftUI 互動 bug |
| `swiftui-navigation-architecture` | 型別化 `Route` enum + `@Observable` router；value-based `NavigationStack`；逐轉場的呈現語意與 macOS 退路；deep link；每個 tab 各自的 path |
| `app-icon-rasterize` | 以 `qlmanage` 把 1024 SVG 圖示點陣化成 asset catalog PNG —— 免 Homebrew |
| `ios-design-mockup` | 從 spec 產出單檔 HTML iOS 設計 mockup —— iPhone 外框 + tokens |
| `interactive-simulator-ux-audit` | 用 `idb`（tap/describe/screenshot）驅動已開機的 Simulator，抓 snapshot 抓不到的導航／modal／safe-area bug |
| `host-driven-xcuitest-e2e` | 透過 Tuist 啟動 App 跑 XCUITest E2E —— 專用 scheme 接線 + macOS 視窗座標點擊驅動 |
| `cloudkit-schema-source-of-truth` | 納入版控的 `.ckdb` + `cktool` 匯出／驗證／部署到 Development；Production 是使用者自持、僅限 Console 的關卡 |

### collaboration-skills（12）—— harness engineering：派工、審查、出貨

| Skill | 一句話說明 |
|---|---|
| `spec-phase-orchestration` | 實作前的文件流水線；逐節核可 |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer 三角；第一輪外觀問題直接 inline；limit(N) |
| `leader-developer-handoff-contract` | 派工 sub-agent 時必備的 5 個元素 |
| `agent-impl-notes-log` | Sub-agent 任務進行中的即時 impl-notes —— 決策、偏離、未決問題 |
| `subagent-conflict-detection` | 檢查新 sub-agent 的目標不與進行中的 worktree 重疊 |
| `methodology-pattern-extractor` | 從會議記錄中萃取重複出現 ≥3 次的模式 |
| `session-to-meeting-log` | 把一場 Claude Code session 整併成會議記錄；是摘要，不是逐字稿 |
| `pr-diff-verification` | Push／開 PR 前，確認 `git show --stat HEAD` 與 commit 宣稱的內容相符 |
| `backlog-routing-by-topic` | 依主題把零散點子路由到對應 spec 檔的 §Backlog |
| `claude-skill-plugin-packaging` | 發佈／安裝 Claude Code 技能 —— depth-1 規則、plugin + marketplace、彙整 |
| `skill-authoring-patterns` | 疊在 `superpowers:writing-skills` 之上的 Apple/Swift 目錄層 —— router 描述、bookend 段落、兩層式 references、證據導向 CR |
| `github-contribution-workflow` | gh-CLI 貢獻循環 —— PR、issue、GitHub 檔案操作、secrets、貢獻流程的 repo 設定；慣例 + merge 前 CLEAN |

### 彙整之外部 plugin（6）—— 以引用方式收錄，完整標註

此處僅列出、**並非在此撰寫**；它們會從原作者自己的 repo 安裝（你拿到的是最新版），並完整標註出處。
**彙整而非佔為己有**：只列出 MIT 相容、不重複的 plugin —— 第一方技能只為真正的空缺而寫。
這道檢查發生在收錄當下，不是每次上游 commit 都重審：因為你安裝的是原作者的最新版，
外部 plugin 的範圍與授權在收錄後仍可能變動（`caveman` 就已經變過）。
外部 plugin 是廣度型的**參考資料**（「這是 API」／「X 要這樣做」）；第一方技能位在下一層，
是**帶立場的預設值與實際上架的戰場故事**（用 iOS 18、單一 Package、swift-testing + snapshot、
OSLog 不用第三方、審查漏掉的執行期 bug）。主題重疊處，兩者差在高度，而非重複。

| Plugin | 作者 | 涵蓋範圍 |
|---|---|---|
| [`apple-skills`](https://github.com/vabole/apple-skills) | vabole (MIT) | 廣泛的 Apple 框架 —— SwiftUI、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit… |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI 模式、Swift Charts、Liquid Glass、Instruments 工具鏈 |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI 陷阱、deprecated API 觀察清單、iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee（技能為 MIT；該 repo 另含 BSL-1.1 授權的 engine） | 極度壓縮的溝通模式 —— 省下約 75% token。之後已長成約 20 個技能的套件，其中部分在講作者自家的 Caveman Cloud 服務（通用 agent 行為） |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | 「懶惰資深工程師」模式 —— 逼出最簡單、最短的解法（通用 agent 行為） |
| [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) | Ayoub G. (MIT) | 常駐的 ADHD 友善輸出模式 —— 行動優先、編號步驟、每一輪重述狀態；相對於 `caveman`（token 壓縮）與 `ponytail`（解法簡化），這個塑形的是結構（通用 agent 行為） |

## 出處

第一方技能萃取並去專案化自 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的
`.claude/skills/` —— 一組 spec-first、由 AI Leader/Developer 打造、已上架的 Apple 平台遊戲作品集 ——
再加上針對公開的 Apple / WCAG / Swift 標準所做的原創整理。彙整之外部 plugin 仍屬其作者的作品，
此處僅以引用方式呈現。催生本 repo 雙 plugin 結構的設計 spec 與計畫原本放在 `docs/superpowers/`，
現已退役、改由 git 歷史保存；用 `git log -- docs/` 可以找回。MIT —— 見 [LICENSE](LICENSE)。

<!-- src-sha: fd9e946885542b0acccc57ec1b94e93b2cc4e697 -->
