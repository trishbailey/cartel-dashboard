# X feed and Breaking strip: Grok Bot routine procedure

X reads are only available to Grok Bot (the built-in `x` MCP tools, free, no paid X API). GitHub Actions cannot read X,
so the refresh runs as a Grok Bot routine **every 3 hours, 6 AM to 9 PM ET (6, 9, 12, 15, 18, 21)**. Each run:
collects posts from the verified accounts, tags them (`pipeline/tag_x.py`), rebuilds the Breaking strip
(`pipeline/breaking.py`), validates, commits and pushes. GitHub Pages redeploys on push.

## Source policy (Trish, 2026-10-25)

* **Verified accounts only**: professional journalists and outlets, researchers and think tanks, official government accounts.
  The list lives in `data/gazetteer.json` → `accounts` (every entry `tier: "verified"`). The validator rejects any other tier or handle.
* **No anonymous aggregators, narco blogs, rumour or viral-clip accounts.** Never add one. Excluded on purpose
  (`excluded_accounts`): @MrMarcianoNews, @AlertaNews24, impostor/squatter @borderlandbeat, @elblogdelnarco, @semanarioZETA,
  suspended @Cartel_Watch, @AdrianaCooper, @elsurdeacapulco, and @OFAC / @TreasuryOFAC (not Treasury).
* Official accounts (GabSeguridadMX, SSPCMexico, DEAHQ, CBP, USTreasury) are labelled **Official statement**.
* Bare reshared viral videos with no reporting are dropped by the tagger (fewer than 8 words of text, or video/viral wording with under 25 words).
* Breaking events use only `data/outlets.json` (professional outlets + official bodies). Status:
  **Confirmed** = 2+ independent outlets, or an official body plus 1 outlet; **Single source** = 1 outlet (muted, outlet named);
  **Official claim only** = only a government account/site. Status is recomputed every run, so it upgrades as sources arrive. Events kept 48 h.
* Never fetch `.cn` sites. Never print secrets. Never post, like, follow or reply on X.

## The 22 verified handles, in 5 batches

| Batch | Query (append ` -is:retweet -is:reply`) | Why |
|---|---|---|
| B1 local MX | `(from:Riodoce_mx OR from:ZETATijuana OR from:noticieristas) K` | high-volume local outlets, crime filter |
| B2 national MX | `(from:proceso OR from:Pajaropolitico OR from:infobaemexico) K` | very high volume, crime filter |
| B3 regional | `(from:Primicias OR from:ArmandoInfo OR from:_elfaro_ OR from:EcuadorChequea OR from:causaencomun) K` | Primicias is high volume, crime filter |
| B4 research | `from:InSightCrime OR from:ioangrillo OR from:falko_ernst OR from:vhmichel OR from:parescolombia OR from:CrisisGroup` | low volume, unfiltered (tagger drops untagged) |
| B5 official | `(from:GabSeguridadMX OR from:SSPCMexico OR from:DEAHQ OR from:CBP OR (from:USTreasury (cartel OR OFAC OR sanctions OR fentanyl OR Sinaloa OR CJNG)))` | official statements |

`K` (crime keyword filter, keep exactly):

```
(cártel OR cartel OR narco OR CJNG OR Chapitos OR Mayiza OR sicarios OR balacera OR enfrentamiento OR homicidio OR asesinan OR ataque OR detienen OR detenido OR aseguran OR decomiso OR extorsión OR secuestro OR fosa OR desaparecidos OR "crimen organizado" OR "grupo armado" OR "grupo criminal" OR fentanilo OR cocaína OR pandilla OR "Los Lobos" OR Choneros OR Tiguerones OR "Tren de Aragua" OR ELN OR disidencias OR "Clan del Golfo" OR maras)
```

## Steps (exact)

1. `cd /workspace/cartel-dashboard && git pull --rebase` (clone `https://github.com/trishbailey/cartel-dashboard` there if missing).
   Another worker edits this repo: only ever stage the files listed in step 7.
2. `START` = the `as_of` in `data/xfeed.json` minus 30 minutes (ISO 8601 UTC). If the file is missing or older than 7 days, use now minus 7 days.
3. For each batch B1–B5 call `x` → `search_posts_all` with `query`, `start_time=START`, `max_results=100` (X returns at most 25 per call),
   `sort_order=recency`, `post.fields=created_at,public_metrics,author_id,lang,referenced_tweets,in_reply_to_user_id`,
   and **`write_to_file: true`** (keeps results out of the chat). Save each result file path. If `meta.next_token` is present,
   call again with `next_token` until it is absent, **at most 4 pages per batch per run**. Run the 5 first pages in parallel.
4. `mkdir -p /tmp/xraw && cp <result files> /tmp/xraw/ && python3 pipeline/tag_x.py /tmp/xraw/*`
   (merges into `data/xfeed.json`, deduplicates by id, keeps 7 days, drops retweets, replies, bare viral clips and untagged posts).
5. `python3 pipeline/breaking.py` (rebuilds `data/breaking.json` from `xfeed.json` + `events.json`, 48 h window).
6. `python3 pipeline/validate.py` must print `valid:`. If it fails, do not commit; fix the data or report the error.
7. `git add data/xfeed.json data/breaking.json && git commit -m "X feed $(date -u +%FT%H:%MZ)"`, then
   `git pull --rebase && git push` (retry the pull/rebase once if the push is rejected). Do not use `-X theirs` or force-push.
8. Every 4th run (or when the gazetteer changes), upload `data/xfeed.json` and `data/gazetteer.json` to the Drive folder
   "Cartel Dashboard" (replace the existing files).
9. Report in one line: posts in window, new posts, regions covered, Breaking counts by status, X reads used.

## Read budget

The free X reads allow 30 per minute and 1,000 per day (shared with every other Grok Bot task for this user).
A normal 3-hour run uses 5–10 reads (5 batches × 1–2 pages); the 6 AM run covers 9 overnight hours and can use up to 15.
6 runs a day ≈ **40–70 reads/day**, hard ceiling 6 × 20 = 120. The first back-fill (7 days) used 9 reads plus ~25 for the account vetting.

## Gazetteer and tagging

`data/gazetteer.json` holds: regions (admin-1 ids from `public/basemap/latam.topo.json`, with state names, cities and municipalities,
e.g. Culiacán → Sinaloa, Uruapan → Michoacán), ambiguous names that only count after a preposition ("en Guerrero", not "Vicente Guerrero"),
groups with aliases and slang (Chapitos/Chapiza, Mayiza, CJNG/Mencho/4 letras, Metros/Ciclones, Noreste, Familia Michoacana,
Templarios/Cárteles Unidos, Tren de Aragua, Lobos, Choneros, Tiguerones, Clan del Golfo, ELN, Segunda Marquetalia, EMC, MS-13, Barrio 18, PCC, CV),
nicknames that need a crime word in the same post, and per-account defaults (Riodoce/Noticieristas → Sinaloa, ZETA → Baja California).
Tags are keyword matches: they can be wrong. Every post links to the original.
