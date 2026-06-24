---
name: widgetkit-and-live-activities
description: Build WidgetKit timelines (StaticConfiguration, AppIntentConfiguration, TimelineProvider, reload policies), Lock Screen and watch accessory families, interactive widgets with Button/Toggle backed by AppIntent (iOS 17+), Control Center controls (iOS 18), and Live Activities with ActivityKit Dynamic Island regions and APNs remote updates. Invoke when creating a home-screen or Lock Screen widget, adding Live Activity / Dynamic Island support, choosing a reload policy, or debugging widget timeline staleness.
---

# WidgetKit & Live Activities

## When to invoke

- Creating any home-screen, Lock Screen, or StandBy widget.
- Choosing between `StaticConfiguration` and `AppIntentConfiguration` for a configurable widget.
- Debugging a widget that shows stale data or never reloads.
- Adding `Button(intent:)` or `Toggle(isOn:intent:)` interactive controls to a widget (iOS 17+).
- Implementing a Live Activity with Dynamic Island for an ongoing event (delivery, workout, game score).
- Setting up APNs remote updates for Live Activities.
- Targeting Apple Watch complications that share code with iOS Lock Screen accessories.

## Widget anatomy

A widget is a Swift package target that imports `WidgetKit` and `SwiftUI`. Three types are required:

1. **Entry** — a `TimelineEntry` with a `date` and any payload the view needs.
2. **Provider** — a `TimelineProvider` (or `AppIntentTimelineProvider`) that produces entries.
3. **Widget** — ties configuration, provider, and view together.

```swift
import WidgetKit
import SwiftUI

struct StepEntry: TimelineEntry {
    let date: Date
    let steps: Int
}

struct StepProvider: TimelineProvider {
    func placeholder(in context: Context) -> StepEntry {
        StepEntry(date: .now, steps: 0)
    }

    func getSnapshot(in context: Context, completion: @escaping (StepEntry) -> Void) {
        completion(StepEntry(date: .now, steps: 4_200))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<StepEntry>) -> Void) {
        let entry = StepEntry(date: .now, steps: HealthStore.shared.todaySteps())
        // Reload at midnight to reset the daily counter.
        let midnight = Calendar.current.startOfDay(for: .now).addingTimeInterval(86_400)
        completion(Timeline(entries: [entry], policy: .after(midnight)))
    }
}

@main
struct StepWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "com.example.StepWidget", provider: StepProvider()) { entry in
            StepView(entry: entry)
                .containerBackground(.fill.tertiary, for: .widget)
        }
        .configurationDisplayName("Steps")
        .description("Shows your step count for the day.")
        .supportedFamilies([.systemSmall, .systemMedium, .accessoryCircular, .accessoryRectangular])
    }
}
```

## Configurable widgets: `AppIntentConfiguration`

When a user should be able to pick which item a widget tracks (a city, a project, a stock), use `AppIntentConfiguration` and a companion `WidgetConfigurationIntent`.

```swift
struct CityWeatherIntent: WidgetConfigurationIntent {
    static var title: LocalizedStringResource = "City"
    @Parameter(title: "City", default: CityEntity.london)
    var city: CityEntity
}

struct WeatherProvider: AppIntentTimelineProvider {
    func placeholder(in context: Context) -> WeatherEntry { ... }
    func snapshot(for configuration: CityWeatherIntent, in context: Context) async -> WeatherEntry { ... }
    func timeline(for configuration: CityWeatherIntent, in context: Context) async -> Timeline<WeatherEntry> {
        let forecast = await WeatherService.fetch(city: configuration.city)
        let entries = forecast.hourly.map { WeatherEntry(date: $0.date, temp: $0.temp) }
        return Timeline(entries: entries, policy: .atEnd)
    }
}

// In the Widget body:
AppIntentConfiguration(kind: "com.example.WeatherWidget", intent: CityWeatherIntent.self, provider: WeatherProvider()) { entry in
    WeatherView(entry: entry)
        .containerBackground(.fill.tertiary, for: .widget)
}
```

`AppIntentTimelineProvider` has an `async` API (no completion handlers); prefer it for new widgets.

## Reload policies

The `policy` parameter of `Timeline` controls when WidgetKit requests a new timeline:

| Policy | Meaning |
|---|---|
| `.atEnd` | Request a new timeline after the last entry's date passes. Use for paginated forecasts. |
| `.after(Date)` | Request a new timeline at a specific future date regardless of entries. Use for daily resets or scheduled refreshes. |
| `.never` | Do not reload automatically. Use when the app pushes timeline updates via `WidgetCenter.shared.reloadTimelines(ofKind:)`. |

WidgetKit throttles background refreshes — typically 40–70 per day per widget family. Do not assume sub-minute granularity. For real-time data, use a Live Activity instead.

Push a reload from the host app after the user changes data:

```swift
WidgetCenter.shared.reloadTimelines(ofKind: "com.example.StepWidget")
// Or reload all widgets at once:
WidgetCenter.shared.reloadAllTimelines()
```

## Widget families and constraints

```
systemSmall / systemMedium / systemLarge / systemExtraLarge   — Home Screen
accessoryCircular / accessoryRectangular / accessoryInline    — Lock Screen & Apple Watch
```

- Use `.containerBackground` (iOS 17+) instead of a `ZStack` background — the system applies it correctly across StandBy, the Lock Screen, and iPad home screen.
- No scrolling, no video, no GIFs. All content is rendered as a snapshot.
- Memory budget is tight (~30 MB for the render pass). Avoid loading large images inside the timeline provider.
- Mark content that should be redacted during Lock Screen privacy mode with `.privacySensitive()`.
- Deep-link from a widget using `widgetURL(_:)` (applies to the whole widget) or `Link(destination:)` (iOS 17+ for individual regions in `systemMedium` and larger).

```swift
StepView(entry: entry)
    .widgetURL(URL(string: "myapp://steps")!)
```

## Interactive widgets (iOS 17+)

`Button` and `Toggle` backed by an `AppIntent` run in a lightweight background process — no app launch needed.

```swift
struct ToggleAlarmIntent: AppIntent {
    static var title: LocalizedStringResource = "Toggle Alarm"
    @Parameter(title: "Alarm ID") var alarmID: String
    func perform() async throws -> some IntentResult {
        try await AlarmStore.shared.toggle(id: alarmID)
        return .result()
    }
}

struct AlarmWidgetView: View {
    let entry: AlarmEntry
    var body: some View {
        Toggle(isOn: entry.isEnabled, intent: ToggleAlarmIntent(alarmID: entry.id)) {
            Label("Alarm", systemImage: "alarm")
        }
        .toggleStyle(.button)
    }
}
```

After `perform()` completes, reload the timeline to reflect the updated state:

```swift
func perform() async throws -> some IntentResult {
    try await AlarmStore.shared.toggle(id: alarmID)
    WidgetCenter.shared.reloadTimelines(ofKind: "com.example.AlarmWidget")
    return .result()
}
```

See `app-intents-and-shortcuts` for `AppIntent` authoring details and `@Dependency` injection.

## Widget previews

Use the `#Preview` macro (Xcode 15+) with a widget family:

```swift
#Preview(as: .systemSmall) {
    StepWidget()
} timeline: {
    StepEntry(date: .now, steps: 3_000)
    StepEntry(date: .now.addingTimeInterval(3600), steps: 7_500)
}
```

Supply multiple entries to preview the timeline stepping forward in Xcode's canvas.

## Live Activities: ActivityKit

Live Activities display real-time information on the Lock Screen and Dynamic Island for an ongoing event (a delivery, a sports game, a workout).

### Defining the attributes

```swift
import ActivityKit

struct DeliveryAttributes: ActivityAttributes {
    // Static — set once at launch, never changes.
    let orderID: String
    let restaurant: String

    // Dynamic — updated throughout the activity's lifetime.
    struct ContentState: Codable, Hashable {
        var status: String
        var minutesAway: Int
    }
}
```

### Starting an activity

```swift
let attributes = DeliveryAttributes(orderID: "42", restaurant: "Sakura")
let initialState = DeliveryAttributes.ContentState(status: "Preparing", minutesAway: 30)
let content = ActivityContent(state: initialState, staleDate: .now.addingTimeInterval(900))

let activity = try Activity.request(
    attributes: attributes,
    content: content,
    pushType: .token   // pass nil if you only update from the app
)
```

- `staleDate` — the date after which WidgetKit shows a visual stale indicator. Set it to reflect when the data is no longer trustworthy.
- `pushType: .token` enables APNs remote updates (see below).

### Updating and ending

```swift
let updatedState = DeliveryAttributes.ContentState(status: "On the way", minutesAway: 8)
let updatedContent = ActivityContent(state: updatedState, staleDate: .now.addingTimeInterval(300))
await activity.update(updatedContent)

// End the activity (persists on Lock Screen briefly, then disappears).
let finalState = DeliveryAttributes.ContentState(status: "Delivered", minutesAway: 0)
await activity.end(ActivityContent(state: finalState, staleDate: .now), dismissalPolicy: .after(.now.addingTimeInterval(30)))
```

### Dynamic Island views

Implement the Live Activity view inside a `Widget` conformance that uses `ActivityConfiguration`:

```swift
struct DeliveryLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: DeliveryAttributes.self) { context in
            // Lock Screen banner
            LockScreenDeliveryView(context: context)
                .containerBackground(.fill.tertiary, for: .widget)
        } dynamicIsland: { context in
            DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    Label(context.state.status, systemImage: "box.truck")
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Text("\(context.state.minutesAway) min")
                }
                DynamicIslandExpandedRegion(.bottom) {
                    ProgressView(value: progressFraction(context.state))
                }
            } compactLeading: {
                Image(systemName: "box.truck")
            } compactTrailing: {
                Text("\(context.state.minutesAway)m")
            } minimal: {
                Image(systemName: "box.truck")
            }
        }
    }
}
```

Dynamic Island regions:
- **`compactLeading` / `compactTrailing`** — shown when one other app also has an active Live Activity.
- **`minimal`** — tiny dot view when pushed to the ring.
- **`expanded`** — full expanded island with `.leading`, `.trailing`, `.center`, `.bottom` sub-regions.

### Remote updates via APNs

When `pushType: .token`, observe the push token and send updates server-side:

```swift
for await tokenData in activity.pushTokenUpdates {
    let token = tokenData.map { String(format: "%02x", $0) }.joined()
    await server.registerLiveActivityToken(token, for: activity.id)
}
```

APNs payload (sent with `apns-push-type: liveactivity` and `apns-topic: <BundleID>.push-type.liveactivity`):

```json
{
  "aps": {
    "timestamp": 1700000000,
    "event": "update",
    "content-state": { "status": "On the way", "minutesAway": 8 },
    "relevance-score": 75,
    "stale-date": 1700000900
  }
}
```

- Payload cap is ~8 KB.
- Maximum Live Activity duration is 8 hours; it can be extended to 12 hours via update.
- `relevance-score` (0–100) determines which Live Activity the Dynamic Island shows first when multiple are active.
- Set `"event": "end"` to terminate the activity from the server.

## Verification checklist

- `.containerBackground` is used instead of a manual `ZStack` background (required for StandBy / iPad compatibility).
- `.privacySensitive()` wraps any value that should be hidden on the Lock Screen when "Show Previews" is off.
- Timeline entries are spaced no closer than ~5 minutes to respect background refresh budgets.
- `AppIntentConfiguration` widgets reference a `WidgetConfigurationIntent`, not a plain `AppIntent`.
- Interactive `Button(intent:)` and `Toggle(isOn:intent:)` reload the timeline after `perform()` completes.
- `ActivityAttributes.ContentState` conforms to `Codable & Hashable`.
- `pushType: .token` is passed to `Activity.request` only when the server is set up to send APNs live-activity pushes — otherwise pass `nil`.
- `staleDate` is set to a realistic freshness window, not `.distantFuture`.
- Live Activity end is called (or the server sends `"event": "end"`) within 8 hours of start.

## Related skills

- `app-intents-and-shortcuts` — `AppIntent` protocol, `@Parameter`, `AppShortcutsProvider`, `AppEntity` / `EntityQuery`, and `@Dependency` injection that power interactive widget buttons and `ControlWidget`.
- `swiftui-state-and-composition` — view decomposition, `containerBackground`, and render performance rules that apply equally inside widget views.
