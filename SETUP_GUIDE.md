# PromptWars Bangalore — Setup Guide
# Run this before the event. Takes ~5 minutes.

## STEP 1: Place AGENTS.md at project root
# When you create your workspace in Antigravity, copy AGENTS.md to the root.
# This makes the agent follow competition rules from the first prompt.

# Structure after setup:
# my-promptwars-project/
# ├── AGENTS.md                         ← copy here
# └── .agent/
#     └── skills/
#         ├── deploy-cloud-run/
#         │   └── SKILL.md
#         ├── security-audit/
#         │   └── SKILL.md
#         ├── gemini-integration/
#         │   └── SKILL.md
#         ├── firebase-leaderboard/
#         │   └── SKILL.md
#         ├── web-game-scaffold/
#         │   └── SKILL.md
#         └── accessibility-checker/
#             └── SKILL.md

## STEP 2: Skills go here (Workspace Scope)
# Per the official Antigravity docs, workspace skills live in:
#   <workspace-root>/.agent/skills/
#
# Copy each skill folder there before the event.

## STEP 3: Optional — Global Skills (available in ALL your workspaces)
# Place skills here for reuse across projects:
#   ~/.gemini/antigravity/skills/
# Good candidates: security-audit, gemini-integration, accessibility-checker

## STEP 4: Verify in Antigravity
# Open Agent Manager → type: "what skills do you have available?"
# Agent should list all 6 skills. If not, check folder paths.

## STEP 5: Pre-event practice prompts (run these at home)
# "Use the web-game-scaffold skill to create a basic dodge game"
# "Use the gemini-integration skill to add an AI hint system"
# "Use the security-audit skill to check this project"
# "Use the deploy-cloud-run skill to deploy"
# "Use the accessibility-checker skill before submission"

## CHEATSHEET — Competition Day Prompts
# ─────────────────────────────────────────────────────
# When problem is revealed:
#   "Plan a web [game/app] for [problem]. Use Planning Mode. 
#    Use web-game-scaffold skill. Integrate Gemini API. Deploy to Cloud Run."
#
# Every 30 minutes:
#   "Run security-audit skill and fix all issues"
#   "Run accessibility-checker skill"
#   "Commit all changes with a conventional commit message"
#
# Before each submission:
#   "Run full pre-submission checklist from AGENTS.md"
#   "Use deploy-cloud-run skill to ship"
#########################
