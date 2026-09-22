from pathlib import Path
import argparse
import json
import shutil


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

AUDIT_JSON = (
    ROOT
    / "data"
    / "course-resource-audit.json"
)

DEST_DIR = (
    ROOT
    / "src"
    / "site"
    / "assets"
    / "video"
    / "course"
)

MAPPING_JSON = (
    ROOT
    / "data"
    / "course-video-migration-map.json"
)


# ============================================================
# HELPERS
# ============================================================

def destination_filename(source_path):
    """
    Keep the original filename structure but normalize
    filename case for predictable Linux/server URLs.

    Examples:

        MOTHERS_EXTRAORDINARY.mp4
        -> mothers_extraordinary.mp4

        MEN-WOMEN-BRAINS.mp4
        -> men-women-brains.mp4
    """

    return source_path.name.lower()


def select_video_match(record):
    """
    Return the unique WTKvideos match for an approved
    migrate-local-video-candidate record.

    If multiple different WTKvideos files match the same
    resource, return None so the record can be reviewed
    manually rather than guessed.
    """

    matches = [
        match
        for match in record.get(
            "local_matches",
            [],
        )
        if match.get("source") == "WTKvideos"
    ]

    # Remove duplicate paths if any.
    unique = {}

    for match in matches:
        unique[
            match["path"]
        ] = match

    matches = list(
        unique.values()
    )

    if len(matches) != 1:
        return None

    return matches[0]


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Copy confirmed Transformation Course videos "
            "from WTKvideos into the new site."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Actually copy files. "
            "Without --apply this is a dry run."
        ),
    )

    args = parser.parse_args()


    if not AUDIT_JSON.exists():
        raise RuntimeError(
            f"Audit file not found: {AUDIT_JSON}"
        )


    records = json.loads(
        AUDIT_JSON.read_text(
            encoding="utf-8",
        )
    )


    candidates = [
        record
        for record in records
        if record.get(
            "suggested_action"
        )
        == "migrate-local-video-candidate"
    ]


    print()
    print("=" * 72)
    print("TRANSFORMATION COURSE VIDEO MIGRATION")
    print("=" * 72)

    print()
    print(
        "Mode:",
        "APPLY" if args.apply else "DRY RUN",
    )

    print(
        "Audit candidates:",
        len(candidates),
    )


    migration_records = []
    skipped = []


    for record in candidates:

        match = select_video_match(
            record
        )

        if not match:

            skipped.append({
                "id":
                    record["id"],

                "source_url":
                    record["source_url"],

                "reason":
                    (
                        "Expected exactly one "
                        "WTKvideos match"
                    ),
            })

            continue


        source = Path(
            match["path"]
        )


        if not source.exists():

            skipped.append({
                "id":
                    record["id"],

                "source_url":
                    record["source_url"],

                "reason":
                    f"Source file missing: {source}",
            })

            continue


        if source.stat().st_size == 0:

            skipped.append({
                "id":
                    record["id"],

                "source_url":
                    record["source_url"],

                "reason":
                    f"Source file is empty: {source}",
            })

            continue


        filename = (
            destination_filename(
                source
            )
        )


        destination = (
            DEST_DIR
            / filename
        )


        new_url = (
            "/assets/video/course/"
            + filename
        )


        migration_records.append({
            "resource_id":
                record["id"],

            "label":
                record["label"],

            "legacy_url":
                record["source_url"],

            "lessons":
                record["lessons"],

            "match_type":
                match["match_type"],

            "source_path":
                str(source),

            "destination_path":
                str(destination),

            "new_url":
                new_url,

            "size_bytes":
                source.stat().st_size,
        })


    # ========================================================
    # COLLISION CHECK
    # ========================================================

    destinations = {}

    for record in migration_records:

        destination = (
            record[
                "destination_path"
            ]
        )

        destinations.setdefault(
            destination,
            [],
        ).append(record)


    collisions = {
        path: items
        for path, items
        in destinations.items()
        if len({
            item["source_path"]
            for item in items
        }) > 1
    }


    if collisions:

        print()
        print(
            "ERROR: destination filename collisions "
            "were detected."
        )

        for path, items in collisions.items():

            print()
            print(path)

            for item in items:
                print(
                    "  ",
                    item["source_path"],
                )

        raise RuntimeError(
            "Resolve filename collisions "
            "before migration."
        )


    # ========================================================
    # SHOW PLAN
    # ========================================================

    print()
    print(
        "Ready to migrate:",
        len(migration_records),
    )

    print(
        "Skipped:",
        len(skipped),
    )


    total_bytes = sum(
        item["size_bytes"]
        for item in migration_records
    )

    print(
        "Total size:",
        f"{total_bytes / 1024 / 1024:.1f} MB",
    )


    print()
    print("-" * 72)


    for record in migration_records:

        lessons = ", ".join(
            str(number)
            for number in record["lessons"]
        )

        print()
        print(
            record["resource_id"],
            f"(lesson(s): {lessons})",
        )

        print(
            "  old:",
            record["legacy_url"],
        )

        print(
            "  src:",
            record["source_path"],
        )

        print(
            "  new:",
            record["new_url"],
        )

        print(
            "  match:",
            record["match_type"],
        )


    # ========================================================
    # SKIPPED
    # ========================================================

    if skipped:

        print()
        print("=" * 72)
        print("SKIPPED")
        print("=" * 72)

        for item in skipped:

            print()
            print(
                item["id"],
                item["source_url"],
            )

            print(
                " ",
                item["reason"],
            )


    # ========================================================
    # DRY RUN ENDS HERE
    # ========================================================

    if not args.apply:

        print()
        print("=" * 72)

        print(
            "Dry run only. "
            "No files were changed."
        )

        print()
        print(
            "Run again with --apply "
            "to perform the copy:"
        )

        print()
        print(
            "python3 "
            "scripts/migrate_course_videos.py "
            "--apply"
        )

        return


    # ========================================================
    # APPLY
    # ========================================================

    DEST_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    copied = 0
    already_present = 0


    for record in migration_records:

        source = Path(
            record["source_path"]
        )

        destination = Path(
            record[
                "destination_path"
            ]
        )


        if destination.exists():

            source_size = (
                source.stat().st_size
            )

            destination_size = (
                destination.stat().st_size
            )


            if (
                source_size
                != destination_size
            ):

                raise RuntimeError(
                    "Destination already exists "
                    "with a different file size:\n"
                    f"{destination}"
                )


            print(
                "EXISTS:",
                destination.name,
            )

            already_present += 1
            continue


        shutil.copy2(
            source,
            destination,
        )

        print(
            "COPIED:",
            destination.name,
        )

        copied += 1


    # ========================================================
    # WRITE MIGRATION MAP
    # ========================================================

    MAPPING_JSON.write_text(
        json.dumps(
            migration_records,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


    print()
    print("=" * 72)
    print("MIGRATION COMPLETE")
    print("=" * 72)

    print()
    print(
        "Copied:",
        copied,
    )

    print(
        "Already present:",
        already_present,
    )

    print(
        "Skipped:",
        len(skipped),
    )

    print()
    print(
        "Video directory:",
        DEST_DIR.relative_to(ROOT),
    )

    print(
        "Migration map:",
        MAPPING_JSON.relative_to(ROOT),
    )


if __name__ == "__main__":
    main()