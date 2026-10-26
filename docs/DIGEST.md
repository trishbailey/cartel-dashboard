# What's new digest (data/whatsnew.json)

The dashboard's "What's new" section (public/whatsnew.js, under the leaders section) shows **digested intelligence grouped under
ongoing trends**, not raw feeds. X posts and articles are used only as **sources** (footnotes). It supersedes the raw Breaking
strip and the Storylines tile, which whatsnew.css hides; their code and data stay in place.

## Schema
```
{as_of, note,
 trends: [{id, title, groups[], regions[], view: mx|all|sa, context, context_sources[],
           status?: escalating|steady|easing  (ONLY with status_sources[] holding sourced counts),
           developments: [{date YYYY-MM-DD, place, text, verification, regions[], groups[], sources[]}]}],   # 2-5 per trend, newest first
 other: [ up to 3 developments that fit no trend ]}
```
A source is a `data/sources.json` id or `{url, name, title, date}`. verification is one of `Confirmed` (2+ independent reliable
sources), `Single source`, `Official claim only` (only a government or official account says it).

## Routine: refresh after each X-feed run and in the daily reasoner
1. `git pull --rebase`. Read what changed since `whatsnew.json.as_of`: new posts in `data/xfeed.json` (use `text_en`),
   `data/breaking.json` events (their `status`, `outlets`), `data/events.json` headlines, and arc/storyline files in `data/arcs/`.
2. Drop noise: one-off crime-blotter items (single shootings, local arrests with no group or trend link), lifestyle, sport,
   duplicates and reposts. Use reliable sources only: no anonymous blogs, rumours, viral clips, aggregators, or `.cn` sites.
3. Attach each meaningful item to an existing trend. Merge posts and articles on the same event into **one** development:
   one analytic sentence on what happened and why it matters inside the trend. Do not paste the post. Watch the gap between
   what actors say and what they do, and follow the money (laundering, extortion, credit, sanctions).
4. Open a new trend only when 3+ sourced items share a thread. Keep 4-7 trends; merge or retire the quietest one.
   Up to 3 strong items that fit no trend go in `other`.
5. Set verification from the source count: two different outlets = Confirmed. Several posts from the same outlet count once.
6. Update `context` (1-2 plain sentences, sourced) when a trend has moved, for example a leader killed or a truce. Set `status`
   only when sourced counts show it, and give the counts in `status_sources`.
7. Age out developments older than about 7 days and keep at most 5 per trend, newest first.
8. Language: describe and analyse; never predict or prescribe. Banned: will, likely to, expected to, should, must, forecast,
   predict, recommend.
9. Edit the content in `pipeline/mk_whatsnew.py` (it resolves `x:<post id>` and `u:<url prefix>` refs into source objects),
   run `python3 pipeline/mk_whatsnew.py && python3 pipeline/validate.py`, then `git add data/whatsnew.json pipeline/mk_whatsnew.py`,
   commit as "What's new <UTC timestamp>", `git pull --rebase`, and push. Never force-push. Never print secrets.
   If you edit data/whatsnew.json by hand instead, commit only that file.
