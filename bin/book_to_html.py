#!./var/venv/bin/python

import os
import pprint
import argparse


from jinja2 import Environment, BaseLoader, FileSystemLoader
from binder.model import *
from binder.parser import *
from binder.numbering import *
from binder.utils import *



parser = argparse.ArgumentParser(
                    prog='Latex Book to html',
                    description='Script to try to convert a latex book to our special html')
parser.add_argument('book')
parser.add_argument('--debug', action='store_true')

        
if __name__ == "__main__":
    args = parser.parse_args()
    book = args.book
    if book.endswith('/'):
        book = book[:-1]

    environment = Environment(loader=FileSystemLoader("src/templates"))
    template = environment.get_template("chapter.jinja")
    partial_template = environment.get_template("chapter.partial.jinja")

    book = parse_book(book, f"assets/books/{book}/book.tex")

    for chapter in book.chapters:
        filename = f"dist/books/{book.id}/{slugify(chapter.index)}/index.html"
        if args.debug:
            pp = pprint.PrettyPrinter(indent=1)
            pp.pprint(chapter)
        references = book.references
        # print(references)
        is_text = lambda x: isinstance(x, Inline)
        content = template.render(
            references=references,
            book=book,
            chapter=chapter,
            slug=slugify,
            is_text=is_text,
        )
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, mode="w", encoding="utf-8") as message:
            message.write(content)

        partial_filename = f"dist/books/{book.id}/{slugify(chapter.index)}/index.partial.html"
        
        content = partial_template.render(
            references=references,
            book=book,
            chapter=chapter,
            slug=slugify,
            is_text=is_text,
        )
        os.makedirs(os.path.dirname(partial_filename), exist_ok=True)
        with open(partial_filename, mode="w", encoding="utf-8") as message:
            message.write(content)