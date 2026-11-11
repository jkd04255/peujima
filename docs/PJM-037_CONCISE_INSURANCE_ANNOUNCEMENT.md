# PJM-037 — Concise insurance result announcements

- Status: Draft PR; G3 merge approval required.
- Scope: accessibility refinement to the existing insurance result announcement.
- Problem: the full result article is marked as a polite live status, so screen readers may announce a long coverage summary, procedure list, evidence, and fine print together after a selection is submitted.
- Change: remove the live-region semantics from the long article. The existing deliberate submit flow moves keyboard and screen-reader focus to the result heading; the article and all visible content remain available for normal navigation.
- Preserved: result wording, policy and cost data, evidence links, collapsed procedure details, insurer/care selection, photos, navigation, hospital search, virtual booking, insurance content, and disclaimers.
- Acceptance:
  - After submit, the result heading receives focus and remains a heading.
  - The long article and detailed breakdown are not exposed as one live region.
  - Changing a selector still clears stale results without moving focus.
  - Full Chromium, WebKit, axe, nearby map, virtual booking, and static build QA pass on the exact PR head.
- Boundaries: G2 overall remains HOLD; no live booking/insurance/personal-data integrations; Pages remains user-triggered manually; actual iPhone Safari/Instagram browser QA remains unverified.
