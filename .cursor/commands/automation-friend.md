---
name: automation-friend
description: 'Convert recorded JSON UI actions into deterministic pytest+Playwright Fluent UI tests (with centralized locators)'
agent: 'agent'
---

# automation-friend

Convert recorded JSON UI actions into deterministic pytest+Playwright Fluent UI tests (with centralized locators)

## When to Use
- Use when given a JSON array of UI actions (`click`, `input`, `verifyText`) and the goal is a runnable pytest+Playwright Fluent UI test.
- Skip for unrelated refactors or Page Object requests (forbidden).

## Role
Senior Playwright + pytest engineer producing deterministic tests with centralized locators, Fluent steps, no hardcoded URLs/selectors, and English-only comments.

## Workflow (lean)
**Step 0 – Environment check**: Read `data/environments/dev.json`; require `base_url`, `api_config.base_url`, and `test_users.admin` email/password. If missing/blank, pause and ask for an update.

**Step 1 – Validate input**  
- UI: expect JSON action objects with `action` + `locators`. Normalize locator arrays (trim, dedupe, keep order). Treat locators as candidates; pick a primary + minimal fallbacks.  
- API: expect cURL/HTTP details; parse method/path/headers/body; replace host with `config.api_url` / `config.config["api_config"]["base_url"]`; normalize for Fluent API helpers.  
- Redacted data: load from `config` (e.g., `config.test_users["admin"]["password"]`); fall back to `os.getenv(...)` (default `E2E_PASSWORD`) only if absent.

**Step 2 – Pick feature and targets**  
- Feature defaults: `auth` for login flows, `dashboard` for obvious dashboard, otherwise `generated`; API flows can use `api` or endpoint-derived.  
- Targets: UI → `locators/<feature>_locators.py`, optional `components/<feature>_components.py`, tests under `tests/ui/test_<feature>_<scenario>.py`; API → `tests/api/test_<feature>_<scenario>.py` using `utils/fluent_api.py`.

**Step 3 – Locators/components (UI only)**  
- Locators for single elements; components (subclass `BaseComponent`) for multi-selector widgets (nav, header, modals, tables, pagination). Keep component selectors private; tests call component methods.  
- Locator ranking: `[data-testid]` > `[data-cy]/stable data-*` > text selectors > simple CSS > xpath last.  
- **Avoid icon selectors** (e.g., `i.v-icon`, `i.icon`, `[class*="icon"]`, `svg.icon`, etc.); a screen may have many identical icons, making them non-unique. Prefer data attributes, text selectors, or parent context (e.g., button/link containing the icon) instead.  
- **Displayed text matching priority**: When elements are identified by visible text (especially when CSS transforms text like uppercase/lowercase), prefer base selectors (e.g., `span.v-tabs__item__text`) over text selectors (e.g., `text=PRE-ARRIVAL`) in locator definitions. The test code will use displayed text functions to match by inner_text (displayed text after CSS) rather than text_content (DOM text). This handles cases where DOM has "Pre-Arrival" but CSS displays "PRE-ARRIVAL".  
- Define `FOO`, `FOO_FALLBACKS`, `FOO_LOCATORS = [FOO, *FOO_FALLBACKS]`. Never inline selectors in tests.

**Step 4 – Reuse sequences**  
- Detect contiguous repeated action patterns (len ≥ 3, e.g., username → password → login). Prefer an existing fixture/helper; otherwise create a fixture in `fixtures/` (ensure `pytest_plugins` discovery) or a helper at the end of the test file. Keep secrets in env/config; skip if unavailable. Keep refactors minimal and deterministic.

**Step 5 – Generate test (Fluent, deterministic)**  
- Markers: `@pytest.mark.ui` + business markers (e.g., `auth`, `smoke`).  
- Names: test functions start with `test_verify_`; titles in `fluent_test()` start with "Verify"; add a docstring describing the verification.  
- Use `fluent_test(page, "Verify ...")`; navigate with `config.base_url`. No hardcoded URLs/selectors; rely on locators/components.  
- `test.step()` must chain directly to the next call on the same line (`then()/and_also()`). Prefer verification steps to start with "Verify"; `expected` optional.  
- **Displayed text functions priority (MANDATORY)**: When interacting with or verifying elements by visible text, ALWAYS prefer displayed text functions over regular text selectors:
  - **Actions**: Use `click_element_by_displayed_text(base_selector, displayed_text)` instead of `click_element(text=...)` when matching by text
  - **Verifications**: Use `element_by_displayed_text(base_selector, displayed_text)` and `should_have_displayed_text()` / `should_contain_displayed_text()` instead of `element(text=...)` and `should_contain_text()` when verifying displayed text
  - **Rationale**: Displayed text functions match by inner_text (text after CSS transforms), which is what users actually see, while text selectors match by text_content (DOM text), which may differ due to CSS transforms (e.g., "Pre-Arrival" in DOM vs "PRE-ARRIVAL" displayed)
- Use Fluent helpers for locator robustness; no custom loops; no Page Objects. API steps use `fluent_api_test` seeded from `config.api_url`/`config.config["api_config"]["base_url"]`. Secrets from `config`, then env, else skip.

**Step 6 Mandatory – Self-check**  
- No hardcoded URLs or inline selectors; English-only comments.  
- No icon selectors (e.g., `i.v-icon`, `i.icon`, `[class*="icon"]`, `svg.icon`); prefer data attributes, text selectors, or parent context instead.  
- **Displayed text functions used**: When matching/verifying by visible text, verify that displayed text functions (`click_element_by_displayed_text`, `element_by_displayed_text`, `should_have_displayed_text`, etc.) are used instead of regular text selectors (`text=...`, `should_contain_text`).  
- Imports at top; helpers at file end.  
- Fluent navigation/waits used; `test.step` chaining respected.  
- Test names start `test_verify_`; titles start "Verify".

**Step 7 Mandatory – Run tests and fix error**  
- Ensure `.venv/` exists (`python3 -m venv .venv` if needed).  
- Install deps: `./.venv/bin/python -m pip install -r requirements.txt`.  
- Run the created file: `./.venv/bin/python -m pytest tests/ui|api/test_<feature>_<scenario>.py`; fix and rerun until green.
- **Locator error fallback strategy**: If a test fails due to locator/selector errors (element not found, timeout, etc.), try switching between displayed text functions and regular text selectors:
  - **If using displayed text function fails** (e.g., `click_element_by_displayed_text()`, `element_by_displayed_text()`): Fallback to regular text selector (e.g., `click_element("text=...")`, `element("text=...")`) - the DOM text might match the displayed text
  - **If using regular text selector fails** (e.g., `click_element("text=PRE-ARRIVAL")`): Switch to displayed text function (e.g., `click_element_by_displayed_text(base_selector, "PRE-ARRIVAL")`) - CSS transforms might have changed the displayed text
  - **Same logic applies to verify functions**: Switch between `should_have_displayed_text()`/`should_contain_displayed_text()` and `should_contain_text()` as needed
  - Only switch if the error is clearly locator-related (element not found, timeout waiting for element); do not switch for other types of errors (assertion failures, logic errors, etc.)

**Step 8 – Document**  
- Generate docs from steps: update `docs/test_cases.md`; run `scripts/generate_test_cases.py` to refresh `docs/test_cases.xlsx`. Automation code stays the source of truth.

## Output Requirements (when invoked)
- Bullet list of files created/updated.
- `@locators` section for `locators/<feature>_locators.py` (or note none).
- `@components` section for `components/<feature>_components.py` (or note none).
- Generated test file content (`tests/ui/...` or `tests/api/...`).
- Tiny “how to run” section.
