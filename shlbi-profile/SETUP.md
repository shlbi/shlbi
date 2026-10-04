# Publish Saif Alshalabi's profile

The package is finished locally. It has **not** been uploaded to GitHub.

## Publish using your browser — no Git commands

1. Sign into GitHub as **shlbi**. Create a new repository named **shlbi**, select **Public**, turn **Add README** on, and create it. The profile repository name must match your username.
2. Extract this ZIP. Open the inner `shlbi-profile` folder: you should see `README.md`, `assets`, `scripts`, `data`, `tests`, and `.github`.
3. In `shlbi/shlbi`, choose **Add file → Upload files**. Drag the **contents** of that extracted folder onto the upload page, keeping subfolders intact. Upload the prepared README even though it replaces the starter README.
4. Commit the files to **main**, then visit your GitHub profile.

**Do not upload the ZIP itself. Do not upload the outer `shlbi-profile` folder as a nested folder.** The repository needs `README.md` and `assets/` at its root.

Correct structure:

```text
shlbi/shlbi
├── README.md
├── assets/
│   ├── hero.svg
│   ├── repot.svg
│   ├── kinetic.svg
│   ├── osmo.svg
│   ├── activity.svg
│   ├── footer.svg
│   ├── linkedin.svg
│   ├── repot-link.svg
│   ├── mobile/
│   └── static/
├── data/activity.json
├── scripts/
├── tests/
├── .github/workflows/refresh-profile.yml
├── .gitignore
└── SETUP.md
```

If a repository named `shlbi` already exists, upload into that repository instead. This README is meant to replace that repository's README, not any other project's README.

## Daily Build Pulse refresh

All artwork and the included activity snapshot work without a workflow. The optional workflow refreshes the latest default-branch commit of **REPOT, Kinetic, and OSMO**, then updates the activity images and commit links. It is not a complete contribution history or personal contribution score.

The workflow file is `.github/workflows/refresh-profile.yml`. Once that file and the scripts are uploaded to `main`, it is configured to run on the initial relevant push, by manual dispatch, and daily at **10:23 UTC**. Scheduling is performed by GitHub Actions, not by this chat. No workflow has been executed from this session.

For a manual first refresh, open the repository's **Actions** tab, select **Refresh build pulse**, and choose **Run workflow**. Enable Actions if GitHub prompts you. A repository or organization policy can prevent workflows from running or writing; check the failed run before changing any settings. The YAML requests `contents: write` only in this profile repository and uses GitHub's built-in token. You do not need to create or paste a personal access token.

Scheduled runs can be delayed, and GitHub may disable scheduled workflows in public repositories after 60 days without repository activity. The timestamp on the card is the last successful snapshot check, not a claim that the card is live. If a refresh fails, the checked-in snapshot remains available. This schedule assumes your default branch is `main`; change both the workflow branch filter and final push target if yours has another name.

To leave the profile fully static, omit the `.github` folder from the upload. The visual SVG animations still play; only the activity data stays fixed at the included snapshot.

## Edit later

Your bio, project descriptions, links, tools, and lab notes are ordinary Markdown/HTML in `README.md`.

The original illustrations are authored in `scripts/build_art.py`. To regenerate them locally with Python 3.10 or newer:

```bash
python scripts/build_art.py
python scripts/update_activity.py --from-cache
python -m unittest discover -s tests -v
```

To fetch new public repository metadata instead of redrawing the saved snapshot:

```bash
python scripts/update_activity.py
```

The generators use Python's standard library. The published profile needs no Python, server, hosting service, font download, third-party stats widget, or secret. The Python code runs only when you explicitly use it locally or let the included GitHub workflow run.

## Motion, mobile, and image fallbacks

The hero and REPOT feature panel use different layouts on narrow screens. CSS animates the modular S, the feature transfer, Kinetic's abstract traffic ring, and OSMO's stylized curves. Explicit `<picture>` fallbacks select static artwork when the viewer requests reduced motion. The text and links remain usable without the animations.

These are **concept illustrations**, not screenshots, product recordings, contribution heatmaps, or scientific measurements. OSMO's drawn curves are decorative geometry. The activity card is separate and is based on real public repository commits.

## Verification and provenance

`VERIFICATION.md` records the local checks. The self-contained HTML preview in the outer package is for viewing the result, not a replacement for the GitHub README. Its surrounding page approximates GitHub's Markdown presentation; exact live GitHub rendering has not been checked.

The initial activity snapshot was populated from the connected GitHub reads in this session. Only repository name, public status, default branch, commit SHA, commit subject, date, and commit URL are retained; no author email or private-repository data is included.

Project descriptions were based on the public READMEs for:

- REPOT: `https://github.com/shlbi/graft`
- Kinetic: `https://github.com/shlbi/kinetic`
- OSMO: `https://github.com/shlbi/osmo`

The checkout action is pinned to the commit returned for `actions/checkout`'s `v6` tag at package creation, not a floating tag. No other third-party action is used.

Official GitHub references:

- Profile README requirements: `https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme`
- Browser file upload: `https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository`
- Workflow schedules: `https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule`
