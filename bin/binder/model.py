from typing import ClassVar
from dataclasses import dataclass

## TEXT: Basic strings, might be formatted

@dataclass
class Inline:
    following: "Inline"

@dataclass
class Text(Inline):
    text: str

class BoldText(Text):
    pass

class ItalicText(Text):
    pass

class Equation(Text):
    pass

class Separator(Text):
    # Hidden separator, useful to create some sense of text control
    pass

class BreakLine(Text):
    # A manual // breakline
    pass

class Dots(Text):
    # The ... character
    pass
    
## SECTIONS: Sections and subsections with a numbering

@dataclass
class Label:
    section_index: str 
    id: str
    parent: object = None
    @property
    def label_type(self):
        return self.id.split(':')[0]

    @property
    def label_name(self):
        return self.id.split(':')[-1]

    @property
    def chapter_index(self):
        return self.section_index.split('.')[0]

@dataclass
class Reference(Inline):
    id: str
    _name: str = None

    def name(self, labels):
        if self._name: return self._name
        label = labels.get(self.id)
        if label and label.name: return label.name
        return self.id

@dataclass
class Hyperlink(Reference):
    pass
    
@dataclass
class Section:
    numbering: ClassVar = 'CHAPTERS.SECTIONS'
    index: str
    title: str
    tokens: list

    @property
    def references(self):
        for token in self.tokens:
            if hasattr(token, 'label') and token.label is not None:
                yield token
            elif hasattr(token, 'references'):
                yield from token.references

class Subsection(Section):
    numbering: ClassVar = 'CHAPTERS.SECTIONS.SUBSECTIONS'

class Chapter(Section):
    numbering: ClassVar = 'CHAPTERS'
    is_appendix: bool = False

    @property
    def sections(self):
        for token in self.tokens:
            if isinstance(token, Section) and token.__class__ == Section:
                yield token

@dataclass
class Theorem:
    numbering: ClassVar = 'CHAPTERS.SECTIONS.THEOREMS'
    label_type: ClassVar = 'thm'
    tokens: list[Text]
    index: str
    _name: str = None
    label: Label = None

    @property
    def name(self):
        if self._name: return self._name
        return f"Théorème {self.index}"

class Lemma(Theorem):
    numbering: ClassVar = 'CHAPTERS.SECTIONS.THEOREMS'
    label_type: ClassVar = 'lem'

    @property
    def name(self):
        if self._name: return self._name
        return f"Lemme {self.index}"

class Corollary(Theorem):
    numbering: ClassVar = 'CHAPTERS.SECTIONS.THEOREMS.COROLLARIES'
    label_type: ClassVar = 'cor'
        
    @property
    def name(self):
        if self._name: return self._name
        return f"Corollaire {self.index}"
    

@dataclass
class Explanation:
    tokens: list[Text]

@dataclass
class Proof:
    tokens: list[Text]
    index: str
    _name: str = None
    explanation: Explanation = None
    following: "Proof" = None
    preceding: "Proof" = None

    @property
    def children(self):
        yield self
        if self.following:
            yield from self.following.children

    @property
    def name(self):
        return self._name or "Preuve"

class Example(Proof):
    @property
    def name(self):
        return self._name or "Exemple"
    
@dataclass
class Definition:
    name: str
    tokens: list[Text]
    label: Label = None


@dataclass
class Book:
    id: str
    title: str
    chapters: list[Chapter]

    def previous_index(self, chapter):
        """ Returns the index of the chapter before the referenced chapter """
        previous = None
        for c in self.chapters:
            if c.index == chapter.index:
                return previous
            else:
                previous = c

    def next_index(self, chapter):
        """ Returns the index of the chapter before the referenced chapter """
        found = False
        for c in self.chapters:
            if found: return c
            if c.index == chapter.index:
                found = True
        return None

    @property
    def references(self):
        d = {}
        for chapter in self.chapters:
            for ref in chapter.references:
                d[ref.label.id] = ref
        return d

