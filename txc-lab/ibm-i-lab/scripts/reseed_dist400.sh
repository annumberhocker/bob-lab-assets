#!/bin/bash
# reseed_dist400.sh [--lib DIST400] [--kit /home/admin/DIST400] [--no-save]
# Reloads the sample data from data/loaddata.sql, resets the CUTOFF data area to zero,
# removes held ROUTESHEET spool files for the current user, and re-saves the library.
# Use after smoke-testing the master so the save file always carries pristine data.
set -u
LIB="DIST400"; KIT="$(cd "$(dirname "$0")/.." && pwd)"; SAVE=1
while [ $# -gt 0 ]; do case "$1" in
  --lib) LIB="$2"; shift 2;; --kit) KIT="$2"; shift 2;; --no-save) SAVE=0; shift;;
  *) echo "unknown option $1"; exit 2;; esac; done
cl() { echo "  CL> $1"; if ! system -v "$1" > /tmp/cl.out 2>&1; then echo "  FAILED:"; sed 's/^/    /' /tmp/cl.out; return 1; fi; }
liblist -a "$LIB" >/dev/null 2>&1 || { echo "liblist failed; run with /QOpenSys/pkgs/bin/bash"; exit 1; }
cl "RUNSQLSTM SRCSTMF('$KIT/data/loaddata.sql') COMMIT(*NONE) NAMING(*SYS) DFTRDBCOL($LIB) ERRLVL(20)" || exit 1
cl "CHGDTAARA DTAARA($LIB/CUTOFF) VALUE(0)" || exit 1
system "DLTSPLF FILE(ROUTESHEET) JOB(*) SPLNBR(*LAST)" >/dev/null 2>&1
for t in CUSTMAST ITEMMAST CONTRACT ORDHDR ORDDTL; do
  printf "   %-9s %s\n" "$t" "$(system "DSPFD FILE($LIB/$t) TYPE(*MBR)" 2>/dev/null | grep -i 'Current number of records' | awk '{print $NF}')"
done
if [ "$SAVE" -eq 1 ]; then
  system "CHKOBJ OBJ(QGPL/DIST400) OBJTYPE(*FILE)" >/dev/null 2>&1 || cl "CRTSAVF FILE(QGPL/DIST400)"
  cl "CLRSAVF FILE(QGPL/DIST400)"
  cl "SAVLIB LIB($LIB) DEV(*SAVF) SAVF(QGPL/DIST400) TGTRLS(*CURRENT) DTACPR(*HIGH)" || exit 1
  cl "CPYTOSTMF FROMMBR('/QSYS.LIB/QGPL.LIB/DIST400.FILE') TOSTMF('$KIT/DIST400.savf') STMFOPT(*REPLACE) CVTDTA(*NONE)" || exit 1
  echo "saved to $KIT/DIST400.savf"
fi
