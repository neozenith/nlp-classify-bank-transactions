"""Convert textcat annotation from JSONL to spaCy v3 .spacy format."""
# Standard Library
import warnings
from pathlib import Path

# Third Party
import spacy
import srsly
import typer
from spacy.tokens import DocBin


def convert(lang: str, input_path: Path, output_path: Path):
    nlp = spacy.blank(lang)
    db = DocBin()
    for line in srsly.read_jsonl(input_path):
        doc = nlp.make_doc(line["text"])
        doc.cats = line["cats"]
        db.add(doc)
    db.to_disk(output_path)


if __name__ == "__main__":
    typer.run(convert)
