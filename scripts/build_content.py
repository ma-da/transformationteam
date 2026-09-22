from pathlib import Path

import frontmatter
import markdown

from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
)

import re


RESOURCE_INVENTORY_RE = re.compile(
    r"<!-- RESOURCE-INVENTORY:START -->"
    r".*?"
    r"<!-- RESOURCE-INVENTORY:END -->",
    flags=re.DOTALL,
)


ROOT = Path(__file__).resolve().parents[1]

CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
SITE = ROOT / "src" / "site"


env = Environment(
    loader=FileSystemLoader(TEMPLATES),
    autoescape=select_autoescape(["html"])
)

template = env.get_template("base.html")


def markdown_to_html(text):
    return markdown.markdown(
        text,
        extensions=[
            "extra",
            "sane_lists",
            "smarty",
            "toc",
        ],
    )


def build_page(md_file):

    post = frontmatter.load(md_file)

    metadata = post.metadata

    output_path = SITE / metadata["output"]

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )
    
    public_markdown = (
        RESOURCE_INVENTORY_RE.sub(
            "",
            post.content,
        )
    )

    content_html = markdown_to_html(
        public_markdown
    )

    page_type = metadata.get(
        "page_type",
        "article",
    )

    lesson_number = metadata.get(
        "lesson_number"
    )

    previous_url = None
    next_url = None

    if (
        page_type == "lesson"
        and lesson_number is not None
    ):
        lesson_number = int(
            lesson_number
        )

        if lesson_number == 1:
            previous_url = "/course/index.html"
        else:
            previous_url = (
                f"/course/lesson-{lesson_number - 1}.html"
            )

        if lesson_number == 21:
            next_url = "/course/index.html"
        else:
            next_url = (
                f"/course/lesson-{lesson_number + 1}.html"
            )    

    html = template.render(
        title=metadata["title"],
        description=metadata.get(
            "description",
            ""
        ),
        eyebrow=metadata.get(
            "eyebrow",
            ""
        ),
        page_type=page_type,
        lesson_number=lesson_number,
        previous_url=previous_url,
        next_url=next_url,
        content_html=content_html,
    )

    output_path.write_text(
        html,
        encoding="utf-8"
    )

    print(
        f"Built: "
        f"{output_path.relative_to(ROOT)}"
    )


for md_file in sorted(
    CONTENT.rglob("*.md")
):
    build_page(md_file)