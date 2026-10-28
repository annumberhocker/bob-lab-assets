#!/usr/bin/env python3
"""Generate the 'Prompts and Commands' text file from lab.md, for the room.
It lists what the Participant Guide shows and nothing else: every $$ line (typed in a terminal) and >> line (pasted
into the Bob chat) from "Key concept: modes" onward, skipping %fac regions, grouped under the nearest heading in guide
order, so nobody has to retype a prompt. The facilitator's setup commands are in the Facilitator Guide, not here.
Usage: python3 gen_prompts.py lab.md "out.txt"
"""
import sys
src, out = sys.argv[1], sys.argv[2]
title = "Bob for i, Foodservice Distribution Use Case lab: prompts and commands to paste"
body, heading, started, region = [], None, False, None
for line in open(src, encoding='utf-8').read().split('\n'):
    if not started:
        started = line.startswith('## Key concept: modes')
        if not started: continue
    if line.startswith('%par') or line.startswith('%fac'): region = line[1:4]; continue
    if line.startswith('%end'): region = None; continue
    if region == 'fac': continue
    if line.startswith('## ') or line.startswith('### '):
        heading = line.lstrip('#').strip()
    elif line.startswith('$$ ') or line.startswith('>> '):
        if heading is not None:
            if body: body.append('')
            body += ['-- ' + heading, '']
            heading = None
        body.append(('[terminal] ' if line.startswith('$$') else '[bob] ') + line[3:].strip())
has_term = any(l.startswith('[terminal]') for l in body)
head = [title, "=" * len(title), "Replace nn with your two-digit participant ID everywhere (LABnn, DIST4nn)."]
head.append("Lines marked [terminal] are typed in a terminal window; lines marked [bob] are pasted into the Bob chat." if has_term
            else "Every line is pasted into the Bob chat, in the order the Participant Guide asks for it.")
head += ["", ""]
open(out, 'w', encoding='utf-8').write('\n'.join(head + body) + '\n')
print(f"{out}: {sum(1 for l in body if l.startswith('['))} prompts and commands")
