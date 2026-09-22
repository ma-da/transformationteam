from pathlib import Path
from urllib.parse import urlparse, unquote
from collections import Counter
import csv
import json
import re


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

CONTENT_DIR = ROOT / "content" / "course"
ARCHIVE_DIR = ROOT / "archive" / "original-httpdocs"
DATA_DIR = ROOT / "data"

CSV_OUT = DATA_DIR / "course-resource-audit.csv"
JSON_OUT = DATA_DIR / "course-resource-audit.json"

# ============================================================
# ADDITIONAL LOCAL MEDIA SOURCES
# ============================================================

WINDOWS_WTK_VIDEO_DIR = Path(
    r"C:\datasources\WTKvideos"
)

WSL_WTK_VIDEO_DIR = Path(
    "/mnt/c/datasources/WTKvideos"
)


if WINDOWS_WTK_VIDEO_DIR.exists():
    WTK_VIDEO_DIR = WINDOWS_WTK_VIDEO_DIR
elif WSL_WTK_VIDEO_DIR.exists():
    WTK_VIDEO_DIR = WSL_WTK_VIDEO_DIR
else:
    WTK_VIDEO_DIR = None
    
   
# ============================================================
# SETTINGS
# ============================================================

RESOURCE_BLOCK_RE = re.compile(
    r"<!-- RESOURCE-INVENTORY:START -->"
    r"(.*?)"
    r"<!-- RESOURCE-INVENTORY:END -->",
    re.DOTALL,
)

RESOURCE_LINE_RE = re.compile(
    r"""
    ^-\s+
    \*\*(?P<label>.*?)\*\*
    \s+—\s+
    <(?P<url>[^>]+)>
    (?:\s+
        _\(legacy:\s*
        (?P<legacy>.*?)
        \)_
    )?
    \s*$
    """,
    re.VERBOSE,
)

LESSON_RE = re.compile(
    r"lesson-(\d+)\.md$",
    re.IGNORECASE,
)


MEDIA_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".bmp",
    ".tif",
    ".tiff",

    ".mp4",
    ".webm",
    ".mov",
    ".avi",
    ".flv",
    ".swf",

    ".mp3",
    ".wav",
    ".ogg",
    ".m4a",

    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".zip",
}


LEGACY_HOSTS = {
    "transformationteam.net",
    "www.transformationteam.net",
    "personalgrowthcourses.net",
    "www.personalgrowthcourses.net",
}


VIDEO_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "vimeo.com",
    "www.vimeo.com",
}


# ============================================================
# HELPERS
# ============================================================

def normalized_stem(value):
    """
    Normalize filenames / URL slugs for conservative
    local-media matching.

    elephant_artist
    elephant-artist
    Elephant Artist

    all become:

    elephantartist
    """

    value = unquote(
        str(value)
    )

    value = Path(value).stem.lower()

    return re.sub(
        r"[^a-z0-9]+",
        "",
        value,
    )

def find_local_matches(
    url,
    local_index,
):
    """
    Find possible local files corresponding to a legacy
    Transformation Team / Personal Growth Courses URL.

    We deliberately do NOT match arbitrary external hosts
    against local filenames. That avoids false matches such
    as Wikipedia pages named "Milgram_experiment" matching
    MILGRAM_EXPERIMENT.mp4.

    Matching preference:
      1. exact basename
      2. exact stem
      3. normalized stem
    """

    host = url_host(url)

    # --------------------------------------------------------
    # IMPORTANT:
    # Only legacy sites represented by our local collections
    # are eligible for automatic local matching.
    # --------------------------------------------------------

    if host not in LEGACY_HOSTS:
        return []


    try:
        parsed = urlparse(url)

        path = unquote(
            parsed.path
        ).rstrip("/")

        basename = Path(path).name

    except Exception:
        return []


    if not basename:
        return []


    basename_lower = (
        basename.lower()
    )

    stem_lower = (
        Path(basename)
        .stem
        .lower()
    )

    normalized = normalized_stem(
        basename
    )


    # --------------------------------------------------------
    # 1. Exact filename
    # --------------------------------------------------------

    matches = local_index[
        "basename"
    ].get(
        basename_lower,
        [],
    )

    if matches:

        return [
            {
                **item,
                "match_type":
                    "exact-filename",
            }
            for item in matches
        ]


    # --------------------------------------------------------
    # 2. Exact stem
    #
    # Example:
    #
    # /video/elephant_artist
    #
    # matches:
    #
    # ELEPHANT_ARTIST.mp4
    # elephant_artist.php
    # --------------------------------------------------------

    matches = local_index[
        "stem"
    ].get(
        stem_lower,
        [],
    )

    if matches:

        return [
            {
                **item,
                "match_type":
                    "exact-stem",
            }
            for item in matches
        ]


    # --------------------------------------------------------
    # 3. Normalized stem
    #
    # Example:
    #
    # gratefulness_david_steindl_rast
    #
    # matches:
    #
    # GRATEFULNESS_DAVID_STEINDL-RAST.mp4
    # --------------------------------------------------------

    if normalized:

        matches = local_index[
            "normalized_stem"
        ].get(
            normalized,
            [],
        )

        if matches:

            return [
                {
                    **item,
                    "match_type":
                        "normalized-stem",
                }
                for item in matches
            ]


    return []    

def lesson_number(path):
    match = LESSON_RE.search(path.name)

    if not match:
        return None

    return int(match.group(1))


def normalize_url(url):
    return url.strip()


def url_host(url):
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def url_suffix(url):
    try:
        path = unquote(
            urlparse(url).path
        )

        return Path(path).suffix.lower()

    except Exception:
        return ""


def url_basename(url):
    try:
        path = unquote(
            urlparse(url).path
        )

        return Path(path).name

    except Exception:
        return ""


def classify_resource(url, section):
    """
    Broad content type.
    """

    host = url_host(url)
    suffix = url_suffix(url)

    if suffix in MEDIA_EXTENSIONS:
        return "media-file"

    if host in VIDEO_HOSTS:
        return "embedded-video"

    if section == "Media & files":
        return "media"

    return "link"


def classify_action(
    url,
    local_matches,
):
    """
    Suggest an action without automatically changing anything.
    """

    host = url_host(url)
    suffix = url_suffix(url)

    try:
        path = unquote(
            urlparse(url).path
        ).lower()
    except Exception:
        path = ""


    # --------------------------------------------------------
    # LOCAL WTK VIDEO
    # --------------------------------------------------------

    has_wtk_video = any(
        item["source"] == "WTKvideos"
        for item in local_matches
    )

    if has_wtk_video:

        # Strongest case:
        # old PGC /video/... URL maps to local video file.
        if "/video/" in path:
            return (
                "migrate-local-video-candidate"
            )

        # A local video happens to match a story/page URL.
        # Review manually before replacing the page with video.
        return (
            "review-local-video-candidate"
        )


    # --------------------------------------------------------
    # LEGACY LOCAL PAGE / FILE
    # --------------------------------------------------------

    has_archive_match = any(
        item["source"] == "legacy-archive"
        for item in local_matches
    )

    if has_archive_match:
        return (
            "review-local-page-candidate"
        )


    # --------------------------------------------------------
    # OBSOLETE MEDIA
    # --------------------------------------------------------

    if suffix in {
        ".swf",
        ".flv",
    }:
        return "replace-obsolete"


    # --------------------------------------------------------
    # LEGACY HOSTED BUT NOT FOUND LOCALLY
    # --------------------------------------------------------

    if host in LEGACY_HOSTS:
        return "review-legacy-hosted"


    # --------------------------------------------------------
    # EXTERNAL SOURCES
    # --------------------------------------------------------

    if host in VIDEO_HOSTS:
        return "review-external-media"


    if host == "web.archive.org":
        return "review-archived-link"


    if suffix in MEDIA_EXTENSIONS:
        return "review-external-file"


    return "review-external-link"


# ============================================================
# BUILD ARCHIVE FILE INDEX
# ============================================================

def build_local_file_index():
    """
    Build indexes for files that may be reused by the new site.

    Sources:
      - legacy Transformation Team archive
      - C:\\datasources\\WTKvideos

    Returns indexes by:
      - exact basename
      - exact stem
      - normalized stem
    """

    index = {
        "basename": {},
        "stem": {},
        "normalized_stem": {},
    }


    def add_file(
        path,
        source_name,
    ):

        basename = path.name.lower()
        stem = path.stem.lower()

        normalized = normalized_stem(
            path.name
        )


        record = {
            "path": str(path),
            "source": source_name,
        }


        index["basename"].setdefault(
            basename,
            [],
        ).append(record)


        index["stem"].setdefault(
            stem,
            [],
        ).append(record)


        if normalized:

            index[
                "normalized_stem"
            ].setdefault(
                normalized,
                [],
            ).append(record)


    # --------------------------------------------------------
    # Legacy site archive
    # --------------------------------------------------------

    if ARCHIVE_DIR.exists():

        for path in ARCHIVE_DIR.rglob("*"):

            if path.is_file():

                add_file(
                    path,
                    "legacy-archive",
                )


    # --------------------------------------------------------
    # WTK video collection
    # --------------------------------------------------------

    if (
        WTK_VIDEO_DIR
        and WTK_VIDEO_DIR.exists()
    ):

        for path in WTK_VIDEO_DIR.rglob("*"):

            if path.is_file():

                add_file(
                    path,
                    "WTKvideos",
                )

    else:

        print(
            "WARNING: WTKvideos directory "
            "not found."
        )


    return index


# ============================================================
# EXTRACT RESOURCES FROM MARKDOWN
# ============================================================

def extract_resources(md_file):
    text = md_file.read_text(
        encoding="utf-8",
        errors="replace",
    )

    lesson = lesson_number(
        md_file
    )

    match = RESOURCE_BLOCK_RE.search(
        text
    )

    if not match:
        print(
            f"WARNING: no resource inventory in "
            f"{md_file.name}"
        )
        return []

    block = match.group(1)

    section = None
    results = []

    for raw_line in block.splitlines():

        line = raw_line.strip()

        if line == "### Media & files":
            section = "Media & files"
            continue

        if line == "### Links":
            section = "Links"
            continue

        resource_match = (
            RESOURCE_LINE_RE.match(line)
        )

        if not resource_match:
            continue

        url = normalize_url(
            resource_match.group("url")
        )

        label = (
            resource_match.group("label")
            .strip()
        )

        legacy = (
            resource_match.group("legacy")
            or ""
        )

        legacy_files = [
            item.strip()
            for item in legacy.split(",")
            if item.strip()
        ]

        results.append({
            "lesson": lesson,
            "section": section or "",
            "label": label,
            "url": url,
            "legacy_source_files": (
                legacy_files
            ),
        })

    return results


# ============================================================
# CONSOLIDATE
# ============================================================

def consolidate_resources(
    raw_resources,
    local_index,
):
    """
    Deduplicate resources by URL across all lessons
    and attach possible local file matches.
    """

    combined = {}


    for item in raw_resources:

        url = item["url"]


        if url not in combined:

            local_matches = find_local_matches(
                url,
                local_index,
            )


            combined[url] = {
                "id": None,

                "resource_type":
                    classify_resource(
                        url,
                        item["section"],
                    ),

                "label":
                    item["label"],

                "source_url":
                    url,

                "host":
                    url_host(url),

                "lessons": [],

                "legacy_source_files": [],

                "local_matches":
                    local_matches,

                "suggested_action":
                    classify_action(
                        url,
                        local_matches,
                    ),

                "status":
                    "needs-review",

                "new_url":
                    "",

                "notes":
                    "",
            }


        record = combined[url]


        # ----------------------------------------------------
        # LESSONS
        # ----------------------------------------------------

        lesson = item["lesson"]

        if (
            lesson is not None
            and lesson not in record["lessons"]
        ):
            record["lessons"].append(
                lesson
            )


        # ----------------------------------------------------
        # LEGACY PHP SOURCE FILES
        # ----------------------------------------------------

        for filename in (
            item["legacy_source_files"]
        ):

            if (
                filename
                not in record[
                    "legacy_source_files"
                ]
            ):
                record[
                    "legacy_source_files"
                ].append(
                    filename
                )


        # ----------------------------------------------------
        # LABEL
        #
        # Prefer a more descriptive label if the same
        # resource appears with different labels.
        # ----------------------------------------------------

        if (
            len(item["label"])
            > len(record["label"])
        ):
            record["label"] = (
                item["label"]
            )


    # ========================================================
    # FINALIZE RECORDS
    # ========================================================

    records = list(
        combined.values()
    )


    # Sort lesson numbers and legacy source files.

    for record in records:

        record[
            "lessons"
        ].sort()

        record[
            "legacy_source_files"
        ].sort()


    # Sort output by:
    #   1. first lesson in which resource appears
    #   2. label

    records.sort(
        key=lambda item: (
            min(
                item["lessons"]
                or [999]
            ),
            item["label"].lower(),
        )
    )


    # Stable readable IDs.

    for number, record in enumerate(
        records,
        start=1,
    ):

        record["id"] = (
            f"resource-{number:04d}"
        )


    return records


# ============================================================
# OUTPUT
# ============================================================

def write_json(records):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    JSON_OUT.write_text(
        json.dumps(
            records,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def write_csv(records):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "id",
        "resource_type",
        "label",
        "source_url",
        "host",
        "lessons",
        "legacy_source_files",
        "local_matches",
        "suggested_action",
        "status",
        "new_url",
        "notes",
    ]

    with CSV_OUT.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
        )

        writer.writeheader()

        for record in records:

            row = dict(record)

            row["lessons"] = ";".join(
                str(n)
                for n in record["lessons"]
            )

            row[
                "legacy_source_files"
            ] = ";".join(
                record[
                    "legacy_source_files"
                ]
            )

            row["local_matches"] = ";".join(
                (
                    f'{item["source"]}'
                    f'|{item["match_type"]}'
                    f'|{item["path"]}'
                )
                for item in record[
                    "local_matches"
                ]
            )

            writer.writerow(row)


# ============================================================
# REPORT
# ============================================================

def print_summary(records):

    print()
    print("=" * 72)
    print("TRANSFORMATION COURSE RESOURCE AUDIT")
    print("=" * 72)

    print()
    print(
        "Unique resources:",
        len(records),
    )

    print()

    # --------------------------------------------------------
    # Resource types
    # --------------------------------------------------------

    print("Resource types:")

    types = Counter(
        item["resource_type"]
        for item in records
    )

    for key, count in types.most_common():
        print(
            f"  {count:4}  {key}"
        )


    # --------------------------------------------------------
    # Suggested actions
    # --------------------------------------------------------

    print()
    print("Suggested actions:")

    actions = Counter(
        item["suggested_action"]
        for item in records
    )

    for key, count in actions.most_common():
        print(
            f"  {count:4}  {key}"
        )


    # --------------------------------------------------------
    # Hosts
    # --------------------------------------------------------

    print()
    print("Top hosts:")

    hosts = Counter(
        item["host"] or "(local/unknown)"
        for item in records
    )

    for host, count in hosts.most_common(20):
        print(
            f"  {count:4}  {host}"
        )


    # --------------------------------------------------------
    # Resources used by multiple lessons
    # --------------------------------------------------------

    shared = [
        item
        for item in records
        if len(item["lessons"]) > 1
    ]

    print()
    print(
        "Resources used by multiple lessons:",
        len(shared),
    )


    # --------------------------------------------------------
    # Any local matches
    # --------------------------------------------------------

    matched = [
        item
        for item in records
        if item.get("local_matches")
    ]

    print(
        "Resources with local file matches:",
        len(matched),
    )


    # --------------------------------------------------------
    # WTKvideos matches
    # --------------------------------------------------------

    wtk_video_matches = [
        item
        for item in records
        if any(
            match.get("source") == "WTKvideos"
            for match in item.get(
                "local_matches",
                [],
            )
        )
    ]

    print(
        "Matched in WTKvideos:",
        len(wtk_video_matches),
    )


    # --------------------------------------------------------
    # Legacy archive matches
    # --------------------------------------------------------

    archive_matches = [
        item
        for item in records
        if any(
            match.get("source") == "legacy-archive"
            for match in item.get(
                "local_matches",
                [],
            )
        )
    ]

    print(
        "Matched in legacy archive:",
        len(archive_matches),
    )


    # --------------------------------------------------------
    # Match types
    # --------------------------------------------------------

    match_types = Counter()

    for item in matched:

        for match in item.get(
            "local_matches",
            [],
        ):
            match_types[
                match.get(
                    "match_type",
                    "unknown",
                )
            ] += 1

    print()
    print("Local match types:")

    for key, count in match_types.most_common():
        print(
            f"  {count:4}  {key}"
        )


    # --------------------------------------------------------
    # Output files
    # --------------------------------------------------------

    print()
    print("Generated:")

    print(
        " ",
        CSV_OUT.relative_to(ROOT),
    )

    print(
        " ",
        JSON_OUT.relative_to(ROOT),
    )


# ============================================================
# MAIN
# ============================================================

def main():

    lesson_files = sorted(
        CONTENT_DIR.glob(
            "lesson-*.md"
        ),
        key=lambda path: (
            lesson_number(path)
            or 999
        ),
    )

    if not lesson_files:
        raise RuntimeError(
            "No lesson Markdown files found."
        )

    print(
        f"Scanning "
        f"{len(lesson_files)} lessons..."
    )


    local_index = (
        build_local_file_index()
    )


    raw_resources = []

    for md_file in lesson_files:

        resources = (
            extract_resources(
                md_file
            )
        )

        raw_resources.extend(
            resources
        )

        print(
            f"Lesson "
            f"{lesson_number(md_file):02}: "
            f"{len(resources)} resources"
        )


    records = consolidate_resources(
        raw_resources,
        local_index,
    )


    write_json(records)
    write_csv(records)

    print_summary(records)


if __name__ == "__main__":
    main()