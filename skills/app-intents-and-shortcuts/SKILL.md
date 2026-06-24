---
name: app-intents-and-shortcuts
description: Design and implement App Intents for Siri, Shortcuts, Spotlight, interactive widgets, and iOS 18 Control Center controls; covers AppIntent/perform(), @Parameter, AppShortcutsProvider, AppEntity/EntityQuery, SetFocusFilterIntent, and @Dependency injection into intents. Invoke when adding Siri support, building a Shortcuts action, exposing app data as entities, powering a widget Button or Toggle with an intent, or wiring up a Control Center widget.
---

# App Intents & Shortcuts

## When to invoke

- Adding a Siri voice command or Shortcuts automation action to an app.
- Exposing app data (tasks, timers, favourites) to Spotlight or Shortcuts as queryable entities.
- Powering an interactive widget `Button` or `Toggle` with a background action (iOS 17+).
- Building an iOS 18 Control Center control with `ControlWidget`.
- Implementing a Focus filter via `SetFocusFilterIntent`.
- Asking "how do I inject a service into an intent" or "how does `@Dependency` work with App Intents".

## Core building block: `AppIntent`

Every action starts with a type conforming to `AppIntent`. The system calls `perform()` and you return a result.

```swift
import AppIntents

struct StartTimerIntent: AppIntent {
    static var title: LocalizedStringResource = "Start Timer"
    static var description = IntentDescription("Starts a countdown timer for the specified duration.")

    @Parameter(title: "Duration", default: 25, requestValueDialog: "How many minutes?")
    var minutes: Int

    func perform() async throws -> some IntentResult & ProvidesDialog {
        let timer = try await TimerService.shared.start(minutes: minutes)
        return .result(dialog: "Started a \(minutes)-minute timer.")
    }
}
```

Key points:

- `perform()` returns `some IntentResult`. The most common concrete returns are:
  - `.result()` — no output, just completes.
  - `.result(value:)` — returns a typed value (used when other intents chain into this one).
  - `.result(dialog:)` — speaks a confirmation phrase in Siri.
  - `.result(dialog:view:)` — attaches a SwiftUI snippet to the Siri response card.
- `static var title` is the display name in Shortcuts and Spotlight. It must be a `LocalizedStringResource`.
- `IntentDescription` provides the longer description shown in the Shortcuts gallery.
- `@Parameter` marks each input. The `title` is user-facing; `default` pre-fills the value; `requestValueDialog` is the prompt Siri speaks when the value is missing.

## Surfacing actions: `AppShortcutsProvider`

Define which of your intents surface automatically in Siri and Spotlight — no user setup required:

```swift
struct TimerShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: StartTimerIntent(),
            phrases: [
                "Start a timer with \(.applicationName)",
                "Begin \(.applicationName) countdown"
            ],
            shortTitle: "Start Timer",
            systemImageName: "timer"
        )
    }
}
```

- `\(.applicationName)` is a required interpolation in at least one phrase per shortcut — Siri uses it to route the utterance to your app.
- Phrases are matched phonetically; provide two to four variants covering natural speech patterns.
- Call `TimerShortcuts.updateAppShortcutParameters()` whenever the parameter options change (for example, after the user creates a new timer preset) so Siri's donation index stays current.
- Shortcuts built from `AppShortcutsProvider` appear in Spotlight search and the Shortcuts gallery without any user configuration.

## Exposing data: `AppEntity` and `EntityQuery`

When an intent operates on a user-defined item (a project, a contact, a recipe), model it as an `AppEntity` so Siri and Shortcuts can resolve it by name.

```swift
struct ProjectEntity: AppEntity {
    static var typeDisplayRepresentation = TypeDisplayRepresentation(name: "Project")
    static var defaultQuery = ProjectQuery()

    let id: UUID
    var displayRepresentation: DisplayRepresentation {
        DisplayRepresentation(title: "\(name)")
    }

    var name: String
}

struct ProjectQuery: EntityQuery {
    func entities(for identifiers: [UUID]) async throws -> [ProjectEntity] {
        try await ProjectStore.shared.fetch(ids: identifiers).map(\.asEntity)
    }

    func suggestedEntities() async throws -> [ProjectEntity] {
        try await ProjectStore.shared.recent().map(\.asEntity)
    }
}
```

- `TypeDisplayRepresentation` is the plural/singular name shown in the Shortcuts parameter picker.
- `DisplayRepresentation` is the per-instance label Siri reads back ("You selected **Quarterly Review**").
- For small, bounded collections (status values, difficulty levels), conform to `EnumerableEntityQuery` and implement `allEntities()` instead of `suggestedEntities()` — the system caches the full list for offline resolution.
- Reference the entity in an intent via `@Parameter var project: ProjectEntity`.

## Interactive widgets: intent-backed `Button` and `Toggle`

From iOS 17, widget buttons and toggles are backed by `AppIntent` directly. The intent runs in a lightweight extension process — no widget reload required.

```swift
struct ToggleFavouriteIntent: AppIntent {
    static var title: LocalizedStringResource = "Toggle Favourite"

    @Parameter(title: "Item ID")
    var itemID: String

    func perform() async throws -> some IntentResult {
        try await FavouriteStore.shared.toggle(id: itemID)
        return .result()
    }
}

// Inside the widget's view:
Button(intent: ToggleFavouriteIntent(itemID: entry.id)) {
    Image(systemName: entry.isFavourite ? "star.fill" : "star")
}
Toggle(isOn: entry.isEnabled, intent: TogglePowerIntent(itemID: entry.id)) {
    Label("Enable", systemImage: "bolt")
}
```

Constraints: `perform()` must complete within a few seconds; it cannot present UI or trigger alerts. For feedback, reload the widget timeline after the intent finishes: `WidgetCenter.shared.reloadTimelines(ofKind: "com.example.MyWidget")`.

## iOS 18 Control Center: `ControlWidget`

A `ControlWidget` puts a persistent tile in Control Center, backed by an intent that runs on tap.

```swift
import WidgetKit

struct TimerControl: ControlWidget {
    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(kind: "com.example.TimerControl", provider: TimerControlProvider()) { value in
            ControlWidgetButton(action: StartTimerIntent()) {
                Label(value.isRunning ? "Stop Timer" : "Start Timer", systemImage: "timer")
            }
        }
    }
}

struct TimerControlProvider: ControlValueProvider {
    var previewValue: TimerControlValue { TimerControlValue(isRunning: false) }
    func currentValue() async throws -> TimerControlValue {
        TimerControlValue(isRunning: await TimerService.shared.isRunning)
    }
}

struct TimerControlValue {
    let isRunning: Bool
}
```

`ControlWidgetButton` and `ControlWidgetToggle` accept an `AppIntent` directly. Add the `ControlWidget` extension target in Xcode; it shares the same App Intents extension as your Shortcuts actions.

## Focus filters: `SetFocusFilterIntent`

A Focus filter lets iOS configure your app when the user activates a Focus mode (Work, Sleep, etc.):

```swift
struct TimerFocusFilter: SetFocusFilterIntent {
    static var title: LocalizedStringResource = "Configure Timer for Focus"

    @Parameter(title: "Allow Reminders", default: true)
    var allowReminders: Bool

    func perform() async throws -> some IntentResult {
        AppSettings.shared.remindersEnabled = allowReminders
        return .result()
    }
}
```

Register the filter in the app's `Info.plist` under `NSFocusedContextPrimaryAttribute`. iOS calls `perform()` when the Focus activates or its parameters change.

## Injecting services with `@Dependency`

App Intents run in a separate extension process. Reach app services through `@Dependency` (from `pointfreeco/swift-dependencies`) or through a shared `AppGroup` container. Avoid singletons that rely on the main app process being alive.

```swift
struct StartTimerIntent: AppIntent {
    @Dependency var timerStore: TimerStore  // resolved via swift-dependencies container

    func perform() async throws -> some IntentResult {
        try await timerStore.start(minutes: minutes)
        return .result()
    }
}
```

For the live app target, register the concrete implementation in `withDependencies` at startup. For tests, override in `withDependencies { $0.timerStore = FakeTimerStore() }`.

## `openAppWhenRun` and `ProgressReportingIntent`

- Set `static var openAppWhenRun = true` when the intent needs to display UI or start a multi-step flow in the foreground app. Siri launches the app before calling `perform()`.
- Conform to `ProgressReportingIntent` for long-running work. Assign `self.progress` a `Progress` object; the system reflects it in the Shortcuts UI:

```swift
struct ExportIntent: AppIntent, ProgressReportingIntent {
    func perform() async throws -> some IntentResult {
        progress.totalUnitCount = 100
        for step in 0..<100 {
            try await doWork(step)
            progress.completedUnitCount = Int64(step + 1)
        }
        return .result()
    }
}
```

## Testing intents

Intents are plain `async throws` functions — unit-test them directly without the Shortcuts runtime.

```swift
@Test func startsTimerWithCorrectDuration() async throws {
    let store = FakeTimerStore()
    var intent = StartTimerIntent()
    intent.minutes = 15
    withDependencies { $0.timerStore = store } operation: {
        _ = try await intent.perform()
    }
    #expect(store.lastStartedMinutes == 15)
}
```

For parameter resolution, test `EntityQuery` implementations independently by calling `suggestedEntities()` or `entities(for:)` directly.

## Verification checklist

- Every `AppShortcut` phrase contains `\(.applicationName)`.
- `AppShortcutsProvider.updateAppShortcutParameters()` is called after any change to parameter options.
- `AppEntity` conforms to `Identifiable` with a stable `id` (UUID or persistent store key — never an index).
- Intents that must display UI set `openAppWhenRun = true`; all others avoid it (forces foreground launch unnecessarily).
- The intent extension shares an `AppGroup` container (or uses `swift-dependencies`) with the host app — no direct XPC calls into the main process.
- `perform()` is tested without the Shortcuts runtime using fake dependencies.
- `ControlWidget` and interactive widget intents complete in under a few seconds; longer work is dispatched via `BackgroundTasks`.

## Related skills

- `widgetkit-and-live-activities` — `Button(intent:)` and `Toggle(isOn:intent:)` in widget views; `ControlWidget` deployment; timeline reload after intent completes.
- `swift-dependency-injection` — `@Dependency` registration, `withDependencies` overrides in tests, and why the intent extension process cannot share in-memory singletons with the host app.
