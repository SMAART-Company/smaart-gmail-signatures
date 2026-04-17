# team-images

Team headshots for SMAART Gmail signatures.

## Spec

- **Format:** JPG (run the normalizer — it handles PNG/HEIC input)
- **Dimensions:** 200×200 square, centered crop
- **File size:** under 100 KB (jsDelivr caches; Gmail clips messages past ~102 KB)
- **Filename:** `firstname-lastname.jpg` — lowercase, hyphenated

## Adding a headshot

1. Drop the original in this folder (any format, any size).
2. From the repo root, run:

   ```
   python3 scripts/build-assets.py
   ```

3. The script crops to 200×200, compresses under 100 KB, overwrites the source with a `.jpg`, and renames spaces/capitals to `kebab-case`.

## Referenced from

Signatures pull each photo via jsDelivr:

```
https://cdn.jsdelivr.net/gh/SMAART-Company/smaart-gmail-signatures@main/team-images/<slug>.jpg
```

The slug must match a `<option>` in `index.html` for it to appear in the generator dropdown.
