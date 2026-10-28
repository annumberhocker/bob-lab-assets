Keys for the lab IBM i (TechZone reservation of 2026-10-07)

  Host        169.61.149.228   port 22
  Admin       user ITZUSER     key itz-admin-key.pem    (setup, build, reset; never used by participants)
  Participant user LAB01       key LAB01.pem            (created by the setup script; one key per LABnn)

Log in from a terminal, after unzipping the kit into your Downloads folder:

  chmod 600 ~/Downloads/DIST400/keys/*.pem
  ssh -i ~/Downloads/DIST400/keys/itz-admin-key.pem ITZUSER@169.61.149.228
  ssh -i ~/Downloads/DIST400/keys/LAB01.pem LAB01@169.61.149.228

In Bob's IBM i connection dialog: host 169.61.149.228, port 22, user LABnn, password empty,
Private Key = the LABnn.pem file.

The setup script, run with --keys, makes one key per participant on the IBM i in /home/ITZUSER/DIST400/scripts/keys/
and never overwrites one that exists. Facilitator Guide step 5 copies them all back into keys/participants/ with one
scp command. LAB01.pem here is that key for LAB01 on the host above; on a different LPAR it is useless until the setup
script has run there.

A key only works with its own user. ITZUSER with LAB01.pem, or LAB01 with the admin key, is refused.
If you reserve a different LPAR, replace itz-admin-key.pem with that reservation's key and update the host above.
These files are private keys to a live server: keep the kit inside the team.
