# Latin America Cartel Dashboard

A static, $0 dashboard covering trafficking routes and US crossing points, cartel money flows (including Chinese money laundering networks), cartel and terrorist-designated group networks, Chinese influence in the region, and daily local Latin American reporting.

- **Data** lives in `data/` as JSON and GeoJSON, separate from the code. Every route, edge and claim cites an id in `data/sources.json`, which holds the URL.
- **Collection:** `.github/workflows/daily.yml` runs `pipeline/collect.py` at 10:00 UTC. It uses free RSS and the Brave free tier (`BRAVE_API_KEY` secret) and blocks .cn hosts.
- **Analysis:** a daily Grok Bot routine follows `docs/REASONER.md` and commits `data/reasoner/YYYY-MM-DD.json`. `render.yml` validates it and applies it. No paid model API is used.
- **Site:** `public/` uses d3 and d3-sankey (vendored) and a bundled Natural Earth basemap, with no tile keys. GitHub Pages builds it with `pipeline/build.sh` (`pages.yml`). A `render.yaml` is included for when a Render slot is free.

It describes and analyzes what has happened. It does not predict or prescribe.
