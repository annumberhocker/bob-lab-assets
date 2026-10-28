#!/bin/bash
# reset_dist400_user.sh NN | ALL
# Re-clones one participant's library from the master and clears their home directory.
# Never touches the master DIST400. Safe to run repeatedly.
set -u
MASTER="${MASTER:-DIST400}"; BASE="${BASE:-DIST4}"; PREFIX="${PREFIX:-LAB}"
[ $# -ge 1 ] || { echo "usage: $0 NN | ALL"; exit 2; }
cl() { echo "  CL> $1"; system -v "$1" > /tmp/cl.out 2>&1 || { echo "  FAILED:"; sed 's/^/    /' /tmp/cl.out; return 1; }; }
obj_exists() { system "CHKOBJ OBJ($1) OBJTYPE($2)" >/dev/null 2>&1; }
reset_one() {
  local nn="$1" PRF LIB HOME_DIR
  PRF="${PREFIX}${nn}"; LIB="${BASE}${nn}"; HOME_DIR="/home/${PRF}"
  obj_exists "QSYS/$PRF" "*USRPRF" || { echo "-- no profile $PRF, skipping"; return; }
  echo "-- resetting $nn: $LIB and $HOME_DIR"
  obj_exists "QSYS/$LIB" "*LIB" && cl "DLTLIB LIB($LIB)"
  cl "CPYLIB FROMLIB($MASTER) TOLIB($LIB) CRTLIB(*YES)" || return
  system "CHGOWN OBJ('/QSYS.LIB/$LIB.LIB') NEWOWN($PRF) SUBTREE(*ALL)" >/dev/null 2>&1   # CPF223A for members is expected
  cl "GRTOBJAUT OBJ($LIB) OBJTYPE(*LIB) USER(*PUBLIC) AUT(*EXCLUDE)"
  # clear the home directory but keep .ssh: it holds the participant's login key (sshd is key-only on TechZone)
  if [ -d "$HOME_DIR" ]; then find "$HOME_DIR" -mindepth 1 -maxdepth 1 ! -name .ssh -exec rm -rf {} +; fi
  mkdir -p "$HOME_DIR"; chown "$PRF" "$HOME_DIR"; chmod 700 "$HOME_DIR"
  # re-install the public key if it is missing and the setup script generated one
  PUB="$(cd "$(dirname "$0")" && pwd)/keys/$PRF.pub"
  if [ ! -s "$HOME_DIR/.ssh/authorized_keys" ] && [ -f "$PUB" ]; then
    mkdir -p "$HOME_DIR/.ssh"; cp "$PUB" "$HOME_DIR/.ssh/authorized_keys"
    chown -R "$PRF" "$HOME_DIR/.ssh"; chmod 700 "$HOME_DIR/.ssh"; chmod 600 "$HOME_DIR/.ssh/authorized_keys"
    echo "   key re-installed from $PUB"
  fi
  echo "   done"
}
if [ "$1" = "ALL" ]; then
  for (( n = 1; n <= 99; n++ )); do nn=$(printf "%02d" "$n"); obj_exists "QSYS/${PREFIX}${nn}" "*USRPRF" && reset_one "$nn"; done
else
  reset_one "$(printf "%02d" "$((10#$1))")"
fi
