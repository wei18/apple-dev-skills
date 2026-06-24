# apple-dev-skills

> 給 AI 編碼 agent 用的 **Swift／Apple 平台 skill 策展目錄**（[Claude Code](https://code.claude.com)）。
> 內含**原創第一方 skill**（某專案淬煉的 pattern ＋ 公開標準主題），**外加以 by-reference 方式聚合、指向原 repo 並署名作者的最佳外部 skill plugin**——非複製。
>
> English version: [`README.md`](README.md)

這個 repo 同時是兩件事：

- 一個 **Claude Code plugin**（`apple-dev-skills`）——`skills/` 下 30 個第一方 `SKILL.md`，命名空間 `apple-dev-skills:<skill>`。內容來自某真實上架專案自身經驗，以及公開的 Apple／WCAG／Swift 文件。
- 一個 **marketplace 目錄**，同時收錄最佳的**外部** skill plugin。那些從**作者自己的 repo** 安裝（完整署名）；此處沒有任何一項是抄襲或重做別人的 skill。

**本 README 即函式庫的單一真相來源（SSOT）。**

---

## Roadmap（agenda）

| Phase | 內容 | 狀態 |
|---|---|---|
| **1 — 抽離** | 把某專案可移植 skill 抽出、通用化、做成可 submodule 消費的 plugin | ✅ 完成 |
| **2 — 獨立函式庫** | README 當 SSOT · `npx skills add` 安裝路徑 · 可聚合其他 repo 的 marketplace 目錄（機制見 [`claude-skill-plugin-packaging`](skills/claude-skill-plugin-packaging/SKILL.md)） | ✅ 完成 |
| **3 — 策展與聚合** | 巡了高星 Swift/Apple skill repo，將最佳的 MIT plugin **以 by-reference 聚合**（指向作者原 repo、署名——見下方），而非重做它們。第一方 skill **只**為「無可聚合 plugin 的真實缺口」而寫（無障礙、依賴注入、效能）。決策：[CURATION.md](CURATION.md) | ✅ 完成 |

詳細狀態、spec→impl 對齊、未來階段：**[ROADMAP.md](ROADMAP.md)**。

---

## 安裝

> Claude Code 透過 **plugin 系統**發現共享 skill，而非 `.claude/skills/` 下的裸資料夾。本 repo 同時是 plugin 與 marketplace。

### 選項 A — marketplace（最簡單）

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills
```

我們的 skill 以 `apple-dev-skills:<skill-name>` 載入。同一 marketplace 也提供[聚合的外部 plugin](#聚合的外部-skill)——可從作者 repo 安裝任一個，例如 `/plugin install swiftui-expert@apple-dev-skills`。

### 選項 B — vendored submodule，逐 repo 釘版

把第一方 plugin vendored 進某 repo 並釘版，再以 **project-scope local-path marketplace** 註冊，使其從被釘版的 submodule 載入：

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v0.5.0 && cd -
```

然後把以下 commit 進該 repo 的 `.claude/settings.json`（協作者會被提示 trust workspace，之後自動註冊）：

```json
{
  "extraKnownMarketplaces": {
    "apple-dev-skills": {
      "source": { "source": "directory", "path": "./.claude/skills/apple-dev-skills" }
    }
  },
  "enabledPlugins": { "apple-dev-skills@apple-dev-skills": true }
}
```

光是 `git submodule add` **不會讓 skill 出現**——上面的 marketplace 註冊才是讓 Claude Code 載入它們的關鍵。

### 選項 C — `npx skills`（扁平 skill、非 plugin）

用開源 [`skills`](https://github.com/vercel-labs/skills) CLI 把選定的第一方 `SKILL.md` 複製進 agent 的 skills 目錄，**扁平、無命名空間**：

```bash
npx skills add wei18/apple-dev-skills --list                       # 瀏覽完整索引
npx skills add wei18/apple-dev-skills --skill swift6-concurrency   # 單一 skill
npx skills add wei18/apple-dev-skills --all -a claude-code         # 全部
```

---

## 第一方 skill 索引（30）

### Platform defaults（10）

| Skill | 一句話 |
|---|---|
| `swift6-concurrency` | Swift 6 語言模式 + 完整並行檢查；預設 Sendable；`@preconcurrency` 逃生口 |
| `apple-platform-targets` | 預設 iOS 18／macOS 15、Xcode 16+；採 Liquid Glass／最新 OS-only API 才升 26 |
| `swiftpm-modularization` | 單 Package 多 target、薄 App、DI composition root、framework import 受限、一對一 test target |
| `swift-testing-baseline` | swift-testing（不用 XCTest）+ pointfreeco snapshot；protocol fakes；snapshot 進 git；strict-content/tolerant-board gate；CI Xcode 鎖版 |
| `xcode-cloud-single-track-ci` | 單軌 Xcode Cloud；4 種 workflow（PR／Main／Release／Periodic）；PR CI 含 pre-merge |
| `mise-tool-management` | mise 管二進位 CLI 工具；dev + CI 共用 `.mise.toml`；混合 OS CI 的 macOS-only-tool `os` guard |
| `oslog-logger-defaults` | `os.Logger`（不用第三方）；subsystem = bundle ID、category = module；預設 `.private` |
| `apple-three-piece-analytics` | ASC Analytics + MetricKit + Game Center；不用第三方追蹤；`PrivacyInfo.xcprivacy` 必備 |
| `telemetry-facade-pattern` | 單一 `Telemetry` target、fan-out facade；OSLog／NoOp／MetricKit／GameCenter sink；sink 接線陷阱 |
| `ai-translated-localization` | 預設 7 語系；AI 翻譯流程；`Localizable.xcstrings`；逐 key 完整度 + shared-key gate 盲點 |

### Process & collaboration（7）

| Skill | 一句話 |
|---|---|
| `spec-phase-orchestration` | 實作前文件 pipeline（README + design／foundations／plan／methodology + meetings）；逐節核准 |
| `subagent-review-cycles` | Leader／Developer／Code-Reviewer 三角；round-1 美化 inline；limit(N) 輪 |
| `leader-developer-handoff-contract` | 派 sub-agent 必含 5 要素：scope／inputs／skills／return format／verification |
| `agent-impl-notes-log` | sub-agent 任務進行中的 `meetings/{date}_{topic}.impl-notes.md`——決策、偏離、未決問題 |
| `subagent-conflict-detection` | 派發前檢查新 sub-agent 的目標檔不與進行中 sub-agent 的 worktree 重疊 |
| `methodology-pattern-extractor` | 從 meeting log 萃取重複 ≥ 3 次的 pattern；append 到 `methodology.md` |
| `session-to-meeting-log` | 把 Claude Code session 整理成 `meetings/{date}_{topic}.md`；摘要而非逐字 |

### Ops & review（10）

| Skill | 一句話 |
|---|---|
| `pr-diff-verification` | push／PR 前，驗 `git show --stat HEAD` 與 commit 訊息宣稱相符 |
| `backlog-routing-by-topic` | 把零散點子依主題路由到對應 spec 檔的 §Backlog |
| `apple-public-repo-security` | 公開 iOS／macOS repo 三道防線（lefthook + gitleaks／CI post-clone／secret scanning）+ 先輪替的洩漏 SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`，給「進 binary 但不能進 PR diff」的 ID |
| `monetization-sdk-integration` | 新增／升級／稽核第三方變現 SDK；把 `import GoogleMobileAds` 隔離在單一 bridge 檔 |
| `app-store-review-rejections` | 診斷 App Review 被拒並針對含廣告 + IAP + CloudKit + Game Center 的免費 App 會踩的 guideline 強化送審 |
| `swiftui-interaction-footguns` | 純 code review 漏掉的 SwiftUI 互動 bug 清單（tap-target、safe-area、sizeClass、`.task` re-fire） |
| `app-icon-rasterize` | 用 `qlmanage` 把 1024 SVG app icon 點陣成 asset-catalog PNG——免 Homebrew／cloud |
| `ios-design-mockup` | 從 spec 產單檔 HTML iOS 設計 mockup——iPhone frame + SVG 導覽箭頭 + design-token 面板 |
| `claude-skill-plugin-packaging` | 如何散布／安裝 skill——depth-1 發現規則、plugin + marketplace 打包、vendored-submodule + committed project-scope settings 配方、by-reference 聚合其他 repo、各種坑 |

### App engineering（3）

這幾項涵蓋目前無「授權相容的外部 CC plugin」的主題；內容為原創，蒸餾自公開的 Apple HIG／WCAG／Swift 文件。

| Skill | 一句話 |
|---|---|
| `ios-accessibility-engineering` | SwiftUI & UIKit 具體的 VoiceOver／Dynamic Type／觸控目標／Reduce Motion 實作 + 稽核，含對 App Review 的 WCAG 2.2 對應 |
| `swift-dependency-injection` | 經 protocol 注入 + 單一 composition root 的可測試接縫、SwiftUI environment vs 建構子注入、`@TaskLocal` 覆寫、Swift 6 `Sendable` 依賴規則 |
| `ios-performance-engineering` | 量測與修復效能——Instruments（Time Profiler／Hangs／SwiftUI）、CI 的 `xctrace`、hang/hitch 預算、啟動時間、記憶體與洩漏、二進位大小、MetricKit 現場遙測 |

---

## 聚合的外部 skill

這些**非本處撰寫**。它們是優秀的社群 skill plugin，本 marketplace 以 **by-reference** 收錄——從作者自己的 repo 安裝，完整保留作者署名，且你永遠拿到他們的最新版。加上本 marketplace（選項 A），即可以 `<plugin>@apple-dev-skills` 安裝任一個。

| Plugin | 作者 | License | 涵蓋 |
|---|---|---|---|
| [`apple-skills`](https://github.com/vabole/apple-skills) | vabole | MIT | 廣泛 Apple 框架——SwiftUI、Swift Testing、Concurrency、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit、MapKit、TipKit… |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (AvdLee) | MIT | SwiftUI patterns、Swift Charts、macOS 多視窗、Liquid Glass、Instruments-trace 工具鏈 |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (twostraws) | MIT | LLM 常犯的 SwiftUI 陷阱、deprecated-API 清單、無障礙、iOS 26／Liquid Glass |

若你維護一個高品質、授權相容的 Swift／Apple skill plugin 並希望被收錄於此，歡迎開 issue。

---

## 來源與署名

第一方 skill 從 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的 `.claude/skills/`（一個 spec-first、由 AI Leader/Developer 打造的上架 Apple 平台遊戲組合）抽離並通用化，加上對公開 Apple／WCAG／Swift 標準的原創撰寫。上方聚合的外部 plugin 仍屬各自作者的著作與財產，僅以 by-reference 方式呈現。

## License

MIT（第一方內容）—— 見 [LICENSE](LICENSE)。聚合的外部 plugin 由各自作者授權（收錄時皆為 MIT）。
