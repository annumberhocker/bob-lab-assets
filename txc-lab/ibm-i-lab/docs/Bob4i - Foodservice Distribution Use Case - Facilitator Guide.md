<!-- Facilitator Guide, generated from guide-source/lab.md by gen_md.py. Edit lab.md, not this file. -->

# IBM Bob Premium Package for i

**Facilitator Guide: Foodservice Distribution Use Case**

- **Duration:** 60 minutes. Workshop slot: Lab 2, 11:30 to 12:30, after Lab 1 (foundational Bob overview).
- **Audience:** IBM i / AS/400 developers and team leads who maintain an in-house order, pricing or inventory system. No prior AI tooling experience needed.
- **Format:** Facilitator-led. Participants drive their own Bob IDE.
- **Environment:** IBM i 7.6 LPAR with the DIST400 sample application restored. One user profile and one library per participant: LAB01 owns DIST401, LAB02 owns DIST402, and so on.

### How to use this guide

This is the facilitator edition: how to set up the environment, the day-before checks and the clock for the hour. The exercises themselves, with every prompt and what a good answer looks like, are in the Participant Guide; run the hour from that one. Setup takes about 45 minutes the first time and is done days before.

### What participants will do

| Exercise | What you will do | Use case it answers | Time |
|---|---|---|---|
| 0 | Connect Bob to IBM i and have it write an overview of the library | Application documentation generation | 4 min |
| 1 | Understand a 1998 pricing program you have never seen | Code documentation generation | 9 min |
| 2 | Find out what a customer-number expansion would break, then draw the application flow | Interface and dependency mapping; application flow documentation | 10 min |
| 3 | Map the database with one command | Data model documentation | 5 min |
| 4 | Extract the pricing rules nobody wrote down | Business process documentation | 9 min |
| 5 | Modernize the pricing program and compile it | Modernization with a reviewable audit trail | 11 min |
| 6 | Write the runbook for the nightly job and pull the audit evidence | Operational documentation and runbooks; audit evidence and compliance support | 7 min |
| 7 | Wrap-up and hackathon starting points |  | 2 min |

> **The theme running through this lab: recommended starting points for documenting and modernizing an RPG application.** The exercises run in the order a team should actually work: generate the documentation that does not exist, map the dependencies, extract the business rules, then modernize with evidence at every step. Exercises 1, 4 and 5 all work on the same program, OE005, so by the end the room has understood it, documented it, modernized it and proved it still prices the same.

> **How to read the boxes** A box captioned "Paste into the Bob chat" is a prompt: copy it exactly into Bob's chat panel and press Enter. A box captioned "Type in the terminal" is a command for a terminal window, not for Bob. A box captioned "What you should see" is Bob's expected output; do not type it.

### About the sample application

DIST400 is a fixed-format RPG order-to-cash system for a broadline foodservice distributor, written in the style of a 1998 shop. Customers (restaurants, schools, hospitals) order cases of items. Items live in dry, cooler or freezer zones. Some items are catch-weight: sold by the pound, with the real weight only known when the case is picked. Pricing comes from a customer contract if one is in effect, otherwise from the customer's price class, otherwise list. Orders are cut off nightly and printed as route sheets.

| Object | What it is |
|---|---|
| CUSTMAST, ITEMMAST, INVBAL | Customer master, item master, on-hand by warehouse |
| CONTRACT, PRICELST, SUBITEM | Contract prices with effective dates, price-class list prices, substitution items |
| ORDHDR, ORDDTL | Order header and lines |
| OE001, OE005, OE010, OE020 | Order entry, price lookup, allocation and substitution, pick confirm |
| CM001, IN001, RP010 | Customer maintenance, inventory inquiry, nightly route sheet |

> **FACILITATOR GLOSSARY** Catch weight: a case of chicken or cheese is sold per pound and every case weighs something different, so order entry prices on an average weight and the invoice is corrected to the scale weight at pick time. Price class: a customer group such as schools or healthcare that gets its own price list. Cutoff: the nightly moment after which orders are locked, allocated and routed.

## Before the lab: facilitator setup

Everything in this section is typed into a terminal, on your TechZone RHEL 9 VM or on a Mac. If you have never used Linux: a terminal is a text window where you paste one command, press Enter, and read what comes back. Copy each command exactly. The only thing to replace is \<IP address>, which is written in the kit file keys/README.txt. Every command refers to files inside the kit, which step 1 puts at ~/Downloads/DIST400, so nothing has to be found or configured anywhere else. Allow 45 minutes the first time.

### 1. Get the kit onto your computer

1. In Box, open the lab folder, right-click the DIST400 folder and choose Download. Box gives you DIST400.zip in your Downloads folder.
2. Open a terminal. On the VM: click Activities, type Terminal, press Enter. On a Mac: Applications, Utilities, Terminal. Inside Bob: menu Terminal, then New Terminal.
3. Unpack the kit, then lock the key files so only you can read them. The ssh command refuses a key that other users could read, and a zip does not keep that protection, so the third command is not optional.

*Type in the terminal*
```sh
cd ~/Downloads
```

*Type in the terminal*
```sh
unzip -o DIST400.zip
```

*Type in the terminal*
```sh
chmod 600 ~/Downloads/DIST400/keys/*.pem
```

4. Check the keys are there. You should see itz-admin-key.pem, LAB01.pem and README.txt.

*Type in the terminal*
```sh
ls ~/Downloads/DIST400/keys
```

> **If you work straight from the Box Drive folder on a Mac** copy the kit into Downloads first, with the Box path in quotes because it contains spaces, then run the chmod command above. Every path in this guide assumes ~/Downloads/DIST400.

### 2. On the RHEL VM only: install the tools

A Mac already has ssh, scp and unzip built in; skip this step there. On the VM, paste this and press Enter. It installs ssh and scp, the secure login and copy commands, and unzip. If they are already there it says "Nothing to do". If it asks for a password, that is the VM's own password from your TechZone reservation, not the IBM i one.

*Type in the terminal*
```sh
sudo dnf install -y openssh-clients unzip
```

### 3. The IBM i you are connecting to

1. The kit file keys/README.txt names the IBM i address, the admin user ITZUSER and the two key files. The admin key, keys/itz-admin-key.pem, is the only key that logs in as ITZUSER. The LABnn.pem files are participant keys and log in only as their own LABnn. Mixing them up is refused.
2. If you reserve a different LPAR from TechZone, download that reservation's key, copy it over keys/itz-admin-key.pem and update the address in keys/README.txt. Reservations expire, so check the LPAR is alive the day before.

*Open in a browser:* <https://techzone.ibm.com/collection/69caf21433fe65185ca16a84?platform=69caf32c33fe65185ca16a96>

3. Test the login. The first time, it asks "Are you sure you want to continue connecting (yes/no/[fingerprint])?": type yes and press Enter. An IBM Technology Zone banner appears, then a prompt ending in a dollar sign. You are now typing on the IBM i. Type exit and press Enter to come back.

*Type in the terminal*
```sh
ssh -i ~/Downloads/DIST400/keys/itz-admin-key.pem ITZUSER@<IP address>
```

### 4. Copy the kit to the IBM i

> **What "the IFS" means** The IBM i has an ordinary folder tree like Linux, called the Integrated File System, or IFS. The folder /home/ITZUSER is the admin user's home folder in it. The save file and the scripts have to be in that folder tree before the IBM i can use them, and scp is the command that copies them there.

1. Copy the whole kit to the IBM i. The -r means "and everything inside it". It takes about a minute and prints one line per file.

*Type in the terminal*
```sh
scp -i ~/Downloads/DIST400/keys/itz-admin-key.pem -r ~/Downloads/DIST400 ITZUSER@<IP address>:/home/ITZUSER/
```

2. Check that it arrived:

*Type in the terminal*
```sh
ssh -i ~/Downloads/DIST400/keys/itz-admin-key.pem ITZUSER@<IP address> ls /home/ITZUSER/DIST400
```

Expected: a list that includes DIST400.savf, README.md, data, keys, scripts and src.

### 5. Build the libraries and the participants with one command

1. Log in to the IBM i again with the admin key:

*Type in the terminal*
```sh
ssh -i ~/Downloads/DIST400/keys/itz-admin-key.pem ITZUSER@<IP address>
```

2. Run the setup script. The long first word is the full path of the IBM i's bash shell, because the IBM i's default shell is an old one that cannot run these scripts. Replace 23 with the number of participants plus three spares.

*Type in the terminal*
```sh
/QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/setup_dist400_lab.sh -f /home/ITZUSER/DIST400/DIST400.savf -n 23 --keys
```

3. It runs for a few minutes, prints a block for each participant, and ends with a table: ID, profile, password, library. The table is also saved on the IBM i as /home/ITZUSER/DIST400/scripts/participants.csv, and there is one key file per participant in /home/ITZUSER/DIST400/scripts/keys/.
4. Running it again is safe. Participants that already exist are skipped with their passwords and keys untouched, so after -n 23 a later run with -n 24 adds only number 24. Add --pwreset only when someone needs a password issued again.
5. Type exit to leave the IBM i.
6. Copy the participant keys back into the kit on your computer so you can hand them out. They land in ~/Downloads/DIST400/keys/participants, one LABnn.pem per person.

*Type in the terminal*
```sh
scp -i ~/Downloads/DIST400/keys/itz-admin-key.pem -r ITZUSER@<IP address>:/home/ITZUSER/DIST400/scripts/keys ~/Downloads/DIST400/keys/participants
```

> **FACILITATOR NOTE** For each ID the script restores the master library DIST400 from the save file the first time, then creates profile LABnn with its own password, home folder /home/LABnn and current library DIST4nn, copies DIST400 to DIST4nn and makes LABnn the owner of everything in it. With --keys it also writes keys/LABnn.pem and installs the matching public key, which is the only login the TechZone IBM i accepts as shipped. To let people type passwords instead, set PasswordAuthentication yes in /QOpenSys/QIBM/UserData/SC1/OpenSSH/etc/sshd_config and reload sshd; the script prints the exact steps at the end. Nothing is shared between participants except the read-only master DIST400.

### 6. Participant IDs and key files

1. Assign IDs at the 10:00 Lab Setup slot, in seating order, starting at 01. Each person writes their ID on the participant card on page 1.
2. The ID is the only thing they need to remember: profile LABnn, library DIST4nn, key file LABnn.pem, same nn.
3. Give each person only their own LABnn.pem from ~/Downloads/DIST400/keys/participants, through the room's shared Box folder or chat. They save it in the home folder on their VM, for example /home/\<their user>/LAB07.pem.
4. Keep the spare IDs for late arrivals and for anyone whose library needs a reset mid-lab.

> **FACILITATOR NOTE** Twenty people clicking Connect at the same minute can exceed the SSH daemon's default limit on simultaneous unauthenticated connections, and a few will see "connection refused". Either have the room connect in two waves, or raise the limit once by running this one line on the IBM i, logged in as ITZUSER: /QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/sshd_maxstartups.sh

### 7. Each participant's VM

1. A TechZone RHEL 9 VM with IBM Bob installed (v2.0.0 or higher) and the IBM Bob Premium Package for i extension enabled.
2. Their row from the participant table: the IBM i IP address, profile LABnn, and their LABnn.pem saved in their home folder (or the password, if you enabled password login).
3. The IBM i connection created and tested during the 10:00 Lab Setup slot. Exercise 0 only re-verifies it.

Verify the Premium Package is active: the chat mode selector must offer **IBM i Developer** and **IBM i Database**, and the Bob workflows panel, opened with the play icon at the top of the chat, must list **RPG Modernization** and **Business Rules Extraction**. If the two modes are missing, the Premium Package is not enabled and the lab cannot run.

### 8. Reset between sessions

Exercise 5 recompiles OE005 in the participant's library and Exercises 0, 4 and 6 write files to their home folder. To put participant 07 back to the starting point, log in to the IBM i with the admin key and run the reset:

*Type in the terminal*
```sh
ssh -i ~/Downloads/DIST400/keys/itz-admin-key.pem ITZUSER@<IP address>
```

*Type in the terminal*
```sh
/QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/reset_dist400_user.sh 07
```

That deletes and re-copies DIST407 and clears /home/LAB07. Use ALL instead of 07 to reset everyone. It is safe to run repeatedly and never touches DIST400.

### If a setup step goes wrong

| What you see | What it means and what to do |
|---|---|
| Warning: Identity file ... not accessible: No such file or directory | The kit is not at ~/Downloads/DIST400, or the path was typed differently. Run ls ~/Downloads/DIST400/keys; if nothing is listed, redo step 1. |
| WARNING: UNPROTECTED PRIVATE KEY FILE | The key is readable by others, which a zip causes. Run the chmod 600 command from step 1 again. |
| Permission denied (publickey) | Key and user do not match. ITZUSER logs in only with keys/itz-admin-key.pem; LABnn logs in only with its own LABnn.pem. Check both the -i path and the user name before the @ sign. |
| Connection timed out, or kex_exchange_identification | TechZone throttles bursts of new connections. Wait two minutes and retry; do not retry in a loop. |
| bash: command not found, on the IBM i | You typed bash. Use the full path /QOpenSys/pkgs/bin/bash as shown. |
| sudo: you are not in the sudoers file | Log in to the VM as root instead, or ask TechZone for the VM's admin password. |
| Password does not meet all password rules | The IBM i requires 15 characters. Leave the script's default password, or pass --pwprefix with a longer one. |

> **Windows side note** On a Windows 10 or 11 laptop the same ssh and scp commands work in PowerShell. Replace ~ with C:\Users\\\<you> and skip the chmod command.

## Day-before pre-flight checklist

1. Log in to the IBM i with keys/itz-admin-key.pem and confirm the LPAR answers; TechZone reservations expire.
2. On the machine you will demo from, open Bob with an empty folder as the workspace, never the kit folder; otherwise Bob reads the local source instead of the IBM i.
3. Run the reset for one spare ID, then connect in Bob as that participant with its key and run Exercise 0 and the Exercise 5 workflow end to end. Reset the spare again afterwards.
4. Confirm the Bob team account has Premium Package for i seats for everyone attending, and that each VM shows the IBM i Developer and IBM i Database modes.
5. Print or share the participant table and the key files; one key per person, nobody gets two.
6. Have the Participant Guide and the Prompts and Commands text file in the room's shared folder so prompts can be pasted, not typed.

## Running the hour

Lab 2 runs 11:30 to 12:30; the clock adds up to sixty minutes and assumes everyone connected during the 10:00 setup slot. If the overview is still being written at 11:37, move on; it finishes in the background. If you are running late, Exercises 2, 3 and 6A can be dropped without breaking anything later; never drop 1, 4 or 5, they are the story.

| Clock | Exercise | Minutes | Cue to move on |
|---|---|---|---|
| 11:30 | Modes primer | 3 | Everyone can name the two IBM i modes |
| 11:33 | 0 Connect and overview | 4 | Object Browser shows DIST4nn with its source files |
| 11:37 | 1 Understand OE005 | 9 | The Y2K window has been explained to the room |
| 11:46 | 2 Blast radius and flow | 10 | Seventeen objects on screen, level check explained, diagram drawn |
| 11:56 | 3 /erd | 5 | Diagram on screen; point at the missing foreign keys |
| 12:01 | 4 Business rules | 9 | The school discount has been found |
| 12:10 | 5 Modernize | 11 | Compile message seen; price check returned |
| 12:21 | 6 Runbook and audit | 7 | Runbook on screen; one audit row |
| 12:28 | 7 Wrap-up | 2 | Hackathon topics named; 12:30 |
