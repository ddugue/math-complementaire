from TexSoup import TexSoup

from .utils import pop_or_none, next_or_none, get_or_none
from .model import *
from .numbering import Index


def parse_ref(cls, ref, contents):
    name = None
    if (len(ref.args) > 1):
        name = ref.args[1].string
    return cls(id=str(ref.args[0].string), _name=name)

def parse_text_group(tokens):
    "Take arbitrary tokens and tries to group them for text"
    groups = []
    group = None
    while tokens:
        token = tokens.pop()
        if isinstance(token, Inline):
            if not group:
                group = TextGroup(tokens=[])
            if isinstance(token, Text):
                cls = token.__class__
                splitted = token.text.split('\n\n', 1)
                if len(splitted) > 1:
                    token = cls(text=splitted[0])
                    tokens.append(cls(text=splitted[1]))
            group.tokens.append(token)
        else:
            # Not a text object! We must close the current active group
            if group:
                groups.append(group)
                group = None
            groups.append(token)
    if group:
        groups.append(group)
    return groups


def parse_text(cls, text, contents):
    if text == "\\\\":
        cls = BreakLine
    return cls(text=text)

def parse_label(label, contents):
    return Label(id=str(label.args[0].string), section_index=NUMBERING.value('CHAPTERS.SECTIONS.SUBSECTIONS'))


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
    
    tokens = parse_text_group(parse_content(contents, until=clss))
    section = cls(index=inx, title=title, tokens=tokens)
    
    if isinstance(section, Chapter):
        section.is_appendix = is_appendix
    return section
  

def parse_definition(definition, contents):
    if len(definition.args) == 0:
        print("For this script, definitions must have an argument [DEFINITION] to identify it")
        print("Skipping definition...")
        return
    term = definition.args[0].string
    tokens = parse_content(definition.contents[1:])
    label = None
    for token in tokens:
        if isinstance(token, Label) and token.label_type == 'def':
            label = token
        elif isinstance(token, Label):
            print("Unknown label (don't know how to associate): " + str(token))
    item = Definition(name=term, tokens=list(filter(lambda t: not isinstance(t, Label), tokens)), label=label)
    if label: label.parent = item
    return item

def parse_example_or_proof(cls, example, contents):
    NUMBERING.get('CHAPTERS.SECTIONS.THEOREMS.COROLLARIES').bump()
    inx = NUMBERING.value('CHAPTERS.SECTIONS.THEOREMS.COROLLARIES')
    

    name = get_or_none(example.args, 0)
    if name:
        tokens = parse_content(example.contents[1:])
        name = name.string
    else:
        tokens = parse_content(example.contents)

##########
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
        tokens = parse_content(theorem.contents[1:])
        name = name.string
    else:
        tokens = parse_content(theorem.contents)
    label = None
    for token in tokens:
        if isinstance(token, Label) and token.label_type == cls.label_type:
            label = token
        elif isinstance(token, Label):
            print("Unknown label (don't know how to associate): " + str(token))
    item = cls(tokens=list(filter(lambda t: not isinstance(t, Label), tokens)), index=inx, _name=name, label=label)
    if label: label.parent = item
    return item

def parse_explanation(explanation, contents):
    tokens = parse_content(explanation.contents)
    return Explanation(tokens=tokens)

def parse_list(list, contents):
    tokens = parse_content(list.contents)
    return List(items=tokens)

def parse_item(item, contents):
    tokens = parse_content(contents, until='item')
    return Item(tokens=tokens)

def parse_tokens(token, contents):
    if hasattr(token, "name"):
        match token.name:
            case 'chapter':
                return parse_section([Chapter], token, contents)
            case 'section':
                return parse_section([Chapter, Section], token, contents)
            case 'subsection':
                return parse_section([Chapter, Section, Subsection], token, contents)
            case 'textbf':
                return parse_text(BoldText, token.string, contents)
            case 'textit':
                return parse_text(ItalicText, token.string, contents)
            case '$':
                return parse_text(Equation, str(token), contents)
            case '$$':
                return parse_text(Equation, str(token), contents)
            case 'sep':
                return parse_text(Separator, '', contents)
            case 'dots':
                return parse_text(Dots, '…', contents)
            case 'definition':
                return parse_definition(token, contents)
            case 'proof':
                return parse_example_or_proof(Proof, token, contents)
            case 'example':
                return parse_example_or_proof(Example, token, contents)
            case 'comment':
                return parse_explanation(token, contents)
            case 'theorem':
                return parse_theorem(Theorem, token, contents)
            case 'lemma':
                return parse_theorem(Lemma, token, contents)
            case 'corollary':
                return parse_theorem(Corollary, token, contents)
            case 'label':
                return parse_label(token, contents)
            case 'autoref':
                return parse_ref(Reference, token, contents)
            case 'hyperref':
                return parse_ref(Reference, token, contents)
            case 'href':
                return parse_ref(Hyperlink, token, contents)
            case 'item':
                return parse_item(token, contents)
            case 'itemize':
                return parse_list(token, contents)
            case 'appendix':
                NUMBERING.get('CHAPTERS').change_format(Index.UPPERCASE)
                global IS_APPENDIX
                IS_APPENDIX = True
            case _:
                print(f"Unknown parsing for {token.name}")
    else:
        return parse_text(Text, token, contents)

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
        tokens = parse_content(contents)

        for t in tokens:
            if isinstance(t, Chapter):
                chapters.append(t)
            else:
                raise str(t) + " is not a chapter !! uh uh."
        
    return Book(id=id, title=title, chapters=chapters)

def parse_content(contents, until=None):
    """ Return a list of Model objects for our AST """
    models = []
    
    while True:
        content = pop_or_none(contents)
        peek = get_or_none(contents, 0)
        if content:
            tokens = parse_tokens(content, contents)
            if isinstance(tokens, list):
                models.extend(tokens)
            else:
                models.append(tokens) # Single item
        if peek is None or peek == until:
            break
    return models
