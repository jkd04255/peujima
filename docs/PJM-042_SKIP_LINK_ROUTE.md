# PJM-042 — Skip link preserves the current route

- Status: G3 conditional review; **do not merge until exact PR HEAD complete QA is green**.
- Base: `main` a97962c74dd7b3f137b0c57a04b2690937b4ee1e (PJM-041).
- Scope: one accessibility/keyboard navigation bug; no design or product-data changes.

## Problem
The visible-on-focus "본문으로 건너뛰기" link points to `#main-content`, while the app uses the same fragment to encode `#home`, `#nearby`, `#clinics`, and `#insurance`. Following that link using native fragment navigation discards the active route in the address bar and can make Back/reload return to the wrong screen.

## Behavior / acceptance
1. Keep the native skip **link** and its existing focus-visibility design.
2. On activation, focus the existing `main#main-content` without overwriting the route hash or adding browser history.
3. Align the main content below the current sticky header at mobile and desktop widths.
4. Browser Back after a separate route transition goes back to the previous route, not `#main-content`.
5. Chromium 320/390/1440px and WebKit 390px automated regression, JS-error check and full PJM-011/012/013/014 accessibility and functional QA pass on the exact PR head.

## Implementation
- `pjm013-navigation.js`: intercept activation of the existing skip link, prevent native fragment mutation, move focus to main, and scroll below sticky navigation without changing app state.
- `tests/test_pjm_042_skip_link_route.py`: active insurance route, keyboard Enter, focus/viewport alignment, subsequent navigation and Back, JS errors.
- `.github/workflows/pjm-014-qa.yml`: run new regression in the full QA job.

## Safety and release
- Keep pet photos, minimal typography, all three animal modes, actual nearby Kakao discovery, demo appointment calendar and insurance/cost guides intact.
- **G2 entire gate HOLD**; no real booking, insurance settlement, paid API, auth, personal-data persistence, or new integrations.
- GitHub Pages **manual deployment by user only**. No new deploy or merge before a successful full PR QA check.
- Actual iPhone Safari and Instagram in-app-browser QA is not verified.
