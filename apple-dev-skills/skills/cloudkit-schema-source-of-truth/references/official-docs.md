Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Deploying an iCloud Container's Schema | https://developer.apple.com/documentation/cloudkit/deploying-an-icloud-container-s-schema | "you can't delete record types or fields that are already in production"; deploy copies indexes, but the no-delete list doesn't cover indexes |
| Designing and Creating a CloudKit Database | https://developer.apple.com/documentation/cloudkit/designing-and-creating-a-cloudkit-database | Only additive schema changes; just-in-time schema |
| Inspecting and Editing an iCloud Container's Schema | https://developer.apple.com/documentation/cloudkit/inspecting-and-editing-an-icloud-container-s-schema | Viewing/removing indexes; fields in a production schema can't be deleted |
| Automate CloudKit tests with cktool and declarative schema (WWDC21) | https://developer.apple.com/videos/play/wwdc2021/10118/ | Management tokens; export/import; "it is possible to add and remove indexes in production" (overrides the add-only index claim elsewhere in this skill) |
