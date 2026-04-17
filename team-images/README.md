# team-images

Team headshots and profile photos used in SMAART Gmail signatures.

## Requirements

- **Format:** PNG (transparent background) or JPG
- **Dimensions:** 200x200px, square, centered on face
- **File size:** under 100 KB (Gmail clips long messages past ~102 KB)
- **Filename:** `firstname-lastname.png` — lowercase, hyphenated, no spaces
  - Example: `daniel-corcega.png`

## Usage

Images are referenced by the signature generator via the repo's raw GitHub URL:

```
https://raw.githubusercontent.com/SMAART-Company/smaart-gmail-signatures/main/team-images/<filename>
```

Gmail fetches and proxies the image once per recipient, so a stable raw URL is sufficient — no CDN required.
