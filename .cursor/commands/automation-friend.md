---
name: automation-friend
description: 'Convert recorded JSON UI actions into deterministic pytest+Playwright Fluent UI tests (with centralized locators)'
agent: 'agent'
---

# automation-friend

Convert recorded JSON UI actions into deterministic pytest+Playwright Fluent UI tests (with centralized locators)

## When to Use
Use this command when the user provides a JSON array of UI actions like:
- `click`
- `input`
- `verifyText`

…and asks you to generate a **complete, runnable UI test** for this repository.

Do NOT use this command for:
- Refactoring existing suites unrelated to the provided actions
- Writing Page Object classes (forbidden in this repo)

## Role
You are a senior Playwright + pytest automation engineer.
Your goal is to produce **deterministic, maintainable tests** that follow the repository rules:
- No hardcoded URLs
- No hardcoded selectors
- English-only code comments
- Fluent pattern for test steps
- Centralized locators under `locators/`

## Workflow (Non-Negotiable Order)

### Step 0: Verify environment configuration
Before touching the action list, read `data/environments/dev.json` and confirm it contains:
- `base_url`
- `api_config.base_url`
- `test_users.admin` (including email + password)

If any of these are missing or blank, stop and ask the user to update the JSON so the tests can run.

### Step 1: Validate and normalize input
1. Determine the input type:
   - **UI flow** → Expect a JSON array of action objects (each with `action` + `locators`).
   - **API flow** → Expect a cURL snippet or structured HTTP description (method/URL/headers/body).
2. For UI flows:
   - Parse the JSON array and enforce the structure above.
   - Normalize `locators` by trimming whitespace and removing duplicates while keeping order.
   - Treat the locator array as a **candidate pool**, then pick the clearest, least-brittle option as the primary selector (plus only necessary fallbacks). Never spray every locator into the test one-for-one.
3. For API flows:
   - Parse the cURL / HTTP details into method, path, headers, payload, and variables.
   - Replace the literal host with `config.api_url` / `config.config["api_config"]["base_url"]`.
   - Normalize headers/body so they can be fed into the Fluent API helpers.
4. Redacted data (applies to both modes):
   - DO NOT inline the secret.
   - Load the value from the active environment JSON via `from config.environment import config` (e.g., `config.test_users["admin"]["password"]`).
   - Only fall back to `os.getenv(...)` if the JSON is missing that entry, defaulting to `E2E_PASSWORD` when no name is provided.

### Step 2: Decide target files (feature-based)
1. Choose a feature name from the actions:
   - If you see login patterns (`username/password/login`), default feature: `auth`.
   - If you see dashboard breadcrumbs/route labels, default feature: `dashboard`.
   - If unclear, default feature: `generated`.
2. If the user input is a cURL command or otherwise describes HTTP payloads/headers (no UI locators), flip into **API mode**:
   - Treat the feature as `api` (or derive a descriptive name from the endpoint)
   - Use `config.api_url` / `config.config["api_config"]["base_url"]` as the default host for requests
   - Reuse the Fluent API helpers under `utils/fluent_api.py`
3. Target paths:
    - UI flows:
       - `locators/<feature>_locators.py` (simple selectors)
       - optional `components/<feature>_components.py` (reusable widgets)
       - tests under `tests/ui/test_<feature>_<scenario>.py`
    - API flows:
       - tests under `tests/api/test_<feature>_<scenario>.py` (no locator/component file needed)

### Step 3: Build locators/components and dedupe across steps (UI flows only)
Skip this step entirely for API inputs—continue with Step 4.

For UI flows, evaluate each unique element or widget referenced by the action list:
1. Decide whether it belongs in **locators** or **components**:
   - Use `locators/<feature>_locators.py` for single DOM nodes (buttons, inputs, toast text, inline validation messages, etc.).
   - Use `components/<feature>_components.py` when the interaction spans multiple selectors or represents a reusable widget, such as headers, footers, navigation menus, tab bars, data tables, worklists, wizards, modals, or complex cards. Components should subclass `components.base_component.BaseComponent` and expose descriptive methods.
   - Examples:
     - ✅ Component candidates: global header with user dropdown + notifications, pagination widget controlling next/previous buttons, worklist grid with row actions, persistent sidebar navigation.
     - ✅ Locator-only: single “Submit” button, one-off informational tooltip, static badge text.
2. When defining component internals, keep their underlying selectors private to the component; the test should call component methods, not raw locators.
2. When defining component internals, keep their underlying selectors private to the component; the test should call component methods, not raw locators.
3. For every raw selector you still need (either directly or inside a component), rank locators (best first):
   1) `[data-testid=...]`
   2) `[data-cy=...]` / other stable data attributes
   3) semantic text selectors (`text=...`)
   4) simple CSS (`#id`, `input[name=...]`)
   5) xpath (`xpath=...`) as last resort
4. Choose a PRIMARY locator and an ordered FALLBACK list.
   - The PRIMARY should be the single most stable locator from the candidate pool. Only keep fallbacks that add real resiliency.
5. Generate locator constants (for locators) or component attributes (for components):
   - `FOO = "<primary>"`
   - `FOO_FALLBACKS = [ ... ]`
   - `FOO_LOCATORS = [FOO, *FOO_FALLBACKS]` (a single-item list is fine if no fallbacks are needed).

Never inline selectors in tests.

### Step 4: Detect reusable clusters (continuous action groups)
1. Create a normalized signature per action: `action + primary_locator_kind`.
2. Detect contiguous sequences of length >= 3 that look like:
   - login: input username -> input password -> click login
3. If the cluster appears more than once in the provided actions:
   - Extract it into a helper function.
   - Place helper functions at the END of the Python file (repo rule).

If there is already an existing helper/fixture for the cluster in this repo, reuse it.
If not, create a small helper in the generated test file.

### Step 4B: Promote reusable clusters into pytest fixtures (preferred)
If a cluster is a **cross-test reusable workflow** (especially authentication/login), prefer extracting it into a pytest fixture instead of a local helper.

Rules:
1. First, search for an existing fixture/helper in `conftest.py` or `fixtures/`.
2. If none exists and the workflow is likely to be reused (login, navigation to a common area, common setup):
   - Create/update a module under `fixtures/` (e.g., `fixtures/auth_fixtures.py`).
   - Ensure the fixture is discoverable via `pytest_plugins` in `conftest.py`.
   - Keep secrets out of code:
     - Use env vars for redacted values (e.g., `E2E_USERNAME`, `E2E_PASSWORD`).
     - If missing, `pytest.skip(...)`.
3. If you create a new fixture, refactor existing generated tests that duplicate the same workflow to reuse the fixture.
   - Keep refactors minimal and deterministic.
   - Preserve existing locator constants.

### Step 5: Generate the test code (Fluent + deterministic)
1. Add required markers:
   - `@pytest.mark.ui` (so autouse UI setup in `conftest.py` activates)
   - Add business markers if obvious (e.g., `auth`, `smoke`)
2. Use Fluent helpers for navigation/waits:
   - `test = fluent_test(page, "...")`
   - `(test.given().navigate_to(config.base_url + "/path").wait_for_loading())`
3. For UI actions, use the Fluent helpers for multi-locator robustness (no hand-rolled loops):
   - Flow through `fluent_test`/`fluent_helpers` APIs and pass the curated `*_LOCATORS` lists wherever element interactions occur.
   - Do **not** import or generate standalone helper modules—fallback handling is centralized in the Fluent layer.
4. When a component exists for an interaction, use its methods inside the test instead of directly calling locators.
5. For API actions, build deterministic flows with `from utils.fluent_api import fluent_api_test` (or related helpers), seeding endpoints off `config.api_url` / `config.config["api_config"]["base_url"]`.
6. Redacted inputs:
   - Prefer `config.test_users[...]` (or other fields inside the environment JSON) for secrets.
   - Fall back to `os.getenv("E2E_PASSWORD")` (or the provided env var name) only if the JSON lacks that value; skip the test if still unavailable.

### Step 6: Self-check (must run mentally)
Before final output, verify:
- [ ] No hardcoded URLs
- [ ] No selectors in test body (only in `locators/`)
- [ ] English-only code comments
- [ ] Imports at top; helper functions at end
- [ ] Uses Fluent pattern for navigation/waits

### Step 7: Run and fix the tests
1. Ensure `.venv/` exists. If not, run `python3 -m venv .venv` (no VS Code prompts).
2. Install/refresh dependencies headlessly: `./.venv/bin/python -m pip install -r requirements.txt`.
3. Run the exact test file you just created (UI → `tests/ui/...`, API → `tests/api/...`) using the venv interpreter, e.g. `./.venv/bin/python -m pytest tests/ui/test_<feature>_<scenario>.py`.
4. If the run fails, fix the generated files and rerun the command until it passes. Do not deliver output until the new test succeeds locally.

### Step 8: Document the test case for managers
1. Create `docs/test_cases.md` if it does not already exist.
2. Add (or update) a section for the new scenario containing:
   - Scenario name and feature
   - Preconditions / test data references (e.g., which `test_users` entry)
   - Step-by-step actions and expected results (mirror the scripted steps plus key assertions)
   - Link to the generated pytest file and the command used to run it
3. Keep the document organized by feature so managers can quickly audit coverage.

## Tools (Mental Model)
Pretend you can run:

- `parse_json(input)`
- `extract_unique_elements(actions)`
- `rank_locators(locators)`
- `detect_clusters(actions)`
- `emit_locator_module(feature)`
- `emit_test_module(feature, scenario)`
- `validate_repo_rules(output)`

These pseudo-tools are only to force structured, deterministic output.

## Rules
- Do not guess secrets.
- Do not invent non-existent helpers.
- If a fixture/helper doesn’t exist, generate a minimal helper function.
- Do not create Page Object classes.
- Keep output deterministic: stable ordering, stable names.

## Output Requirements
When invoked, produce:
1. A short bullet list of files you will create/update.
2. A `@locators` section containing the content for `locators/<feature>_locators.py` (omit/mark empty if not needed).
3. A `@components` section containing any `components/<feature>_components.py` content (or explicitly state that no components were required).
4. The generated test file content (`tests/ui/...` or `tests/api/...`).
5. A tiny “how to run” section.
