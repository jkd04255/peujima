# PJM-039 — Booking calendar keyboard focus visibility

- Status: Draft PR; G3 approval required before merge.
- Scope: visible keyboard focus for calendar date, time, and week-navigation controls.
- Problem: the global warm beige focus ring is low contrast against the calendar's cream and pale green surfaces, making keyboard position harder to track.
- Change: use the existing dark forest-green palette for a 3px outline with 3px offset on these calendar controls when focused via keyboard.
- Preserved: calendar layout, seven-day dates, time slots, week navigation, booking behavior, photos, insurance, hospital search, and all demo/safety messages.
- Acceptance:
  - Chromium at 320/390/1440px and WebKit at 390px expose the same high-contrast focus indicator on a date, a time slot, and the enabled week-navigation button.
  - The calendar remains free of horizontal overflow and JS errors.
  - Existing full Chromium/WebKit/axe, PJM-011/012/013, and static build regression succeeds on the exact PR head.
- Boundaries: G2 overall remains HOLD; no live booking/insurance/personal-data integration; Pages remains manually triggered; actual iPhone Safari/Instagram browser QA remains unverified.
