from specs import *

def pf(member, text, recfmt, fields, keys, unique=False):
    L = [AC("**TEXT:" + text), AC(), AC(text), AC("DIST400 foodservice distribution sample  (c) lab kit"), AC()]
    if unique: L.append(A(kw='UNIQUE'))
    L.append(A(rec='R', name=recfmt, kw="TEXT('" + text[:26] + "')"))
    for name, ln, dt, dec, hdg in fields:
        L.append(A(name=name, ln=ln, dt=dt, dec=dec, kw="COLHDG('" + hdg + "')"))
    for k in keys:
        L.append(A(rec='K', name=k))
    save('QDDSSRCF', member + '.pf', L)

pf('CUSTMAST', 'Customer master', 'CUSTMASR', [
    ('CUSTNO', 6, 'S', 0, 'Customer'), ('CNAME', 30, 'A', '', 'Name'), ('CADDR', 30, 'A', '', 'Address'),
    ('CCITY', 20, 'A', '', 'City'), ('CSTATE', 2, 'A', '', 'St'), ('CROUTE', 3, 'S', 0, 'Route'),
    ('CSTOP', 3, 'S', 0, 'Stop'), ('PCLASS', 1, 'A', '', 'Price class'), ('DLVDAY', 7, 'A', '', 'Dlv days'),
    ('CSTAT', 1, 'A', '', 'Status')], ['CUSTNO'], unique=True)
pf('ITEMMAST', 'Item master', 'ITEMMASR', [
    ('ITEMNO', 6, 'S', 0, 'Item'), ('IDESC', 30, 'A', '', 'Description'), ('IPACK', 10, 'A', '', 'Pack/size'),
    ('IBRAND', 10, 'A', '', 'Brand'), ('ICATEG', 3, 'A', '', 'Category'), ('IZONE', 1, 'A', '', 'Zone D/C/F'),
    ('CWFLAG', 1, 'A', '', 'Catch wt'), ('AVGWGT', 7, 'P', 2, 'Avg weight'), ('UNITPK', 5, 'B', 0, 'Units/case'),
    ('SHELFL', 5, 'B', 0, 'Shelf days')], ['ITEMNO'], unique=True)
pf('INVBAL', 'Inventory balance by warehouse', 'INVBALR', [
    ('IWHSE', 2, 'A', '', 'Whse'), ('IITEM', 6, 'S', 0, 'Item'), ('ONHAND', 9, 'B', 0, 'On hand'),
    ('ALLOC', 9, 'B', 0, 'Allocated')], ['IWHSE', 'IITEM'], unique=True)
pf('CONTRACT', 'Customer contract prices', 'CONTRACR', [
    ('CCUST', 6, 'S', 0, 'Customer'), ('CITEM', 6, 'S', 0, 'Item'), ('CPRICE', 7, 'P', 2, 'Contract price'),
    ('CEFFDT', 6, 'S', 0, 'Effective YYMMDD'), ('CEXPDT', 6, 'S', 0, 'Expires YYMMDD')], ['CCUST', 'CITEM', 'CEFFDT'])
pf('PRICELST', 'Price list by price class', 'PRICELSR', [
    ('PITEM', 6, 'S', 0, 'Item'), ('PCLASS', 1, 'A', '', 'Price class'), ('LPRICE', 7, 'P', 2, 'Price')],
    ['PITEM', 'PCLASS'], unique=True)
pf('SUBITEM', 'Substitution items', 'SUBITEMR', [
    ('SITEM', 6, 'S', 0, 'Item'), ('SSUB', 6, 'S', 0, 'Substitute')], ['SITEM'], unique=True)
pf('ORDHDR', 'Order header', 'ORDHDRR', [
    ('ORDNO', 7, 'S', 0, 'Order'), ('OCUST', 6, 'S', 0, 'Customer'), ('ODLVDT', 6, 'S', 0, 'Delivery YYMMDD'),
    ('OROUTE', 3, 'S', 0, 'Route'), ('OSTOP', 3, 'S', 0, 'Stop'), ('OSTAT', 1, 'A', '', 'Status'),
    ('OENTDT', 6, 'S', 0, 'Entered YYMMDD'), ('OENTBY', 10, 'A', '', 'Entered by')], ['ORDNO'], unique=True)
pf('ORDDTL', 'Order detail lines', 'ORDDTLR', [
    ('DORDNO', 7, 'S', 0, 'Order'), ('DLINE', 3, 'S', 0, 'Line'), ('DITEM', 6, 'S', 0, 'Item'),
    ('QTYORD', 5, 'S', 0, 'Qty ordered'), ('QTYSHP', 5, 'S', 0, 'Qty shipped'), ('CWGHT', 7, 'P', 2, 'Catch weight'),
    ('UPRICE', 7, 'P', 2, 'Unit price'), ('PSRC', 1, 'A', '', 'Price source'), ('SUBFLG', 1, 'A', '', 'Sub'),
    ('DOITEM', 6, 'S', 0, 'Orig item')], ['DORDNO', 'DLINE'], unique=True)

# ---- logical files ----
def lf(member, text, recfmt, pfile, fields, keys):
    L = [AC("**TEXT:" + text), AC(), AC(text), AC()]
    L.append(A(rec='R', name=recfmt, kw='PFILE(' + pfile + ')'))
    for fld in fields:
        if len(fld) == 2: L.append(A(name=fld[0], kw=fld[1]))
        elif len(fld) == 1: L.append(A(name=fld[0]))
        else: L.append(A(name=fld[0], ln=fld[1], dt=fld[2], dec=fld[3]))
    for k in keys: L.append(A(rec='K', name=k))
    save('QDDSSRC', member + '.lf', L)

lf('CUSTMSL1', 'Customers by route and stop', 'CUSTMSR1', 'CUSTMAST',
   [('CUSNBR', 'RENAME(CUSTNO)'), ('CNAME',), ('CADDR',), ('CCITY',), ('CSTATE',), ('CROUTE',), ('CSTOP',),
    ('PCLASS',), ('DLVDAY',), ('CSTAT',)], ['CROUTE', 'CSTOP'])
lf('ITEMMSZ', 'Item master, binary fields as zoned', 'ITEMMSZR', 'ITEMMAST',
   [('ITEMNO',), ('IDESC',), ('IPACK',), ('IBRAND',), ('ICATEG',), ('IZONE',), ('CWFLAG',), ('AVGWGT',),
    ('UNITPK', 5, 'S', 0), ('SHELFL', 5, 'S', 0)], ['ITEMNO'])
lf('INVBALZ', 'Inventory balance, binary as zoned', 'INVBALZR', 'INVBAL',
   [('IWHSE',), ('IITEM',), ('ONHAND', 9, 'S', 0), ('ALLOC', 9, 'S', 0)], ['IWHSE', 'IITEM'])
lf('CONTRCL1', 'Contracts by item and customer', 'CONTRACR', 'CONTRACT', [], ['CITEM', 'CCUST'])
lf('ORDHDRL1', 'Orders by delivery date, route, stop', 'ORDHDRR', 'ORDHDR', [], ['ODLVDT', 'OROUTE', 'OSTOP'])
lf('ORDDTLL1', 'Order lines by item', 'ORDDTLR', 'ORDDTL', [], ['DITEM'])

# ---- display files ----
def dspf(member, text, recfmt, title, fkeys, body, msgline=22):
    L = [AC("**TEXT:" + text), AC(), AC(text), AC()]
    L.append(A(kw='DSPSIZ(24 80 *DS3)'))
    for kw in fkeys: L.append(A(kw=kw))
    L.append(A(rec='R', name=recfmt))
    L.append(A(kw='OVERLAY'))
    L.append(A(line=1, pos=2, kw="'DIST400'"))
    L.append(A(line=1, pos=30, kw="'" + title + "'"))
    L.append(A(line=1, pos=70, kw='DATE EDTCDE(Y)'))
    for row in body:
        L.append(A(**row))
    L.append(A(name='SMSG', ln=50, dt='A', use='O', line=msgline, pos=2))
    save('QDDSSRCD', member + '.dspf', L)

def lit(line, pos, text): return dict(line=line, pos=pos, kw="'" + text + "'")
def fld(name, ln, dt, dec, use, line, pos, kw=''):
    # display files: numeric fields use keyboard shift Y (numeric only); S is not valid with EDTCDE
    return dict(name=name, ln=ln, dt=('Y' if dt == 'S' else dt), dec=dec, use=use, line=line, pos=pos, kw=kw)

dspf('OE001DF', 'Order entry screen', 'OE001R1', 'ORDER ENTRY',
     ["CF03(03 'Exit')", "CF06(06 'Accept line')", "CF12(12 'Cancel')"], [
    lit(3, 2, 'Order . . . :'), fld('SORDNO', 7, 'S', 0, 'O', 3, 17, 'EDTCDE(Z)'),
    lit(3, 30, 'Line . . :'), fld('SLINE', 3, 'S', 0, 'O', 3, 41, 'EDTCDE(Z)'),
    lit(5, 2, 'Customer . . :'), fld('SCUST', 6, 'S', 0, 'B', 5, 17), fld('SNAME', 30, 'A', '', 'O', 5, 26),
    lit(7, 2, 'Item . . . . :'), fld('SITEM', 6, 'S', 0, 'B', 7, 17), fld('SIDESC', 30, 'A', '', 'O', 7, 26),
    lit(9, 2, 'Quantity . . :'), fld('SQTY', 5, 'S', 0, 'B', 9, 17),
    lit(9, 30, 'Unit price :'), fld('SPRICE', 7, 'S', 2, 'O', 9, 43, 'EDTCDE(2)'),
    lit(9, 55, 'Source :'), fld('SPSRC', 1, 'A', '', 'O', 9, 64),
    lit(12, 2, 'Enter customer, item and quantity'), lit(13, 2, 'then F6 to accept the line.'),
    lit(23, 2, 'F3=Exit  F6=Accept  F12=Cancel')])

dspf('OE020DF', 'Pick confirm / catch weight entry', 'OE020R1', 'PICK CONFIRM',
     ['CF03', 'CF06', 'CF12'], [
    lit(3, 2, 'Order . . . :'), fld('SORDNO', 7, 'S', 0, 'B', 3, 17),
    lit(3, 30, 'Line . . :'), fld('SLINE', 3, 'S', 0, 'B', 3, 41),
    lit(5, 2, 'Customer . . :'), fld('SNAME', 30, 'A', '', 'O', 5, 17),
    lit(7, 2, 'Item . . . . :'), fld('SITEM', 6, 'S', 0, 'O', 7, 17, 'EDTCDE(Z)'), fld('SIDESC', 30, 'A', '', 'O', 7, 26),
    lit(9, 2, 'Qty to ship  :'), fld('SQTY', 5, 'S', 0, 'O', 9, 17, 'EDTCDE(Z)'),
    lit(11, 2, 'Scale weight :'), fld('SCWGHT', 7, 'S', 2, 'B', 11, 17),
    lit(23, 2, 'F3=Exit  F6=Record wt  F12=Clear')])

dspf('CM001DF', 'Customer maintenance', 'CM001R1', 'CUSTOMER MAINTENANCE',
     ["CF03(03 'Exit')", "CF06(06 'Update')", "CF12(12 'Clear')"], [
    lit(3, 2, 'Customer . . :'), fld('SCUST', 6, 'S', 0, 'B', 3, 17),
    lit(5, 2, 'Name . . . . :'), fld('SNAME', 30, 'A', '', 'B', 5, 17),
    lit(6, 2, 'Address  . . :'), fld('SADDR', 30, 'A', '', 'B', 6, 17),
    lit(7, 2, 'City . . . . :'), fld('SCITY', 20, 'A', '', 'B', 7, 17), fld('SSTATE', 2, 'A', '', 'B', 7, 40),
    lit(9, 2, 'Route/stop . :'), fld('SROUTE', 3, 'S', 0, 'B', 9, 17), fld('SSTOP', 3, 'S', 0, 'B', 9, 22),
    lit(10, 2, 'Price class  :'), fld('SPCLAS', 1, 'A', '', 'B', 10, 17),
    lit(10, 22, 'R=Restaurant S=School H=Health'),
    lit(23, 2, 'Enter=Get  F3=Exit  F6=Update'), lit(23, 34, 'F12=Clear')])

dspf('IN001DF', 'Inventory inquiry', 'IN001R1', 'INVENTORY INQUIRY',
     ["CF03(03 'Exit')"], [
    lit(3, 2, 'Item . . . . :'), fld('SITEM', 6, 'S', 0, 'B', 3, 17), fld('SIDESC', 30, 'A', '', 'O', 3, 26),
    lit(5, 2, 'Zone . . . . :'), fld('SZONE', 1, 'A', '', 'O', 5, 17),
    lit(5, 22, '(D=Dry C=Cooler F=Freezer)'),
    lit(7, 2, 'On hand  . . :'), fld('SONHND', 9, 'S', 0, 'O', 7, 17, 'EDTCDE(Z)'),
    lit(8, 2, 'Allocated  . :'), fld('SALLOC', 9, 'S', 0, 'O', 8, 17, 'EDTCDE(Z)'),
    lit(9, 2, 'Available  . :'), fld('SAVAIL', 9, 'S', 0, 'O', 9, 17, 'EDTCDE(Z)'),
    lit(11, 2, 'Units/case . :'), fld('SUNITP', 5, 'S', 0, 'O', 11, 17, 'EDTCDE(Z)'),
    lit(12, 2, 'Shelf days . :'), fld('SSHELF', 5, 'S', 0, 'O', 12, 17, 'EDTCDE(Z)'),
    lit(23, 2, 'Enter=Inquire   F3=Exit')])

# ---- printer file ----
L = [AC("**TEXT:Route sheet printer file"), AC(), AC('Route sheet printer file'), AC()]
L += [A(rec='R', name='RP010H1', kw='SKIPB(1) SPACEA(2)'),
      A(pos=2, kw="'DIST400'"), A(pos=25, kw="'ROUTE SHEET FOR DELIVERY'"),
      A(name='PDLVDT', ln=6, dt='S', dec=0, use='O', pos=51), A(pos=60, kw="'ROUTE'"),
      A(name='PROUTE', ln=3, dt='S', dec=0, use='O', pos=66, kw='EDTCDE(Z)'),
      A(pos=72, kw="'PAGE'"), A(pos=77, kw='PAGNBR'),
      A(rec='R', name='RP010C1', kw='SPACEB(1)'),
      A(pos=2, kw="'STOP'"), A(name='PSTOP', ln=3, dt='S', dec=0, use='O', pos=7, kw='EDTCDE(Z)'),
      A(pos=12, kw="'CUST'"), A(name='PCUST', ln=6, dt='S', dec=0, use='O', pos=17),
      A(name='PNAME', ln=30, dt='A', use='O', pos=25),
      A(rec='R', name='RP010D1', kw='SPACEB(1)'),
      A(name='PLINE', ln=3, dt='S', dec=0, use='O', pos=5, kw='EDTCDE(Z)'),
      A(name='PITEM', ln=6, dt='S', dec=0, use='O', pos=10),
      A(name='PIDESC', ln=30, dt='A', use='O', pos=18),
      A(pos=50, kw="'ORD'"), A(name='PQTY', ln=5, dt='S', dec=0, use='O', pos=54, kw='EDTCDE(Z)'),
      A(pos=61, kw="'SHP'"), A(name='PSHIP', ln=5, dt='S', dec=0, use='O', pos=65, kw='EDTCDE(Z)'),
      A(name='PSUB', ln=1, dt='A', use='O', pos=72),
      A(rec='R', name='RP010T1', kw='SPACEB(2)'),
      A(pos=2, kw="'TOTAL CASES TO LOAD'"), A(name='PCASES', ln=7, dt='S', dec=0, use='O', pos=24, kw='EDTCDE(Z)')]
save('QDDSSRCD', 'RP010PF.prtf', L)
