# PJM-041 — Route-change focus continuity

- Status: Draft PR; G3 review required before merge.
- Scope: keep keyboard and assistive-technology users oriented when the single-page app changes routes.
- Problem: activating a service route replaces the navigation controls; without an explicit focus destination, keyboard focus can fall back to the document and the new page may not be announced.
- Change: after in-app route navigation and browser back/forward navigation, move programmatic focus to the existing `main#main-content` landmark with `preventScroll`. Existing scroll-to-top behavior and optional region-input focus remain intact.
- Preserved: route behavior, history, booking flow, photos, maps, insurance content, all UI copy, and demo/safety boundaries.
- Acceptance:
  - Keyboard activation of a service route focuses the main landmark and updates the visible navigation item's `aria-current`.
  - Browser back restores the home route and focus to the main landmark.
  - Chromium 320/390/1440px and WebKit 390px pass without JavaScript errors.
  - Existing full Chromium/WebKit/axe and PJM-011/012/013 feature regressions pass on the exact PR head.
- Boundaries: G2 overall remains HOLD; no production booking/insurance/personal-data integration; Pages remains user-triggered manually; actual iPhone Safari/Instagram browser QA remains unverified.
