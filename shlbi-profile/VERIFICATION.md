# Local verification

Package prepared for **Saif Alshalabi** / **shlbi** on October 4, 2026 (UTC).

## Observed checks

- **21 offline unit tests passed**, zero failures, using `python -m unittest discover -s tests -v`.
- All **18 SVG assets** parsed as valid XML, and every text element remained inside its SVG viewport in the local Chromium check.
- All README image paths resolved to included files. No fonts, scripts, external images, or foreignObject elements are embedded in the SVG artwork.
- The locally rendered Markdown preview was checked at **1200, 768, 390, and 320 CSS-pixel viewport widths**, in both light and dark modes. No page-level horizontal overflow or missing images was observed. All four section-navigation links found their targets.
- The mobile hero source was selected below the configured 600-pixel breakpoint.
- The header animation changed pixels when loaded as an image, rather than only when opened as a standalone SVG.
- The explicit reduced-motion `<picture>` fallback produced a static image. Static alternatives are included for all four animated illustrations; hero and REPOT also have mobile static versions.
- Activity-generator tests cover rejection of private/unexpected/duplicate repositories, malformed commit links and SHAs, invalid subjects, XML escaping, marker validation, preservation of surrounding README text, deterministic drawing, and failure without publication after an API error.

## Scope and limitations

The preview uses a local approximation of GitHub's Markdown styling, not a screenshot from a deployed GitHub profile. The assets and content are the actual package files. Native GitHub styling, image caching, and sanitization can affect the final presentation.

**No GitHub repository was created and no files were pushed from this session.** Available GitHub connector actions were read-only, and the local Git environment was not authenticated. The live profile, GitHub Actions workflow, external LinkedIn page, and live REPOT application were not exercised by these checks.

The initial activity entries were read from the connected GitHub tool. The updater's error handling and transformations were tested offline; its future scheduled execution in GitHub Actions has not yet been observed. Project artwork is illustrative, not evidence of a product run or scientific experiment.
