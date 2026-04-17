"""Build unprompted variants from template, practices and examples."""

import re
from pathlib import Path


VARIANTS = {
    "mini": "src/examples/mini.md",
    "enacted": "src/examples/enacted.md",
    "original": "src/examples/original.md",
}


def parse_practices(text):
    """Parse numbered entries from practices file, returning a dict keyed by number."""
    entries = {}
    parts = re.split(r"(?m)^(\d+)\. ", text.strip())
    # parts[0] is empty or preamble, then alternating: number, content
    for i in range(1, len(parts), 2):
        number = parts[i]
        content = parts[i + 1].strip()
        entries[number] = content
    return entries


def parse_examples(text):
    """Parse example entries, returning a dict keyed by number.

    Each entry starts with 'NN. For example:' followed by the example content.
    The last entry may include trailing text.
    """
    entries = {}
    parts = re.split(r"(?m)^(\d+)\. For example:\n", text.strip())
    # parts[0] is empty or preamble, then alternating: number, content
    for i in range(1, len(parts), 2):
        number = parts[i]
        content = parts[i + 1].strip()
        entries[number] = content
    return entries


def build_variant(template, practices, examples, output_path):
    """Build a single variant by combining practices with examples."""
    blocks = []
    for number in practices:
        practice_text = practices[number]
        if number in examples:
            practice_text += " For example:\n\n" + examples[number]
        blocks.append(practice_text)

    combined = "\n\n".join(blocks)
    output = template.replace("TODO", combined)

    Path(output_path).write_text(output)
    print(f"Built {output_path}")


def build_combined(template, practices, mini_examples, enacted_examples, output_path):
    """Build combined variant using mini examples as 'Like' and enacted as 'For example'."""
    blocks = []
    for number in practices:
        practice_text = practices[number]
        if number in mini_examples:
            practice_text += " " + mini_examples[number]
        if number in enacted_examples:
            practice_text += " For example:\n\n" + enacted_examples[number]
        blocks.append(practice_text)

    combined = "\n\n".join(blocks)
    output = template.replace("TODO", combined)

    Path(output_path).write_text(output)
    print(f"Built {output_path}")


def build():
    src = Path("src")
    template = (src / "template.md").read_text()
    practices = parse_practices((src / "practices.md").read_text())

    for name, examples_path in VARIANTS.items():
        examples = parse_examples(Path(examples_path).read_text())
        build_variant(template, practices, examples, f"unprompted-{name}.md")

    # Build open variant with practices only, no examples
    build_variant(template, practices, {}, "unprompted-bare.md")

    # Build combined variant using mini (Like) + enacted (For example)
    mini_examples = parse_examples((src / "examples" / "mini.md").read_text())
    enacted_examples = parse_examples((src / "examples" / "enacted.md").read_text())
    build_combined(template, practices, mini_examples, enacted_examples, "unprompted.md")

    # Build SKILL.md by concatenating frontmatter and the enacted variant
    frontmatter = (src / "frontmatter.md").read_text()
    combined = Path("unprompted.md").read_text()
    Path("SKILL.md").write_text(frontmatter + combined)
    print("Built SKILL.md")


if __name__ == "__main__":
    build()
