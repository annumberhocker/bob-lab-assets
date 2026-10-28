#!/QOpenSys/pkgs/bin/bash
# DIST400 batch smoke tests; run detached: nohup bash smoke.sh > /tmp/smoke.out 2>&1 &
liblist -a DIST400 >/dev/null 2>&1
q() { qsh -c "db2 \"$1\"" 2>&1 | grep -v -E '^\s*$' | head -${2:-6}; }
res() { qsh -c "db2 \"SELECT CAST(DATA_AREA_VALUE AS VARCHAR(80)) AS RESULT FROM TABLE(QSYS2.DATA_AREA_INFO('TSTPRC','DIST400'))\"" 2>&1 | grep -E 'OE005' | head -1; }
echo "=== db2 via qsh sanity: open orders ==="; q "SELECT COUNT(*) AS OPEN_ORDERS FROM DIST400.ORDHDR WHERE OSTAT = 'O'"
echo "=== T1 contract price: cust 100230 item 201410 qty 5 date 261015  (expect PRICE=0004250 SRC=C) ==="
system "CALL DIST400/TSTPRC PARM('100230' '201410' '00005' '261015')" 2>&1 | grep -E "OE005|CPF|RNQ|MCH" | head -3; res
echo "=== T2 school class S, no contract: cust 100240 item 200017  (expect PRICE=0007184 SRC=P) ==="
system "CALL DIST400/TSTPRC PARM('100240' '200017' '00002' '261015')" 2>&1 | grep -E "OE005|CPF|RNQ|MCH" | head -3; res
echo "=== T3 catch weight, class R: cust 100230 item 200001  (expect PRICE=0063469 SRC=P) ==="
system "CALL DIST400/TSTPRC PARM('100230' '200001' '00001' '261015')" 2>&1 | grep -E "OE005|CPF|RNQ|MCH" | head -3; res
echo "=== T4 Y2K cliff: cust 100046 item 201736 has a contract expiring 991231  (expect SRC=P, not C) ==="
q "SELECT CCUST, CITEM, CPRICE, CEFFDT, CEXPDT FROM DIST400.CONTRACT WHERE CCUST = 100046 AND CITEM = 201736"
system "CALL DIST400/TSTPRC PARM('100046' '201736' '00001' '261015')" 2>&1 | grep -E "OE005|CPF|RNQ|MCH" | head -3; res
echo "=== T5 unknown item (expect SRC=X) ==="
system "CALL DIST400/TSTPRC PARM('100230' '999999' '00001' '261015')" 2>&1 | grep -E "OE005|CPF|RNQ|MCH" | head -3; res
echo "=== before cutoff: orders for 261008 by status ==="
q "SELECT OSTAT, COUNT(*) AS N FROM DIST400.ORDHDR WHERE ODLVDT = 261008 GROUP BY OSTAT"
echo "=== C1 ORDCUTOF 261008 ==="
system "CALL DIST400/ORDCUTOF PARM('261008')" > /tmp/cutoff1.out 2>&1; echo "exit=$?"
grep -E "Cutoff|CPF|RNQ|MCH|RNX" /tmp/cutoff1.out | head -5
echo "--- route sheet output lines: $(wc -l < /tmp/cutoff1.out); sample:"; grep -nE "ROUTE SHEET|TOTAL CASES" /tmp/cutoff1.out | head -4; sed -n "1,22p" /tmp/cutoff1.out | cut -c1-100
echo "=== after cutoff: orders for 261008 by status (expect all R); line stats; allocations; data area ==="
q "SELECT OSTAT, COUNT(*) AS N FROM DIST400.ORDHDR WHERE ODLVDT = 261008 GROUP BY OSTAT"
q "SELECT COUNT(*) AS LINES, SUM(CASE WHEN QTYSHP > 0 THEN 1 ELSE 0 END) AS SHIPPED, SUM(CASE WHEN QTYSHP < QTYORD THEN 1 ELSE 0 END) AS SHORT, SUM(CASE WHEN SUBFLG = 'Y' THEN 1 ELSE 0 END) AS SUBS FROM DIST400.ORDDTL d JOIN DIST400.ORDHDR h ON h.ORDNO = d.DORDNO WHERE h.ODLVDT = 261008"
q "SELECT COUNT(*) AS ITEMS_ALLOCATED, SUM(ALLOC) AS CASES_ALLOCATED FROM DIST400.INVBAL WHERE ALLOC > 0"
q "SELECT DATA_AREA_VALUE FROM TABLE(QSYS2.DATA_AREA_INFO('CUTOFF','DIST400'))" 4
echo "=== C2 ORDCUTOF 261008 again (expect: Cutoff already run) ==="
system "CALL DIST400/ORDCUTOF PARM('261008')" 2>&1 | grep -E "Cutoff|CPF9898|CPF" | head -3
echo "=== spool files from the cutoff (held ROUTESHEET expected, unless system copied+deleted them) ==="
q "SELECT SPOOLED_FILE_NAME, STATUS, TOTAL_PAGES FROM TABLE(QSYS2.SPOOLED_FILE_INFO(USER_NAME => 'ITZUSER')) WHERE SPOOLED_FILE_NAME IN ('ROUTESHEET','RP010PF') ORDER BY CREATION_TIMESTAMP DESC" 6
echo "SMOKE DONE"
