# PJM-036 — Concise hospital result announcements

- Status: Draft PR; G3 approval required before merge.
- Scope: one accessibility-focused interaction change in nearby hospital search.
- Problem: a polite live region wrapped around the full result list can ask screen readers to announce many hospital cards after a search.
- Change: announce only the concise result count and sort order in a polite, atomic status; keep the hospital list itself outside a live region.
- Preserved: map, geolocation consent flow, regional search, radius filter, distance ordering, hospital cards, selection feedback, and external map/phone links.
- Acceptance:
  - Initial and updated result counts are exposed through one polite status.
  - Individual hospital cards are not automatically announced as live updates.
  - Chromium and WebKit marker-selection and nearby-search regression pass; axe checks and full QA pass on the exact PR head.
- Boundaries: G2 overall remains HOLD; no production booking/insurance/personal-data integrations; Pages remains user-triggered manually; actual iPhone Safari/Instagram browser QA remains unverified.
