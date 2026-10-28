# IBM Bob Premium Package for i
%par
#sub Participant Guide: Foodservice Distribution Use Case
%end
%fac
#sub Facilitator Guide: Foodservice Distribution Use Case
%end

%kv
| Duration | 60 minutes. Workshop slot: Lab 2, 11:30 to 12:30, after Lab 1 (foundational Bob overview). |
| Audience | IBM i / AS/400 developers and team leads who maintain an in-house order, pricing or inventory system. No prior AI tooling experience needed. |
| Format | Facilitator-led. Participants drive their own Bob IDE. |
| Environment | IBM i 7.6 LPAR with the DIST400 sample application restored. One user profile and one library per participant: LAB01 owns DIST401, LAB02 owns DIST402, and so on. |

%par
### Your participant card

Your facilitator gives you a two-digit ID. Write it here and use it everywhere this guide says nn.

%kv
| Your ID (nn) | put your ID here |
| User profile | LABnn |
| Key file | LABnn.pem, given by your facilitator |
| Your library | DIST4nn |

Nothing you do in DIST4nn can affect anyone else. Your profile owns the library, your current library is already set to it, and your home directory on the server is yours alone.

%end
%fac
### How to use this guide

This is the facilitator edition: how to set up the environment, the day-before checks and the clock for the hour. The exercises themselves, with every prompt and what a good answer looks like, are in the Participant Guide; run the hour from that one. Setup takes about 45 minutes the first time and is done days before.

%end
### What participants will do

| Exercise | What you will do | Use case it answers | Time |
| 0 | Connect Bob to IBM i and have it write an overview of the library | Application documentation generation | 4 min |
| 1 | Understand a 1998 pricing program you have never seen | Code documentation generation | 9 min |
| 2 | Find out what a customer-number expansion would break, then draw the application flow | Interface and dependency mapping; application flow documentation | 10 min |
| 3 | Map the database with one command | Data model documentation | 5 min |
| 4 | Extract the pricing rules nobody wrote down | Business process documentation | 9 min |
| 5 | Modernize the pricing program and compile it | Modernization with a reviewable audit trail | 11 min |
| 6 | Write the runbook for the nightly job and pull the audit evidence | Operational documentation and runbooks; audit evidence and compliance support | 7 min |
| 7 | Wrap-up and hackathon starting points | | 2 min |

!! **The theme running through this lab: recommended starting points for documenting and modernizing an RPG application.** The exercises run in the order a team should actually work: generate the documentation that does not exist, map the dependencies, extract the business rules, then modernize with evidence at every step. Exercises 1, 4 and 5 all work on the same program, OE005, so by the end the room has understood it, documented it, modernized it and proved it still prices the same.

!! **How to read the boxes** A box captioned "Paste into the Bob chat" is a prompt: copy it exactly into Bob's chat panel and press Enter. A box captioned "Type in the terminal" is a command for a terminal window, not for Bob. A box captioned "What you should see" is Bob's expected output; do not type it.

### About the sample application

DIST400 is a fixed-format RPG order-to-cash system for a broadline foodservice distributor, written in the style of a 1998 shop. Customers (restaurants, schools, hospitals) order cases of items. Items live in dry, cooler or freezer zones. Some items are catch-weight: sold by the pound, with the real weight only known when the case is picked. Pricing comes from a customer contract if one is in effect, otherwise from the customer's price class, otherwise list. Orders are cut off nightly and printed as route sheets.

| Object | What it is |
| CUSTMAST, ITEMMAST, INVBAL | Customer master, item master, on-hand by warehouse |
| CONTRACT, PRICELST, SUBITEM | Contract prices with effective dates, price-class list prices, substitution items |
| ORDHDR, ORDDTL | Order header and lines |
| OE001, OE005, OE010, OE020 | Order entry, price lookup, allocation and substitution, pick confirm |
| CM001, IN001, RP010 | Customer maintenance, inventory inquiry, nightly route sheet |

!! **FACILITATOR GLOSSARY** Catch weight: a case of chicken or cheese is sold per pound and every case weighs something different, so order entry prices on an average weight and the invoice is corrected to the scale weight at pick time. Price class: a customer group such as schools or healthcare that gets its own price list. Cutoff: the nightly moment after which orders are locked, allocated and routed.

%fac
## Before the lab: facilitator setup

Everything in this section is typed into a terminal, on your TechZone RHEL 9 VM or on a Mac. If you have never used Linux: a terminal is a text window where you paste one command, press Enter, and read what comes back. Copy each command exactly. The only thing to replace is <IP address>, which is written in the kit file keys/README.txt. Every command refers to files inside the kit, which step 1 puts at ~/Downloads/DIST400, so nothing has to be found or configured anywhere else. Allow 45 minutes the first time.

### 1. Get the kit onto your computer

1. In Box, open the lab folder, right-click the DIST400 folder and choose Download. Box gives you DIST400.zip in your Downloads folder.
2. Open a terminal. On the VM: click Activities, type Terminal, press Enter. On a Mac: Applications, Utilities, Terminal. Inside Bob: menu Terminal, then New Terminal.
3. Unpack the kit, then lock the key files so only you can read them. The ssh command refuses a key that other users could read, and a zip does not keep that protection, so the third command is not optional.

$$ cd ~/Downloads

$$ unzip -o DIST400.zip

$$ chmod 600 ~/Downloads/DIST400/keys/*.pem

4. Check the keys are there. You should see itz-admin-key.pem, LAB01.pem and README.txt.

$$ ls ~/Downloads/DIST400/keys

!! **If you work straight from the Box Drive folder on a Mac** copy the kit into Downloads first, with the Box path in quotes because it contains spaces, then run the chmod command above. Every path in this guide assumes ~/Downloads/DIST400.

### 2. On the RHEL VM only: install the tools

A Mac already has ssh, scp and unzip built in; skip this step there. On the VM, paste this and press Enter. It installs ssh and scp, the secure login and copy commands, and unzip. If they are already there it says "Nothing to do". If it asks for a password, that is the VM's own password from your TechZone reservation, not the IBM i one.

$$ sudo dnf install -y openssh-clients unzip

### 3. The IBM i you are connecting to

1. The kit file keys/README.txt names the IBM i address, the admin user ITZUSER and the two key files. The admin key, keys/itz-admin-key.pem, is the only key that logs in as ITZUSER. The LABnn.pem files are participant keys and log in only as their own LABnn. Mixing them up is refused.
2. If you reserve a different LPAR from TechZone, download that reservation's key, copy it over keys/itz-admin-key.pem and update the address in keys/README.txt. Reservations expire, so check the LPAR is alive the day before.

$$ https://techzone.ibm.com/collection/69caf21433fe65185ca16a84?platform=69caf32c33fe65185ca16a96

3. Test the login. The first time, it asks "Are you sure you want to continue connecting (yes/no/[fingerprint])?": type yes and press Enter. An IBM Technology Zone banner appears, then a prompt ending in a dollar sign. You are now typing on the IBM i. Type exit and press Enter to come back.

$$ ssh -i ~/Downloads/DIST400/keys/itz-admin-key.pem ITZUSER@<IP address>

### 4. Copy the kit to the IBM i

!! **What "the IFS" means** The IBM i has an ordinary folder tree like Linux, called the Integrated File System, or IFS. The folder /home/ITZUSER is the admin user's home folder in it. The save file and the scripts have to be in that folder tree before the IBM i can use them, and scp is the command that copies them there.

1. Copy the whole kit to the IBM i. The -r means "and everything inside it". It takes about a minute and prints one line per file.

$$ scp -i ~/Downloads/DIST400/keys/itz-admin-key.pem -r ~/Downloads/DIST400 ITZUSER@<IP address>:/home/ITZUSER/

2. Check that it arrived:

$$ ssh -i ~/Downloads/DIST400/keys/itz-admin-key.pem ITZUSER@<IP address> ls /home/ITZUSER/DIST400

Expected: a list that includes DIST400.savf, README.md, data, keys, scripts and src.

### 5. Build the libraries and the participants with one command

1. Log in to the IBM i again with the admin key:

$$ ssh -i ~/Downloads/DIST400/keys/itz-admin-key.pem ITZUSER@<IP address>

2. Run the setup script. The long first word is the full path of the IBM i's bash shell, because the IBM i's default shell is an old one that cannot run these scripts. Replace 23 with the number of participants plus three spares.

$$ /QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/setup_dist400_lab.sh -f /home/ITZUSER/DIST400/DIST400.savf -n 23 --keys

3. It runs for a few minutes, prints a block for each participant, and ends with a table: ID, profile, password, library. The table is also saved on the IBM i as /home/ITZUSER/DIST400/scripts/participants.csv, and there is one key file per participant in /home/ITZUSER/DIST400/scripts/keys/.
4. Running it again is safe. Participants that already exist are skipped with their passwords and keys untouched, so after -n 23 a later run with -n 24 adds only number 24. Add --pwreset only when someone needs a password issued again.
5. Type exit to leave the IBM i.
6. Copy the participant keys back into the kit on your computer so you can hand them out. They land in ~/Downloads/DIST400/keys/participants, one LABnn.pem per person.

$$ scp -i ~/Downloads/DIST400/keys/itz-admin-key.pem -r ITZUSER@<IP address>:/home/ITZUSER/DIST400/scripts/keys ~/Downloads/DIST400/keys/participants

!! **FACILITATOR NOTE** For each ID the script restores the master library DIST400 from the save file the first time, then creates profile LABnn with its own password, home folder /home/LABnn and current library DIST4nn, copies DIST400 to DIST4nn and makes LABnn the owner of everything in it. With --keys it also writes keys/LABnn.pem and installs the matching public key, which is the only login the TechZone IBM i accepts as shipped. To let people type passwords instead, set PasswordAuthentication yes in /QOpenSys/QIBM/UserData/SC1/OpenSSH/etc/sshd_config and reload sshd; the script prints the exact steps at the end. Nothing is shared between participants except the read-only master DIST400.

### 6. Participant IDs and key files

1. Assign IDs at the 10:00 Lab Setup slot, in seating order, starting at 01. Each person writes their ID on the participant card on page 1.
2. The ID is the only thing they need to remember: profile LABnn, library DIST4nn, key file LABnn.pem, same nn.
3. Give each person only their own LABnn.pem from ~/Downloads/DIST400/keys/participants, through the room's shared Box folder or chat. They save it in the home folder on their VM, for example /home/<their user>/LAB07.pem.
4. Keep the spare IDs for late arrivals and for anyone whose library needs a reset mid-lab.

!! **FACILITATOR NOTE** Twenty people clicking Connect at the same minute can exceed the SSH daemon's default limit on simultaneous unauthenticated connections, and a few will see "connection refused". Either have the room connect in two waves, or raise the limit once by running this one line on the IBM i, logged in as ITZUSER: /QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/sshd_maxstartups.sh

### 7. Each participant's VM

1. A TechZone RHEL 9 VM with IBM Bob installed (v2.0.0 or higher) and the IBM Bob Premium Package for i extension enabled.
2. Their row from the participant table: the IBM i IP address, profile LABnn, and their LABnn.pem saved in their home folder (or the password, if you enabled password login).
3. The IBM i connection created and tested during the 10:00 Lab Setup slot. Exercise 0 only re-verifies it.

Verify the Premium Package is active: the chat mode selector must offer **IBM i Developer** and **IBM i Database**, and the Bob workflows panel, opened with the play icon at the top of the chat, must list **RPG Modernization** and **Business Rules Extraction**. If the two modes are missing, the Premium Package is not enabled and the lab cannot run.

### 8. Reset between sessions

Exercise 5 recompiles OE005 in the participant's library and Exercises 0, 4 and 6 write files to their home folder. To put participant 07 back to the starting point, log in to the IBM i with the admin key and run the reset:

$$ ssh -i ~/Downloads/DIST400/keys/itz-admin-key.pem ITZUSER@<IP address>

$$ /QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/reset_dist400_user.sh 07

That deletes and re-copies DIST407 and clears /home/LAB07. Use ALL instead of 07 to reset everyone. It is safe to run repeatedly and never touches DIST400.

### If a setup step goes wrong

| What you see | What it means and what to do |
| Warning: Identity file ... not accessible: No such file or directory | The kit is not at ~/Downloads/DIST400, or the path was typed differently. Run ls ~/Downloads/DIST400/keys; if nothing is listed, redo step 1. |
| WARNING: UNPROTECTED PRIVATE KEY FILE | The key is readable by others, which a zip causes. Run the chmod 600 command from step 1 again. |
| Permission denied (publickey) | Key and user do not match. ITZUSER logs in only with keys/itz-admin-key.pem; LABnn logs in only with its own LABnn.pem. Check both the -i path and the user name before the @ sign. |
| Connection timed out, or kex_exchange_identification | TechZone throttles bursts of new connections. Wait two minutes and retry; do not retry in a loop. |
| bash: command not found, on the IBM i | You typed bash. Use the full path /QOpenSys/pkgs/bin/bash as shown. |
| sudo: you are not in the sudoers file | Log in to the VM as root instead, or ask TechZone for the VM's admin password. |
| Password does not meet all password rules | The IBM i requires 15 characters. Leave the script's default password, or pass --pwprefix with a longer one. |

!! **Windows side note** On a Windows 10 or 11 laptop the same ssh and scp commands work in PowerShell. Replace ~ with C:\Users\<you> and skip the chmod command.

---

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
| 11:30 | Modes primer | 3 | Everyone can name the two IBM i modes |
| 11:33 | 0 Connect and overview | 4 | Object Browser shows DIST4nn with its source files |
| 11:37 | 1 Understand OE005 | 9 | The Y2K window has been explained to the room |
| 11:46 | 2 Blast radius and flow | 10 | Seventeen objects on screen, level check explained, diagram drawn |
| 11:56 | 3 /erd | 5 | Diagram on screen; point at the missing foreign keys |
| 12:01 | 4 Business rules | 9 | The school discount has been found |
| 12:10 | 5 Modernize | 11 | Compile message seen; price check returned |
| 12:21 | 6 Runbook and audit | 7 | Runbook on screen; one audit row |
| 12:28 | 7 Wrap-up | 2 | Hackathon topics named; 12:30 |


%end
## Key concept: modes

Spend three minutes here before Exercise 0. Modes are the concept everything else builds on.

**A mode is a persona, a toolset and a set of permissions. Same Bob, different expert.**

| Mode | Persona | Use it for |
| IBM i Developer | Senior IBM i developer | RPG, DDS, CL, modernization, compiling, workflows |
| IBM i Database | Db2 for i expert | SQL, schema, indexes, performance, /erd |
| Your own custom modes | Whatever the team needs | Onboarding, code review, shop standards |

!! **Why IBM's modes matter** Anyone can prompt an AI to act like an RPG expert. What you cannot write into a prompt is the ability to read a source member out of QSYS, compile it, or query Db2. IBM's modes ship roughly fifty encoded IBM i skills plus real tools, grounded in IBM's own documentation. A custom mode changes how Bob talks. IBM's modes change what Bob can do.

---

## Exercise 0: Connect to IBM i and have Bob write the library overview

Goal: establish the connection everything else depends on, then have Bob document the application before anyone reads a line of code.

!! **Start with an empty workspace.** In Bob choose File, then Open Folder, and pick a new, empty folder, for example one named lab-LABnn. Never open the lab kit folder or any folder that holds source. If Bob can see a local copy of the code it reads that instead of the IBM i, and the exercises stop showing what they are meant to show.

1. In Bob, click the IBM i icon (plug) in the left Activity Bar.
2. Click New Connection.
3. Enter the host, port 22 and your user profile LABnn. Leave the password empty and point the Private Key field at the LABnn.pem file your facilitator gave you. The lab IBM i accepts keys only; a password works only if your facilitator tells you they turned password login on.
4. Click Connect. On a first connection Bob asks whether to create /home/LABnn/.vscode with permissions 700: choose Yes. Then wait for the green confirmation.
5. In Object Browser click the filter icon (the funnel) to create a filter. The name is only a label; the Libraries field is what matters. Enter: Filter name DIST4nn, Filtering type Simple, Libraries DIST4nn, Objects *, Object types *ALL, Members *, Member type *, Member text *, and leave the two date fields blank. Save. The tree now shows DIST4nn with its programs, data files and six source files. If you see QGPL or only source files, edit the filter: Libraries or Object types is still at its default.
6. Right-click DIST4nn. It is already your current library because it is set on your profile; if the menu offers Set as Current Library, choose it.
7. Open the Bob chat panel, set the mode to **IBM i Developer**, and paste the prompt below, substituting your library name. Bob's own /init command only documents the folder open on your computer, which is empty on purpose, so the prompt asks for the same thing from the server.

>> Scan library DIST4nn on the IBM i. List every program, file and source member, read the source, and write a file named AGENTS.md in this workspace that describes what the application is, which programs call which, which files each program reads or writes, and the conventions you notice. Everything is on the server; do not ask me to add files.

### What it does

Bob lists the objects in your library, reads the members off the server and writes AGENTS.md into your empty workspace: what the application is, which programs call which, which files each one uses, and the conventions it found. It keeps working while you start Exercise 1. Come back and read it at the end of Exercise 1; it is the application overview nobody ever wrote. If Bob answers in the chat instead of writing the file, that is fine; the content is the same.

!! **FACILITATOR NOTE** On your own machine the kit folder is the trap: opened as the workspace, Bob answers Exercise 1 from src/ and quotes the local copy, and Exercise 5 asks for a local path instead of reporting "QSYS workspace detected". Check the first line of every Bob answer: it should name a member on the server, not a path starting with src/. The two filter mistakes everyone makes: typing the library name into the filter name and leaving Library at QGPL, and leaving the object type at the default \*SRCPF, which hides every program and file so the library looks empty. Both show up as a wrong-looking tree in step 5. If Bob asks which library to scan, give it DIST4nn. Watch the status lines: it should be listing objects and reading members on the server, not looking at local folders.

✓ **CHECKPOINT** You can expand DIST4nn and see programs (\*PGM), files (\*FILE) and source files QRPGSRC, QRPGLESRC, QDDSSRCF, QDDSSRCD and QCLSRC, and the overview is being written.

%par
---
%end

## Exercise 1: Understand a program you have never seen

Goal: get a useful explanation of unfamiliar 1998 RPG in under a minute.

?? The scenario: a customer called to dispute an invoice price. The analyst asks you how pricing works. The program that prices every line is OE005, and nobody remembers writing it.

1. In Object Browser, under your DIST4nn filter, scroll past the programs and data files to the six source folders near the bottom. They are shown in lowercase: qclsrc, qddssrc, qddssrcd, qddssrcf, qrpglesrc, qrpgsrc. Expand qrpgsrc, labelled QRPGSRC source.
2. Click oe005.rpg, labelled Price lookup, to open it. Read it for fifteen seconds. Do not worry about understanding it. The source must come from the server this way; the src folder in the lab kit on your computer holds the same code, but Bob needs to read it from the IBM i for these exercises to work.
3. Open the Bob chat panel and set the mode to **IBM i Developer**.
4. Type the prompt below.

>> What does this program do?

%fac
### What to expect

Bob identifies OE005 as a called price-lookup program. It takes customer, item, quantity and order date as parameters and returns a unit price and a one-character price source: C for contract, P for price class, L for list. It lists the four files it reads, CUSTMAST for the customer's price class and type, ITEMMAST, CONTRACT and PRICELST, and explains that catch-weight items are priced per pound times the item's average weight.

%end
%par
### What to expect

Bob should name the program's purpose, its six parameters and the four files it reads, and quote at least one detail that appears nowhere in the program itself, something it could only know by reading a file definition.

%end
### Watch Bob's status lines while it works

?? "Let me read the active file first."

?? "Now let me look at the CONTRACT and ITEMMAST file definitions to understand the fields."

!! **This is the moment worth pausing on.** Bob read the program, saw that the fields it uses are defined externally in DDS, fetched those file definitions too, and combined them. That is how it can tell you CEXPDT is a six-digit date, something that appears nowhere in the program. Pasting the program into a general-purpose chatbot would have missed it, because you would have had to know the DDS existed.

### Now go deeper

>> How does the program decide whether a contract price is still in effect?

%fac
Expected: it compares the order date to CEFFDT and CEXPDT, which are six-digit YYMMDD dates. Before comparing, it adds 1000000 to any date whose year is below 50 so that 26 sorts after 98. That is a Y2K window, and it means a contract expiring in 2050 or later will silently price at list.

%end
%par
Expected: a specific description of how two six-digit dates are compared, and the year in which the comparison stops working. If Bob does not name the year, the next prompt makes it.

%end
### Then ask about 2050

>> What happens to a contract that expires in 2050?

%fac
Expected: "This is a bug." A year of 50 or above windows to the 1900s, so a contract expiring in 2050 is treated as expired in 1950 and prices at list; Bob may add that the shop's 991231 "no expiry" contracts window to 1999 and have been pricing at list since 2000. Verified 2026-10-08.

%end
%par
Expected: Bob calls it a bug, names the year it starts, and may notice that some contracts in the file are already on the wrong side of it.

%end
!! **FACILITATOR NOTE** Expect the first answer to explain the window without naming the year; the 2050 prompt is what makes Bob say "this is a bug" and point out that the shop's 991231 no-expiry contracts are already pricing at list today. The line to land: "A two-digit year, a windowing trick, and a cliff in 2050. That is not in any spec. The person who knew it retired." Bob's proper fix, an eight-digit date in CONTRACT, is the bridge to Exercise 2: ask what that change would touch. Then scroll to the top of the source and point at the header comment: OE005 PRICE LOOKUP, D.KOWALSKI, 03/12/98. Ask the room how many programs like this they maintain.

Before moving on, open the AGENTS.md from Exercise 0 in your workspace, or scroll back to that answer if Bob gave it in the chat, and find OE005 in it. The one-line description there should match what Bob just told you.

✓ **CHECKPOINT** You can explain to the analyst where a line price comes from, without knowing RPG, and you have a written application overview you did not write.

%par
---
%end

## Exercise 2: What breaks if I change this?

Goal: see the full blast radius of a change before making it, then get the application flow drawn from the code.

?? The scenario: an acquisition means customer numbers will no longer fit in six digits. Sounds like a one-field change to CUSTMAST.

1. Stay in **IBM i Developer** mode.
2. There is nothing to set for this one. The prompt names your library and Bob scans it on its own, as it did in Exercise 0; the Object Browser has no library-level context option, and none is needed.
3. Paste the prompt below, substituting your library name.

>> If we expanded the customer number in DIST4nn from 6 to 8 digits for the acquisition, what would break? Show me every program, file and screen that carries it, and draw a diagram.

%fac
### What Bob should find

**One value. Five different names.**

| Where | It is called | Notes |
| Database file CUSTMAST | CUSTNO | the real field, 6 digits zoned |
| Logical file CUSTMSL1 | CUSNBR | renamed here, keyed by route and stop |
| Files ORDHDR and CONTRACT, and their logicals ORDHDRL1 and CONTRCL1 | OCUST, CCUST | same value, different file, different name |
| 7 RPG programs | CUST# | five chain on it via a data structure at positions 1 to 6; two, OE010 and OE011, only open ORDHDR and fail a level check after the rebuild |
| CL program TSTPRC | &CUST | a six-character test variable |
| Screens CM001DF, OE001DF and printer file RP010PF | SCUST, PCUST | what the user sees and what prints |

**Total blast radius: 17 objects.** Three physical files, three logicals, seven RPG programs, one CL program, two display files and one printer file. Bob's first answer on 2026-10-08 found 14: everything except OE010, OE011 and ORDHDRL1, which it called unaffected. The follow-ups below get the rest.

%end
%par
### What a good answer looks like

The same value under at least four different field names, across database files, logical files, programs, screens and the printer file, with a diagram, a total count and a migration order. The total will almost certainly be short by three objects; the follow-up below finds them.

%end
### Only if Bob found fewer than four names for the field

Skip this if it found the renamed fields on its own. Otherwise paste:

>> The logical file calls it CUSNBR, the order and contract files call it OCUST and CCUST, and the screens call it SCUST. Find those too and give me the new total.

### Now ask the question that catches the missing three

Bob has almost certainly listed OE010, OE011 and the logical file ORDHDRL1 as unaffected, because they never use the customer number. Paste this whether it did or not:

>> What happens to OE010 and OE011 the first night the cutoff runs after ORDHDR is rebuilt with the new format? They never use the customer number.

%fac
Expected: Bob explains that the record layout of an externally described file is frozen into an OPM program when it is compiled, so both programs must be recompiled even though their source does not change by a character, and it adds a recompile step to its migration plan. Verified 2026-10-08: it did exactly that, but described the symptom as silent corruption, OSTAT read from the wrong byte, nothing crashes, nobody notices for days. That is what happens on a file with level checking turned off. ORDHDR and ORDHDRL1 in DIST4nn have LVLCHK(*YES), the default, checked with DSPFD on 2026-10-08, so what actually happens is that the cutoff job fails at open with CPF4131, Level check on file ORDHDRL1 (OE011 opens the logical first), and ends with the CL program's own message, Cutoff FAILED for delivery date 261008, see job log, then rerun. Proven on this LPAR on 2026-10-08. Before you say so, ask the room who agrees with Bob; the RPG veterans will not, and that is the point: the fix was right, the symptom was wrong, and the platform knowledge was theirs. Then have everyone make Bob check:

%end
%par
Expected: Bob explains that the record layout of a file is frozen into each program when it is compiled, so both programs must be recompiled even though their source does not change by a character, and it adds them to the list. Now read its description of what goes wrong. If it says nothing crashes and the data quietly goes wrong, that is only true for a file whose level checking was switched off. Yours has it on, as every file does by default, so the nightly job would fail at open with a level check instead. Bob had the fix right and the symptom wrong; the platform knowledge was still yours to supply. Make it check:

%end
>> Does ORDHDR in DIST4nn have level checking on? Check the file attribute, then tell me again what actually happens the first night, and whether that changes the fix.

Expected: Bob checks the file, reports LVLCHK(*YES), corrects itself to a level-check failure at open, and keeps the same fix: recompile the two programs and rebuild the logical file.

%fac
!! **The point of this exercise** Search this code for CUSTNO and you get one file. The real answer is seventeen; it is called something different at every layer, and three of them never use the field at all. Miss one of those and the nightly job fails with a level check the first night; turn level checking off, as many shops did, and it quietly reads the wrong bytes instead.

%end
%par
!! **The point of this exercise** Search this code for the field name you know and you get one file. The real answer is much larger, because the value is called something different at every layer, and some programs are affected without ever using it. Miss one of those and a batch job fails in the middle of the night, or, if level checking was switched off, quietly reads the wrong bytes.

%end
!! **FACILITATOR NOTE** Verified 2026-10-08: the right-click menu on a library offers library-list and source-file actions only, no context option, so the prompt does the scoping. Bob's first answer searched QSYS for CUSTNO, then for the aliases, caught TSTPRC, drew the diagram and wrote the migration order unprompted. In the follow-up its byte arithmetic was also off, a one-byte shift where the zoned field grows by two, but that is beside the point. The last prompt had not been run as of 2026-10-08; confirm its answer in your walkthrough. To show the level check for real, the kit's scripts/lvlchk_demo.sh rebuilds ORDHDR with an 8-digit customer number in a scratch library LVLTEST and submits the cutoff without recompiling. Run on 2026-10-08: the job ended in under a second with CPF4131 on ORDHDRL1, RPG1216, RPG9001 and the Cutoff FAILED message, and the library was deleted afterwards. Run it the day before and keep the log; or run it with KEEP and ask Bob why job LVLCHK failed. If short on time, skip the last prompt and tell the room what the check would show.

### Now draw the flow

>> Draw the order-to-cash flow of DIST4nn as a diagram: from order entry through pricing, allocation, pick confirm and the nightly cutoff. Show which program calls which, and which files each one reads or writes.

%fac
Expected: OE001 calls OE005 for every line; OE020 writes catch weights to ORDDTL; the CL job ORDCUTOF calls OE011, which runs OE010 for every open order, then RP010 for the route sheets. Every arrow came from a CALL or an F-spec; there is no design document. Verified 2026-10-08: Bob drew all of that and added the order status lifecycle, O to A to R, pointed out that OE010 skips lines already shipped so the cutoff can be rerun after a failure, and that the CUTOFF data area is stamped last. Remember those three points: they are the restart section of the Exercise 6 runbook, and Bob has just derived them from the code.

%end
%par
Expected: a diagram that shows order entry calling the pricing program, the nightly cutoff job driving allocation and the route sheet, and the files between them. Every arrow should come from a CALL or a file declaration in the source; there is no design document.

%end
✓ **CHECKPOINT** You can name at least six programs affected by a change to one database field, including two that never use it, and you have a flow diagram of the application.

%par
---
%end

## Exercise 3: Map the database

Goal: see the second built-in mode, and generate the data model documentation that does not exist. Five minutes: run the command, look at the diagram, move on.

1. Switch the chat mode to **IBM i Database**. Note that this is a different persona, not a different tool.
2. Type the command below, substituting your library name.

>> /erd DIST4nn

### What it does

Queries Db2's own system catalogue views, SYSTABLES, SYSCOLUMNS, SYSCST and SYSREFCST, then draws the relationships, marking primary keys, foreign keys, unique constraints and cardinality. It is reading the live database, not guessing.

%fac
Expect ORDDTL in the middle, connected to ORDHDR, ITEMMAST and INVBAL, with CONTRACT and PRICELST hanging off CUSTMAST and ITEMMAST.

| Table | Rows |
| ORDDTL | 48,600 |
| ORDHDR | 9,720 |
| ITEMMAST | 2,500 |
| CUSTMAST | 400 |
| CONTRACT | 1,850 |

%end
%par
Expect eight tables with the order lines in the middle, and look at whether any foreign keys are declared at all.

%end
!! **FACILITATOR NOTE** Verified 2026-10-08: Bob ran the catalogue queries, drew all eight physical files with ORDDTL in the middle, stated that SYSCST and SYSREFCST are empty and that every relationship is implied by DDS keys and program logic, listed the basis for each one (which program chains what), left the six logical files out as access paths, and flagged PCLASS as a convention with no master table. Point at CONTRACT: the ERD shows no foreign key to CUSTMAST because there is none; referential integrity lives in the programs. Then ITEMMSZ and INVBALZ: two logical files whose only job is converting binary quantities to zoned so the OPM programs can read them. The ERD shows the clue, UNITPK, SHELFL, ONHAND and ALLOC as INTEGER. "Nobody would design that today. But it works, and it is load-bearing. That is the real problem: not rewriting, but knowing what you cannot safely touch." To have Bob say it instead of you, paste the prompt below; not yet run as of 2026-10-08.

%fac
>> Why do the logical files ITEMMSZ and INVBALZ exist, and what would break if someone deleted them?

%end

✓ **CHECKPOINT** You have a diagram of a database nobody documented, generated from the live system.

%par
---
%end

## Exercise 4: Extract the pricing rules nobody wrote down

Goal: turn the program from Exercise 1 into a rules document a pricing analyst can read. This is the exercise participants remember.

?? The scenario: the analyst from Exercise 1 is back. They do not want an explanation of the code. They want the rules, in order, in English, so they can check them against the contract with the customer.

1. Switch back to **IBM i Developer** mode.
2. In Object Browser, under DIST4nn, expand qrpgsrc and click oe005.rpg, then click its editor tab so it is focused.
3. Click the Run Workflow icon, the play triangle at the top of the chat panel. It first asks where to run the workflow: choose **Run Workflow in Library List**. The Bob workflows panel opens with thirteen workflows.
4. Scroll to the bottom and click **Start** on **Business Rules Extraction**. Not the similar one named Extract business rules higher up; that is Bob's generic workflow, and the one at the bottom is the IBM i version that reads the member off the server.
5. Click **Get Started**. Bob switches itself to IBM i Developer mode, reports "QSYS workspace detected", and asks whether to start the workflow for DIST4nn/QRPGSRC/OE005.rpg, the member in your active tab. Leave Yes selected and click **Continue**.
6. The workflow has eight steps and runs on its own for about three minutes: it parses the program, lists the four files it depends on, CUSTMAST, ITEMMAST, CONTRACT and PRICELST, extracts the rules from the main line and from the WINDOW subroutine, writes the report and draws three diagrams.
7. At the end it asks where to save the report, with an IFS path already filled in: /home/LABnn/dist4nn/docs/business-rules/OE005-business-rules.md. Accept it and click **Continue**, then click **Open File** when it reports the file saved. The file is on the IBM i, in your home folder, so you can also open it from the IFS Browser in the IBM i panel later.

!! **FACILITATOR NOTE** Verified 2026-10-08 as LAB01: play icon, then the workspace picker, then the thirteen-workflow panel, then Get Started, then the member confirmation. If someone sees "select a file" with a laptop path instead of the QSYS member question, their active editor tab is not the OE005 member: have them click the tab and start again. The workspace picker's Library List choice is what the walkthrough used.

%fac
### What to expect

Bob writes an eight-section report and opens it in the editor when you click Open File: executive summary, detailed rules, validations, calculations, decision logic, data integrity, process flow, assumptions. The rules are in section 2, one named subsection each, with a summary table at the end of the section. The six it must find, in the order the program applies them:

| # | Rule | Where it hides |
| 1 | The item must exist in ITEMMAST; otherwise the line gets source X and no price. | First chain |
| 2 | If a CONTRACT row exists for the customer and item and the order date falls between its effective and expiry dates, use the contract price. | Main loop |
| 3 | Otherwise the PRICELST row for the item and the customer's price class, source P; failing that, the list price, price class 0, source L. | Second and third lookups; one rule in Bob's report |
| 4 | Customers in price class S get a further 2 percent off any non-contract price, rounded half up. | A hard-coded compare nobody documented |
| 5 | If the item is catch-weight, multiply the per-pound price by the item's average weight to get a per-case price. | ITEMMAST CWFLAG test |
| 6 | Dates are compared with a Y2K window: years below 50 are treated as 20xx. | The WINDOW subroutine from Exercise 1 |

Verified 2026-10-08: Bob's report named all six in this order, called rule 4 "Educational Institution Price Adjustment", stated that it excludes contract prices "to avoid double discounting", drew the decision tree, and listed the 2050 century pivot under Ambiguities and Stakeholder Clarification Items. The saved report is in the kit at facilitator/OE005-business-rules.md.

%end
%par
### What to expect

Bob writes an eight-section report and opens it in the editor when you click Open File. The rules are in section 2, one named subsection each, with a summary table at the end of the section. Expect six, in the order the program applies them. Count them, then look for the one that is in no spec and could not be guessed from the screens. There is at least one.

%end
!! **FACILITATOR NOTE** Rule 4 is the payoff. Ask the room: "Is the school discount in your pricing spec?" It is not in this one either. It is in a single compare on one line of a 1998 program, and the analyst would never have found it. Then ask who would have been called at 6 pm when a school district disputed an invoice.

✓ **CHECKPOINT** You have a rules document, generated from the source, that names a rule no one in the room knew existed.

%par
---
%end

## Exercise 5: Modernize and compile

Goal: convert the 1998 fixed-format pricing program to modern free-format and build it on the server, then prove it prices the same.

!! **Before you start: in Object Browser, under DIST4nn, expand qrpgsrc, click oe005.rpg, and click that editor tab so it is focused.** The workflow runs against the active editor: an IBM i member is read off the server; anything else makes it ask for a file path on your laptop.

1. Stay in **IBM i Developer** mode.
2. With OE005 open and focused, type the prompt below.
3. Bob answers with an RPG Modernization card: click **Start workflow**. The welcome shows the pipeline it will follow, from selecting the member and detecting its type to converting to free format in a compile loop and a summary report. Click **Get Started**.
4. It detects the member in your active tab and asks whether to start the workflow for DIST4nn/QRPGSRC/OE005.rpg. Leave Yes selected and click **Continue**. It recognises OPM RPG, writes a temporary ILE fixed-format copy named OE005_T into QRPGLESRC, and starts a subagent to compile and fix that copy first.
5. Bob asks before it runs anything on the server, and the compile loop runs many commands, so answer the first prompts in the way that covers the rest. When "Tools awaiting approval" shows a CRTBNDRPG command, click **Approve for task**. When it says an SQL statement with CALL QSYS2.QCMDEXC requires explicit approval, choose **Yes, and remove "CALL" from denied SQL statement types**. Answer "once" or "just this time" and it stops at every compile.
6. When it asks you to confirm the output member location, the suggestion is DIST4nn/QRPGLESRC/OE005.RPGLE: keep **Use suggested location** and click **Continue**.
7. The free-format conversion then runs as a nine-step task: it loads its RPG skills, analyses the member, writes the conversion and compiles until clean. Expect it to rewrite the source at least once. The parameters of this program are one-field data structures, which collide with the parameter names in the new procedure interface, and Bob works that out on its own; the thinking you see is it doing so. Let it finish.

>> Can you modernize this program?

**You are in the right place if the workflow says "Active RPG Member Detected" with your library's member and never asks for a path on your computer.**

### What to expect

Bob writes free-format ILE RPG to QRPGLESRC, then compiles it on the server:

== CRTBNDRPG PGM(DIST4nn/OE005) SRCFILE(DIST4nn/QRPGLESRC) SRCMBR(OE005)

Bob's summary report ends with the compile status, severity 00, and the number of attempts it needed; five is normal for this program, because its parameters are one-field data structures that clash with the names in the new procedure interface until Bob sorts that out.

At the bottom of the chat panel, click File Changed to see the before and after diff. The Y2K window from Exercise 1 is now a free-format subroutine you can read without a column ruler. Exercise 6 will show you the new object's attribute from the catalogue.

!! **Why this exercise matters** Bob did not suggest code for you to copy somewhere. It wrote source onto the server and compiled it there; severity 00 means it built clean. The new program exists because you approved each step, and it is still RPG, still on IBM i, still called by OE001 with the same parameters.

### Now prove it still prices the same

>> Compare the original OE005 in QRPGSRC with the modernized version in QRPGLESRC. Confirm the pricing precedence is identical: contract, then price class, then list, with the catch-weight and class S adjustments. For customer 100230, item 201410, quantity 5, order date 15 October 2026, what unit price and price source does each version return?

%fac
Correct answer: both versions return 42.50, source C; customer 100230 (Lakeside Diner) has a contract on item 201410 at 42.50 for all of 2026.

%end
%par
Bob should report that both versions return the same unit price and the same price source for that customer and item.

%end
### Only if Bob reports a difference

That is a real finding, not a lab error. Paste:

>> Show me the line in each version that produces the different result, side by side, and tell me which one is wrong.

!! **FACILITATOR NOTE** The data loader seeds that contract row on purpose so this check is deterministic. If asked about automated tests: two RPGUnit workflows ship with the product, Test Plan Creation and Test Suite Implementation, and OE005 is an ideal target. Running the tests needs RPGUnit installed on the LPAR, a one-time setup that is not part of this lab.

✓ **CHECKPOINT** A program written in 1998 has been converted, compiled and verified against a known price, with a reviewable diff.


## Exercise 6: Runbook and audit evidence

Goal: produce the two documents operations and audit keep asking for, from the system itself.

?? The scenario: the nightly cutoff job failed at 2 am last month and the only person who knew how to restart it was on vacation. Operations wants a runbook. Separately, internal audit wants to know what changed in this library this quarter and who changed it.

### Part A: the runbook

1. Stay in **IBM i Developer** mode.
2. In Object Browser, under DIST4nn, expand the folder qclsrc, labelled QCLSRC source, and click ordcutof.clp, labelled Nightly order cutoff, to open it.
3. Type the prompt below. This is the longest single answer Bob writes in the lab, about two minutes, with a flowchart and SQL checks at the end. If a red Request Failed box appears instead, click **Retry**: the failure is on Bob's service side, not in your prompt, and a retry or two gets through.

>> Write a runbook for this nightly job for the operations team: what it does step by step, what must be true before it runs, what each step's failure looks like on the job log, and how to restart safely from each step without allocating any order twice.

### What to expect

%fac
Bob reads the CL and the programs it calls, then writes a four-step runbook: check the CUTOFF data area is not already set for the delivery date; call OE011, which runs OE010 for every open order on that date; call RP010 to print route sheets, held on the job's output queue; set the orders to status R and stamp the data area. The restart section should say that step 2 is safe to re-run because OE010 skips lines that already have an allocated quantity, and that step 3 can be re-run after clearing the spooled files.

%end
%par
Expect a four-step runbook, guard, allocate, print, close out, that says for each step whether it is safe to run again and why, and cites the line in the source that makes the rerun safe. A good answer goes one better. The header comment in OE010 claims a rerun is always safe, but the program updates the inventory balance before it saves the line's shipped quantity, so a job that dies between those two writes leaves one line that a rerun would allocate twice. If Bob reports that exception and tells operations how to check for it, it is right, and it found something the comment got wrong.

%end
!! **FACILITATOR NOTE** Ask who in the room could have written that restart section from memory. Then point out that the "safe to re-run" claim is not an opinion: Bob found the allocated-quantity test in OE010 and cited the line. If Bob does not cite it, ask "How do you know step 2 is safe to re-run? Show me the line in OE010."

### Part B: the audit evidence

1. Switch the chat mode to **IBM i Database**.
2. Type the prompt below, substituting your library name.

>> Which objects in DIST4nn were created or changed today? For each one show the user who created it, the owner, when it was created, the source file and member it was built from, and the program attribute.

### What to expect

Two rows. The first is OE005: type *PGM, attribute RPGLE, created today by LABnn, your own profile, built from DIST4nn/QRPGLESRC member OE005. The second is the source file QRPGLESRC itself, still created by the facilitator's profile on the build date but changed today, because the workflow added and removed members in it. Bob may add that the temporary member and program OE005_T were created and deleted during the workflow, so they no longer appear, and that for an ILE program it took the source location from the bound module rather than the object description. Every other object in the library was created by the facilitator's profile on the build date from QRPGSRC. Bob is reading the object statistics from the QSYS2 catalogue services, the same data an auditor would ask you to export.

!! **Why this exercise matters** Together with the diff and the approval trail from Exercise 5, that row is the audit evidence: who, what, when, from which source, and what changed. Bob gathers the evidence and writes the documents. It is not a compliance tool and the guide does not claim it is; the controls are still yours.

%fac
### Facilitator demo: the live job table

!! **FACILITATOR DEMO, if there is a minute** In the same mode, paste the prompt below. Bob queries the live job table and answers. Say plainly that this is a one-off question, not monitoring; the operational intelligence use case starts here but needs a scheduled process around it.

>> What jobs are running on this system right now, and which five are using the most CPU?

%end

✓ **CHECKPOINT** You have a runbook for a job you did not write, and an audit row for a change you did make.

%par
---
%end

## Exercise 7: Wrap-up and hackathon starting points

Six things participants just did, none of which base Bob can do:

1. Had Bob write an overview of a whole library from the server, and read source directly off IBM i with no copy-paste.
%fac
2. Traced a customer-number change across seventeen objects, through four renames and three programs that never use the field, and drew the application flow from the code.
%end
%par
2. Traced a customer-number change across every object that carries it, under every name it uses, and drew the application flow from the code.
%end
3. Generated a database diagram from the live system catalogue.
%fac
4. Extracted six pricing rules from a 1998 program, including one nobody knew about.
%end
%par
4. Extracted the pricing rules from a 1998 program, including one nobody knew about.
%end
5. Modernized and compiled that program on the server, with approval at each step, and proved it prices the same.
6. Wrote a runbook for the nightly job and pulled the audit evidence for the change, from the system itself.

### Starting points for the hackathon

Each of these runs in the same DIST4nn library and picks up where an exercise left off.

| Topic | Starts from | What you would do |
| Library-wide dependency map | Exercise 2 | Open the Understand Dashboard, create an application for DIST4nn, run the scan, and compare its dependency graph to what Bob found by hand. |
| Prove it with tests | Exercise 5 | Run the RPGUnit Test Plan Creation workflow on OE005, then Test Suite Implementation. The six rules from Exercise 4 are the test cases. |
| Your own reviewer | Exercise 5 | Build a custom mode in the ibm-i-developer group called Shop Standards Reviewer with your team's rules, and have it review the modernized OE005. |
| Make the cutoff faster | Exercise 6 | Give the order-selection query from ORDCUTOF to /review, then run the Index Advisor workflow and apply its recommendation. |
| Operational intelligence | Exercise 6 | Have Bob write a SQL service query for jobs, locks or spool backlog, then schedule it with the job scheduler and route the output to a data queue or email. |
| Green screen to web | Exercise 1 | Generate a React page for inventory inquiry against IN001's files, running on the LPAR in PASE. |

---

## Troubleshooting

| Symptom | Cause and fix |
| Bob's answer starts with "Read file src/..." | Bob is reading a local copy from its workspace. Open an empty folder as the workspace, reconnect, ask again. |
| IFS Browser shows /home/ITZUSER with a warning | The connection's home directory was copied from another connection. In the connection settings set Home Directory to /home/LABnn; the workflows write there. |
| Bob says "paste the source code here" | Not connected. Reconnect via the IBM i icon. Most common issue in this lab. |
| "IBM i MCP tools are currently disabled" | Same cause: no active IBM i connection. |
| Object Browser shows QGPL, or looks empty | The filter's Library field is still QGPL, or its object type is still \*SRCPF. Edit the filter: Library DIST4nn, object type \*ALL. |
| Workflow asks for a local file path | The active editor is not an IBM i member. Cancel, click the OE005 tab, re-run. |
| Business Rules Extraction is not in the Bob workflows panel | Premium Package not fully installed. Fall back to the prompt "List every business rule in this program, numbered, in order" in IBM i Developer mode. |
| /erd returns nothing | Reconnect the IBM i connection and retry. |
| Your library shows changes you did not make | You connected with someone else's profile. Profile and library numbers must match your ID. Reconnect as LABnn. |
| The Exercise 0 prompt says the workspace is empty and asks for files | Bob read the prompt as being about the local folder. Make sure the mode is IBM i Developer and the prompt names DIST4nn on the IBM i; if it persists, ask it to list the objects in DIST4nn first. |
| A red Request Failed box with AI_APICallError | Bob's model service failed, not your prompt or your connection. Click Retry; it can take two or three tries. Anything Bob already wrote is kept: click Show all next to files changed. |
| Audit query in Exercise 6 returns no rows | Exercise 5 did not recompile, or you are in a different library, or the IBM i clock runs on UTC and has already passed midnight. Ask for "in the last 24 hours" instead; ask for "since the library was built" to see the facilitator's rows. |
| Compile fails in Exercise 5 | Do not debug live. Show the diff instead; the generated code is still the point. |
| Modes selector missing IBM i modes | Premium Package not enabled. The lab cannot run without it. |

**Exercises 2, 3 and 6A are independent. Exercises 4 and 5 build on 1; if 1 fails, open OE005 and move on. Exercise 6B needs the recompile from Exercise 5.**

%fac
---

## Questions participants ask

Scripted answers for the questions that come up in every session. The last one matters most.

**"Does it change code without asking?"**

?? No. Every step is approval-gated, as you saw in Exercise 5.

**"How is this different from Copilot or ChatGPT?"**

?? They cannot see your system: no reading a source member, no Db2, no compile. You would copy-paste, and they do not know IBM i conventions.

**"Where does our code go?"**

?? Bob connects over SSH to your own machine and reads source from there. [Insert IBM's exact statement on where inference runs, what is retained and the training opt-out before the lab. Do not improvise this answer.]

**"Our system is bigger than this. Can it handle our whole codebase?"**

?? Start with one program, prove it, then scale; that is what the workflows are for. The Understand Dashboard scans a whole library; ask for a follow-up session on that.

!! **If you do not know an answer: "Let me get you the exact answer instead of guessing." Never invent a capability.**

%end