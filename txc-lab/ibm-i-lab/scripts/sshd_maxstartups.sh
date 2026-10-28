#!/QOpenSys/pkgs/bin/bash
# sshd_maxstartups.sh
# Optional, for a room of 20+ people clicking Connect in the same minute: raises the IBM i sshd limit on
# simultaneous not-yet-authenticated logins from the default 10:30:100 to 30:30:100, then makes sshd re-read
# its configuration with a HUP signal, which keeps every existing session alive. Safe to run more than once.
#
# Run on the IBM i, logged in as the admin profile, exactly like this (one line):
#   /QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/sshd_maxstartups.sh
#
# Skip it if the room can connect in two waves; a refused connection only needs a retry.
set -u
CFG=/QOpenSys/QIBM/UserData/SC1/OpenSSH/etc/sshd_config
[ -f "$CFG" ] || { echo "sshd_config not found at $CFG; nothing changed"; exit 1; }

if grep -qE '^MaxStartups' "$CFG"; then
  echo "already set: $(grep -E '^MaxStartups' "$CFG")"
else
  cp "$CFG" "$CFG.bak-$(date +%Y%m%d%H%M%S)" || { echo "cannot back up $CFG; the admin profile needs *ALLOBJ (QSECOFR can do it)"; exit 1; }
  echo "MaxStartups 30:30:100" >> "$CFG" || { echo "cannot write $CFG; nothing changed"; exit 1; }
  echo "added: MaxStartups 30:30:100 (backup kept next to the file)"
fi

PID=$(ps -ef | grep "sbin/sshd$" | grep -v grep | awk '{print $2}' | head -1)
if [ -n "$PID" ]; then
  kill -HUP "$PID" && echo "sshd (pid $PID) re-read its configuration; existing sessions untouched"
else
  echo "could not find the sshd daemon process; from a 5250 session run ENDTCPSVR SERVER(*SSHD) then STRTCPSVR SERVER(*SSHD)"
fi
