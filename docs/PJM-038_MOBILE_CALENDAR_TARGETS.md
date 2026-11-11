# PJM-038 — Mobile booking calendar week controls

- Status: Draft PR; G3 approval required before merge.
- Scope: touch target sizing for the previous/next week buttons in the existing 7-day virtual booking calendar.
- Problem: the two mobile calendar navigation buttons render at 34×34 CSS px, making a frequently used control harder to tap than the surrounding date and time choices.
- Change: at viewports up to 620px, expand the existing controls to 44×44px; desktop dimensions remain 34×34px.
- Preserved: calendar layout, seven-day timeline, dates, time slots, clinician selection, booking preview, photos, maps, insurance, and all safety copy. No booking behavior or data source changes.
- Acceptance:
  - Chromium checks 320/390/768/1440px and WebKit checks 320/390px.
  - Both week controls are at least 44×44px on mobile and remain 34×34px on desktop.
  - The seven-day strip remains present, no horizontal overflow or JavaScript errors.
  - Existing Chromium/WebKit/axe/map/booking/build regression succeeds on the exact PR head.
- Boundaries: G2 overall remains HOLD; no production booking/insurance/personal-data integration; Pages remains manually triggered; actual iPhone Safari/Instagram QA remains unverified.
