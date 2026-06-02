# smaart-gmail-signatures

Gmail signatures for SMAART Company — designed for Gmail's rendering constraints (table-based HTML, inline CSS, hosted images).

## Layout

```
/                         this README + signature generator
├── index.html            fill-in-the-form generator with live preview + copy button
├── signatures/
│   └── template.html     raw HTML template with {{TOKEN}} placeholders
├── team-images/          200x200 JPG headshots (firstname-lastname.jpg)
├── logos/                SMAART logos, kebab-case filenames
├── social-icons/         48x48 PNG icons (navy circles, white glyphs)
└── scripts/
    └── build-assets.py   one-shot normalizer: crops photos, moves logos, generates icons
```

## Generate a signature

1. Open `index.html` in a browser (or serve it anywhere static).
2. Fill in your name, title, email, phone, and social URLs.
3. Click **Copy HTML**.
4. In Gmail → ⚙ → **See all settings** → **Signature** → **Create new** → paste. Set as default for new and reply messages.

## Asset hosting

Image URLs in the generated HTML default to:

```
https://cdn.jsdelivr.net/gh/SMAART-Company/smaart-gmail-signatures@main/<path>
```

jsDelivr serves public GitHub repos globally over HTTPS with aggressive caching — no extra infrastructure required.

**If this repo stays private, images will not render in recipients' inboxes.** Two options:

- Make the repo public (branding assets are low-sensitivity).
- Change the **Asset base URL** field in the generator to a public domain, e.g. `https://smaartcompany.com/signatures`, and mirror the three asset folders there.

## Image permanence — so signatures never break

A signature already sent points at fixed image URLs forever. Those URLs keep
resolving only if three things stay true. Treat these as hard rules:

1. **The repo stays PUBLIC.** jsDelivr only serves public repos. Making this
   repo private instantly breaks every signature already in every inbox.
2. **Asset files are APPEND-ONLY. Never delete or rename a file** in
   `team-images/`, `logos/`, or `social-icons/`. An old signature references an
   exact path (e.g. `logos/irs-ea.png`); remove or rename it and that signature
   shows a broken image. To update someone's photo, **keep the same filename**
   (overwrite in place) or add a new file alongside the old one — never delete.
3. **Don't rewrite history on `main`.** No force-push, no rebasing published
   commits. jsDelivr resolves `@main` against live history; rewriting it can
   orphan asset paths.

After adding or replacing assets, push to `main` and purge the CDN cache so the
change is served immediately (jsDelivr caches the `@main` tag ~12h):

```
curl https://purge.jsdelivr.net/gh/SMAART-Company/smaart-gmail-signatures@main/logos/<file>
```

If a recipient still sees an old/broken image, bump the **Image cache version**
field in the generator and re-copy — that busts Gmail's image proxy
(`ci3.googleusercontent.com`), which caches by full URL for ~7 days.

**For a frozen, never-changing reference** (e.g. an executive signature you want
immutable), set the **Asset base URL** to a pinned commit instead of `@main`:
`…/smaart-gmail-signatures@<commit-sha>/…`. jsDelivr serves SHA-pinned URLs as
permanently immutable. Trade-off: assets added in later commits won't appear
until you bump the SHA.

## Adding a new teammate

1. Drop their headshot (any size, any format) in `team-images/` as `firstname-lastname.<ext>`.
2. Run `python3 scripts/build-assets.py` — it crops to 200x200, compresses under 100 KB, overwrites the original with a `.jpg`.
3. Commit. The name will appear in the generator's photo dropdown after you add it to `index.html` (`<option>` list).

## Brand tokens (used in the signature)

- Navy `#0D004C` — name, links, logo border
- Green `#39B54A` — vertical accent bar
- White `#FFFFFF` — on-navy icon glyphs

No hardcoded colors outside these.
