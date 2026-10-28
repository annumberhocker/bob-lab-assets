from specs import *

MSGS = ['CUSTOMER NOT FOUND', 'ITEM NOT FOUND', 'LINE ADDED - ENTER NEXT ITEM OR F3 TO EXIT', 'ORDER CANCELLED',
        'ENTER QUANTITY', 'ITEM NOT PRICED', 'WEIGHT RECORDED', 'ORDER LINE NOT FOUND', 'CUSTOMER UPDATED', 'CUSTOMER ADDED']
def msgdata():
    return ['**'] + [m.ljust(50) for m in MSGS]
def header(text, lines):
    L = [HC('**TEXT:' + text), HC()]
    L += [HC(x) for x in lines]
    L.append(HC())
    return L
KEYDS = [I3DS('KEYDS'), I3SF(1, 6, 'CUST#', 0)]
LRRET = [C3(op='SETON', hi='LR'), C3(op='RETRN')]
def c(*a, **k): return C3(*a, **k)

# =================================================================== OE005
L = header('Price lookup - contract/class/list', [
    ' OE005  - PRICE LOOKUP                           DKOWALSKI  03/12/98',
    ' CALLED BY OE001 FOR EVERY ORDER LINE.',
    ' RETURNS UNIT PRICE AND SOURCE: C=CONTRACT P=PRICE CLASS L=LIST',
    '                                X=ITEM NOT FOUND',
    ' MOD 11/02/99 DK  DATE WINDOW FOR Y2K, SEE WINDOW SUBR',
    ' MOD 06/15/01 TM  SCHOOL DISCOUNT PER R.MARTIN (NO TICKET)'])
L += [F3('CUSTMAST', 'I', keyed=True), F3('ITEMMAST', 'I', keyed=True), F3('CONTRACT', 'I', keyed=True), F3('PRICELST', 'I', keyed=True)]
L += KEYDS
L += [IC(' PARMS LIVE IN A DS SO THEY ARE ZONED. C-SPEC FIELDS ARE PACKED AND'),
      IC(' THE SCREENS AND CL PASS ZONED DIGITS.                    DK 03/12/98'),
      IC(' AN *ENTRY PARM CANNOT BE A DS SUBFIELD, SO EACH PARM IS ITS OWN DS.'),
      I3DS('PCUSTD'), I3SF(1, 6, 'WCUST', 0), I3DS('PITEMD'), I3SF(1, 6, 'WITEM', 0),
      I3DS('PQTYD'), I3SF(1, 5, 'WQTY', 0), I3DS('PDATED'), I3SF(1, 6, 'WDATE', 0),
      I3DS('PPRICD'), I3SF(1, 7, 'WPRICE', 2)]
L += [c('*ENTRY', 'PLIST'), c(op='PARM', res='PCUSTD'), c(op='PARM', res='PITEMD'),
      c(op='PARM', res='PQTYD'), c(op='PARM', res='PDATED'),
      c(op='PARM', res='PPRICD'), c(op='PARM', res='WSRC', ln=1),
      c('CTKEY', 'KLIST'), c(op='KFLD', res='WCUST'), c(op='KFLD', res='WITEM'),
      c('PLKEY', 'KLIST'), c(op='KFLD', res='WITEM'), c(op='KFLD', res='PCLASS'),
      CC(),
      c(op='Z-ADD', f2='0', res='WPRICE'), c(op='MOVE', f2="' '", res='WSRC'), c(op='MOVE', f2="'0'", res='WCLASS', ln=1),
      c(op='Z-ADD', f2='WCUST', res='CUST#'),
      c('CUST#', 'CHAIN', 'CUSTMAST', hi='90'),
      c(op='MOVE', f2='PCLASS', res='WCLASS', ind='N90'),
      c('WITEM', 'CHAIN', 'ITEMMAST', hi='91'),
      c(op='MOVE', f2="'X'", res='WSRC', ind=' 91'),
      c(op='GOTO', f2='DONE', ind=' 91'),
      CC(' WINDOW THE ORDER DATE SO 00-49 COMPARES AFTER 98'),
      c(op='Z-ADD', f2='WDATE', res='WDTIN', ln=6, dec=0), c(op='EXSR', f2='WINDOW'), c(op='Z-ADD', f2='WDTOUT', res='WORDDT', ln=7, dec=0),
      CC(' 1. CONTRACT PRICE IN EFFECT ON THE ORDER DATE'),
      c('CTKEY', 'SETLL', 'CONTRACT'), c('CTKEY', 'READE', 'CONTRACT', eq='92'),
      c('*IN92', 'DOWEQ', "'0'"), c('WSRC', 'ANDEQ', "' '"),
      c(op='Z-ADD', f2='CEFFDT', res='WDTIN'), c(op='EXSR', f2='WINDOW'), c(op='Z-ADD', f2='WDTOUT', res='WEFF', ln=7, dec=0),
      c(op='Z-ADD', f2='CEXPDT', res='WDTIN'), c(op='EXSR', f2='WINDOW'), c(op='Z-ADD', f2='WDTOUT', res='WEXP', ln=7, dec=0),
      c('WORDDT', 'IFGE', 'WEFF'), c('WORDDT', 'ANDLE', 'WEXP'),
      c(op='Z-ADD', f2='CPRICE', res='WPRICE'), c(op='MOVE', f2="'C'", res='WSRC'),
      c(op='END'),
      c('CTKEY', 'READE', 'CONTRACT', eq='92'),
      c(op='END'),
      CC(' 2. PRICE CLASS PRICE   3. LIST PRICE (CLASS 0)'),
      c('WSRC', 'IFEQ', "' '"),
      c(op='MOVE', f2='WCLASS', res='PCLASS'),
      c('PLKEY', 'CHAIN', 'PRICELST', hi='93'),
      c('*IN93', 'IFEQ', "'0'"),
      c(op='Z-ADD', f2='LPRICE', res='WPRICE'), c(op='MOVE', f2="'P'", res='WSRC'),
      c(op='ELSE'),
      c(op='MOVE', f2="'0'", res='PCLASS'),
      c('PLKEY', 'CHAIN', 'PRICELST', hi='94'),
      c('*IN94', 'IFEQ', "'0'"),
      c(op='Z-ADD', f2='LPRICE', res='WPRICE'), c(op='MOVE', f2="'L'", res='WSRC'),
      c(op='END'),
      c(op='END'),
      CC(' SCHOOLS GET 2 PCT OFF ANYTHING NOT ON CONTRACT  (TM 06/01)'),
      c('WCLASS', 'IFEQ', "'S'"), c('WSRC', 'ANDNE', "' '"),
      c(op='MULT', f2='.98', res='WPRICE', ha='H'),
      c(op='END'),
      c(op='END'),
      CC(' CATCH WEIGHT ITEMS ARE PRICED PER LB - CONVERT TO PER CASE'),
      c('CWFLAG', 'IFEQ', "'Y'"), c('WSRC', 'ANDNE', "' '"),
      c(op='MULT', f2='AVGWGT', res='WPRICE', ha='H'),
      c(op='END'),
      c('DONE', 'TAG')] + LRRET + [
      CC(' Y2K WINDOW: YY UNDER 50 IS 20YY. ADD 1000000 SO 26 SORTS AFTER 98'),
      c('WINDOW', 'BEGSR'),
      c(op='Z-ADD', f2='WDTIN', res='WDTOUT', ln=7, dec=0),
      c('WDTIN', 'IFLT', '500000'),
      c(op='ADD', f2='1000000', res='WDTOUT'),
      c(op='END'),
      c(op='ENDSR')]
save('QRPGSRC', 'OE005.rpg', L)

# =================================================================== OE010
L = header('Allocate order lines and substitute', [
    ' OE010  - ALLOCATE ORDER LINES / SUBSTITUTE      DKOWALSKI  04/02/98',
    ' CALLED WITH ORDER NUMBER BY OE001 (RELEASE) AND OE011 (CUTOFF).',
    ' TAKES STOCK FROM WHSE 01. IF SHORT, TRIES THE SUBSTITUTE ITEM.',
    ' LINES WITH QTYSHP ALREADY SET ARE SKIPPED SO A RERUN IS SAFE.'])
L += [F3('ORDDTL', 'U', keyed=True), F3('INVBALZ', 'U', keyed=True), F3('SUBITEM', 'I', keyed=True), F3('ORDHDR', 'U', keyed=True)]
L += [I3DS('PORDD'), I3SF(1, 7, 'WORDNO', 0)]
L += [c('*ENTRY', 'PLIST'), c(op='PARM', res='PORDD'),
      c('DTKEY', 'KLIST'), c(op='KFLD', res='WORDNO'),
      c('IVKEY', 'KLIST'), c(op='KFLD', res='WWHSE'), c(op='KFLD', res='WIITEM'),
      c(op='MOVE', f2="'01'", res='WWHSE', ln=2), c(op='Z-ADD', f2='0', res='WIITEM', ln=6, dec=0),
      c('DTKEY', 'SETLL', 'ORDDTL'), c('DTKEY', 'READE', 'ORDDTL', eq='80'),
      c('*IN80', 'DOWEQ', "'0'"),
      CC(' SKIP LINES ALREADY ALLOCATED - THIS IS WHAT MAKES A RERUN SAFE'),
      c('QTYSHP', 'IFEQ', '0'),
      c(op='Z-ADD', f2='DITEM', res='WIITEM'), c(op='EXSR', f2='GETQTY'),
      c('WALLOC', 'IFEQ', '0'),
      c('DITEM', 'CHAIN', 'SUBITEM', hi='81'),
      c('*IN81', 'IFEQ', "'0'"),
      c(op='Z-ADD', f2='SSUB', res='WIITEM'), c(op='EXSR', f2='GETQTY'),
      c('WALLOC', 'IFNE', '0'),
      c(op='Z-ADD', f2='DITEM', res='DOITEM'), c(op='Z-ADD', f2='SSUB', res='DITEM'), c(op='MOVE', f2="'Y'", res='SUBFLG'),
      c(op='END'), c(op='END'), c(op='END'),
      c(op='Z-ADD', f2='WALLOC', res='QTYSHP'), c(op='UPDAT', f2='ORDDTLR'),
      c(op='END'),
      c('DTKEY', 'READE', 'ORDDTL', eq='80'),
      c(op='END'),
      CC(' MARK THE ORDER ALLOCATED'),
      c('WORDNO', 'CHAIN', 'ORDHDR', hi='82'),
      c(op='MOVE', f2="'A'", res='OSTAT', ind='N82'), c(op='UPDAT', f2='ORDHDRR', ind='N82')] + LRRET + [
      CC(' GETQTY: TAKE WHAT WHSE 01 HAS FOR WIITEM, RETURN WALLOC'),
      c('GETQTY', 'BEGSR'),
      c(op='Z-ADD', f2='0', res='WALLOC', ln=5, dec=0),
      c('IVKEY', 'CHAIN', 'INVBALZ', hi='83'),
      c('*IN83', 'IFEQ', "'0'"),
      c('ONHAND', 'SUB', 'ALLOC', 'WAVAIL', ln=9, dec=0),
      c('WAVAIL', 'IFGE', 'QTYORD'),
      c(op='Z-ADD', f2='QTYORD', res='WALLOC'),
      c(op='ELSE'),
      c('WAVAIL', 'IFGT', '0'),
      c(op='Z-ADD', f2='WAVAIL', res='WALLOC'),
      c(op='END'), c(op='END'),
      c('WALLOC', 'IFGT', '0'),
      c(op='ADD', f2='WALLOC', res='ALLOC'), c(op='UPDAT', f2='INVBALZR'),
      c(op='END'), c(op='END'),
      c(op='ENDSR')]
save('QRPGSRC', 'OE010.rpg', L)

# =================================================================== OE011
L = header('Cutoff driver - allocate all open orders', [
    ' OE011  - NIGHTLY CUTOFF DRIVER                  DKOWALSKI  04/02/98',
    ' CALLED BY ORDCUTOF WITH THE DELIVERY DATE (YYMMDD).',
    ' CALLS OE010 FOR EVERY OPEN ORDER ON THAT DATE.'])
L += [F3('ORDHDRL1', 'I', keyed=True)]
L += [IC(' NUMERIC FILE FIELDS ARE PACKED INSIDE THE PROGRAM. OE010 WANTS A ZONED'),
      IC(' ORDER NUMBER, SO IT GOES THROUGH A DS BEFORE THE CALL.     DK 04/02/98'),
      I3DS('PDATED'), I3SF(1, 6, 'WDLVDT', 0), I3DS('PORDD'), I3SF(1, 7, 'WORDNO', 0)]
L += [c('*ENTRY', 'PLIST'), c(op='PARM', res='PDATED'),
      c('HDKEY', 'KLIST'), c(op='KFLD', res='WDLVDT'),
      c('HDKEY', 'SETLL', 'ORDHDRL1'), c('HDKEY', 'READE', 'ORDHDRL1', eq='80'),
      c('*IN80', 'DOWEQ', "'0'"),
      c('OSTAT', 'IFEQ', "'O'"),
      c(op='Z-ADD', f2='ORDNO', res='WORDNO'),
      c(op='CALL', f2="'OE010'"), c(op='PARM', res='PORDD'),
      c(op='END'),
      c('HDKEY', 'READE', 'ORDHDRL1', eq='80'),
      c(op='END')] + LRRET
save('QRPGSRC', 'OE011.rpg', L)

# =================================================================== OE001
L = header('Order entry', [
    ' OE001  - ORDER ENTRY                            DKOWALSKI  03/09/98',
    ' ONE LINE AT A TIME. ENTER PRICES THE LINE VIA OE005, F6 ADDS IT.',
    ' FIRST ACCEPTED LINE CREATES THE ORDER HEADER.'])
L += [F3('OE001DF', 'C', dev='WORKSTN'), F3('CUSTMAST', 'I', keyed=True), F3('ITEMMAST', 'I', keyed=True),
      F3('ORDHDR', 'U', keyed=True, add=True), F3('ORDDTL', 'O', desig=' ')]
L += [E3('MSG')]
L += KEYDS + [IC(' OE005 WANTS ZONED PARMS. SCREEN FIELDS ARE PACKED INSIDE THE PROGRAM,'),
      IC(' SO THEY ARE STAGED IN THESE DS FIELDS AROUND THE CALL.      DK 03/09/98'),
      I3DS('PCUSTD'), I3SF(1, 6, 'WCUST', 0), I3DS('PITEMD'), I3SF(1, 6, 'WITEM', 0),
      I3DS('PQTYD'), I3SF(1, 5, 'WQTY', 0), I3DS('PPRICD'), I3SF(1, 7, 'WPRICE', 2),
      I3DS('TODAYD'), I3SF(1, 6, 'WTODAY', 0), I3DS(kind='SDS'), I3SF(254, 263, 'WUSER')]
L += [CC(' TODAY AS YYMMDD'),
      c(op='Z-ADD', f2='UYEAR', res='WTODAY'), c(op='MULT', f2='10000', res='WTODAY'),
      c(op='Z-ADD', f2='UMONTH', res='WK', ln=4, dec=0), c(op='MULT', f2='100', res='WK'),
      c(op='ADD', f2='WK', res='WTODAY'), c(op='ADD', f2='UDAY', res='WTODAY'),
      c(op='Z-ADD', f2='0', res='SORDNO'), c(op='Z-ADD', f2='0', res='SLINE'),
      c('*IN03', 'DOWEQ', "'0'"),
      c(op='EXFMT', f2='OE001R1'),
      c(op='MOVE', f2='*BLANKS', res='SMSG'),
      c('*IN03', 'IFEQ', "'0'"),
      c('*IN12', 'IFEQ', "'1'"),
      c(op='EXSR', f2='RESET'),
      c(op='ELSE'),
      c(op='EXSR', f2='LINE'),
      c(op='END'), c(op='END'), c(op='END')] + LRRET + [
      CC(' LINE: VALIDATE, PRICE, AND ON F6 WRITE THE DETAIL'),
      c('LINE', 'BEGSR'),
      c(op='Z-ADD', f2='SCUST', res='CUST#'),
      c('CUST#', 'CHAIN', 'CUSTMAST', hi='90'),
      c('*IN90', 'IFEQ', "'1'"), c(op='MOVE', f2='MSG,1', res='SMSG'), c(op='GOTO', f2='LINEND'), c(op='END'),
      c(op='MOVE', f2='CNAME', res='SNAME'),
      c('SITEM', 'IFEQ', '0'), c(op='GOTO', f2='LINEND'), c(op='END'),
      c('SITEM', 'CHAIN', 'ITEMMAST', hi='91'),
      c('*IN91', 'IFEQ', "'1'"), c(op='MOVE', f2='MSG,2', res='SMSG'), c(op='GOTO', f2='LINEND'), c(op='END'),
      c(op='MOVE', f2='IDESC', res='SIDESC'),
      c('SQTY', 'IFEQ', '0'), c(op='MOVE', f2='MSG,5', res='SMSG'), c(op='GOTO', f2='LINEND'), c(op='END'),
      c(op='Z-ADD', f2='SCUST', res='WCUST'), c(op='Z-ADD', f2='SITEM', res='WITEM'), c(op='Z-ADD', f2='SQTY', res='WQTY'),
      c(op='CALL', f2="'OE005'"),
      c(op='PARM', res='PCUSTD'), c(op='PARM', res='PITEMD'), c(op='PARM', res='PQTYD'),
      c(op='PARM', res='TODAYD'), c(op='PARM', res='PPRICD'), c(op='PARM', res='SPSRC'),
      c(op='Z-ADD', f2='WPRICE', res='SPRICE'),
      c('SPSRC', 'IFEQ', "'X'"), c(op='MOVE', f2='MSG,6', res='SMSG'), c(op='GOTO', f2='LINEND'), c(op='END'),
      c('*IN06', 'IFEQ', "'1'"),
      c('SORDNO', 'IFEQ', '0'), c(op='EXSR', f2='NEWORD'), c(op='END'),
      c(op='ADD', f2='1', res='SLINE'),
      c(op='Z-ADD', f2='SORDNO', res='DORDNO'), c(op='Z-ADD', f2='SLINE', res='DLINE'), c(op='Z-ADD', f2='SITEM', res='DITEM'),
      c(op='Z-ADD', f2='SQTY', res='QTYORD'), c(op='Z-ADD', f2='0', res='QTYSHP'), c(op='Z-ADD', f2='0', res='CWGHT'),
      c(op='Z-ADD', f2='SPRICE', res='UPRICE'), c(op='MOVE', f2='SPSRC', res='PSRC'), c(op='MOVE', f2="' '", res='SUBFLG'),
      c(op='Z-ADD', f2='0', res='DOITEM'),
      c(op='WRITE', f2='ORDDTLR'),
      c(op='MOVE', f2='MSG,3', res='SMSG'),
      c(op='Z-ADD', f2='0', res='SITEM'), c(op='Z-ADD', f2='0', res='SQTY'), c(op='Z-ADD', f2='0', res='SPRICE'),
      c(op='MOVE', f2="' '", res='SPSRC'), c(op='MOVE', f2='*BLANKS', res='SIDESC'),
      c(op='END'),
      c('LINEND', 'ENDSR'),
      CC(' NEWORD: NEXT ORDER NUMBER IS LAST ONE PLUS ONE'),
      c('NEWORD', 'BEGSR'),
      c('*HIVAL', 'SETGT', 'ORDHDR'),
      c(op='READP', f2='ORDHDR', eq='95'),
      c('*IN95', 'IFEQ', "'1'"),
      c(op='Z-ADD', f2='1', res='WORDNO', ln=7, dec=0),
      c(op='ELSE'),
      c('ORDNO', 'ADD', '1', 'WORDNO'),
      c(op='END'),
      c(op='Z-ADD', f2='WORDNO', res='ORDNO'), c(op='Z-ADD', f2='SCUST', res='OCUST'), c(op='Z-ADD', f2='WTODAY', res='ODLVDT'),
      c(op='Z-ADD', f2='CROUTE', res='OROUTE'), c(op='Z-ADD', f2='CSTOP', res='OSTOP'), c(op='MOVE', f2="'O'", res='OSTAT'),
      c(op='Z-ADD', f2='WTODAY', res='OENTDT'), c(op='MOVE', f2='WUSER', res='OENTBY'),
      c(op='WRITE', f2='ORDHDRR'),
      c(op='Z-ADD', f2='WORDNO', res='SORDNO'), c(op='Z-ADD', f2='0', res='SLINE'),
      c(op='ENDSR'),
      c('RESET', 'BEGSR'),
      c(op='Z-ADD', f2='0', res='SORDNO'), c(op='Z-ADD', f2='0', res='SLINE'), c(op='Z-ADD', f2='0', res='SCUST'),
      c(op='Z-ADD', f2='0', res='SITEM'), c(op='Z-ADD', f2='0', res='SQTY'), c(op='Z-ADD', f2='0', res='SPRICE'),
      c(op='MOVE', f2='*BLANKS', res='SNAME'), c(op='MOVE', f2='*BLANKS', res='SIDESC'), c(op='MOVE', f2="' '", res='SPSRC'),
      c(op='MOVE', f2='MSG,4', res='SMSG'),
      c(op='ENDSR')] + msgdata()
save('QRPGSRC', 'OE001.rpg', L)

# =================================================================== OE020
L = header('Pick confirm - catch weight entry', [
    ' OE020  - PICK CONFIRM / CATCH WEIGHT            DKOWALSKI  05/20/98',
    ' PICKER KEYS ORDER AND LINE, SCALE WEIGHT, F6 TO RECORD.',
    ' FUNCTION KEYS READ FROM THE WORKSTN FEEDBACK AREA, NOT INDICATORS.'])
L += [F3('OE020DF', 'C', dev='WORKSTN'), F3K('INFDS', 'WSDS'),
      F3('ORDDTL', 'U', keyed=True), F3('ORDHDR', 'I', keyed=True), F3('CUSTMAST', 'I', keyed=True), F3('ITEMMAST', 'I', keyed=True)]
L += [E3('MSG')]
L += [I3DS('WSDS'), I3SF(369, 369, 'KEY')] + KEYDS
L += [c('DTKEY', 'KLIST'), c(op='KFLD', res='SORDNO'), c(op='KFLD', res='SLINE'),
      c('KEY', 'DOWNE', "X'33'"),
      c(op='EXFMT', f2='OE020R1'),
      c(op='MOVE', f2='*BLANKS', res='SMSG'),
      c('KEY', 'IFEQ', "X'3C'"),
      c(op='EXSR', f2='RESET'),
      c(op='END'),
      c('KEY', 'IFNE', "X'33'"), c('KEY', 'ANDNE', "X'3C'"),
      c(op='EXSR', f2='SHOW'),
      c(op='END'),
      c(op='END')] + LRRET + [
      c('SHOW', 'BEGSR'),
      c('DTKEY', 'CHAIN', 'ORDDTL', hi='90'),
      c('*IN90', 'IFEQ', "'1'"), c(op='MOVE', f2='MSG,8', res='SMSG'), c(op='GOTO', f2='SHOWND'), c(op='END'),
      c('DORDNO', 'CHAIN', 'ORDHDR', hi='91'),
      c(op='Z-ADD', f2='OCUST', res='CUST#'),
      c('CUST#', 'CHAIN', 'CUSTMAST', hi='92'),
      c(op='MOVE', f2='CNAME', res='SNAME', ind='N92'),
      c('DITEM', 'CHAIN', 'ITEMMAST', hi='93'),
      c(op='Z-ADD', f2='DITEM', res='SITEM'),
      c(op='MOVE', f2='IDESC', res='SIDESC', ind='N93'),
      c(op='Z-ADD', f2='QTYSHP', res='SQTY'),
      CC(" X'36' IS F6"),
      c('KEY', 'IFEQ', "X'36'"),
      c(op='Z-ADD', f2='SCWGHT', res='CWGHT'), c(op='UPDAT', f2='ORDDTLR'), c(op='MOVE', f2='MSG,7', res='SMSG'),
      c(op='END'),
      c('SHOWND', 'ENDSR'),
      c('RESET', 'BEGSR'),
      c(op='Z-ADD', f2='0', res='SORDNO'), c(op='Z-ADD', f2='0', res='SLINE'), c(op='Z-ADD', f2='0', res='SITEM'),
      c(op='Z-ADD', f2='0', res='SQTY'), c(op='Z-ADD', f2='0', res='SCWGHT'),
      c(op='MOVE', f2='*BLANKS', res='SNAME'), c(op='MOVE', f2='*BLANKS', res='SIDESC'),
      c(op='ENDSR')] + msgdata()
save('QRPGSRC', 'OE020.rpg', L)

# =================================================================== CM001
L = header('Customer maintenance', [
    ' CM001  - CUSTOMER MAINTENANCE                   DKOWALSKI  03/04/98',
    ' ENTER RETRIEVES, F6 UPDATES OR ADDS, F12 CLEARS.'])
L += [F3('CM001DF', 'C', dev='WORKSTN'), F3('CUSTMAST', 'U', keyed=True, add=True)]
L += [E3('MSG')] + KEYDS
L += [c('*IN03', 'DOWEQ', "'0'"),
      c(op='EXFMT', f2='CM001R1'),
      c(op='MOVE', f2='*BLANKS', res='SMSG'),
      c('*IN03', 'IFEQ', "'0'"),
      c('*IN12', 'IFEQ', "'1'"),
      c(op='EXSR', f2='RESET'),
      c(op='ELSE'),
      c('*IN06', 'IFEQ', "'1'"),
      c(op='EXSR', f2='SAVE'),
      c(op='ELSE'),
      c(op='EXSR', f2='GET'),
      c(op='END'), c(op='END'), c(op='END'), c(op='END')] + LRRET + [
      c('GET', 'BEGSR'),
      c(op='Z-ADD', f2='SCUST', res='CUST#'),
      c('CUST#', 'CHAIN', 'CUSTMAST', hi='90'),
      c('*IN90', 'IFEQ', "'1'"),
      c(op='MOVE', f2='MSG,1', res='SMSG'),
      c(op='ELSE'),
      c(op='MOVE', f2='CNAME', res='SNAME'), c(op='MOVE', f2='CADDR', res='SADDR'), c(op='MOVE', f2='CCITY', res='SCITY'),
      c(op='MOVE', f2='CSTATE', res='SSTATE'), c(op='Z-ADD', f2='CROUTE', res='SROUTE'), c(op='Z-ADD', f2='CSTOP', res='SSTOP'),
      c(op='MOVE', f2='PCLASS', res='SPCLAS'),
      c(op='END'),
      c(op='ENDSR'),
      c('SAVE', 'BEGSR'),
      c(op='Z-ADD', f2='SCUST', res='CUST#'),
      c('CUST#', 'CHAIN', 'CUSTMAST', hi='90'),
      c(op='Z-ADD', f2='SCUST', res='CUSTNO'),
      c(op='MOVE', f2='SNAME', res='CNAME'), c(op='MOVE', f2='SADDR', res='CADDR'), c(op='MOVE', f2='SCITY', res='CCITY'),
      c(op='MOVE', f2='SSTATE', res='CSTATE'), c(op='Z-ADD', f2='SROUTE', res='CROUTE'), c(op='Z-ADD', f2='SSTOP', res='CSTOP'),
      c(op='MOVE', f2='SPCLAS', res='PCLASS'),
      c('*IN90', 'IFEQ', "'1'"),
      c(op='MOVE', f2="'YNYNYNN'", res='DLVDAY'), c(op='MOVE', f2="'A'", res='CSTAT'),
      c(op='WRITE', f2='CUSTMASR'), c(op='MOVE', f2='MSG,10', res='SMSG'),
      c(op='ELSE'),
      c(op='UPDAT', f2='CUSTMASR'), c(op='MOVE', f2='MSG,9', res='SMSG'),
      c(op='END'),
      c(op='ENDSR'),
      c('RESET', 'BEGSR'),
      c(op='Z-ADD', f2='0', res='SCUST'), c(op='MOVE', f2='*BLANKS', res='SNAME'), c(op='MOVE', f2='*BLANKS', res='SADDR'),
      c(op='MOVE', f2='*BLANKS', res='SCITY'), c(op='MOVE', f2='*BLANKS', res='SSTATE'), c(op='Z-ADD', f2='0', res='SROUTE'),
      c(op='Z-ADD', f2='0', res='SSTOP'), c(op='MOVE', f2="' '", res='SPCLAS'),
      c(op='ENDSR')] + msgdata()
save('QRPGSRC', 'CM001.rpg', L)

# =================================================================== RP010
L = header('Route sheet print', [
    ' RP010  - ROUTE SHEETS FOR A DELIVERY DATE       DKOWALSKI  06/11/98',
    ' CALLED BY ORDCUTOF AFTER ALLOCATION. ONE HEADER PER ROUTE,',
    ' ONE LINE PER CUSTOMER STOP, ONE LINE PER ORDER LINE.',
    ' OVERFLOW IS INDICATOR 99: EXTERNALLY DESCRIBED PRTF, OA-OV NOT ALLOWED.'])
L += [F3('ORDHDRL1', 'I', keyed=True), F3('CUSTMAST', 'I', keyed=True), F3('ORDDTL', 'I', keyed=True),
      F3('ITEMMAST', 'I', keyed=True), F3('RP010PF', 'O', desig=' ', dev='PRINTER', ovf='99')]
L += KEYDS + [I3DS('PDATED'), I3SF(1, 6, 'WDLVDT', 0)]
L += [c('*ENTRY', 'PLIST'), c(op='PARM', res='PDATED'),
      c('HDKEY', 'KLIST'), c(op='KFLD', res='WDLVDT'),
      c('DTKEY', 'KLIST'), c(op='KFLD', res='ORDNO'),
      c(op='Z-ADD', f2='0', res='WROUTE', ln=3, dec=0), c(op='Z-ADD', f2='0', res='PCASES'), c(op='Z-ADD', f2='WDLVDT', res='PDLVDT'),
      c('HDKEY', 'SETLL', 'ORDHDRL1'), c('HDKEY', 'READE', 'ORDHDRL1', eq='80'),
      c('*IN80', 'DOWEQ', "'0'"),
      c('OSTAT', 'IFNE', "'O'"),
      c('OROUTE', 'IFNE', 'WROUTE'),
      c(op='Z-ADD', f2='OROUTE', res='WROUTE'), c(op='Z-ADD', f2='OROUTE', res='PROUTE'), c(op='WRITE', f2='RP010H1'),
      c(op='END'),
      c(op='Z-ADD', f2='OCUST', res='CUST#'),
      c('CUST#', 'CHAIN', 'CUSTMAST', hi='90'),
      c(op='MOVE', f2='*BLANKS', res='PNAME'), c(op='MOVE', f2='CNAME', res='PNAME', ind='N90'),
      c(op='Z-ADD', f2='OSTOP', res='PSTOP'), c(op='Z-ADD', f2='OCUST', res='PCUST'),
      c(op='EXSR', f2='PRTOVF'), c(op='WRITE', f2='RP010C1'),
      c('DTKEY', 'SETLL', 'ORDDTL'), c('DTKEY', 'READE', 'ORDDTL', eq='81'),
      c('*IN81', 'DOWEQ', "'0'"),
      c('DITEM', 'CHAIN', 'ITEMMAST', hi='91'),
      c(op='MOVE', f2='*BLANKS', res='PIDESC'), c(op='MOVE', f2='IDESC', res='PIDESC', ind='N91'),
      c(op='Z-ADD', f2='DLINE', res='PLINE'), c(op='Z-ADD', f2='DITEM', res='PITEM'), c(op='Z-ADD', f2='QTYORD', res='PQTY'),
      c(op='Z-ADD', f2='QTYSHP', res='PSHIP'), c(op='MOVE', f2='SUBFLG', res='PSUB'), c(op='ADD', f2='QTYSHP', res='PCASES'),
      c(op='EXSR', f2='PRTOVF'), c(op='WRITE', f2='RP010D1'),
      c('DTKEY', 'READE', 'ORDDTL', eq='81'),
      c(op='END'),
      c(op='END'),
      c('HDKEY', 'READE', 'ORDHDRL1', eq='80'),
      c(op='END'),
      c(op='WRITE', f2='RP010T1')] + LRRET + [
      c('PRTOVF', 'BEGSR'),
      c('*IN99', 'IFEQ', "'1'"),
      c(op='WRITE', f2='RP010H1'), c(op='SETOF', hi='99'),
      c(op='END'),
      c(op='ENDSR')]
save('QRPGSRC', 'RP010.rpg', L)

# =================================================================== IN001 (RPG IV fixed)
L = [put([(6, 'H'), (7, '*'), (8, '**TEXT:Inventory inquiry')]), put([(6, 'H'), (7, '*')]),
     put([(6, 'H'), (7, '*'), (8, ' IN001  - INVENTORY INQUIRY                      TMORALES   09/14/04')]),
     put([(6, 'H'), (7, '*'), (8, ' REWRITTEN IN ILE RPG (STILL FIXED FORMAT) WHEN WE MOVED TO V5R3.')]),
     put([(6, 'H'), (7, '*'), (8, ' USES THE Z LOGICALS BECAUSE THE BINARY FIELDS GAVE THE OLD CODE FITS.')]),
     put([(6, 'H'), (7, '*')]),
     F4('IN001DF', 'C', dev='WORKSTN'), F4('ITEMMSZ', 'I', keyed=True), F4('INVBALZ', 'I', keyed=True),
     D4('WWHSE', 'S', to=2, dt='A', kw="INZ('01')"),
     C4('IVKEY', 'KLIST'), C4(op='KFLD', res='WWHSE'), C4(op='KFLD', res='SITEM'),
     C4(op='DOW', f2='*IN03 = *OFF'),
     C4(op='EXFMT', f2='IN001R1'),
     C4(op='EVAL', f2='SMSG = *BLANKS'),
     C4(op='IF', f2='*IN03 = *OFF'),
     C4('SITEM', 'CHAIN', 'ITEMMSZ', hi='90'),
     C4(op='IF', f2='*IN90'),
     C4(op='EVAL', f2="SMSG = 'ITEM NOT FOUND'"),
     C4(op='ELSE'),
     C4(op='EVAL', f2='SIDESC = IDESC'), C4(op='EVAL', f2='SZONE = IZONE'),
     C4(op='EVAL', f2='SUNITP = UNITPK'), C4(op='EVAL', f2='SSHELF = SHELFL'),
     C4('IVKEY', 'CHAIN', 'INVBALZ', hi='91'),
     C4(op='IF', f2='NOT *IN91'),
     C4(op='EVAL', f2='SONHND = ONHAND'), C4(op='EVAL', f2='SALLOC = ALLOC'), C4(op='EVAL', f2='SAVAIL = ONHAND - ALLOC'),
     C4(op='ELSE'),
     C4(op='EVAL', f2='SONHND = 0'), C4(op='EVAL', f2='SALLOC = 0'), C4(op='EVAL', f2='SAVAIL = 0'),
     C4(op='ENDIF'),
     C4(op='ENDIF'), C4(op='ENDIF'),
     C4(op='ENDDO'),
     C4(op='EVAL', f2='*INLR = *ON')]
save('QRPGLESRC', 'IN001.rpgle', L)
