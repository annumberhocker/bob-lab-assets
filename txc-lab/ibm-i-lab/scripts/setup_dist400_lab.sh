#!/bin/bash
# setup_dist400_lab.sh
# Restores the DIST400 master library from a save file, creates one user profile
# per participant (LAB01..LABnn) and clones one library per participant (DIST401..DIST4nn).
# Run in PASE (ssh) on the IBM i as a profile with *SECADM and *ALLOBJ (the TechZone admin user).
#
# Usage:
#   setup_dist400_lab.sh -f /home/admin/DIST400/DIST400.savf -n 23
#   setup_dist400_lab.sh --skip-restore --range 5 8          # (re)create participants 05..08 only
#
# Options:
#   -f, --savf-path PATH   IFS path of the DIST400 save file (required unless --skip-restore)
#   -n, --participants N   create participants 01..N
#   -r, --range M N        create participants M..N
#   --master LIB           master library name            (default DIST400)
#   --base   PREFIX        participant library prefix     (default DIST4  -> DIST401..)
#   --prefix PREFIX        participant profile prefix     (default LAB    -> LAB01..)
#   --pwprefix TEXT        password prefix, password = TEXT+nn (default Foodservice-2026-, which satisfies
#                          the TechZone rules QPWDLVL 4, *MINLEN15, *LMTPRFNAME; check DSPSYSVAL QPWDRULES on a new box)
#   --skip-restore         do not restore the master; it already exists
#   --force                delete and re-create a participant library that already exists
#   --pwreset              set the password again on profiles that already exist (by default they are left alone)
#
# Rerunning is safe: participants that already exist are skipped, so after -n 23, running -n 24 adds only number 24.
#   --keys                 also generate an SSH key pair per participant into scripts/keys/LABnn.pem and install
#                          the public key in /home/LABnn/.ssh/authorized_keys (TechZone sshd ships PasswordAuthentication no)
#   --dry-run              print the commands without running them
set -u

SAVF_PATH=""; START=1; END=0; MASTER="DIST400"; BASE="DIST4"; PREFIX="LAB"; PWPREFIX="Foodservice-2026-"
SKIP_RESTORE=0; FORCE=0; DRY=0; KEYS=0; PWRESET=0
while [ $# -gt 0 ]; do
  case "$1" in
    -f|--savf-path) SAVF_PATH="$2"; shift 2;;
    -n|--participants) START=1; END="$2"; shift 2;;
    -r|--range) START="$2"; END="$3"; shift 3;;
    --master) MASTER="$2"; shift 2;;
    --base) BASE="$2"; shift 2;;
    --prefix) PREFIX="$2"; shift 2;;
    --pwprefix) PWPREFIX="$2"; shift 2;;
    --skip-restore) SKIP_RESTORE=1; shift;;
    --force) FORCE=1; shift;;
    --keys) KEYS=1; shift;;
    --pwreset) PWRESET=1; shift;;
    --dry-run) DRY=1; shift;;
    -h|--help) sed -n '2,24p' "$0"; exit 0;;
    *) echo "unknown option $1"; exit 2;;
  esac
done
[ "$END" -ge 1 ] || { echo "give -n N or -r M N"; exit 2; }
[ "$SKIP_RESTORE" -eq 1 ] || [ -n "$SAVF_PATH" ] || { echo "-f SAVF_PATH is required unless --skip-restore"; exit 2; }
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CSV="$SCRIPT_DIR/participants.csv"

cl() {  # run a CL command; print it; stop on failure unless called with IGNORE
  local ignore=0; [ "$1" = "IGNORE" ] && { ignore=1; shift; }
  echo "  CL> $1"
  [ "$DRY" -eq 1 ] && return 0
  if ! system -v "$1" > /tmp/cl.out 2>&1; then
    if [ "$ignore" -eq 1 ]; then return 1; fi
    echo "  FAILED:"; sed 's/^/    /' /tmp/cl.out; exit 1
  fi
  return 0
}
obj_exists() { system "CHKOBJ OBJ($1) OBJTYPE($2)" >/dev/null 2>&1; }

echo "== DIST400 lab setup =="
echo "master=$MASTER base=$BASE profiles=${PREFIX}nn range=$START..$END"

# ---- Phase 1: master library --------------------------------------------------------------
if [ "$SKIP_RESTORE" -eq 0 ]; then
  if obj_exists "QSYS/$MASTER" "*LIB"; then
    echo "-- master $MASTER already exists, skipping restore (use --force after DLTLIB to rebuild)"
  else
    echo "-- restoring $MASTER from $SAVF_PATH"
    [ -f "$SAVF_PATH" ] || { echo "save file not found: $SAVF_PATH"; exit 1; }
    obj_exists "QGPL/$MASTER" "*FILE" || cl "CRTSAVF FILE(QGPL/$MASTER) TEXT('DIST400 lab master save file')"
    cl "CPYFRMSTMF FROMSTMF('$SAVF_PATH') TOMBR('/QSYS.LIB/QGPL.LIB/$MASTER.FILE') MBROPT(*REPLACE) CVTDTA(*NONE)"
    cl "RSTLIB SAVLIB(DIST400) DEV(*SAVF) SAVF(QGPL/$MASTER) RSTLIB($MASTER) MBROPT(*ALL) ALWOBJDIF(*ALL)"
  fi
fi
echo "-- making $MASTER read-only for everyone"
cl "GRTOBJAUT OBJ($MASTER) OBJTYPE(*LIB) USER(*PUBLIC) AUT(*USE)"
cl "GRTOBJAUT OBJ($MASTER/*ALL) OBJTYPE(*ALL) USER(*PUBLIC) AUT(*USE)"

# ---- Phase 2: participants ----------------------------------------------------------------
[ "$DRY" -eq 1 ] || { [ -f "$CSV" ] || echo "id,profile,password,library" > "$CSV"; }
printf "\n%-4s %-8s %-20s %-10s\n" ID PROFILE PASSWORD LIBRARY
for (( n = START; n <= END; n++ )); do   # no seq in PASE
  nn=$(printf "%02d" "$n")
  PRF="${PREFIX}${nn}"; LIB="${BASE}${nn}"; PW="${PWPREFIX}${nn}"; HOME_DIR="/home/${PRF}"
  echo "-- participant $nn: profile $PRF, library $LIB"
  # library first, so the profile's CURLIB exists when the profile is created
  if obj_exists "QSYS/$LIB" "*LIB"; then
    if [ "$FORCE" -eq 1 ]; then cl "DLTLIB LIB($LIB)"; else echo "   $LIB exists, keeping it (use --force to rebuild)"; fi
  fi
  if ! obj_exists "QSYS/$LIB" "*LIB"; then
    cl "CPYLIB FROMLIB($MASTER) TOLIB($LIB) CRTLIB(*YES)"
  fi
  SHOWPW="$PW"
  if obj_exists "QSYS/$PRF" "*USRPRF"; then
    if [ "$PWRESET" -eq 1 ]; then
      cl "CHGUSRPRF USRPRF($PRF) PASSWORD('$PW') CURLIB($LIB) HOMEDIR('$HOME_DIR') PWDEXP(*NO) STATUS(*ENABLED)"
    else
      echo "   $PRF exists, keeping it and its password (use --pwreset to set the password again)"
      cl IGNORE "CHGUSRPRF USRPRF($PRF) CURLIB($LIB) HOMEDIR('$HOME_DIR') STATUS(*ENABLED)" || true
      SHOWPW="(unchanged)"
    fi
  else
    cl "CRTUSRPRF USRPRF($PRF) PASSWORD('$PW') USRCLS(*PGMR) SPCAUT(*NONE) CURLIB($LIB) HOMEDIR('$HOME_DIR') PWDEXP(*NO) TEXT('Bob for i lab participant $nn')"
  fi
  if [ "$DRY" -eq 0 ]; then
    mkdir -p "$HOME_DIR"; chown "$PRF" "$HOME_DIR"; chmod 700 "$HOME_DIR"
    if [ "$KEYS" -eq 1 ]; then
      mkdir -p "$SCRIPT_DIR/keys"; chmod 700 "$SCRIPT_DIR/keys"
      if [ ! -f "$SCRIPT_DIR/keys/$PRF.pem" ]; then
        /QOpenSys/QIBM/ProdData/SC1/OpenSSH/bin/ssh-keygen -q -t rsa -b 3072 -N '' -C "$PRF lab participant key" -f "$SCRIPT_DIR/keys/$PRF.pem" </dev/null
        mv "$SCRIPT_DIR/keys/$PRF.pem.pub" "$SCRIPT_DIR/keys/$PRF.pub"
      fi
      mkdir -p "$HOME_DIR/.ssh"; cp "$SCRIPT_DIR/keys/$PRF.pub" "$HOME_DIR/.ssh/authorized_keys"
      chown -R "$PRF" "$HOME_DIR/.ssh"; chmod 700 "$HOME_DIR/.ssh"; chmod 600 "$HOME_DIR/.ssh/authorized_keys"
      echo "   key installed: $SCRIPT_DIR/keys/$PRF.pem (give this file to participant $nn)"
    fi
  fi
  # CPF223A "n objects not changed" is expected: source members have no owner
  cl IGNORE "CHGOWN OBJ('/QSYS.LIB/$LIB.LIB') NEWOWN($PRF) SUBTREE(*ALL)" || true
  cl "GRTOBJAUT OBJ($LIB) OBJTYPE(*LIB) USER(*PUBLIC) AUT(*EXCLUDE)"
  printf "%-4s %-8s %-20s %-10s\n" "$nn" "$PRF" "$SHOWPW" "$LIB"
  [ "$DRY" -eq 1 ] || grep -q "^$nn," "$CSV" || echo "$nn,$PRF,$SHOWPW,$LIB" >> "$CSV"
done

cat <<NOTE

Participant table written to $CSV
Each participant connects in Bob with: host <this LPAR>, port 22, user LABnn, and EITHER the password above
OR the key file scripts/keys/LABnn.pem (made with --keys). TechZone LPARs ship sshd with "PasswordAuthentication no";
passwords only work after the facilitator sets it to yes in /QOpenSys/QIBM/UserData/SC1/OpenSSH/etc/sshd_config and
reloads sshd (kill -HUP <master sshd pid>, or ENDTCPSVR/STRTCPSVR SERVER(*SSHD)). Keys work as shipped.

OPTIONAL, for a room of 20+ connecting in the same minute: raise the sshd login limit by running this one line
here on the IBM i (it backs up the config, adds MaxStartups 30:30:100, and reloads sshd without dropping sessions):
  /QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/sshd_maxstartups.sh
Skip it if the room can connect in two waves; a refused connection only needs a retry.
NOTE
