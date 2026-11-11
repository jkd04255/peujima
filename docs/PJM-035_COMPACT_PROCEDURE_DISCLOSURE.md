# PJM-035 — Compact procedure disclosure

- Status: Draft PR review; G3 approval required before merge.
- Scope: one UI change in the insurance result.
- Problem: treatment and examination breakdowns can contain many rows and push the main coverage summary far down the mobile screen.
- Change: keep the existing procedure heading and item count visible, and place the detailed rows behind a native, keyboard-operable disclosure that starts collapsed.
- Preserved: existing coverage summary, costs, evidence links, fine print, photos, visual language, and all hospital search, demo booking, insurance, and cost information.
- Acceptance:
  - The insurer and care selectors still produce the same result and clear stale results.
  - Procedure details are collapsed on initial result display and can be expanded by keyboard or pointer.
  - Expanded details retain all existing row names, prices, evidence grades, and source/fine-print behavior.
  - Chromium and WebKit regression, axe checks, map/booking regression, and Pages build succeed on the exact PR head.
- Boundaries: G2 overall remains HOLD; no production integration; real iPhone Safari and Instagram browser testing remain unverified; do not merge or deploy before G3 approval.
