from pathlib import Path
import argparse
import json
import re


ROOT = Path(__file__).resolve().parents[1]

CONTENT_DIR = (
    ROOT
    / "content"
    / "course"
)

MAPPING_JSON = (
    ROOT
    / "data"
    / "course-video-migration-map.json"
)


RESOURCE_BLOCK_RE = re.compile(
    r"("
    r"<!-- RESOURCE-INVENTORY:START -->"
    r".*?"
    r"<!-- RESOURCE-INVENTORY:END -->"
    r")",
    flags=re.DOTALL,
)


def replace_outside_inventory(
    text,
    replacements,
):
    """
    Replace legacy video URLs in public lesson content,
    while preserving the editorial Resource inventory
    exactly as it is.
    """

    pieces = RESOURCE_BLOCK_RE.split(
        text
    )

    replacement_count = 0


    for index, piece in enumerate(
        pieces
    ):

        # Odd-numbered pieces are the captured
        # Resource inventory blocks.
        if (
            piece.startswith(
                "<!-- RESOURCE-INVENTORY:START -->"
            )
        ):
            continue


        for old_url, new_url in replacements:

            count = piece.count(
                old_url
            )

            if count:

                piece = piece.replace(
                    old_url,
                    new_url,
                )

                replacement_count += count


        pieces[index] = piece


    return (
        "".join(pieces),
        replacement_count,
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Replace confirmed legacy course video URLs "
            "with local site video URLs."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Write changes. "
            "Without --apply, perform a dry run."
        ),
    )

    args = parser.parse_args()


    if not MAPPING_JSON.exists():

        raise RuntimeError(
            f"Migration map not found: "
            f"{MAPPING_JSON}"
        )


    records = json.loads(
        MAPPING_JSON.read_text(
            encoding="utf-8",
        )
    )


    replacements = [
        (
            record["legacy_url"],
            record["new_url"],
        )
        for record in records
    ]


    print()
    print("=" * 72)
    print("COURSE VIDEO LINK REWRITE")
    print("=" * 72)

    print()
    print(
        "Mode:",
        "APPLY"
        if args.apply
        else "DRY RUN",
    )

    print(
        "Video mappings:",
        len(replacements),
    )


    changed_files = []
    total_replacements = 0


    lesson_files = sorted(
        CONTENT_DIR.glob(
            "lesson-*.md"
        )
    )


    for path in lesson_files:

        original = path.read_text(
            encoding="utf-8",
        )


        revised, count = (
            replace_outside_inventory(
                original,
                replacements,
            )
        )


        if not count:
            continue


        changed_files.append(
            (
                path,
                count,
                revised,
            )
        )

        total_replacements += count


    print()
    print(
        "Lesson files affected:",
        len(changed_files),
    )

    print(
        "URLs replaced:",
        total_replacements,
    )

    print()


    for path, count, _ in changed_files:

        print(
            f"{path.name}: "
            f"{count} replacement(s)"
        )


    if not args.apply:

        print()
        print(
            "Dry run only. "
            "No Markdown files changed."
        )

        print()
        print(
            "Run with --apply to write changes:"
        )

        print()
        print(
            "python3 "
            "scripts/rewrite_course_video_links.py "
            "--apply"
        )

        return


    for path, _, revised in changed_files:

        path.write_text(
            revised,
            encoding="utf-8",
        )


    print()
    print(
        "Markdown updates complete."
    )


if __name__ == "__main__":
    main()