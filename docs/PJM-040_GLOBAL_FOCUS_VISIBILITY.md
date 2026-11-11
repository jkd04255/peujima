# PJM-040 — App-wide keyboard focus visibility

- Status: Merged to main by PR #35 at 2026-11-11; Pages remains user-triggered manually.
- Scope: consistent keyboard focus indication for navigation, hospital search, booking calendar, and insurance controls.
- Problem: the former warm beige global outline is too close to the light cream surfaces, and the calendar-specific dark ring from PJM-039 differs from other controls.
- Change: standardize focused buttons, links, inputs, and selects to a 3px forest-green outline with a 3px offset; this also makes PJM-039's calendar behavior consistent with the rest of the interface.
- Preserved: all control behavior, booking flow, photos, routes, maps, insurance content, and disclosures.
- Acceptance:
  - Chromium 320/390/1440px and WebKit 390px keyboard-test visible navigation, search input/action, booking date/time/week navigation, and insurance selector/action.
  - Every tested control uses the same 3px forest-green outline and 3px offset.
  - No horizontal overflow or JavaScript errors; existing Chromium/WebKit/axe and full feature regression passes on the exact PR head.
- Boundaries: G2 overall remains HOLD; no production integrations; Pages remains user-triggered manually; actual iPhone Safari/Instagram browser QA remains unverified.
