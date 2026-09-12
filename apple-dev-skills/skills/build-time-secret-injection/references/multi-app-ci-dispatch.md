# Multi-App CI Dispatch

### Multi-app dispatch in `ci_post_clone.sh`

When one repo ships multiple app schemes (e.g. AppA + AppB), XCC sets `$CI_PRODUCT` and `$CI_XCODE_SCHEME` per workflow. Case-switch on the scheme to pick the right env-var prefix:

```bash
case "${CI_XCODE_SCHEME:-${CI_PRODUCT:-}}" in
  AppA)
    APP_ID="${APP_A_ADMOB_APP_ID:?missing APP_A_ADMOB_APP_ID}"
    BANNER_UNIT_ID="${APP_A_ADMOB_BANNER_UNIT_ID:?missing APP_A_ADMOB_BANNER_UNIT_ID}"
    ;;
  AppB)
    APP_ID="${APP_B_ADMOB_APP_ID:?missing APP_B_ADMOB_APP_ID}"
    BANNER_UNIT_ID="${APP_B_ADMOB_BANNER_UNIT_ID:?missing APP_B_ADMOB_BANNER_UNIT_ID}"
    ;;
  *)
    echo "Unknown CI_XCODE_SCHEME: ${CI_XCODE_SCHEME:-}" >&2
    exit 1
    ;;
esac
cat > Tuist/AdMob.xcconfig <<EOF
ADMOB_APP_ID = ${APP_ID}
ADMOB_BANNER_UNIT_ID = ${BANNER_UNIT_ID}
EOF
```

Run **before** `tuist generate` so the per-target xcconfig reference resolves.
