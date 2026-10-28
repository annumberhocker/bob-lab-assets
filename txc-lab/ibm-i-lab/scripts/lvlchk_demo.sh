#!/QOpenSys/pkgs/bin/bash
# lvlchk_demo.sh
# Shows what really happens to OE010 and OE011 when ORDHDR is rebuilt with an 8-digit customer number and
# nobody recompiles them: the nightly cutoff stops at open with CPF4131, Level check on file ORDHDRL1, and
# ends with the CL program's own 'Cutoff FAILED ... see job log, then rerun' message. Verified 2026-10-08. Works in a scratch copy of the master library called LVLTEST and
# deletes it afterwards. DIST400 and the participant libraries are never touched.
#
# Run on the IBM i as the admin profile, one line:
#   nohup /QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/lvlchk_demo.sh > /tmp/lvlchk.log 2>&1 < /dev/null &
# then, a minute or two later:
#   cat /tmp/lvlchk.log
# Add KEEP as the first argument to keep LVLTEST and the waiting job for a live demo in Bob
# ("Why is job LVLCHK waiting on a message?").
set -u
LIB=LVLTEST
KEEP=${1:-}
cl() { system "$1"; }
q()  { qsh -c "db2 \"$1\""; }

echo "== 1. Level-check attribute of the file the lab would rebuild (DIST401/ORDHDR)"
system "DSPFD FILE(DIST401/ORDHDR) TYPE(*ATR)" | grep -i "level check" || echo "(no level check line from DSPFD)"

echo "== 2. Scratch copy of the master library"
cl "DLTLIB LIB($LIB)" > /dev/null 2>&1
cl "CPYLIB FROMLIB(DIST400) TOLIB($LIB) CRTLIB(*YES)" || { echo "CPYLIB failed"; exit 1; }

echo "== 3. Record format level identifiers before the change"
system "DSPFD FILE($LIB/ORDHDR) TYPE(*RCDFMT)"   | grep -i "level identifier"
system "DSPFD FILE($LIB/ORDHDRL1) TYPE(*RCDFMT)" | grep -i "level identifier"

echo "== 4. Widen OCUST from 6 to 8 digits and rebuild ORDHDR in place (CHGPF keeps the data and rebuilds ORDHDRL1)"
sed 's/OCUST          6S 0/OCUST          8S 0/' /home/ITZUSER/DIST400/src/QDDSSRCF/ORDHDR.pf > /tmp/ORDHDR8.pf
grep -n "OCUST" /tmp/ORDHDR8.pf
cl "CPYFRMSTMF FROMSTMF('/tmp/ORDHDR8.pf') TOMBR('/QSYS.LIB/$LIB.LIB/QDDSSRCF.FILE/ORDHDR.MBR') MBROPT(*REPLACE)" || { echo "upload failed"; exit 1; }
cl "CHGPF FILE($LIB/ORDHDR) SRCFILE($LIB/QDDSSRCF) SRCMBR(ORDHDR)" || { echo "CHGPF failed"; exit 1; }

echo "== 5. Record format level identifiers after the change (the programs were compiled against the old ones)"
system "DSPFD FILE($LIB/ORDHDR) TYPE(*RCDFMT)"   | grep -i "level identifier"
system "DSPFD FILE($LIB/ORDHDRL1) TYPE(*RCDFMT)" | grep -i "level identifier"

echo "== 6. Orders for delivery date 261008 by status, before"
q "SELECT OSTAT, COUNT(*) AS ORDERS FROM $LIB.ORDHDR WHERE ODLVDT = 261008 GROUP BY OSTAT"

echo "== 7. Submit the nightly cutoff exactly as a scheduler would, with nothing recompiled"
OUT=$(system "SBMJOB CMD(CALL PGM(ORDCUTOF) PARM('261008')) JOB(LVLCHK) JOBQ(QSYSNOMAX) INLLIBL($LIB QTEMP) INQMSGRPY(*RQD) LOG(4 0 *SECLVL) LOGCLPGM(*YES) LOGOUTPUT(*PND)" 2>&1)
echo "$OUT"
JOB=$(echo "$OUT" | awk '/CPC1221/ {print $3}' | head -1)   # PASE grep has no -o
[ -n "$JOB" ] || { echo "could not find the job number in the SBMJOB message"; exit 1; }
sleep 25

echo "== 8. Job status (normally empty: the job ended in under a second; MSGW would mean it is waiting on a message)"
q "SELECT JOB_NAME, JOB_STATUS, FUNCTION_TYPE, FUNCTION FROM TABLE(QSYS2.ACTIVE_JOB_INFO(JOB_NAME_FILTER => 'LVLCHK'))"

echo "== 9. The job log of $JOB"
q "SELECT MESSAGE_ID, MESSAGE_TYPE, CAST(MESSAGE_TEXT AS VARCHAR(110)) AS TEXT FROM TABLE(QSYS2.JOBLOG_INFO('$JOB')) WHERE MESSAGE_ID IS NOT NULL ORDER BY ORDINAL_POSITION"

echo "== 10. Orders by status, after: unchanged, the cutoff never ran"
q "SELECT OSTAT, COUNT(*) AS ORDERS FROM $LIB.ORDHDR WHERE ODLVDT = 261008 GROUP BY OSTAT"

if [ "$KEEP" = KEEP ]; then
  echo "== KEEP: job $JOB left waiting and library $LIB kept; finish with ENDJOB JOB($JOB) OPTION(*IMMED) and DLTLIB $LIB"
else
  echo "== 11. Clean up"
  cl "ENDJOB JOB($JOB) OPTION(*IMMED)" > /dev/null 2>&1 && echo "job $JOB ended"
  sleep 3
  cl "DLTLIB LIB($LIB)" > /dev/null 2>&1 && echo "library $LIB deleted"
fi
echo "DEMO DONE"
