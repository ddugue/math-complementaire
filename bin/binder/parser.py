from TexSoup import TexSoup

from .utils import pop_or_none, next_or_none, get_or_none
from .model import *
from .numbering import Index


def parse_until(cls, contents):
    tokens = []
    remainder = []
    while True:
        content = pop_or_none(contents)
        generated_tokens = parse_token(content, contents)
        found = False
        for token in generated_tokens:
            if found:
                remainder.append(token)
            else:
                for c in cls:
                    if token.__class__ == c:
                        found = True
                        remainder.append(token)
                if not found:
                    tokens.append(token)
        if content is None:
            break
    return (tokens, remainder)


def parse_ref(cls, ref, contents):
    name = None
    if (len(ref.args) > 1):
        name = ref.args[1].string
    following = parse_token(pop_or_none(contents), contents)
    n = next_or_none(following)
    if n and isinstance(n, Inline):
        yield cls(id=str(ref.args[0].string), _name=name, following=n)
    else:
        yield cls(id=str(ref.args[0].string), _name=name, following=None)
        if n:
            yield n
    yield from following

def parse_text(cls, text, contents):
    following = parse_token(pop_or_none(contents), contents)
    if text == "\\\\":
        cls = BreakLine
    n = next_or_none(following)
    next_text = None
    if n and isinstance(n, Inline):
        next_text = n

    splitted = text.split('\n\n')
    for i in range(0, len(splitted)):
        if i == len(splitted) - 1:
            #Last
            yield cls(text=splitted[i], following=next_text)
        else:
            yield cls(text=splitted[i], following=None)
    if n and not next_text:
        yield n
    yield from following

def parse_label(label, contents):
    yield Label(id=str(label.args[0].string), section_index=NUMBERING.value('CHAPTERS.SECTIONS.SUBSECTIONS'))


NUMBERING = Index({ 
    'CHAPTERS': Index({ 
        'SECTIONS': Index({
            'SUBSECTIONS': Index(),
            'THEOREMS': Index({ 
                'COROLLARIES': Index(),
            }),
        })
    })
})
IS_APPENDIX = False

def parse_section(clss, section, contents):
    title = section.string
    cls = clss[-1] # We assume the actual token class is the last separator
    NUMBERING.get(cls.numbering).bump()
    inx = NUMBERING.value(cls.numbering)
    is_appendix = IS_APPENDIX
    
    tokens, next_tokens = parse_until(clss, contents)
    section = cls(index=inx, title=title, tokens=tokens)
    
    if isinstance(section, Chapter):
        section.is_appendix = is_appendix
        print(section.is_appendix)
    yield section
    yield from next_tokens
  

def parse_definition(definition, contents):
    if len(definition.args) == 0:
        print("For this script, definitions must have an argument [DEFINITION] to identify it")
        print("Skipping definition...")
        return
    term = definition.args[0].string
    tokens, _ = parse_until([], definition.contents[1:])
    label = None
    for token in tokens:
        if isinstance(token, Label) and token.label_type == 'def':
            label = token
        elif isinstance(token, Label):
            print("Unknown label (don't know how to associate): " + str(token))
    item = Definition(name=term, tokens=list(filter(lambda t: not isinstance(t, Label), tokens)), label=label)
    if label: label.parent = item
    yield item

def parse_example_or_proof(cls, example, contents):
    NUMBERING.get('CHAPTERS.SECTIONS.THEOREMS.COROLLARIES').bump()
    inx = NUMBERING.value('CHAPTERS.SECTIONS.THEOREMS.COROLLARIES')
    

    name = get_or_none(example.args, 0)
    if name:
        tokens, _ = parse_until([], example.contents[1:])
        name = name.string
    else:
        tokens, _ = parse_until([], example.contents)

    next_tokens = parse_token(pop_or_none(contents), contents)
    n = next_or_none(next_tokens)

    if n and n.__class__ == cls:
        # No Explanation but a following example
        item = cls(tokens=tokens, index=inx, _name=name, following=n)
        n.preceding = item
        yield item
    elif isinstance(n, Explanation):
        # An explanation, we need to check the following one too
        nn = next_or_none(next_tokens)
        if not nn:
            next_tokens = parse_token(pop_or_none(contents), contents)
            nn = next_or_none(next_tokens)
        if nn.__class__ == cls:
            item = cls(tokens=tokens, index=inx, _name=name, explanation=n, following=nn)
            nn.preceding = item
            yield item
        else:
            yield cls(tokens=tokens, index=inx, _name=name, explanation=n)
            if nn: yield nn       
    else:
        yield cls(tokens=tokens, index=inx, _name=name)
        if n: yield n # N exists, but is not an explanation or a following proof/example
    yield from next_tokens

def parse_theorem(cls, theorem, contents):
    NUMBERING.get(cls.numbering).bump()
    inx = NUMBERING.value(cls.numbering)

    name = get_or_none(theorem.args, 0)
    if name:
        tokens, _ = parse_until([], theorem.contents[1:])
        name = name.string
    else:
        tokens, _ = parse_until([], theorem.contents)
    label = None
    for token in tokens:
        if isinstance(token, Label) and token.label_type == cls.label_type:
            label = token
        elif isinstance(token, Label):
            print("Unknown label (don't know how to associate): " + str(token))
    item = cls(tokens=list(filter(lambda t: not isinstance(t, Label), tokens)), index=inx, _name=name, label=label)
    if label: label.parent = item
    yield item

def parse_explanation(explanation, contents):
    tokens, _ = parse_until([], explanation.contents)
    yield Explanation(tokens=tokens)

def parse_token(token, contents):
    if token is None:
        return
    if hasattr(token, "name"):
        match token.name:
            case 'chapter':
                yield from parse_section([Chapter], token, contents)
            case 'section':
                yield from parse_section([Chapter, Section], token, contents)
            case 'subsection':
                yield from parse_section([Chapter, Section, Subsection], token, contents)
            case 'textbf':
                yield from parse_text(BoldText, token.string, contents)
            case 'textit':
                yield from parse_text(ItalicText, token.string, contents)
            case '$':
                yield from parse_text(Equation, str(token), contents)
            case '$$':
                yield from parse_text(Equation, str(token), contents)
            case 'sep':
                yield from parse_text(Separator, '', contents)
            case 'dots':
                yield from parse_text(Dots, '…', contents)
            case 'definition':
                yield from parse_definition(token, contents)
            case 'proof':
                yield from parse_example_or_proof(Proof, token, contents)
            case 'example':
                yield from parse_example_or_proof(Example, token, contents)
            case 'comment':
                yield from parse_explanation(token, contents)
            case 'theorem':
                yield from parse_theorem(Theorem, token, contents)
            case 'lemma':
                yield from parse_theorem(Lemma, token, contents)
            case 'corollary':
                yield from parse_theorem(Corollary, token, contents)
            case 'label':
                yield from parse_label(token, contents)
            case 'autoref':
                yield from parse_ref(Reference, token, contents)
            case 'hyperref':
                yield from parse_ref(Reference, token, contents)
            case 'href':
                yield from parse_ref(Hyperlink, token, contents)
            case 'appendix':
                NUMBERING.get('CHAPTERS').change_format(Index.UPPERCASE)
                global IS_APPENDIX
                IS_APPENDIX = True
            case _:
                print(f"Unknown parsing for {token.name}")
    else:
        yield from parse_text(Text, token, contents)

def parse_book(id, filename):
    chapters = []
    title = "Livre Sans Nom"
    global IS_APPENDIX
    IS_APPENDIX = False

    with open(filename, mode="r", encoding="utf-8") as f:
        txt = f.read()
        soup = TexSoup(txt)

        title_tag = soup.find('title')
        title = title_tag.string if title_tag else "Livre Sans Nom"

        contents = soup.document.contents
        tokens, _ = parse_until([], contents)

        for t in tokens:
            if isinstance(t, Chapter):
                chapters.append(t)
            else:
                raise str(t) + " is not a chapter !! uh uh."
        
    return Book(id=id, title=title, chapters=chapters)