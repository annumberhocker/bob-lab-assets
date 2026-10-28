# Column-exact emitters for DDS, RPG III (RPG/400) and RPG IV fixed-format source.
KIT = "/Users/ryan/Library/CloudStorage/Box-Box/My Documents/Client Engineering/Deals/Sysco/Bob4i_Labs/DIST400/src"

def put(fields):
    buf = [' '] * 100
    for col, txt in fields:
        for k, ch in enumerate(str(txt)):
            buf[col - 1 + k] = ch
    line = ''.join(buf).rstrip()
    assert len(line) <= 80, "line > 80 cols: " + line
    return line

def save(srcf, member, lines):
    import os
    path = os.path.join(KIT, srcf, member)
    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print("wrote", srcf + "/" + member, len(lines), "lines")

# ---------------- DDS ----------------
def A(name='', ln='', dt='', dec='', use='', line='', pos='', kw='', ind='', rec=''):
    f = [(6, 'A')]
    if ind: f.append((8, ind))                 # 8-10 e.g. ' 03' or 'N03'
    if rec: f.append((17, rec))                # R record, K key
    if name: f.append((19, name))
    if ln != '': f.append((30, str(ln).rjust(5)))
    if dt: f.append((35, dt))
    if dec != '': f.append((36, str(dec).rjust(2)))
    if use: f.append((38, use))
    if line != '': f.append((39, str(line).rjust(3)))
    if pos != '': f.append((42, str(pos).rjust(3)))
    if kw:
        assert len(kw) <= 35, 'DDS keyword too long for one line: ' + kw
        f.append((45, kw))
    return put(f)
def AC(text=''):
    return put([(6, 'A'), (7, '*'), (8, text)])

# ---------------- RPG III ----------------
def F3(name, ftype, desig='F', fmt='E', dev='DISK', keyed=False, ovf='', add=False):
    f = [(6, 'F'), (7, name), (15, ftype), (16, desig), (19, fmt)]
    if keyed: f.append((31, 'K'))
    if ovf: f.append((33, ovf))
    f.append((40, dev))
    if add: f.append((66, 'A'))
    return put(f)
def F3K(opt, entry):                           # continuation line: K at 53, option 54-59, entry 60-
    return put([(6, 'F'), (53, 'K'), (54, opt), (60, entry)])
def I3DS(name='', kind='DS'):                  # data structure header; kind DS or SDS
    f = [(6, 'I')]
    if name: f.append((7, name))
    f.append((18 if kind == 'SDS' else 19, kind))
    return put(f)
def I3SF(frm, to, name, dec='', fmt=''):       # subfield: 43 fmt, 44-47 from, 48-51 to, 52 dec, 53-58 name
    f = [(6, 'I')]
    if fmt: f.append((43, fmt))
    f += [(44, str(frm).rjust(4)), (48, str(to).rjust(4))]
    if dec != '': f.append((52, str(dec)))
    f.append((53, name))
    return put(f)
def C3(f1='', op='', f2='', res='', ln='', dec='', hi='', lo='', eq='', ind='', lvl='', ha=''):
    assert len(f1) <= 10 and len(f2) <= 10 and len(res) <= 6 and len(op) <= 5, (f1, op, f2, res)
    f = [(6, 'C')]
    if lvl: f.append((7, lvl))
    if ind: f.append((9, ind))                 # up to 9 chars: 'N01' ' 02' ...
    if f1: f.append((18, f1))
    if op: f.append((28, op))
    if f2: f.append((33, f2))
    if res: f.append((43, res))
    if ln != '': f.append((49, str(ln).rjust(3)))
    if dec != '': f.append((52, str(dec)))
    if ha: f.append((53, ha))
    if hi: f.append((54, hi))
    if lo: f.append((56, lo))
    if eq: f.append((58, eq))
    return put(f)
def CC(text=''):
    return put([(6, 'C'), (7, '*'), (8, text)])
def H3(text=''):
    return put([(6, 'H'), (7, '*'), (8, text)]) if text else put([(6, 'H')])

# ---------------- RPG IV fixed ----------------
def F4(name, ftype, desig='F', fmt='E', dev='DISK', keyed=False, kw=''):
    f = [(6, 'F'), (7, name), (17, ftype), (18, desig), (22, fmt)]
    if keyed: f.append((34, 'K'))
    f.append((36, dev))
    if kw: f.append((44, kw))
    return put(f)
def D4(name, dstype='', frm='', to='', dt='', dec='', kw=''):
    f = [(6, 'D'), (7, name)]
    if dstype: f.append((24, dstype))
    if frm != '': f.append((26, str(frm).rjust(7)))
    if to != '': f.append((33, str(to).rjust(7)))
    if dt: f.append((40, dt))
    if dec != '': f.append((41, str(dec).rjust(2)))
    if kw: f.append((44, kw))
    return put(f)
def C4(f1='', op='', f2='', res='', ln='', dec='', hi='', lo='', eq='', ind=''):
    f = [(6, 'C')]
    if ind: f.append((9, ind))
    if f1: f.append((12, f1))
    if op: f.append((26, op))
    if f2: f.append((36, f2))
    if res: f.append((50, res))
    if ln != '': f.append((64, str(ln).rjust(5)))
    if dec != '': f.append((69, str(dec).rjust(2)))
    if hi: f.append((71, hi))
    if lo: f.append((73, lo))
    if eq: f.append((75, eq))
    return put(f)
def C4C(text=''):
    return put([(6, 'C'), (7, '*'), (8, text)])

def E3(name, per=1, entries=10, length=50):   # compile-time array
    return put([(6, 'E'), (27, name), (33, str(per).rjust(3)), (36, str(entries).rjust(4)), (40, str(length).rjust(3))])
def HC(text=''):
    return put([(6, 'H'), (7, '*'), (8, text)])

def IC(text=''):
    return put([(6, 'I'), (7, '*'), (8, text)])
