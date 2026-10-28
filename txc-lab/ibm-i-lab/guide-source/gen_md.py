#!/usr/bin/env python3
"""Generate the Markdown edition of the Participant Guide or the Facilitator Guide from lab.md.
It reads lab.md exactly as build2.js does, so the .md says what the .docx says: %par and %fac regions, callouts starting
"!! **FACILITATOR" left out of the participant edition, and the facilitator edition ending at "## Key concept: modes".
Boxes become fenced blocks under the same captions, callouts and checkpoints become quotes, %kv tables become lists
with bold keys, numbered steps keep the numbers Word shows, and page breaks are dropped.
Usage: python3 gen_md.py lab.md "out.md" participant|facilitator
"""
import re, sys
src, out = sys.argv[1], sys.argv[2]
audience = (sys.argv[3] if len(sys.argv) > 3 else 'all').lower()
TOKEN = re.compile(r'(\*\*[^*]+\*\*|`[^`]+`|https?://[^\s)]+)')   # build2.js runs(): bold, code, bare URL
JOIN_STOP = re.compile(r'^(#|\||- |\d+\. |---|!! |\$\$ |>> |== |✓ |\?\? |%kv|%par|%fac|%end)')

def esc(t):  # plain text that must render literally
    t = re.sub(r'\\(?=[!-/:-@\[-`{-~])', r'\\\\', t)   # a backslash before punctuation, as in C:\Users\<you>
    t = re.sub(r'([*`<|])', r'\\\1', t)                  # *ALL, <IP address>
    t = re.sub(r'(?<![A-Za-z0-9])_|_(?![A-Za-z0-9])', r'\\_', t)
    return re.sub(r'&(?=#?\w+;)', r'\\&', t)

def inline(text):
    text, parts, last = text.replace('\\*', '*'), [], 0
    for m in TOKEN.finditer(text):
        t = m.group(0)
        parts.append(esc(text[last:m.start()]))
        if t.startswith('**'): parts.append('**' + esc(t[2:-2]) + '**')
        elif t.startswith('`'): parts.append(t)
        else:
            url = t.rstrip('.,;:')
            parts.append('<' + url + '>' + esc(t[len(url):]))
        last = m.end()
    return ''.join(parts) + esc(text[last:])

def lead(s):  # keep the start of a paragraph or list item from reading as a quote, list or heading
    m = re.match(r'\d+(?=[.)]\s)', s)
    if m: return s[:m.end()] + '\\' + s[m.end():]
    return '\\' + s if re.match(r'(>|[+-]\s|#{1,6}(\s|$))', s) else s

def plain(text):  # what a box shows: the markers build2.js would format, without the markers
    return TOKEN.sub(lambda m: m.group(0)[2:-2] if m.group(0).startswith('**')
                     else m.group(0)[1:-1] if m.group(0).startswith('`') else m.group(0), text.replace('\\*', '*'))

def boxed(caption, text, lang):
    body = plain(text)
    fence = '`' * max(3, 1 + max((len(r) for r in re.findall(r'`+', body)), default=0))
    return f'*{caption}*\n{fence}{lang}\n{body}\n{fence}'

md = open(src, encoding='utf-8').read().split('\n')
blocks = []   # (kind, markdown); list items of one kind are joined without a blank line
i, list_id, counts, in_numbered, kv_next, region = 0, 0, {}, False, False, None
while i < len(md):
    line = md[i]
    if audience == 'facilitator' and line.startswith('## Key concept: modes'): break
    if line.strip() == '%par': region = 'participant'; i += 1; continue
    if line.strip() == '%fac': region = 'facilitator'; i += 1; continue
    if line.strip() == '%end': region = None; i += 1; continue
    if region and audience != 'all' and region != audience: i += 1; continue
    if audience == 'participant' and line.startswith('!! **FACILITATOR'): i += 1; continue
    if not line.strip(): i += 1; continue
    if not re.match(r'\d+\. ', line): in_numbered = False
    i += 1
    if line.startswith('#sub '): blocks.append(('p', '**' + inline(line[5:]) + '**'))
    elif line.startswith('# '): blocks.append(('h', '# ' + inline(line[2:])))
    elif line.startswith('## '): blocks.append(('h', '## ' + inline(line[3:])))
    elif line.startswith('### '): blocks.append(('h', '### ' + inline(line[4:])))
    elif line.strip() == '---': pass                                   # page break: nothing in Markdown
    elif line.strip() == '%kv': kv_next = True
    elif line.startswith('|'):
        rows, i = [], i - 1
        while i < len(md) and md[i].startswith('|'):
            cells = [c.strip() for c in md[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r'-+', c) for c in cells): rows.append(cells)
            i += 1
        if kv_next:
            blocks += [('kv', '- **' + inline(r[0]).replace('**', '') + ':** ' + lead(inline(r[1] if len(r) > 1 else '')))
                       for r in rows]
        else:
            n = len(rows[0])
            fmt = lambda r: '| ' + ' | '.join(inline(c) for c in (r + [''] * n)[:n]) + ' |'
            blocks.append(('table', '\n'.join([fmt(rows[0]), '|' + '---|' * n] + [fmt(r) for r in rows[1:]])))
        kv_next = False
    elif line.startswith('!! '): blocks.append(('quote', '> ' + lead(inline(line[3:]))))
    elif line.startswith('$$ '):
        text = line[3:].strip()
        if re.match(r'https?://', text): blocks.append(('p', '*Open in a browser:* ' + inline(text)))
        else: blocks.append(('box', boxed('Type in the terminal', text, 'sh')))
    elif line.startswith('>> '): blocks.append(('box', boxed('Paste into the Bob chat', line[3:].strip(), 'text')))
    elif line.startswith('== '): blocks.append(('box', boxed('What you should see', line[3:].strip(), 'text')))
    elif line.startswith('✓ '): blocks.append(('quote', '> ✓ ' + lead(inline(line[2:]))))
    elif line.startswith('?? '): blocks.append(('p', '*' + inline(line[3:].strip()) + '*'))
    elif line.startswith('- '): blocks.append(('bullet', '- ' + lead(inline(line[2:]))))
    elif re.match(r'\d+\. ', line):
        if not in_numbered and (line.startswith('1. ') or list_id == 0):
            list_id += 1; counts[list_id] = 0
        in_numbered = True; counts[list_id] += 1
        blocks.append(('number', f'{counts[list_id]}. ' + lead(inline(re.sub(r'^\d+\. ', '', line)))))
    else:
        text = line
        while i < len(md) and md[i].strip() and not JOIN_STOP.match(md[i]):
            text += ' ' + md[i].strip(); i += 1
        blocks.append(('p', lead(inline(text))))

edition = {'participant': 'Participant Guide', 'facilitator': 'Facilitator Guide'}.get(audience, 'combined guide')
res = [f'<!-- {edition}, generated from guide-source/lab.md by gen_md.py. Edit lab.md, not this file. -->']
prev = None
for kind, text in blocks:
    res.append(('\n' if kind == prev and kind in ('bullet', 'number', 'kv') else '\n\n') + text)
    prev = kind
open(out, 'w', encoding='utf-8').write(''.join(res) + '\n')
print(f"{out}: {audience} edition, {len(blocks)} blocks")
