# apple-dev-skills

> 用 Claude Code vibe coding iOS 與 Apple 生態系 App 的技能 —— 以及駕馭那個打造它們的 agent 的技能。
>
> 語言：[English](README.md) · [繁體中文](README.zh-Hant.md) · [简体中文](README.zh-Hans.md) · [日本語](README.ja.md)

apple-dev-skills 是一個 **marketplace**，服務對象是要在 **iOS 26 / macOS 26 底線**上打造全新
（greenfield）App —— 從點子做到 App Store 上架 —— 的獨立開發者與小型團隊。第一方技能分成
兩組：**Apple/Swift** 技能對應你正在打造的東西，**harness engineering** 技能（你怎麼駕馭
Claude Code 本身 —— 派工、審查、出貨）。每一支技能都是帶立場的預設值，背後有實際上架的
戰場故事，並受一道一致性把關。旁邊另以引用方式彙整同類最佳的**外部**技能 plugin —— 並非
在此撰寫，僅連結並標註原作者，絕不複製。

## 快速開始

> 技能會依你描述的任務自動觸發 —— 裝好之後，直接描述你的任務即可。

在 Claude Code session 裡執行：

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 26 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 12 harness-engineering skills
```

每次安裝都會開一個詳情面板 —— 選 **User** scope。格式是 `plugin@marketplace`；這個
marketplace 剛好跟它第一個 plugin 同名。

若安裝摘要顯示 `Run /reload-plugins to activate.`，Claude Code 會自動幫你執行；如果它警告
你下一則訊息會重讀整個對話，就手動跑 `/reload-plugins --force`。

裝一個或兩個都可以。外部 plugin 的安裝方式相同，例如 `/plugin install swiftui-expert@apple-dev-skills`。

接著直接描述你要做的事：

- *「我要開一個新的 iOS App」* → `apple-platform-targets` 回答最低部署版本，並依序交棒給
  package 結構、語言模式與測試基準。
- *「App Review 以 guideline 5.1.2 退件」* → `app-store-review-rejections` 把該條款對應到
  修復方式。

要指定某一支，用它的 slash command：`/apple-dev-skills:swift6-concurrency`。`/skills` 會列出
已安裝的全部技能，以及每一支來自哪個 plugin。

> 兩個 plugin 一起裝，會載入全部 38 條第一方描述 —— 約 5,500 tokens，是預設 1% 技能清單
> 預算（200k context 模型下是 2,000 tokens）的約 2.7 倍，還沒算外部 plugin。技能清單預算是
> context window 的 1%；爆量時 Claude Code 會從最少被呼叫的技能開始砍描述；實務上通常
> 就是還沒有呼叫紀錄的新安裝技能。執行 `/doctor` 檢查清單成本，太吃緊就調高 `skillListingBudgetFraction`
> （例如 `0.02`），或透過 `/plugin` 停用不想用的 plugin。

## 目錄

- **Spec** 流程 → `spec-phase-orchestration`
- **Bootstrap** 專案 → `apple-platform-targets`
- **Build** UI → `swiftui-navigation-architecture`
- **Test** 測試 → `swift-testing-baseline`
- **Ship** 上架 → `asc-api-automation`
- **Operate** 營運 → `apple-three-piece-analytics`

完整索引見下方表格。

### apple-dev-skills（26）—— Apple/Swift

| Skill | 一句話說明 |
|---|---|
| `swift6-concurrency` | Swift 6 語言模式 + 完整 concurrency 檢查；預設 actor isolation 為 `MainActor`，只有跨進 `nonisolated` / actor 的程式碼才需要 Sendable |
| `apple-platform-targets` | 預設 iOS 26 / macOS 26、Xcode 26.x；只有既有使用者仍在舊版時才降到 iOS 18 / macOS 15（或 17 / 14） |
| `swiftpm-modularization` | 單一 Package、多 target、薄 App、DI composition root、測試一對一 |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot；protocol fake；嚴格/寬鬆 snapshot 把關 |
| `xcode-cloud-single-track-ci` | 單軌 Xcode Cloud；PR / Main / Release / Periodic；merge 前的 PR CI |
| `local-archive-export-upload` | Xcode Cloud 不可用時的本機 `xcodebuild archive` → export → `altool` 上傳 TestFlight |
| `mise-tool-management` | 用 mise 釘住 CLI 工具版本（swiftlint、xcbeautify…），讓本機開發與 CI 用同一個版本 |
| `oslog-logger-defaults` | 預設的 logging 設定：Apple 自家 `os.Logger`，不用第三方函式庫，log 值預設 private，除非你自己 opt-in |
| `apple-three-piece-analytics` | App Store Connect (ASC) Analytics + MetricKit + Game Center；不用第三方追蹤；PrivacyInfo 必備 |
| `telemetry-facade-pattern` | 一次 `observe(event)` 呼叫扇出到 OSLog / tracking / Game Center 等 sink，MetricKit payload 反向作為事件餵入 —— 換 sink 不必動呼叫端 |
| `ai-translated-localization` | 預設 7 個語系；AI 翻譯流程；`Localizable.xcstrings`；完整度把關 |
| `ios-accessibility-engineering` | SwiftUI 與 UIKit 的 VoiceOver / Dynamic Type / 觸控目標 / Reduce Motion；WCAG 2.2 |
| `swift-dependency-injection` | 讓服務可以為了測試替換 —— protocol 注入 + composition root（environment vs constructor、`@TaskLocal`、Sendable） |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch 預算 / 啟動 / 記憶體 / 二進位大小 / MetricKit |
| `apple-public-repo-security` | 公開 iOS/macOS repo 的三道防線 + rotate-first 洩漏處理 SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`，讓識別碼進得了二進位、出不了 diff |
| `storekit2-iap-defaults` | StoreKit 2 非消耗型 IAP 預設：bridge protocol 測試接縫、entitlements、restore |
| `monetization-sdk-integration` | 新增／升級／稽核變現 SDK；把 `import` 隔離在單一 bridge 檔 |
| `app-store-review-rejections` | 診斷並預先化解 free + 廣告 + IAP + CloudKit + Game Center (GC) 的 App Review 退件類型 |
| `asc-api-automation` | 用 `.p8` 產 ES256 JWT + curl 打 ASC REST API —— TestFlight、metadata、送審、報表；不用 fastlane |
| `swiftui-interaction-footguns` | 純程式碼審查抓不到的已知 SwiftUI 互動 bug |
| `swiftui-navigation-architecture` | SwiftUI 的型別化路由導航 —— 一個 `@Observable` router、`NavigationStack`、deep link、處理好 macOS 退路 |
| `ios-design-mockup` | 從 spec 產出單檔 HTML iOS 設計 mockup —— iPhone 外框 + tokens |
| `interactive-simulator-ux-audit` | 用 `idb`（tap/describe/screenshot）驅動已開機的 Simulator，抓 snapshot 抓不到的導航／modal／safe-area bug |
| `host-driven-xcuitest-e2e` | 透過 Tuist 啟動 App 跑 XCUITest E2E —— 專用 scheme 接線 + macOS 視窗座標點擊驅動 |
| `cloudkit-schema-source-of-truth` | 納入版控的 `.ckdb` + `cktool` 匯出／驗證／匯入到 Development；Production 是使用者自持、僅限 Console 的關卡 |

### collaboration-skills（12）—— harness engineering：派工、審查、出貨

| Skill | 一句話說明 |
|---|---|
| `spec-phase-orchestration` | 實作前的文件流水線；逐節核可 |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer 三角；跑幾輪、什麼算駁回 |
| `leader-developer-handoff-contract` | 派工 sub-agent 時必備的 6 個元素 |
| `agent-impl-notes-log`† | Sub-agent 任務進行中的即時 impl-notes —— 決策、偏離、未決問題 |
| `subagent-conflict-detection` | 檢查新 sub-agent 的目標不與進行中的 worktree 重疊 |
| `methodology-pattern-extractor`† | 從會議記錄中萃取重複出現 ≥3 次的模式 |
| `session-to-meeting-log`† | 把一場 Claude Code session 整併成會議記錄；是摘要，不是逐字稿 |
| `pr-diff-verification` | Push／開 PR 前，確認 `git show --stat --summary HEAD` 與 commit 宣稱的內容相符 |
| `backlog-routing-by-topic`† | 依主題把零散點子路由到對應 spec 檔的 §Backlog |
| `claude-skill-plugin-packaging` | 發佈／安裝 Claude Code 技能 —— depth-1 規則、plugin + marketplace、依專案釘版安裝、以引用方式彙整 |
| `skill-authoring-patterns` | 疊在 `superpowers:writing-skills` 之上的 Apple/Swift 目錄層 —— router 描述、bookend 段落、兩層式 references、證據導向 CR |
| `github-contribution-workflow` | gh-CLI 貢獻循環 —— PR、issue、GitHub 檔案操作、secrets、貢獻流程的 repo 設定；慣例 |

† 需要 `spec-phase-orchestration` 的文件版型（`design.md` / `plan.md` / `meetings/`）。

### 彙整之外部 plugin（7）—— 以引用方式收錄，完整標註

此處僅列出，**並非在此撰寫** —— 從原作者自己的 repo 安裝（你拿到的是最新版），完整標註出處。
**彙整而非佔為己有**：只列出 MIT 相容、不重複的 plugin，且只為真正的空缺而收 —— 這道檢查發生
在收錄當下，不是每次上游 commit 都重審，因此外部 plugin 的範圍與授權在收錄後仍可能變動
（`caveman` 就已經變過）。外部 plugin 是廣度型的**參考資料** —— 「這是 API，這是怎麼做 X 的
方法」。第一方技能比較窄：每個主題一個帶立場的預設值（iOS 26 是底線、單一 Package、
swift-testing + snapshot、只用 OSLog、已知的執行期 bug 要避開）。主題重疊處，兩者不是重複，
而是回答的細節層級不同。

| Plugin | 作者 | 涵蓋範圍 |
|---|---|---|
| [`apple-skills`](https://github.com/Prisma-Labs-Dev/apple-skills) | Prisma Labs (vabole), MIT | 廣泛的 Apple 框架 —— SwiftUI、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit、`apple-aso`、`hig`……以及一份 SwiftUI 效能稽核指南，與 `ios-performance-engineering` 的 Instruments / MetricKit 量測互補；另外還有 `simulator-utils` 與 `xcuitest`（與本目錄 Simulator／XCUITest 技能的分工見下方說明）。有一小部分技能放在 `disabled-skills/` —— 留在 repo 裡但不會被 agent 載入 |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI 模式、Swift Charts、Liquid Glass、Instruments 工具鏈 |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI 陷阱、deprecated API 觀察清單、iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | 極度壓縮的溝通模式 —— 省下約 65% 輸出 token（作者自測）；會裝上 `SessionStart`／`UserPromptSubmit` hook（需要 PATH 上有 `node`，每則 prompt 都會執行）（通用 agent 行為） |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | 「懶惰資深工程師」模式 —— 逼出最簡單、最短的解法（通用 agent 行為） |
| [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) | Ayoub G. (MIT) | 常駐的 ADHD 友善輸出模式 —— 編號步驟、每一輪重述狀態（通用 agent 行為） |
| [`xcode-build-skill`](https://github.com/pzep1/xcode-build-skill) | pz (MIT) | `xcodebuild`/`xcrun simctl` CLI 小抄 —— scheme → 模擬器 → build → install → launch → 截圖 |

`caveman` 的授權：技能本身 MIT；repo 另外還有一個 BSL-1.1 授權的 engine。`caveman` 之後已
長成 20 個技能的套件；其中 4 個（`caveman-discover`、`caveman-manage`、
`caveman-evidence-review`、`caveman-setup`）在講作者自家托管的 Caveman Cloud 商業服務。

`i-have-adhd` 與 `caveman`（token 壓縮）、`ponytail`（解法簡化）不同，它塑形的是每次回答的
**結構**。

`xcode-build-skill`（`xcodebuild`／`simctl` 迴圈）與 `apple-skills:simulator-utils`（`simctl`
單次操作）是 CLI 參考手冊；`interactive-simulator-ux-audit` 用 `idb` 做探索式稽核；
`host-driven-xcuitest-e2e` 接 Tuist scheme 跑 CI —— `apple-skills:xcuitest` 是它假設你已具備
的 API 參考。

`apple-skills` 已從 `vabole` 的個人帳號移轉到 `Prisma-Labs-Dev` 組織；此表列出的是組織版
repo。

## 其他安裝方式

（A 就是上面的快速開始。）

### B —— 團隊固定版本

直接在 `.claude/settings.json` 把 marketplace 鎖定到一個已發佈的 tag —— 不需要 submodule：

```json
{
  "extraKnownMarketplaces": {
    "apple-dev-skills": {
      "source": { "source": "github", "repo": "wei18/apple-dev-skills", "ref": "v1.7.1" }
    }
  },
  "enabledPlugins": {
    "apple-dev-skills@apple-dev-skills": true,
    "collaboration-skills@apple-dev-skills": true
  }
}
```

commit 它 —— 協作者信任該專案資料夾之後就會自動拿到這個 marketplace，不會有額外提示。兩支
第一方 plugin 是相對路徑條目，到這步就已裝好；外部 plugin 是 GitHub 來源，`enabledPlugins`
不會幫別人自動安裝 —— 每位協作者仍要自己跑一次 Claude Code 印出的 `claude plugin install …`
指令。

### C —— `npx skills`（平鋪，不走 plugin）

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

> **路徑 C 不包含彙整而來的外部 plugin。** `npx skills` 會讀取本 repo 的
> `marketplace.json` / `plugin.json`，但只跟隨本地宣告的技能路徑。它不會抓取外部
> plugin 的遠端 `github` / `git-subdir` 來源。所以上述指令只會安裝 38 個第一方技能 ——
> 7 個外部 plugin 會被靜默略過。若要平鋪安裝整份目錄（含外部 plugin，從原作者的 repo 拉取）：

```bash
scripts/install-flat.sh -g          # user-level; drop -g for project-level
scripts/install-flat.sh --dry-run   # preview the `npx skills add` commands
```

## 貢獻

三種幫忙方式：**彙整**一個外部 plugin、**新增**一個第一方技能、或**回報**一則現場筆記
—— 見 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 出處

第一方技能萃取並去專案化自 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的
`.claude/skills/` —— 一組 spec-first、由 AI Leader/Developer 打造、已上架的 Apple 平台遊戲作品集 ——
再加上針對公開的 Apple / WCAG / Swift 標準所做的原創整理。彙整之外部 plugin 仍屬其作者的作品，
此處僅以引用方式呈現。催生本 repo 雙 plugin 結構的設計 spec 與計畫原本放在 `docs/superpowers/`
—— 已退役、改由 git 歷史保存；用 `git log -- docs/` 可以找回。MIT —— 見 [LICENSE](LICENSE)。

<!-- src-sha: 7699870110c96d109c7bcda48151e19787a07aa3 -->
