---
name: swiftdata-persistence
description: Model local data with SwiftData (iOS 17+/macOS 14+) — @Model, ModelContainer, ModelContext, @Query, relationships, schema migration, CloudKit sync, and background concurrency via @ModelActor. Invoke when persisting data on Apple platforms, choosing between SwiftData and Core Data, wiring CloudKit sync, or asking "how do I query / migrate / test with SwiftData".
---

# SwiftData Persistence

## When to invoke

- Starting a new app feature that requires local persistence on iOS 17+/macOS 14+.
- Deciding between SwiftData, raw Core Data, or a flat file / JSON store.
- Adding CloudKit sync to an existing SwiftData stack.
- Designing background processing pipelines that touch the data store.
- Writing schema migrations or handling versioned models.
- Setting up in-memory containers for unit tests.

## Core API surface

### `@Model` and the container chain

`@Model` is a Swift macro applied to a class (not a struct — SwiftData models must be reference types). It synthesises `PersistentModel` conformance, observable tracking via `@Observable`, and codegen for the underlying store schema.

```swift
@Model
final class Task {
    var title: String
    var createdAt: Date
    var isCompleted: Bool

    init(title: String) {
        self.title = title
        self.createdAt = Date()
        self.isCompleted = false
    }
}
```

A `ModelContainer` is the root object: it holds the schema, configuration, and the underlying store (SQLite by default). Create it once per process, typically in the `@main` App:

```swift
@main struct MyApp: App {
    let container: ModelContainer = {
        let schema = Schema([Task.self, Project.self])
        let config = ModelConfiguration(schema: schema, isStoredInMemoryOnly: false)
        return try! ModelContainer(for: schema, configurations: [config])
    }()

    var body: some Scene {
        WindowGroup { ContentView() }
            .modelContainer(container)
    }
}
```

`ModelContext` is the unit-of-work object — the analogue of `NSManagedObjectContext`. SwiftUI injects a main-thread context via `@Environment(\.modelContext)`. Call `insert`, `delete`, and `save` on it directly; contexts auto-save on scene lifecycle events by default.

```swift
@Environment(\.modelContext) private var context

func addTask(title: String) throws {
    let task = Task(title: title)
    context.insert(task)
    try context.save()   // explicit save when you need immediate persistence
}

func remove(_ task: Task) throws {
    context.delete(task)
    try context.save()
}
```

### `@Query` — declarative fetching in SwiftUI

`@Query` drives a live-updating array in any SwiftUI view. The property wrapper listens to store changes and rerenders when results change.

```swift
// Simple — all tasks, creation order
@Query(sort: \Task.createdAt, order: .forward)
private var tasks: [Task]

// With a predicate (Swift 5.9 `#Predicate` macro)
@Query(filter: #Predicate<Task> { !$0.isCompleted },
       sort: \Task.createdAt)
private var pending: [Task]
```

`#Predicate` compiles to a `Foundation.Predicate<T>` that SwiftData translates to SQL. Supported operations: equality, comparisons, `&&`, `||`, `!`, `.contains`, `.hasPrefix`, optional chaining. Unsupported: arbitrary closures, computed properties. If you need complex filtering, fetch unfiltered and filter in memory, or add a denormalised indexed property.

For programmatic fetches outside SwiftUI, use `ModelContext.fetch`:

```swift
let descriptor = FetchDescriptor<Task>(
    predicate: #Predicate { $0.isCompleted },
    sortBy: [SortDescriptor(\Task.createdAt, order: .reverse)]
)
descriptor.fetchLimit = 50
let results = try context.fetch(descriptor)
```

## Relationships

Declare relationships as stored properties. SwiftData infers a one-to-many or many-to-many relationship from the types involved.

```swift
@Model final class Project {
    var name: String
    @Relationship(deleteRule: .cascade, inverse: \Task.project)
    var tasks: [Task] = []
}

@Model final class Task {
    var title: String
    var project: Project?
}
```

`deleteRule` options:
- `.nullify` (default) — sets the inverse to nil when the owner is deleted.
- `.cascade` — deletes all related objects recursively.
- `.deny` — raises an error if the owner still has non-nil relationships.
- `.noAction` — leaves the related objects untouched (use with caution; can leave dangling references).

## Attributes

```swift
@Model final class User {
    @Attribute(.unique) var email: String        // uniqueness constraint
    @Attribute(.externalStorage) var avatar: Data?  // large blobs stored outside SQLite row
    @Attribute(.transformable(by: ColorTransformer.self)) var tint: UIColor?
    // Transient — not persisted, recomputed each load
    @Transient var displayLabel: String { email.components(separatedBy: "@").first ?? email }
}
```

`#Unique` (macro form) lets you declare a compound uniqueness constraint:

```swift
@Model
@Unique(\Task.title, \Task.project)
final class Task { ... }
```

Note: `@Attribute(.unique)` is **incompatible with CloudKit sync** (see below).

## Schema migration

When the model shape changes between app versions, define versioned schemas and a migration plan.

```swift
enum TaskSchemaV1: VersionedSchema {
    static var versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [Task.self] }

    @Model final class Task {
        var title: String
        var createdAt: Date
    }
}

enum TaskSchemaV2: VersionedSchema {
    static var versionIdentifier = Schema.Version(2, 0, 0)
    static var models: [any PersistentModel.Type] { [Task.self] }

    @Model final class Task {
        var title: String
        var createdAt: Date
        var priority: Int = 0   // new column with default
    }
}

enum TaskMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [TaskSchemaV1.self, TaskSchemaV2.self]
    }
    static var stages: [MigrationStage] {
        [migrateV1toV2]
    }
    // Lightweight migration — column added with a default; no custom code needed
    static let migrateV1toV2 = MigrationStage.lightweight(
        fromVersion: TaskSchemaV1.self,
        toVersion: TaskSchemaV2.self
    )
}
```

For non-trivial migrations (renaming, data transformation), use `MigrationStage.custom(fromVersion:toVersion:willMigrate:didMigrate:)`. The `willMigrate` / `didMigrate` closures receive a `ModelContext` in the old / new schema respectively, so you can back-fill values before or after the store upgrade.

Use lightweight stages wherever possible: adding a nullable column, adding a relationship, adding a model type, removing a column. Any structural change the SQLite migration engine cannot infer automatically requires a custom stage.

## CloudKit sync

Pass a `cloudKitDatabase` parameter to `ModelConfiguration`:

```swift
let config = ModelConfiguration(
    schema: schema,
    cloudKitDatabase: .automatic   // uses default CKContainer
)
// or .private(containerIdentifier: "iCloud.com.example.MyApp")
```

CloudKit sync imposes hard constraints on the schema:
- **All properties must be optional or have a default value** — CloudKit cannot guarantee record completeness across devices.
- **`@Attribute(.unique)` is not supported** — CloudKit has no per-field uniqueness enforcement.
- **Relationships must be optional** — required relationships break sync on partial fetches.
- **Enum stored properties need `@Attribute(.transformable(...))`** unless they are `RawRepresentable` with a CloudKit-native raw type.

To coexist with an app that has an existing production CKContainer schema, prefer `ModelConfiguration(cloudKitDatabase: .private("iCloud.com.example.MyApp"))` and ensure your SwiftData schema does not define record types that clash with hand-authored CK record types. SwiftData manages its own namespace (`CD_` prefix on field names) but shares the container.

## Concurrency: `@ModelActor`

`ModelContext` is **not `Sendable`** and must not cross actor boundaries. To do background processing, create a dedicated actor with `@ModelActor`:

```swift
@ModelActor
actor TaskProcessor {
    func markOverdue() throws {
        let cutoff = Date.now.addingTimeInterval(-86_400)
        let descriptor = FetchDescriptor<Task>(
            predicate: #Predicate { !$0.isCompleted && $0.createdAt < cutoff }
        )
        let overdue = try modelContext.fetch(descriptor)
        overdue.forEach { $0.isCompleted = false /* set a flag */ }
        try modelContext.save()
    }
}

// At call site — pass the container, not a context
let processor = TaskProcessor(modelContainer: container)
try await processor.markOverdue()
```

`@ModelActor` synthesises an initialiser that accepts a `ModelContainer` and creates a private `ModelContext` owned by the actor. **Never pass a `@Model` instance across actor boundaries** — pass `PersistentIdentifier` instead and re-fetch on the receiving actor:

```swift
// Crossing actor boundary — pass the ID
let id: PersistentIdentifier = task.persistentModelID
await backgroundActor.process(id: id)

// Inside the actor — re-fetch by ID
func process(id: PersistentIdentifier) throws {
    let task = modelContext.model(for: id) as? Task
    ...
}
```

## When to use SwiftData vs alternatives

| Scenario | Recommendation |
|---|---|
| iOS 17+ only, relational data, CloudKit sync, SwiftUI-first | SwiftData — minimal boilerplate, `@Query` is excellent |
| iOS 15/16 support required | Raw Core Data — SwiftData is iOS 17+ |
| Existing Core Data model in production | Core Data; optionally add a SwiftData layer with `ModelContainer(for: schema, configurations: [config])` setting `NSPersistentStoreDescription` via `ModelConfiguration` URL override |
| Very large binary blobs (video, audio) | Store the file in the filesystem; persist the URL only. `@Attribute(.externalStorage)` helps for moderate sizes |
| Simple key-value or user settings | `UserDefaults` / `@AppStorage` — relational overhead not worth it |
| Structured document with no relationships | `Codable` + JSON / plist in the app's `Documents` directory |

To coexist with a legacy Core Data stack, create the `NSPersistentContainer` as usual and construct the `ModelContainer` with a matching `ModelConfiguration(url:)` pointing to the same SQLite file. Both stacks can read and write the same store, but schema changes must be coordinated manually — SwiftData migrations do not merge with `NSMigratePersistentStoresAutomaticallyOption`.

## Testing

Use an in-memory configuration so tests are hermetic and fast:

```swift
@Suite struct TaskTests {
    var container: ModelContainer
    var context: ModelContext

    init() throws {
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        container = try ModelContainer(for: Task.self, configurations: [config])
        context = ModelContext(container)
    }

    @Test func insertsAndFetches() throws {
        context.insert(Task(title: "Write tests"))
        let all = try context.fetch(FetchDescriptor<Task>())
        #expect(all.count == 1)
        #expect(all.first?.title == "Write tests")
    }
}
```

Do not rely on `@Query` in unit tests — it requires a SwiftUI environment. Test fetch logic directly via `ModelContext.fetch` with `FetchDescriptor`.

## Verification checklist

- `ModelContainer` is created once and injected via `.modelContainer(_:)` — never constructed inside a View.
- All `@Model` types have a no-argument-reachable `init` (even if parameterised) — required for CloudKit sync hydration.
- Any property without a CloudKit-safe default is `Optional` when sync is enabled.
- `@Attribute(.unique)` is absent when CloudKit sync is active.
- Background work uses `@ModelActor`; `PersistentIdentifier` crosses actor boundaries, not model objects.
- Schema migration plan lists every version from v1 to current; missing a stage causes a runtime crash.
- Tests use `isStoredInMemoryOnly: true` — no on-disk SQLite files in the test suite.
- `try context.save()` is called explicitly after mutations in non-SwiftUI code paths.

## Related skills

- `swift6-concurrency`: `@ModelActor` is an `actor`; all Swift 6 actor-isolation rules apply. `ModelContext` non-`Sendable` constraint is enforced at compile time in strict mode.
- `swift-dependency-injection`: inject `ModelContainer` (not `ModelContext`) at the composition root; background actors receive the container and create their own contexts.
