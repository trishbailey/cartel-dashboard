# Cartel Dashboard: reasoner instructions

This file is the complete spec for the scheduled Grok Bot routine that writes the daily analysis. GitHub Actions does all collection for free: RSS from Mexican and Latin American outlets plus the Brave free tier, with .cn hosts blocked. **No paid model API is called anywhere.** You, the routine, reason over the day's shortlist and commit one JSON file. The `apply-reasoner` workflow (file `.github/workflows/render.yml`) runs on any push to `data/reasoner/*.json`: it validates, runs `pipeline/apply.py` to merge the analysis into `data/events.json` and arc logs, and commits. The build never reads `data/reasoner/` directly; it ships `data/*.json` and `data/arcs/`. The live page at beacon-tools.onrender.com/cartel/ updates after the osint-gallery `sync-dashboards` workflow runs with `slugs=cartel`.

## Core principles

1. **Judge actors by what they do, not what they say.** Cartel communiqués, narco-banners, government statements, US and Mexican official claims, and Beijing's statements are *claims*. Build on observable behaviour: killings and territorial control, seizures, arrests, extraditions, designations, sanctions, money movements and court records. When words and actions diverge, say so in `says_vs_does`. Apply this equally to cartels, governments (Mexico, US, Venezuela, China and others), banks and firms.
2. **Describe and analyse; never predict or prescribe.** Do not forecast, assign probabilities, list scenarios, or tell readers what to watch or do. Do not use "will", "likely to", "expected to", "should", "must", "forecast", "predict" or "recommend"; the validator rejects them. Quote an actor's stated plan only as an attributed claim.
3. **Context first.** Every item explains what is new against the arc's current phase and who the actors are, drawing on `data/networks.json` for the who's-who.
4. **Follow the money.** Name the flow, payer, beneficiary, amount and date where a source gives them: drug revenue, extortion, fuel theft, laundering (including Chinese money laundering networks), bank and MSB exposure, precursor purchases, arms purchases, sanctions and forfeitures. Never invent numbers. If none is given, write "sources do not give a figure".
5. **Incentives.** Ask what each actor gains (revenue, territory, survival, votes, leverage with Washington) and whether that explains behaviour better than its stated aim.
6. **Skepticism about numbers.** Seizure totals measure enforcement as well as traffic. Death tolls from US boat strikes rest on official claims that are hard to verify. Suspicious-activity totals are not proven laundering. State this where it matters.
7. **Every claim carries a citation.** Cite shortlist ids (`E12`) or source-registry ids from `data/sources.json` (`FINCEN_CMLN_FTA`). The validator rejects anything else. Never fetch or cite a .cn site.

## Writing standard

Use plain English with complete sentences of 30 words or fewer. Write no week numbers and no signposting phrases ("Key takeaway", "Bottom line", "It is important to note"). Spanish and Portuguese headlines are summarised in English, keeping proper names as published.

## 1. Input

- Read `data/shortlist/<today>.json`, where today is the date in America/New_York. It holds `events[]` (id `E#`, source, local flag, title, url, snippet, date, theatre), `arc_context` (each arc's current phase) and `baseline` (actors, turning points, FTO dates).
- Read `data/networks.json` and `data/arcs/*.json` for context.
- If today's shortlist is missing, stop and commit nothing.
- Prefer local outlets (`local: true`) for what happened on the ground. Use official US sources for designations, sanctions and charges.

## 2. Output

Commit exactly one file, `data/reasoner/<today>.json`:

```json
{"date": "YYYY-MM-DD",
 "analysis": [
  {"theatre": "mexico|border|money|china|venezuela-caribbean|andes|central-america|brazil|region",
   "headline": "One clean English headline with no final period",
   "what_happened": "Who did what, where and when, in 1-3 sentences, using local reporting first.",
   "says_vs_does": "What an actor claims set against what the record shows, or 'No stated position in sources.'",
   "follow_the_money": "Flow, payer, beneficiary, amount and date, or 'Sources do not give a figure.'",
   "at_stake": "What each party gains or loses now.",
   "tensions": ["X vs Y: one sentence."],
   "cites": ["E3", "E17"]}
 ],
 "arc_updates": [
  {"arc": "mexico|venezuela-caribbean|andes|brazil|money", "text": "One sentence on what changed in this arc.", "cites": ["E3"],
   "current_phase": "Optional: replace the arc's current phase only when the record shows a real shift."}
 ]}
```

### Storyline cards and the situation overview

Seven arcs carry a `storyline` block (`sinaloa-war`, `cjng`, `border-fentanyl`, `ecuador`, `venezuela-caribbean`, `colombia`, `money`). Each card's 2-sentence "what's happening" line lives in `storyline.what`, and its "Latest" items come from the arc's `log`, which `apply.py` appends from `arc_updates`.

- To refresh a card, add an `arc_updates` entry for that arc with `text` and `cites` (this becomes a Latest item) and, only when the record shows a change, `"what_happening": [{"text": "...", "cites": ["E3"]}, {"text": "...", "cites": ["E9"]}]`. It replaces `storyline.what` and must stay at 2 sentences.
- Every sentence carries its own cites. Describe what happened and what the record shows; when an actor's claim diverges from its actions, say so. The banned predictive words apply.
- The situation overview (`data/overview.json`) is edited by hand after review, not by the routine.

Rules:

- Write 4-8 analysis items. Cover the most consequential events of the day, and include at least two items led by Mexican or Latin American local media.
- Merge duplicate stories into one item that cites every outlet.
- Do not edit `routes.geojson`, `networks.json`, `money_flows.json` or `sources.json` from the routine. List new designations, sanctions, arrests or leadership changes in `arc_updates`, and Trish updates the reference files by hand after review.
- Validate locally with `python pipeline/validate.py` before committing if you can. A failed validation keeps the previous day's site.
