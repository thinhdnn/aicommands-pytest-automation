# AI-Assisted Test Automation Template

A test automation project template powered by IDE AI custom commands.

Designed to help you auto-organize and generate clean UI test code from recorded actions: fast, consistent, and scalable.

This repo focuses on structure first, so your tests don’t turn into spaghetti when the project grows.

## Table of contents

- [Why this exists](#why-this-exists)
- [How it’s meant to be used](#how-its-meant-to-be-used)
- [Custom command: `automation-friend`](#custom-command-automation-friend)
	- [What it does](#what-it-does)
	- [When to use](#when-to-use)
- [Core principles (non-negotiable)](#core-principles-non-negotiable)
- [What the command generates](#what-the-command-generates)
- [Locator strategy (built-in)](#locator-strategy-built-in)
- [Smart reuse (helpers & fixtures)](#smart-reuse-helpers--fixtures)
- [Tech stack](#tech-stack)
- [TL;DR](#tldr)

## Why this exists

Writing UI tests usually means:

- Repeating the same locators everywhere
- Messy test scripts after recording
- Hardcoded selectors, URLs, or secrets
- Zero consistency between files

This template + AI command solves that by:

- Enforcing one way to organize locators, fixtures, and tests
- Turning raw recorded JSON actions into deterministic `pytest` + Playwright tests
- Keeping your test code clean, readable, and maintainable long-term

Think of it as an automation best-friend living inside your IDE.

## How it’s meant to be used

You use an IDE AI Custom Command (Copilot / Cursor / similar) to:

1. Paste recorded UI actions (JSON)
2. Trigger the command
3. Get ready-to-run test files generated following repo rules

Example (Copilot in VS Code):

1. In Copilot Chat, type:

   ```text
   /automation-friend
   ```

2. Paste your recorded actions JSON:

   ```json
   [
     {
       "url": "https://www.ebay.com/",
       "action": "click",
       "locators": [
         "#gh-ac",
         "input[name=\"_nkw\"]",
         "input[aria-label=\"Search\\ for\\ anything\"]",
         "role=combobox[name=\"Search for anything\"]",
         "input.gh-search-input.gh-tb.ui-autocomplete-input",
         "xpath=//*[@id='gh-ac']"
       ]
     },
     {
       "url": "https://www.ebay.com/",
       "action": "input",
       "locators": [
         "#gh-ac",
         "input[name=\"_nkw\"]",
         "input[aria-label=\"Search\\ for\\ anything\"]",
         "role=combobox[name=\"Search for anything\"]",
         "input.gh-search-input.gh-tb.ui-autocomplete-input",
         "xpath=//*[@id='gh-ac']"
       ],
       "value": "car"
     },
     {
       "url": "https://www.ebay.com/",
       "action": "click",
       "locators": [
         "span.gh-search-button__label",
         "xpath=//div/div[1]/header/section/form/div[2]/button/span",
         "text=Search"
       ]
     },
     {
       "url": "https://www.ebay.com/sch/i.html?_nkw=car&_sacat=0&_from=R40&_trksid=p4432023.m570.l1313",
       "action": "verifyText",
       "locators": [
         "xpath=//div/div/div/ul/li[1]/div/a/div",
         "text=Car & Truck Body Moldings & Trims - apply Category filter"
       ],
       "expected": "Car & Truck Body Moldings & Trims- apply Category filter"
     }
   ]
   ```

No manual refactoring.
No Page Objects.
No chaos.

## Custom command: `automation-friend`

### What it does

`automation-friend` converts recorded JSON UI actions into:

- `pytest` + Playwright UI tests
- Fluent, readable test steps
- Centralized, reusable locators
- Optional fixtures for reusable flows (login, navigation, etc.)

All output strictly follows this repository’s architecture.

### When to use

Use this command when:

- You have a JSON array of UI actions like:

	```json
	[
		{"type": "click", "target": "..."},
		{"type": "input", "target": "...", "value": "..."},
		{"type": "verifyText", "target": "...", "value": "..."}
	]
	```

- You want a complete, runnable UI test generated automatically.

Do not use it for:

- API tests
- Random refactors
- Page Object patterns (explicitly forbidden here)

## Core principles (non-negotiable)

The command always enforces:

- No hardcoded URLs
- No hardcoded selectors
- No secrets in code
- Centralized locators in `locators/`
- Fluent test style
- Deterministic behavior

If something is missing (like env vars), the test will skip safely (instead of failing randomly).

## What the command generates

When invoked, the AI will output:

- Files created/updated
- A locator module, for example:

	```text
	locators/<feature>_locators.py
	```

- A feature-based test file, for example:

	```text
	tests/features/test_<feature>_<scenario>.py
	```

- A short “how to run” section

Everything is structured, named consistently, and ready to commit.

## Locator strategy (built-in)

Locators are ranked automatically (best to worst):

1. `data-testid`
2. `data-cy` or other stable data attributes
3. Semantic text selectors
4. Simple CSS
5. XPath (last resort)

Each element gets:

- A primary locator
- Ordered fallback locators
- Zero inline selectors in tests

## Smart reuse (helpers & fixtures)

The command can detect repeated action patterns:

- Login flows
- Common navigation
- Repeated setups

If a flow is reusable:

- It becomes a `pytest` fixture (preferred), or
- A small helper function (last resort)

Fixtures live in `fixtures/`.
Helpers stay at the end of the test file (repo rule).

## Tech stack

- Python
- `pytest`
- Playwright
- Fluent test helpers
- AI-driven code generation

No Page Objects.
No magic.
Just clean structure.

## TL;DR

1. Record UI actions
2. Paste JSON
3. Run `automation-friend`
4. Get clean, scalable tests