# apple-dev-skills

> 給 **AI agent 驅動的 Swift／Apple 平台開發**用的可重用 [Claude Code](https://code.claude.com) skills。
> 一個 Swift engineer-agent 的專業 skill 函式庫——可組合、自我說明、可經 git submodule 跨專案共享。
>
> English version: [`README.md`](README.md)

本 repo 是一個 **Claude Code skills-directory plugin**：`skills/` 下一組策展過的
`SKILL.md`，在 Claude Code 中以 `apple-dev-skills:` 命名空間出現。這些 skills 是在
打造實際上架的 Apple 平台 App 過程中淬煉、再通用化以供重用。

**本 README 即函式庫的單一真相來源（SSOT）／agenda。**

---

## Roadmap（agenda）

| Phase | 內容 | 狀態 |
|---|---|---|
| **1 — 抽離** | 把可移植 skills 從真實專案抽出、通用化、做成可 submodule 消費的 plugin | ✅ 完成 |
| **2 — 獨立函式庫** | (a) README 當 SSOT/agenda ✓ · (b) **npm／`npx` 安裝路徑** ✓，經 [`skills`](https://github.com/vercel-labs/skills) CLI（`npx skills add wei18/apple-dev-skills`）把 `SKILL.md` 裝成扁平 skills——與命名空間 plugin 互補 · (c) 經 marketplace 目錄聚合其他 skill repo——機制見 [`claude-skill-plugin-packaging`](skills/claude-skill-plugin-packaging/SKILL.md) | ✅ 完成 |
| **3 — 策展生態** | 巡了高星 Swift/Apple skill repo；**補上真正的缺口**（無障礙、依賴注入）為第一方 skill，並對與我們重疊者**推薦**而非收錄。決策：[CURATION.md](CURATION.md) | ✅ 完成 |

---

## 安裝

> Claude Code 透過 **plugin 系統**發現共享 skills，而非 `.claude/skills/` 下的裸資料夾。
> 本 repo 同時是 plugin 與 marketplace（`.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json`），下列任一路徑皆可。

### 選項 A — 全域 marketplace（最簡單）

在 Claude Code 中：

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills
```

skills 全域載入（每個專案）為 `apple-dev-skills:<skill-name>`。

### 選項 B — vendored submodule，逐 repo 釘版

把函式庫 vendored 進某 repo 並釘版，再以 **project-scope local-path marketplace** 註冊，使其從被釘版的 submodule 載入：

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v0.3.0 && cd -
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

光是 `git submodule add` **不會讓 skills 出現**——上面的 marketplace 註冊才是讓 Claude Code 載入它們的關鍵。

### 選項 C — `npx skills`（扁平 skills、非 plugin）

用開源 [`skills`](https://github.com/vercel-labs/skills) CLI 把選定的 `SKILL.md` 直接複製進 agent 的 skills 目錄（`.claude/skills/`），**扁平、無命名空間**（顯示為 `swift6-concurrency` 而非 `apple-dev-skills:swift6-concurrency`）：

```bash
npx skills add wei18/apple-dev-skills --list                       # 瀏覽全部 30 個
npx skills add wei18/apple-dev-skills --skill swift6-concurrency   # 單一 skill
npx skills add wei18/apple-dev-skills --all -a claude-code         # 全部
```

想把少數 skill 當純檔案 vendored 時用這個；想要整個函式庫當版本化、命名空間 plugin 時用選項 A/B。

---

## Skill 索引

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
| `claude-skill-plugin-packaging` | 如何散布／安裝這些 skills——depth-1 發現規則、plugin + marketplace 打包、vendored-submodule + committed project-scope settings 配方、聚合其他 skill repo、各種坑 |

### App engineering（3）

| Skill | 一句話 |
|---|---|
| `swiftui-state-and-composition` | SwiftUI 最佳實務——`@Observable` vs `ObservableObject` 遷移、single-source-of-truth 擁有權、view identity、組合、render 最小化（`swiftui-interaction-footguns` 的 positive 搭檔） |
| `ios-accessibility-engineering` | SwiftUI & UIKit 具體的 VoiceOver／Dynamic Type／觸控目標／Reduce Motion 實作 + 稽核，含對 App Review 的 WCAG 2.2 對應 |
| `swift-dependency-injection` | 經 protocol 注入 + 單一 composition root 的可測試接縫、SwiftUI environment vs 建構子注入、`@TaskLocal` 覆寫、Swift 6 `Sendable` 依賴規則 |

---

## 推薦的外部搭檔 skill

來自生態調查（見 [CURATION.md](CURATION.md)）。這些是高品質的外部 Claude Code skill plugin，與本庫的 SwiftUI 覆蓋**重疊**，故**不收錄**於此——想要更深的 SwiftUI 專項指引可自行加入：

- **[twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill)**（MIT）—— SwiftUI 陷阱／iOS 26 Liquid Glass，作者 Paul Hudson。`/plugin marketplace add twostraws/SwiftUI-Agent-Skill`
- **[AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill)**（MIT）—— SwiftUI patterns + Swift Charts／Instruments-trace 工具鏈，作者 Antoine van der Lee。`/plugin marketplace add AvdLee/SwiftUI-Agent-Skill`

---

## 來源

從 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的 `.claude/skills/` 抽離並通用化——一個 spec-first、由 AI Leader/Developer 打造的上架 Apple 平台遊戲組合。點名該 repo 特定任務／App 的 skill 留在原地；此處皆為專案無關。

## License

MIT —— 見 [LICENSE](LICENSE)。
