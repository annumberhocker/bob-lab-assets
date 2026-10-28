#!/bin/bash
# build_dist400.sh [--lib DIST400] [--kit /home/admin/DIST400] [--no-data] [--no-save]
# Builds the DIST400 sample application from source on the IBM i: creates the library and
# source files, uploads every member, compiles in dependency order, loads the data and
# saves the library to <kit>/DIST400.savf for setup_dist400_lab.sh.
# Run in PASE (ssh) as the admin profile. Compile listings go to the job's spooled files;
# on a failure the script prints the last 40 lines of the listing and stops.
set -u
LIB="DIST400"; KIT="$(cd "$(dirname "$0")/.." && pwd)"; LOAD_DATA=1; SAVE=1
while [ $# -gt 0 ]; do case "$1" in
  --lib) LIB="$2"; shift 2;; --kit) KIT="$2"; shift 2;; --no-data) LOAD_DATA=0; shift;; --no-save) SAVE=0; shift;;
  *) echo "unknown option $1"; exit 2;; esac; done
SRC="$KIT/src"
cl() {  # run a CL command; print it; on failure print the diagnostics and keep the full output
  echo "  CL> $1"
  if ! system -v "$1" > /tmp/cl.out 2>&1; then
    cp /tmp/cl.out /tmp/dist400_last_failure.txt
    echo "  FAILED (full output in /tmp/dist400_last_failure.txt):"
    grep -nE '\*? ?(RNF|CPD|CPF|QRG|SQL|CZM|DDS)[0-9]{4}|Severity|Message Summary|\*[0-9]{4} ' /tmp/cl.out | head -40 | sed 's/^/    /'
    return 1
  fi
}
die() { echo "BUILD STOPPED: $1"; exit 1; }
obj_exists() { system "CHKOBJ OBJ($1) OBJTYPE($2)" >/dev/null 2>&1; }
show_listing() {  # source lines flagged in the listing that cl() just saved
  grep -nB2 -E '^ *\*? *(RNF|CPD|QRG)[0-9]{4}' /tmp/dist400_last_failure.txt | head -60 | sed 's/^/    /'
}

echo "== building $LIB from $SRC =="
obj_exists "QSYS/$LIB" "*LIB" || cl "CRTLIB LIB($LIB) TEXT('Foodservice distribution sample app - Bob lab')" || die "CRTLIB"
liblist -a "$LIB" >/dev/null 2>&1 || die "liblist -a $LIB failed; run this script with /QOpenSys/pkgs/bin/bash"
liblist -a QGPL >/dev/null 2>&1
echo "-- library list: $(system "DSPLIBL" 2>/dev/null | grep -E '^ +[A-Z0-9#$@]+ +(CUR|USR)' | awk '{print $1}' | tr '\n' ' ')"
for sf in QDDSSRCF QDDSSRC QDDSSRCD QRPGSRC QRPGLESRC QCLSRC; do
  obj_exists "$LIB/$sf" "*FILE" || cl "CRTSRCPF FILE($LIB/$sf) RCDLEN(112) TEXT('$sf source')" || die "CRTSRCPF $sf"
done

# ---- upload members: src/<SRCF>/<MBR>.<type> -> LIB/SRCF(MBR) with SRCTYPE=type -----------
echo "-- uploading source members"
for path in "$SRC"/*/*.*; do
  sf=$(basename "$(dirname "$path")"); fname=$(basename "$path"); mbr="${fname%.*}"; typ="${fname##*.}"
  mbr=$(echo "$mbr" | tr '[:lower:]' '[:upper:]'); typ=$(echo "$typ" | tr '[:lower:]' '[:upper:]')
  text=$(head -1 "$path" | sed -n 's/^.*\*\*TEXT:\(.*\)$/\1/p' | sed 's/\*\/.*$//; s/ *$//' | cut -c1-50)
  system "ADDPFM FILE($LIB/$sf) MBR($mbr) SRCTYPE($typ) TEXT('${text:-$mbr}')" >/dev/null 2>&1 || true
  cl "CPYFRMSTMF FROMSTMF('$path') TOMBR('/QSYS.LIB/$LIB.LIB/$sf.FILE/$mbr.MBR') MBROPT(*REPLACE)" || die "upload $sf/$mbr"
  [ -n "$text" ] && system "CHGPFM FILE($LIB/$sf) MBR($mbr) TEXT('$text')" >/dev/null 2>&1
done

# ---- compile in dependency order ---------------------------------------------------------
compile() {  # compile TYPE MBR
  local typ="$1" mbr="$2" cmd
  case "$typ" in
    PF)    cmd="CRTPF FILE($LIB/$mbr) SRCFILE($LIB/QDDSSRCF) SRCMBR($mbr) SIZE(*NOMAX) OPTION(*NOSRC *NOLIST)";;
    LF)    cmd="CRTLF FILE($LIB/$mbr) SRCFILE($LIB/QDDSSRC) SRCMBR($mbr) OPTION(*NOSRC *NOLIST)";;
    DSPF)  cmd="CRTDSPF FILE($LIB/$mbr) SRCFILE($LIB/QDDSSRCD) SRCMBR($mbr) OPTION(*NOSRC *NOLIST)";;
    PRTF)  cmd="CRTPRTF FILE($LIB/$mbr) SRCFILE($LIB/QDDSSRCD) SRCMBR($mbr) OPTION(*NOSRC *NOLIST)";;
    RPG)   cmd="CRTRPGPGM PGM($LIB/$mbr) SRCFILE($LIB/QRPGSRC) SRCMBR($mbr) GENLVL(9) REPLACE(*YES)";;
    RPGLE) cmd="CRTBNDRPG PGM($LIB/$mbr) SRCFILE($LIB/QRPGLESRC) SRCMBR($mbr) DBGVIEW(*SOURCE) REPLACE(*YES)";;
    CLP)   cmd="CRTCLPGM PGM($LIB/$mbr) SRCFILE($LIB/QCLSRC) SRCMBR($mbr) REPLACE(*YES)";;
  esac
  obj_exists "$LIB/$mbr" "*FILE" && [ "$typ" != "RPG" ] && [ "$typ" != "RPGLE" ] && [ "$typ" != "CLP" ] && cl "DLTF FILE($LIB/$mbr)"
  echo "-- $typ $mbr"
  cl "$cmd" || { show_listing; die "$typ $mbr did not compile"; }
}
echo "-- compiling"
for m in CUSTMSL1 ITEMMSZ INVBALZ CONTRCL1 ORDHDRL1 ORDDTLL1; do obj_exists "$LIB/$m" "*FILE" && cl "DLTF FILE($LIB/$m)"; done
for m in CUSTMAST ITEMMAST INVBAL CONTRACT PRICELST SUBITEM ORDHDR ORDDTL; do compile PF $m; done
for m in CUSTMSL1 ITEMMSZ INVBALZ CONTRCL1 ORDHDRL1 ORDDTLL1; do compile LF $m; done
for m in OE001DF OE020DF CM001DF IN001DF; do compile DSPF $m; done
compile PRTF RP010PF
for m in OE005 OE010 OE011 OE001 OE020 CM001 RP010; do compile RPG $m; done
compile RPGLE IN001
compile CLP ORDCUTOF
compile CLP TSTPRC
obj_exists "$LIB/CUTOFF" "*DTAARA" || cl "CRTDTAARA DTAARA($LIB/CUTOFF) TYPE(*DEC) LEN(6 0) VALUE(0) TEXT('Last cutoff delivery date YYMMDD')"
obj_exists "$LIB/TSTPRC" "*DTAARA" || cl "CRTDTAARA DTAARA($LIB/TSTPRC) TYPE(*CHAR) LEN(80) TEXT('TSTPRC last result')"

# ---- data -----------------------------------------------------------------------------------
if [ "$LOAD_DATA" -eq 1 ]; then
  echo "-- loading data (takes a minute or two)"
  cl "RUNSQLSTM SRCSTMF('$KIT/data/loaddata.sql') COMMIT(*NONE) NAMING(*SYS) DFTRDBCOL($LIB) ERRLVL(20)" || die "data load; see RUNSQLSTM listing"
  echo "   row counts (compare with the lab guide, Exercise 3):"
  for t in CUSTMAST ITEMMAST INVBAL CONTRACT PRICELST SUBITEM ORDHDR ORDDTL; do
    printf "   %-9s %s\n" "$t" "$(system "DSPFD FILE($LIB/$t) TYPE(*MBR)" 2>/dev/null | grep -i 'Current number of records' | awk '{print $NF}')"
  done
fi

# ---- save -----------------------------------------------------------------------------------
if [ "$SAVE" -eq 1 ]; then
  echo "-- saving $LIB to $KIT/DIST400.savf"
  obj_exists "QGPL/DIST400" "*FILE" || cl "CRTSAVF FILE(QGPL/DIST400)"
  cl "CLRSAVF FILE(QGPL/DIST400)"
  cl "SAVLIB LIB($LIB) DEV(*SAVF) SAVF(QGPL/DIST400) TGTRLS(*CURRENT) DTACPR(*HIGH)" || die "SAVLIB"
  cl "CPYTOSTMF FROMMBR('/QSYS.LIB/QGPL.LIB/DIST400.FILE') TOSTMF('$KIT/DIST400.savf') STMFOPT(*REPLACE) CVTDTA(*NONE)" || die "CPYTOSTMF"
fi
echo "== build complete =="
