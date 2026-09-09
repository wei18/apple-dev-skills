# apple-dev-skills

> Claude Codeを使ってiOSとAppleエコシステムのアプリをvibe codingするためのスキル集
> ——そして、それらを作り上げるagentを操るためのスキル集でもある。
>
> 言語：[English](README.md) · [繁體中文](README.zh-Hant.md) · [简体中文](README.zh-Hans.md) · [日本語](README.ja.md)

apple-dev-skillsは、アイデアをApp Storeへのリリースまで導く個人開発者や小規模チームのための
**マーケットプレイス**です。ファーストパーティのスキルは大きく二つに分かれています。作って
いるものそのものを担う**Apple/Swift**スキルと、Claude Code自体の操り方——計画、レビュー、
リリース——を担う**harness engineering**スキルです。どのスキルも実際にリリースまで漕ぎ着けた
実戦のエピソードに裏打ちされた、立場のある既定値であり、一貫性ゲートによって守られています。
あわせて、他に類を見ない**外部**スキルプラグインを**参照という形で集約**し——ここでは書かず、
リンクと著者クレジットのみで——決してコピーせずに並べています。

## クイックスタート

> スキルは頼んだ内容から自動的にトリガーされます——インストールしたら、あとはタスクを
> 説明するだけです。

Claude Codeのsession内で実行します。

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 26 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 12 agent-collaboration skills
```

インストール結果に`Run /reload-plugins to activate.`と表示されたら実行してください——古い
クライアントでは常に必要な手順です。

どちらか一方でも両方でもインストール可能です。外部プラグインも同じ方法でインストールできます。
例：`/plugin install swiftui-expert@apple-dev-skills`。

あとはやりたいことを説明するだけです。

- *「新しいiOSアプリを始めたい」* → `apple-platform-targets`が最低デプロイターゲットを決め、
  続けてパッケージ構成、言語モード、テストのベースラインへと順に引き継ぎます。
- *「App Reviewでguideline 5.1.2に引っかかった」* → `app-store-review-rejections`がそのガイド
  ラインを該当する修正方法にマッピングします。

特定のスキルを強制的に呼び出すにはスラッシュコマンドを使います：
`/apple-dev-skills:swift6-concurrency`。`/skills`でインストール済みのスキル一覧と、それぞれが
どのプラグイン由来かを確認できます。

> 新しくインストールされたスキルは、Claude Codeのスキル一覧のcontext予算が溢れたときに
> 最初に説明文を失います。`/doctor`で一覧のコストを確認してください。厳しい場合はsettingsで
> `skillListingBudgetFraction` / `skillOverrides`を調整してください。

## カタログ

- **Spec**（仕様策定）のフロー → `spec-phase-orchestration`
- プロジェクトを**Bootstrap**（起動） → `apple-platform-targets`
- UIを**Build**（構築） → `swiftui-navigation-architecture`
- **Test**（テスト） → `swift-testing-baseline`
- **Ship**（出荷） → `asc-api-automation`
- **Operate**（運用） → `apple-three-piece-analytics`

完全な索引は以下の表を参照してください。

### apple-dev-skills（26）—— Apple/Swift

| Skill | 一言でいうと |
|---|---|
| `swift6-concurrency` | Swift 6言語モード + 完全なconcurrencyチェック；デフォルトでSendable |
| `apple-platform-targets` | デフォルトはiOS 26 / macOS 26、Xcode 26.x；既存ユーザーが旧バージョンの場合のみ18 / 15へ下げる |
| `swiftpm-modularization` | 単一Package、マルチtarget、薄いApp、DI composition root、テストは1対1 |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot；protocol fake；厳格/寛容なsnapshotゲート |
| `xcode-cloud-single-track-ci` | シングルトラックのXcode Cloud；PR / Main / Release / Periodic；merge前のPR CI |
| `local-archive-export-upload` | Xcode Cloudが使えない場合のローカル`xcodebuild archive` → export → `altool`によるTestFlightアップロード |
| `mise-tool-management` | miseでCLIツールのバージョンを固定（swiftlint、xcbeautify…）——ローカル開発とCIで同じバージョンを使う |
| `oslog-logger-defaults` | デフォルトのlogging設定：Apple純正の`os.Logger`、サードパーティ不使用、opt-inしない限りログ値はprivate |
| `apple-three-piece-analytics` | App Store Connect (ASC) Analytics + MetricKit + Game Center；サードパーティトラッキング不使用；PrivacyInfoは必須 |
| `telemetry-facade-pattern` | logging呼び出しは1つ、OSLog / MetricKit / Game Centerへルーティング——呼び出し側を変えずに送り先を差し替えられる |
| `ai-translated-localization` | デフォルトで7言語；AI翻訳フロー；`Localizable.xcstrings`；網羅性ゲート |
| `ios-accessibility-engineering` | SwiftUIとUIKitにおけるVoiceOver / Dynamic Type / タップ領域 / Reduce Motion；WCAG 2.2 |
| `swift-dependency-injection` | テストのためにサービスを差し替え可能にする——protocol注入 + composition root（environment vs constructor、`@TaskLocal`、Sendable） |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch予算 / 起動 / メモリ / バイナリサイズ / MetricKit |
| `apple-public-repo-security` | 公開iOS/macOS repoのための三重防御 + rotate-firstな漏洩対応SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main`——バイナリには含めつつdiffには出さないID管理 |
| `storekit2-iap-defaults` | StoreKit 2の非消耗型IAPデフォルト；bridge protocolのテストシーム、entitlements、restore |
| `monetization-sdk-integration` | マネタイズSDKの追加／アップグレード／監査；`import`を単一のbridgeファイルに隔離 |
| `app-store-review-rejections` | 無料 + 広告 + IAP + CloudKit + Game Center (GC)におけるApp Review却下パターンの診断と事前対策 |
| `asc-api-automation` | `.p8`からES256 JWTを生成 + curlでASC REST APIを叩く——TestFlight、metadata、審査提出、レポート；fastlane不使用 |
| `swiftui-interaction-footguns` | 純粋なコードレビューでは見逃されがちな既知のSwiftUIインタラクションバグ |
| `swiftui-navigation-architecture` | SwiftUI向けの型付きルートナビゲーション——`@Observable`router一つ、`NavigationStack`、ディープリンク、macOSフォールバックも対応済み |
| `ios-design-mockup` | specから単一HTMLファイルのiOSデザインモックアップを生成——iPhoneフレーム + トークン |
| `interactive-simulator-ux-audit` | `idb`（tap/describe/screenshot）で起動中のSimulatorを操作し、スナップショットでは見つからないナビゲーション／モーダル／safe-areaのバグを検出 |
| `host-driven-xcuitest-e2e` | Tuist経由でアプリを起動しXCUITest E2Eを実行——専用scheme配線 + macOSウィンドウ座標でのクリック操作 |
| `cloudkit-schema-source-of-truth` | バージョン管理された`.ckdb` + `cktool`によるDevelopmentへのexport／validate／deploy；ProductionはConsoleのみのユーザー管理ゲート |

### collaboration-skills（12）—— harness engineering：ディスパッチ、レビュー、リリース

| Skill | 一言でいうと |
|---|---|
| `spec-phase-orchestration` | 実装前のドキュメントパイプライン；セクションごとの承認 |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewerのトライアド；1ラウンド目の外観上の指摘はinlineで即対応；limit(N) |
| `leader-developer-handoff-contract` | sub-agentへのディスパッチ時に必須の5要素 |
| `agent-impl-notes-log` | sub-agentタスク進行中のリアルタイムimpl-notes——意思決定、逸脱、未解決の疑問 |
| `subagent-conflict-detection` | 新しいsub-agentの作業対象が進行中のworktreeと重複していないか確認 |
| `methodology-pattern-extractor` | 会議記録から3回以上繰り返されるパターンを抽出 |
| `session-to-meeting-log` | Claude Codeのsessionを会議記録にまとめる；逐語録ではなく要約 |
| `pr-diff-verification` | push／PR作成前に`git show --stat HEAD`がcommitの主張と一致することを確認 |
| `backlog-routing-by-topic` | 散発的なアイデアをトピックごとに対応するspecファイルの§Backlogへ振り分け |
| `claude-skill-plugin-packaging` | Claude Codeスキルの配布／インストール——depth-1ルール、plugin + marketplace、集約 |
| `skill-authoring-patterns` | `superpowers:writing-skills`の上に重なるApple/Swiftカタログ層——routerの説明文、bookendセクション、二層のreferences、エビデンスベースのCR |
| `github-contribution-workflow` | gh-CLIによるコントリビューションループ——PR、issue、GitHubファイル操作、secrets、コントリビューションフローのrepo設定；規約 + merge前のCLEAN |

### 外部プラグイン集約（7）—— 参照によるクレジット付き集約

ここに掲載されているだけで、**ここで書かれたものではありません**——それぞれ著者自身のrepoから
インストールされ（最新版が手に入ります）、著者名を完全にクレジットしています。**集約であって、
我が物にすることではありません**：MIT互換で重複のないプラグインのみを、本当にギャップがある
場合に限って掲載します——このチェックは掲載する時点で一度だけ行われ、上流のcommitのたびに
再審査するわけではないため、外部プラグインの範囲やライセンスは掲載後に変わることがあります
（`caveman`はすでに変わっています）。外部プラグインは幅広い**リファレンス**です——「これが
APIです、Xはこう作ります」。ファーストパーティのスキルはより狭く、トピックごとに立場のある
デフォルト値が一つだけあります（iOS 26を下限に、単一Package、swift-testing + snapshot、
OSLogのみ、避けるべき既知の実行時バグ）。トピックが重なる箇所でも、両者は重複ではなく、
答える詳細度のレベルが違うだけです。

| Plugin | Author | Covers |
|---|---|---|
| [`apple-skills`](https://github.com/Prisma-Labs-Dev/apple-skills) | Prisma Labs (vabole), MIT | 幅広いAppleフレームワーク——SwiftUI、SwiftData、App Intents、WidgetKit、StoreKit、HealthKit……に加え、SwiftUIパフォーマンス監査ガイド（コードファースト、view-update要因）も収録。`ios-performance-engineering` のInstruments / MetricKit計測と相補的 |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUIパターン、Swift Charts、Liquid Glass、Instrumentsツールチェーン |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUIの落とし穴、非推奨APIのウォッチリスト、iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | 超圧縮されたコミュニケーションモード——トークンを約75%削減（汎用的なagentの振る舞い） |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | 「怠け者のシニア開発者」モード——最もシンプルで最短の解法を強制する（汎用的なagentの振る舞い） |
| [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) | Ayoub G. (MIT) | 常時ONのADHDフレンドリーな出力モード——番号付きステップ、毎ターン状態を再掲示（汎用的なagentの振る舞い） |
| [`xcode-build-skill`](https://github.com/pzep1/xcode-build-skill) | pz (MIT) | `xcodebuild`/`xcrun simctl` CLIチートシート——scheme → simulator → build → install → launch → screenshot |

`caveman`のライセンス：skills自体はMIT、repoにはBSL-1.1ライセンスのengineも含まれています。
`caveman`はその後20スキルからなるスイートへと成長しました。そのうち4つ（`caveman-discover`、
`caveman-manage`、`caveman-evidence-review`、`caveman-setup`）は、著者自身がホストする商用
サービスCaveman Cloudについて説明したものです（汎用的なagentの振る舞い）。

`i-have-adhd`は`caveman`（トークン圧縮）や`ponytail`（解法の単純化）とは異なり、構造を
形作ります。

`xcode-build-skill`はCLI駆動で、`interactive-simulator-ux-audit`（idb駆動のインタラクティブ
UX監査）や`host-driven-xcuitest-e2e`（Tuist scheme配線のXCUITest E2E）とは別物です——三者は
重複しません。

`apple-skills`は`vabole`の個人アカウントから`Prisma-Labs-Dev`organizationへ移管されました。
この表には移管後のrepoを掲載しています。

## 他のインストール方法

### B —— チーム向けの固定バージョン

`.claude/settings.json`でmarketplaceをリリース済みのtagに直接固定できます——submoduleは
不要です：

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

これをcommitしておけば、コラボレーターがそのプロジェクトフォルダを信頼した時点で、追加の
確認なしに自動的にこのmarketplaceが使えるようになります。それでもClaude Codeがあるプラグイン
を未インストールと報告する場合は、表示された`/plugin install`コマンドを一度実行してください。

### C —— `npx skills`（フラット、プラグイン不使用）

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

> **経路Cには集約された外部プラグインは含まれません。** `npx skills`はこのrepoの
> `marketplace.json` / `plugin.json`を読み込みますが、ローカルで宣言されたスキルのパスしか
> 辿りません。外部プラグインのリモートの`github` / `git-subdir`ソースは取得しません。その
> ため上記のコマンドは39のファーストパーティスキルしかインストールしません——7つの外部
> プラグインは黙って読み飛ばされます。カタログ全体（外部プラグインを含め、著者のrepoから
> 取得）をフラットにインストールするには：

```bash
scripts/install-flat.sh -g          # user-level; drop -g for project-level
scripts/install-flat.sh --dry-run   # preview the `npx skills add` commands
```

## コントリビューション

貢献する方法は3つあります：外部プラグインを**集約する**、ファーストパーティのスキルを
**追加する**、または現場のフィールドノートを**報告する**——詳しくは
[CONTRIBUTING.md](CONTRIBUTING.md)を参照してください。

## 由来

ファーストパーティのスキルは[`wei18/Sudoku`](https://github.com/wei18/Sudoku)の
`.claude/skills/`から抽出・汎用化されたものです——spec-first、AIのLeader/Developerによって
作られ実際にリリースされたApple platformゲームのポートフォリオです——それに加えて、公開
されているApple / WCAG / Swiftの標準についてのオリジナルの解説を組み合わせています。集約
された外部プラグインは、あくまでその著者自身の作品であり、ここでは参照という形でのみ
紹介しています。このrepoの2プラグイン構成を生み出した設計specと計画は元々
`docs/superpowers/`にありました——現在は廃止され、git履歴として保存されています。
`git log -- docs/`で見つけることができます。MIT——[LICENSE](LICENSE)を参照してください。

<!-- src-sha: f164342e405c92e1e12f5c2d33c64ee2ca162293 -->
