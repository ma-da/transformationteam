# Transformation Team Website

This repository contains the rebuilt **Planetary Transformation Team** website for [TransformationTeam.net](https://www.transformationteam.net/).

The new site is designed as a lightweight, mostly static website with:

- a shared cosmic visual style,
- Markdown-based editable content,
- reusable HTML templates,
- Python-generated page builds,
- a 21-lesson Transformation Course,
- shared media and data assets,
- and minimal JavaScript for navigation, modal, and scroll behavior.

The goal is to make the site easy for the PEERS team to collaboratively maintain without requiring team members to edit HTML directly.

---

## Repository Structure

```text
transformation-team-site/
├── content/
│   ├── fluid-intelligence.md
│   └── course/
│       ├── index.md
│       ├── fable.md
│       ├── lesson-1.md
│       ├── lesson-2.md
│       ├── ...
│       └── lesson-21.md
│
├── data/
│   ├── media-references.txt
│   └── php-dependencies.txt
│
├── scripts/
│   └── build_content.py
│
├── templates/
│   ├── base.html
│   ├── header.html
│   └── footer.html
│
├── src/
│   └── site/
│       ├── index.html
│       ├── style.css
│       ├── fluid-intelligence.html
│       │
│       ├── course/
│       │   ├── index.html
│       │   ├── fable.html
│       │   ├── lesson-1.html
│       │   ├── lesson-2.html
│       │   ├── ...
│       │   └── lesson-21.html
│       │
│       └── assets/
│           ├── data/
│           │   └── transformation-course-appreciations.json
│           ├── fonts/
│           │   └── SpaceGrotesk.woff2
│           ├── images/
│           │   ├── favicon.ico
│           │   ├── hero-eye-cutout.webp
│           │   ├── starry-background.webp
│           │   └── other site images
│           ├── js/
│           │   └── site.js
│           └── video/
│               └── transformation_team.mp4
│
├── .gitattributes
├── .gitignore
└── README.md
```

The local legacy site archive is kept outside the tracked rebuild workflow and is excluded from Git through `.gitignore`.

---

## What Team Members Should Edit

### Markdown content

The primary collaborative content lives under:

```text
content/
```

These are the files the team should edit when revising written site content.

Important files include:

```text
content/fluid-intelligence.md
content/course/fable.md
content/course/index.md
content/course/lesson-1.md
...
content/course/lesson-21.md
```

The lesson Markdown files are the editorial source of truth for the Transformation Course.

**Do not edit the generated lesson HTML files directly.**

After Markdown is updated, the HTML pages are regenerated using the build script.

---

## Lesson Resource Inventories

Each lesson Markdown file contains an editorial **Resource inventory** near the top.

Example:

```markdown
<!-- RESOURCE-INVENTORY:START -->

## Resource inventory

> **Editorial checklist:** These resources were detected in the legacy lesson.
> Review or replace them as the lesson is updated.
> This section is omitted from the public page build.

### Media & files

- Resource name — URL

### Links

- Resource name — URL

<!-- RESOURCE-INVENTORY:END -->
```

These inventories are intended to help the team review and modernize:

- images,
- videos,
- audio,
- documents,
- external links,
- legacy PersonalGrowthCourses.net resources,
- old TransformationTeam.net links,
- Flash-era media,
- and other resources used within each lesson.

The resource inventory is visible in GitHub Markdown editing/review but is removed from the public page when the site is built.

---

## Generated Pages

The public website is built into:

```text
src/site/
```

Examples:

```text
src/site/index.html
src/site/fluid-intelligence.html
src/site/course/index.html
src/site/course/fable.html
src/site/course/lesson-1.html
...
src/site/course/lesson-21.html
```

Course lesson URLs use the flat format:

```text
/course/lesson-1.html
/course/lesson-2.html
...
/course/lesson-21.html
```

The individual lessons do not have separate directories because they share the same site assets and templates.

---

## Building the Site

The page generator is:

```text
scripts/build_content.py
```

It reads the Markdown files from `content/`, renders them through the shared templates, and writes the resulting HTML into `src/site/`.

From the project root:

```bash
python scripts/build_content.py
```

If using Jupyter on Windows:

```python
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"C:\datasources\transformation-team-site")

result = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "build_content.py")],
    cwd=ROOT,
    capture_output=True,
    text=True,
)

print(result.stdout)
print(result.stderr)
```

---

## Shared Templates

Shared page structure is stored in:

```text
templates/
```

### `base.html`

Provides the common HTML shell for generated pages.

### `header.html`

Provides the shared internal-page header.

Internal pages use **Home** at the upper left.

The homepage instead uses **Welcome**, which opens the welcome/invitation modal.

The Transformation Course dropdown includes:

- Cosmic Fable
- Fluid Intelligence
- Course Index
- all 21 lessons

### `footer.html`

Provides the shared footer, including PEERS information and the cosmic background image attribution.

---

## Homepage

The homepage is currently maintained directly at:

```text
src/site/index.html
```

It contains:

- the cosmic hero artwork,
- the main Transformation Team invitation,
- five reflective questions,
- four next-step buttons,
- the Welcome modal,
- the shared Transformation Course navigation,
- and the site footer.

The four buttons below the questions are:

- **I'm Ready** — opens the Welcome modal
- **Cosmic Fable** — `/course/fable.html`
- **Fluid Intelligence** — `/fluid-intelligence.html`
- **21 Lessons** — `/course/index.html`

---

## Main Homepage Questions

These five questions are central to the homepage and are preserved here for easy reference by the team.

### 1

> Have you ever felt that one of the reasons you are here now is to transform your life and to help transform our world to a more meaningful way of living based in love and empowerment?

### 2

> Do you recognize that every person in the world [has a heart](https://www.momentoflove.org/), and that as each of us is a unique manifestation of life in this universe, all people deserve our love and support in moving ever more fully into their magnificence?

### 3

> Are you ready to move [beyond old ways](https://www.wanttoknow.info/070707newparadigm) which focused on fear, secrecy, and polarization, and to instead choose greater love, transparency, and meaningful connection for yourself and everyone around you?

### 4

> Are you willing to work on transforming your own weaknesses and fears? Are you open to exploring deep, [hidden agendas](https://www.wanttoknow.info/) affecting our planet? Do you want to let go of that which doesn't serve your highest good?

### 5

> Are you interested in joining a large team of souls who know that a major part of the reason we came here is to help all who are ready on this planet to transform to a deeper, richer way of living in this eternal sacred moment?

---

## Styling

The entire site uses one shared stylesheet:

```text
src/site/style.css
```

The design includes:

- a full-page cosmic background,
- a transparent/sticky smart-scroll header,
- Space Grotesk typography,
- soft gradient-edged content panels,
- light reading surfaces,
- subtle purple accents,
- a transparent hero eye image,
- responsive mobile layouts,
- and a cosmic-style modal.

Please avoid creating additional page-specific stylesheets unless there is a strong reason. Shared styles should normally be added to `style.css`.

---

## JavaScript

Shared JavaScript is stored at:

```text
src/site/assets/js/site.js
```

Current shared behavior includes:

- Transformation Course dropdown behavior,
- smart header hide/show on scroll,
- Welcome modal behavior on the homepage,
- closing dropdowns when clicking outside,
- and cosmic background scrolling behavior.

The script is written so pages without the homepage modal can still use the same shared file.

---

## Cosmic Background and Hero Assets

Primary visual assets include:

```text
src/site/assets/images/starry-background.webp
src/site/assets/images/hero-eye-cutout.webp
src/site/assets/images/favicon.ico
```

The cosmic background is based on astronomical imagery credited to:

> NASA, ESA, CSA, STScI; Adam Ginsburg, Nazar Budaiev and Taehwa Yoo (University of Florida). Image processing: Alyssa Pagan (STScI).

Original image:

https://go.nasa.gov/46nwvRm

The full attribution should remain present in the site footer.

---

## Appreciation Messages / Testimonials

Transformation Course appreciation messages have been converted from the legacy site into reusable structured data:

```text
src/site/assets/data/transformation-course-appreciations.json
```

Each record contains:

```json
{
  "quote": "Appreciation message text...",
  "attribution": "Name"
}
```

This JSON is intended to be reusable both on TransformationTeam.net and on other PEERS websites or features.

---

## Editing Workflow

For most content updates:

```text
1. Edit the appropriate Markdown file under /content
2. Commit the changes to GitHub
3. Review collaboratively
4. Run scripts/build_content.py
5. Review the generated HTML locally
6. Commit the generated HTML
7. Deploy
```

For lesson content, team members should normally edit:

```text
content/course/lesson-N.md
```

rather than:

```text
src/site/course/lesson-N.html
```

---

## Local Preview

Serve the site from:

```text
src/site/
```

Do **not** serve from the repository root, because root-relative asset URLs such as `/style.css` and `/assets/...` expect `src/site` to be the web root.

From WSL:

```bash
cd /mnt/c/datasources/transformation-team-site/src/site

python3 -m http.server 8080
```

Then open:

```text
http://localhost:8080/
```

Example pages:

```text
http://localhost:8080/course/index.html
http://localhost:8080/course/fable.html
http://localhost:8080/fluid-intelligence.html
http://localhost:8080/course/lesson-1.html
```

---

## Git / GitHub

Repository:

```text
https://github.com/ma-da/transformationteam
```

The repository uses `main` as its primary branch.

Before major automated content or media migrations, create a commit or tag so changes can be easily reviewed or reversed.

The initial rebuilt-site baseline is intended to be tagged:

```text
pre-media-migration
```

---

## Project Principles

When updating the site:

- preserve the original heart and intent of the Transformation Course,
- keep the editing workflow simple for nontechnical team members,
- prefer Markdown for collaboratively edited content,
- avoid duplicating shared layout code,
- keep generated HTML reproducible,
- modernize broken or obsolete media and links,
- preserve attribution and source information,
- keep the site lightweight and privacy-conscious,
- and avoid unnecessary frameworks or dependencies.

The rebuilt site should remain simple enough to understand as a small static website while being structured enough to maintain reliably for years.
