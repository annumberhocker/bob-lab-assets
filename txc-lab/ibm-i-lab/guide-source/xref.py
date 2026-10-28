# Static cross-reference check for the generated RPG III source: every name used in a C-spec
# must be a DDS field of a file the program declares, a field defined with a length in the
# program, an indicator/special word, a literal, a number, or a label/subroutine/key list.
import os, re, glob
SRC = "/Users/ryan/Library/CloudStorage/Box-Box/My Documents/Client Engineering/Deals/Sysco/Bob4i_Labs/DIST400/src"
# collect DDS fields per file (PF/LF/DSPF/PRTF), LF inherits PF fields unless it lists its own
def dds_fields(path):
    names, listed = [], False
    pfile = None
    for ln in open(path):
        ln = ln.rstrip('\n').ljust(80)
        if ln[5] != 'A' or ln[6] == '*': continue
        kw = ln[44:].strip()
        m = re.match(r'PFILE\((\w+)\)', kw)
        if m: pfile = m.group(1)
        name = ln[18:28].strip()
        if name and ln[16] == ' ': names.append(name); listed = True
    return names, pfile, listed
fields = {}
for d, ext in [('QDDSSRCF', 'pf'), ('QDDSSRCD', 'dspf'), ('QDDSSRCD', 'prtf')]:
    for p in glob.glob(f"{SRC}/{d}/*.{ext}"):
        fields[os.path.basename(p).split('.')[0]] = dds_fields(p)[0]
for p in glob.glob(f"{SRC}/QDDSSRC/*.lf"):
    names, pfile, listed = dds_fields(p)
    fields[os.path.basename(p).split('.')[0]] = names if listed else fields[pfile]
rec_names = set()
for p in glob.glob(f"{SRC}/QDDS*/*.*"):
    for ln in open(p):
        ln = ln.ljust(80)
        if ln[5] == 'A' and ln[16] == 'R': rec_names.add(ln[18:28].strip())
SPECIAL = {'*ENTRY', '*BLANKS', '*HIVAL', '*LOVAL', '*ZEROS', '*OFF', '*ON', 'UYEAR', 'UMONTH', 'UDAY', 'UDATE'}
OPS_NAME_F2 = {'EXSR', 'GOTO', 'CALL', 'EXFMT', 'WRITE', 'UPDAT', 'CHAIN', 'READE', 'SETLL', 'SETGT', 'READP', 'READ', 'TAG', 'BEGSR', 'ENDSR', 'KLIST', 'PLIST'}
problems = 0
for p in sorted(glob.glob(f"{SRC}/QRPGSRC/*.rpg")):
    pgm = os.path.basename(p).split('.')[0]
    lines = [l.rstrip('\n').ljust(80) for l in open(p)]
    files, defined, labels, used = [], set(), set(), []
    for ln in lines:
        if ln[6] == '*': continue
        if ln[5] == 'F' and ln[6:14].strip(): files.append(ln[6:14].strip())
        if ln[5] == 'I' and ln[52:58].strip(): defined.add(ln[52:58].strip())
        if ln[5] == 'I' and ln[18:20] == 'DS' and ln[6:12].strip(): defined.add(ln[6:12].strip())
        if ln[5] == 'E': defined.add(ln[26:32].strip())
        if ln[5] == 'C':
            f1, op, f2, res, length = ln[17:27].strip(), ln[27:32].strip(), ln[32:42].strip(), ln[42:48].strip(), ln[48:51].strip()
            if res and length: defined.add(res)
            if op in ('TAG', 'BEGSR', 'KLIST', 'PLIST', 'ENDSR') and f1: labels.add(f1)
            for tok, where in ((f1, 'f1'), (f2, 'f2'), (res, 'res')):
                if not tok: continue
                if where == 'f2' and op in OPS_NAME_F2: continue
                if tok.startswith("'") or tok.startswith("X'") or tok.startswith('*IN') or tok in SPECIAL: continue
                if re.match(r'^-?[\d.]+$', tok): continue
                if ',' in tok: tok = tok.split(',')[0]
                used.append((tok, op, ln.strip()))
    avail = set(defined)
    for f in files:
        if f in fields: avail |= set(fields[f])
        else: print(f"{pgm}: F-spec file {f} has no DDS"); problems += 1
    for tok, op, ln in used:
        if tok not in avail and tok not in labels:
            print(f"{pgm}: undefined name {tok!r} in: {ln}"); problems += 1
    # record formats referenced by WRITE/UPDAT/EXFMT must exist
    for ln in lines:
        if ln[5] == 'C' and ln[27:32].strip() in ('WRITE', 'UPDAT', 'EXFMT'):
            r = ln[32:42].strip()
            if r not in rec_names: print(f"{pgm}: unknown record format {r}"); problems += 1
    print(f"{pgm}: files={files} ok" if not problems else f"{pgm}: checked")
print("PROBLEMS:", problems)
