# apple-dev-skills

> 用 Claude Code vibe coding iOS 与 Apple 生态系统 App 的技能 —— 以及驾驭那个打造它们的 agent 的技能。
>
> 语言：[English](README.md) · [繁體中文](README.zh-Hant.md) · [简体中文](README.zh-Hans.md) · [日本語](README.ja.md)

apple-dev-skills 是一个 **marketplace**，服务对象是要在 **iOS 26 / macOS 26 底线**上打造全新
（greenfield）App —— 从点子做到 App Store 上架 —— 的独立开发者与小型团队。第一方技能分成
两组：**Apple/Swift** 技能对应你正在打造的东西，**harness engineering** 技能（你怎么驾驭
Claude Code 本身 —— 调度、审查、交付）。每一支技能都是带立场的默认值，背后有实际上架的
实战故事，并受一道一致性把关。旁边另以引用方式汇总同类最佳的**外部**技能 plugin —— 并非
在此撰写，仅链接并标注原作者，绝不复制。

## 快速开始

> 技能会依你描述的任务自动触发 —— 装好之后，直接描述你的任务即可。

在 Claude Code session 里执行：

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 26 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 12 harness-engineering skills
```

每次安装都会打开一个详情面板 —— 选 **User** scope。格式是 `plugin@marketplace`；这个
marketplace 刚好跟它第一个 plugin 同名。

若安装摘要显示 `Run /reload-plugins to activate.`，Claude Code 会自动帮你执行；如果它警告
你下一条消息会重读整个对话，就手动跑 `/reload-plugins --force`。

装一个或两个都可以。外部 plugin 的安装方式相同，例如 `/plugin install swiftui-expert@apple-dev-skills`。

接着直接描述你要做的事：

- *“我要开一个新的 iOS App”* → `apple-platform-targets` 回答最低部署版本，并依次移交给
  package 结构、语言模式与测试基准。
- *“App Review 以 guideline 5.1.2 退回”* → `app-store-review-rejections` 把该条款对应到
  修复方案。

要指定某一个，用它的 slash command：`/apple-dev-skills:swift6-concurrency`。`/skills` 会列出
已安装的全部技能，以及每一个来自哪个 plugin。

> 两个 plugin 一起装，会加载全部 38 条第一方描述 —— 约 5,500 tokens，是默认 1% 技能清单
> 预算（200k context 模型下是 2,000 tokens）的约 2.7 倍，还没算外部 plugin。技能清单预算是
> context window 的 1%；超支时 Claude Code 会从最少被调用的技能开始砍描述；实务上通常
> 就是还没有调用记录的新安装技能。执行 `/doctor` 检查清单成本，太吃紧就调高 `skillListingBudgetFraction`
> （例如 `0.02`），或通过 `/plugin` 禁用不想用的 plugin。

## 目录

- **Spec** 流程 → `spec-phase-orchestration`
- **Bootstrap** 项目 → `apple-platform-targets`
- **Build** UI → `swiftui-navigation-architecture`
- **Test** 测试 → `swift-testing-baseline`
- **Ship** 上架 → `asc-api-automation`
- **Operate** 运营 → `apple-three-piece-analytics`

完整索引见下方表格。

### apple-dev-skills（26）—— Apple/Swift

| Skill | 一句话说明 |
|---|---|
| `swift6-concurrency` | Swift 6 语言模式 + 完整 concurrency 检查；默认 actor isolation 为 `MainActor`，只有跨入 `nonisolated` / actor 的代码才需要 Sendable |
| `apple-platform-targets` | 默认 iOS 26 / macOS 26、Xcode 26.x；只有既有用户仍在旧版时才降到 iOS 18 / macOS 15（或 17 / 14） |
| `swiftpm-modularization` | 单一 Package、多 target、薄 App、DI composition root、测试一对一 |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot；protocol fake；严格/宽松 snapshot 把关 |
| `xcode-cloud-single-track-ci` | 单轨 Xcode Cloud；PR / Main / Release / Periodic；merge 前的 PR CI |
| `local-archive-export-upload` | Xcode Cloud 不可用时的本机 `xcodebuild archive` → export → `altool` 上传 TestFlight |
| `mise-tool-management` | 用 mise 钉住 CLI 工具版本（swiftlint、xcbeautify…），让本机开发与 CI 用同一个版本 |
| `oslog-logger-defaults` | 默认的 logging 设置：Apple 自家 `os.Logger`，不用第三方库，log 值默认 private，除非你自己 opt-in |
| `apple-three-piece-analytics` | App Store Connect (ASC) Analytics + MetricKit + Game Center；不用第三方追踪；PrivacyInfo 必备 |
| `telemetry-facade-pattern` | 一次 `observe(event)` 调用扇出到 OSLog / tracking / Game Center 等 sink，MetricKit payload 反向作为事件喂入 —— 换 sink 不必动调用点 |
| `ai-translated-localization` | 默认 7 个语言；AI 翻译流程；`Localizable.xcstrings`；完整度把关 |
| `ios-accessibility-engineering` | SwiftUI 与 UIKit 的 VoiceOver / Dynamic Type / 触控目标 / Reduce Motion；WCAG 2.2 |
| `swift-dependency-injection` | 让服务可以为了测试替换 —— protocol 注入 + composition root（environment vs constructor、`@TaskLocal`、Sendable） |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch 预算 / 启动 / 内存 / 二进制大小 / MetricKit |
| `apple-public-repo-security` | 公开 iOS/macOS repo 的三道防线 + rotate-first 泄漏处理 SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`，让标识符进得了二进制、出不了 diff |
| `storekit2-iap-defaults` | StoreKit 2 非消耗型 IAP 默认值：bridge protocol 测试接缝、entitlements、restore |
| `monetization-sdk-integration` | 新增／升级／审计变现 SDK；把 `import` 隔离在单一 bridge 文件 |
| `app-store-review-rejections` | 诊断并预先化解 free + 广告 + IAP + CloudKit + Game Center (GC) 的 App Review 退回类型 |
| `asc-api-automation` | 用 `.p8` 生成 ES256 JWT + curl 打 ASC REST API —— TestFlight、metadata、送审、报表；不用 fastlane |
| `swiftui-interaction-footguns` | 纯代码审查抓不到的已知 SwiftUI 互动 bug |
| `swiftui-navigation-architecture` | SwiftUI 的类型化路由导航 —— 一个 `@Observable` router、`NavigationStack`、deep link、处理好 macOS 退路 |
| `ios-design-mockup` | 从 spec 生成单文件 HTML iOS 设计 mockup —— iPhone 外框 + tokens |
| `interactive-simulator-ux-audit` | 用 `idb`（tap/describe/screenshot）驱动已启动的 Simulator，抓 snapshot 抓不到的导航／modal／safe-area bug |
| `host-driven-xcuitest-e2e` | 通过 Tuist 启动 App 跑 XCUITest E2E —— 专用 scheme 接线 + macOS 窗口坐标点击驱动 |
| `cloudkit-schema-source-of-truth` | 纳入版控的 `.ckdb` + `cktool` 导出／验证／导入到 Development；Production 是用户自持、仅限 Console 的关卡 |

### collaboration-skills（12）—— harness engineering：调度、审查、交付

| Skill | 一句话说明 |
|---|---|
| `spec-phase-orchestration` | 实现前的文档流水线；逐节核准 |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer 三角；跑几轮、什么算驳回 |
| `leader-developer-handoff-contract` | 调度 sub-agent 时必备的 6 个元素 |
| `agent-impl-notes-log`† | Sub-agent 任务进行中的即时 impl-notes —— 决策、偏离、未决问题 |
| `subagent-conflict-detection` | 检查新 sub-agent 的目标不与进行中的 worktree 重叠 |
| `methodology-pattern-extractor`† | 从会议记录中提取重复出现 ≥3 次的模式 |
| `session-to-meeting-log`† | 把一场 Claude Code session 整合成会议记录；是摘要，不是逐字稿 |
| `pr-diff-verification` | Push／开 PR 前，确认 `git show --stat --summary HEAD` 与 commit 宣称的内容相符 |
| `backlog-routing-by-topic`† | 依主题把零散点子路由到对应 spec 文件的 §Backlog |
| `claude-skill-plugin-packaging` | 发布／安装 Claude Code 技能 —— depth-1 规则、plugin + marketplace、按项目钉版安装、以引用方式汇总 |
| `skill-authoring-patterns` | 叠在 `superpowers:writing-skills` 之上的 Apple/Swift 目录层 —— router 描述、bookend 段落、两层式 references、证据导向 CR |
| `github-contribution-workflow` | gh-CLI 贡献循环 —— PR、issue、GitHub 文件操作、secrets、贡献流程的 repo 设置；惯例 |

† 需要 `spec-phase-orchestration` 的文档版型（`design.md` / `plan.md` / `meetings/`）。

### 汇总的外部 plugin（7）—— 以引用方式收录，完整标注

此处仅列出，**并非在此撰写** —— 从原作者自己的 repo 安装（你拿到的是最新版），完整标注出处。
**汇总而非据为己有**：只列出 MIT 兼容、不重复的 plugin，且只为真正的空缺而收 —— 这道检查发生
在收录当下，不是每次上游 commit 都重审，因此外部 plugin 的范围与授权在收录后仍可能变动
（`caveman` 就已经变过）。外部 plugin 是广度型的**参考资料** —— “这是 API，这是怎么做 X 的
方法”。第一方技能更窄：每个主题一个带立场的默认值（iOS 26 是底线、单一 Package、
swift-testing + snapshot、只用 OSLog、已知的运行时 bug 要避开）。主题重叠处，两者不是重复，
而是回答的细节层级不同。

| Plugin | 作者 | 涵盖范围 |
|---|---|---|
| [`apple-skills`](https://github.com/Prisma-Labs-Dev/apple-skills) | Prisma Labs (vabole), MIT | 广泛的 Apple 框架 —— SwiftUI、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit、`apple-aso`、`hig`……以及一份 SwiftUI 性能审计指南，与 `ios-performance-engineering` 的 Instruments / MetricKit 测量互补；另外还有 `simulator-utils` 与 `xcuitest`（与本目录 Simulator／XCUITest 技能的分工见下方说明）。有一小部分技能放在 `disabled-skills/` —— 留在 repo 里但不会被 agent 加载 |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI 模式、Swift Charts、Liquid Glass、Instruments 工具链 |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI 陷阱、deprecated API 观察清单、iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | 极度压缩的沟通模式 —— 省下约 65% 输出 token（作者自测）；会安装 `SessionStart`／`UserPromptSubmit` hook（需要 PATH 上有 `node`，每条 prompt 都会执行）（通用 agent 行为） |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | “懒惰资深工程师”模式 —— 逼出最简单、最短的解法（通用 agent 行为） |
| [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) | Ayoub G. (MIT) | 常驻的 ADHD 友好输出模式 —— 编号步骤、每一轮重述状态（通用 agent 行为） |
| [`xcode-build-skill`](https://github.com/pzep1/xcode-build-skill) | pz (MIT) | `xcodebuild`/`xcrun simctl` CLI 小抄 —— scheme → 模拟器 → build → install → launch → 截图 |

`caveman` 的授权：技能本身 MIT；repo 另外还有一个 BSL-1.1 授权的 engine。`caveman` 之后已
长成 20 个技能的套件；其中 4 个（`caveman-discover`、`caveman-manage`、
`caveman-evidence-review`、`caveman-setup`）在讲作者自家托管的 Caveman Cloud 商业服务。

`i-have-adhd` 与 `caveman`（token 压缩）、`ponytail`（解法简化）不同，它塑形的是每次回答的
**结构**。

`xcode-build-skill`（`xcodebuild`／`simctl` 循环）与 `apple-skills:simulator-utils`（`simctl`
单次操作）是 CLI 参考手册；`interactive-simulator-ux-audit` 用 `idb` 做探索式审计；
`host-driven-xcuitest-e2e` 接 Tuist scheme 跑 CI —— `apple-skills:xcuitest` 是它假设你已具备
的 API 参考。

`apple-skills` 已从 `vabole` 的个人账号迁移到 `Prisma-Labs-Dev` 组织；此表列出的是组织版
repo。

## 其他安装方式

（A 就是上面的快速开始。）

### B —— 团队固定版本

直接在 `.claude/settings.json` 把 marketplace 锁定到一个已发布的 tag —— 不需要 submodule：

```json
{
  "extraKnownMarketplaces": {
    "apple-dev-skills": {
      "source": { "source": "github", "repo": "wei18/apple-dev-skills", "ref": "v2.0.0" }
    }
  },
  "enabledPlugins": {
    "apple-dev-skills@apple-dev-skills": true,
    "collaboration-skills@apple-dev-skills": true
  }
}
```

commit 它 —— 协作者信任该项目文件夹之后就会自动拿到这个 marketplace，不会有额外提示。两个
第一方 plugin 是相对路径条目，到这一步就已装好；外部 plugin 是 GitHub 来源，`enabledPlugins`
不会帮别人自动安装 —— 每位协作者仍要自己跑一次 Claude Code 打印出的 `claude plugin install …`
命令。

### C —— `npx skills`（平铺，不走 plugin）

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

> **路径 C 不包含汇总而来的外部 plugin。** `npx skills` 会读取本 repo 的
> `marketplace.json` / `plugin.json`，但只跟随本地声明的技能路径。它不会抓取外部
> plugin 的远端 `github` / `git-subdir` 来源。所以上述指令只会安装 38 个第一方技能 ——
> 7 个外部 plugin 会被静默跳过。若要平铺安装整份目录（含外部 plugin，从原作者的 repo 拉取）：

```bash
scripts/install-flat.sh -g          # user-level; drop -g for project-level
scripts/install-flat.sh --dry-run   # preview the `npx skills add` commands
```

## 贡献

三种帮忙方式：**汇总**一个外部 plugin、**新增**一个第一方技能、或**反馈**一则现场笔记
—— 见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 出处

第一方技能提取并去项目化自 [`wei18/Sudoku`](https://github.com/wei18/Sudoku) 的
`.claude/skills/` —— 一组 spec-first、由 AI Leader/Developer 打造、已上架的 Apple 平台游戏作品集 ——
再加上针对公开的 Apple / WCAG / Swift 标准所做的原创整理。汇总的外部 plugin 仍属其作者的作品，
此处仅以引用方式呈现。催生本 repo 双 plugin 结构的设计 spec 与计划原本放在 `docs/superpowers/`
—— 已退役、改由 git 历史保存；用 `git log -- docs/` 可以找回。MIT —— 见 [LICENSE](LICENSE)。

<!-- src-sha: 7924a7df00ae1716dc63a5f4079753769dc081f2 -->
