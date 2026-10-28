# DIST400: a sample IBM i order-to-cash application for the Bob for i lab

DIST400 is a small but complete foodservice-distribution system written the way an IBM i shop would have written it in 1998: fixed-format RPG III, DDS files and screens, and a CL nightly job. It exists so that a hands-on lab can show what IBM Bob and the Bob Premium Package for i do with real legacy code: explain it, map its dependencies, extract its business rules, write its runbook, gather audit evidence, and modernize it to free-format RPG while proving the behaviour did not change. Nothing in it is customer code. Everything in it is deliberately a little old-fashioned, and some of it is deliberately wrong in instructive ways.

This folder is the whole kit: the source, a deterministic data loader, a save file of the built library, the scripts that build, clone and reset it, the two lab guides, and the keys to the lab LPAR. Participants receive only three things from it: the Participant Guide and the prompts file from `docs/`, and their own key file. The rest is for whoever stands the lab up. If you are reading this cold, start with "What the application does" and "Quick start by role".

## What this is for

A one-hour facilitator-led lab (Lab 2 of a Bob workshop) for IBM i developers at a food distributor. Each participant gets their own copy of the library and works through seven exercises in Bob, each mapped to a use case the client asked about:

| Exercise | What the participant does | Use case |
|---|---|---|
| 0 | Connect Bob to the IBM i and have it write an AGENTS.md overview of the library from the server (Bob's /init only documents the local workspace, verified 2026-10-08) | Application documentation generation |
| 1 | Ask Bob what OE005, the pricing program, does; then how it decides a contract is still in effect | Code documentation generation |
| 2 | Ask what breaks if the customer number grows from 6 to 8 digits; have Bob draw the application flow | Interface and dependency mapping; application flow documentation |
| 3 | Run /erd to diagram the database from the live catalogue | Data model documentation |
| 4 | Run the Business Rules Extraction workflow on OE005 | Business process documentation |
| 5 | Run the RPG Modernization workflow on OE005, compile on the server, prove it prices the same | Modernization with an audit trail |
| 6 | Have Bob write the runbook for the nightly cutoff job, then query who changed what today | Operational documentation; audit evidence |
| 7 | Wrap-up and hackathon starting points | |

The guides are in `docs/`: the Participant Guide (the exercises, every prompt, and what a good answer looks like; the facilitator runs the hour from it too) and the Facilitator Guide (environment setup, day-before checks and the hour's clock only; it does not change when the exercises do). Both are built from `guide-source/lab.md`.

## What the application does

A broadline foodservice distributor sells cases of food to restaurants, schools and hospitals. The flow DIST400 implements:

1. **Customer maintenance** (CM001): customers have a route and stop for delivery, delivery days, and a price class: R restaurant, S school, H healthcare.
2. **Order entry** (OE001): a clerk keys a customer, then one item and quantity at a time. Every line is priced by calling **OE005**, the price lookup. F6 accepts the line; the first accepted line creates the order header. Orders start in status O, open.
3. **Pricing** (OE005): contract price if the customer has a contract for the item that is in effect on the order date; otherwise the price for the customer's price class; otherwise list price. Catch-weight items (meat, cheese: sold by the pound, real weight unknown until picked) are priced per pound times the item's average case weight. Schools get a further 2 percent off anything that is not a contract price. Dates are six-digit YYMMDD compared through a Y2K "window".
4. **Nightly cutoff** (ORDCUTOF, a CL job, called with the delivery date as six characters): refuses to run twice for the same date using the CUTOFF data area; calls **OE011**, which calls **OE010** for every open order on that date; OE010 allocates stock from warehouse 01 line by line, tries the substitute item from SUBITEM when short, marks shipped quantities, and sets the order to A, allocated; then **RP010** prints a route sheet per route, held on the output queue; then the orders are set to R, routed, and the data area is stamped. Rerunning after a failure is safe because OE010 skips lines already allocated.
5. **Pick confirm** (OE020): the picker keys order and line and the scale weight for catch-weight items. This screen reads function keys from the workstation feedback area byte 369 instead of indicators, which is the "position 369" archaeology from the original FLIGHT400 lab.
6. **Inventory inquiry** (IN001): on hand, allocated and available for an item. The one program written in RPG IV fixed-format, dated 2004 in its header, reading through the binary-to-zoned logical files.

```
OE001 order entry ──► OE005 price lookup ──► CUSTMAST, ITEMMAST, CONTRACT, PRICELST
      │ writes ORDHDR, ORDDTL
ORDCUTOF (CL, nightly) ──► OE011 ──► OE010 per open order ──► ORDDTL, INVBALZ, SUBITEM, ORDHDR
                        ──► RP010 route sheets ──► RP010PF (printer)
                        ──► RUNSQL: status R; CHGDTAARA CUTOFF
OE020 pick confirm ──► ORDDTL (catch weight)       CM001 ──► CUSTMAST       IN001 ──► ITEMMSZ, INVBALZ
```

## How it is built

**Objects in the library** (37 plus the library itself):

| Kind | Members | Notes |
|---|---|---|
| Physical files (DDS, `src/QDDSSRCF`) | CUSTMAST, ITEMMAST, INVBAL, CONTRACT, PRICELST, SUBITEM, ORDHDR, ORDDTL | Keyed. No foreign keys are declared anywhere; integrity lives in the programs, which the ERD exercise makes visible |
| Logical files (`src/QDDSSRC`) | CUSTMSL1 (by route and stop, renames CUSTNO to CUSNBR), ITEMMSZ and INVBALZ (redefine binary fields as zoned, a 1990s workaround the OPM programs depend on), CONTRCL1, ORDHDRL1 (by delivery date, route, stop), ORDDTLL1 (by item) | |
| Display files (`src/QDDSSRCD`) | OE001DF, OE020DF, CM001DF, IN001DF | 24x80, numeric fields use keyboard shift Y |
| Printer file | RP010PF | Route sheet: header per route, line per stop, line per order line, total |
| RPG III programs (`src/QRPGSRC`, compiled with CRTRPGPGM) | OE001, OE005, OE010, OE011, OE020, CM001, RP010 | OPM, fixed-format, column-exact |
| RPG IV program (`src/QRPGLESRC`, CRTBNDRPG) | IN001 | Fixed-format ILE, the "rewritten in 2004" one |
| CL programs (`src/QCLSRC`) | ORDCUTOF (the nightly job), TSTPRC (a command-line harness that calls OE005 and writes the answer to data area TSTPRC) | |
| Data areas | CUTOFF (*DEC 6,0: last delivery date cut off), TSTPRC (*CHAR 80: last harness result) | |

**Conventions worth knowing before you touch the code**

- Every program parameter is a one-field data structure (PCUSTD, PORDD, PDATED and so on) and callers Z-ADD values into zoned DS fields before each CALL. In RPG III every numeric field that is not a DS subfield is held packed inside the program, while screens, files and CL character variables exchange zoned digits. Pass a file field or a screen field straight through and the callee dies with RPG0907, decimal data error. The first build of this kit did exactly that.
- CL calls the RPG programs with character parameters: `CALL ORDCUTOF PARM('261008')`, `CALL TSTPRC PARM('100230' '201410' '00005' '261015')`. CL *DEC variables are packed and would not match.
- The customer number travels under five names: CUSTNO in CUSTMAST, CUSNBR in CUSTMSL1, OCUST in ORDHDR, CCUST in CONTRACT, CUST# in a data structure at positions 1 to 6 in five programs, and SCUST and PCUST on screens and the route sheet. That is the Exercise 2 blast radius: 17 objects, counting TSTPRC and the two programs that only open ORDHDR.
- Externally described printer files in RPG III need a numeric overflow indicator (RP010 uses 99); display-file numeric fields that carry EDTCDE need keyboard shift Y; record-level printer keywords go on the record line. All three cost a compile round once.
- Header comments carry a fictional author and 1998 dates, plus "MOD" lines for the Y2K window (1999) and the school discount ("PER R.MARTIN, NO TICKET", 2001). Bob finds and quotes these; they are part of the story.

**Sample data** (`data/loaddata.sql`, run by the build with RUNSQLSTM; no random functions, so every build is identical):

| Table | Rows | Shape |
|---|---|---|
| CUSTMAST | 400 | Customers 100001 to 100400, routes 1 to 20, stops 1 to 20; every 10th customer is class S, the next is H, the rest R |
| ITEMMAST | 2,500 | Items 200001 to 202500 in 25 product families; the first 7 of every 25 are proteins: catch weight, cooler zone |
| INVBAL | 2,500 | Warehouse 01; every 37th item has zero on hand so substitution fires |
| PRICELST | 10,000 | Four price classes per item: 0 list, R, S, H |
| SUBITEM | 300 | Every 8th item substitutes to item + 25 |
| CONTRACT | 1,850 | 1,849 generated plus one seeded; every 40th expired in 2025; every 185th carries the shop's "no expiry" value 991231, which the Y2K window reads as 1999 |
| ORDHDR | 9,720 | 135 orders per delivery date from 10 August to 20 October 2026; dates from 7 October on are status O, earlier ones R |
| ORDDTL | 48,600 | Five lines per order |

Seeded rows the guides depend on: customer 100230 LAKESIDE DINER (class R), item 201410 TOMATO DICED CND 6/#10 (not catch weight), and a contract between them at 42.50 effective 260101 to 261231. The Exercise 5 verification asks Bob what both versions of OE005 return for that pair on 261015: 42.50, source C.

## Kit layout

| Path | What it is |
|---|---|
| `src/` | All source members, one folder per IBM i source file. The file extension is the member's SRCTYPE (pf, lf, dspf, prtf, rpg, rpgle, clp). Line 1 of every member carries `**TEXT:` which the build uses as member text |
| `data/loaddata.sql` | The data loader |
| `DIST400.savf` | The built library, saved 2026-10-07 with pristine data, 3.2 MB. Restoring this is the normal way to stand the lab up; building from source is only needed if you change the code |
| `scripts/build_dist400.sh` | Builds the library from `src/` on an IBM i, loads the data, saves to `DIST400.savf` |
| `scripts/setup_dist400_lab.sh` | Restores the master from the save file, creates one profile and one library copy per participant, writes the participant table, optionally generates one SSH key per participant (`--keys`) |
| `scripts/reset_dist400_user.sh` | Puts one participant (or ALL) back to the starting point |
| `scripts/reseed_dist400.sh` | Reloads the master's data, zeroes CUTOFF, re-saves; use after exercising the master |
| `scripts/smoke.sh` | The batch verification: five pricing checks through TSTPRC and a full cutoff for 261008 with database checks after each step |
| `scripts/sshd_maxstartups.sh` | Optional: raises the IBM i sshd limit on simultaneous logins for a room of 20+ and reloads sshd without dropping sessions |
| `scripts/lvlchk_demo.sh` | Optional facilitator demo for Exercise 2: copies DIST400 to a scratch library LVLTEST, rebuilds ORDHDR with an 8-digit customer number, submits the nightly cutoff without recompiling and prints the job log, then cleans up. Never touches DIST400 or DIST4nn. Verified 2026-10-08: CPF4131 on ORDHDRL1, Cutoff FAILED, the job ends in under a second. The copy already on the LPAR predates a fix in this one; the scp in Facilitator Guide step 4 replaces it. |
| `keys/` | `README.txt` with the IBM i address and user names, `itz-admin-key.pem` (logs in as ITZUSER only) and `LAB01.pem` (logs in as LAB01 only). After unzipping run `chmod 600 keys/*.pem`; a zip drops that protection and ssh refuses an unprotected key. Participant keys the setup script generates are copied into `keys/participants/` |
| `docs/` | Participant Guide and Facilitator Guide (docx, pdf and md) and the plain-text prompts file |
| `guide-source/` | `lab.md`, the single source of both guides; `build2.js`, the Word builder; `gen_md.py`, which writes the Markdown editions of both guides; `gen_prompts.py`, which writes the prompts file from the guide's command and prompt lines; `gen_dds.py`, `gen_rpg.py`, `specs.py`, the column-exact generators that produced every DDS and RPG member; `xref.py`, a static check that every field a program uses is defined |
| `facilitator/` | One sample output, nothing the lab needs: `OE005-business-rules.md`, the report the Business Rules Extraction workflow wrote during the 2026-10-08 walkthrough, for anyone who asks what the workflow produces. |

## Status, as of 2026-10-08

- Built and verified on an IBM i 7.6 TechZone LPAR on 2026-10-07: all 37 objects compile, the data loads with the counts above, and `smoke.sh` passes in full: pricing correct on five rule paths (contract, class with the school discount, catch weight, the Y2K cliff, unknown item) and the cutoff for 261008 routes all 135 orders, ships 658 lines, leaves 17 short, substitutes 1, allocates 657 items and refuses a second run.
- Walked end to end in the Bob IDE as participant LAB01 on 2026-10-08, Exercises 0 to 6, against DIST401 on the LPAR named in `keys/README.txt`. Every step the Participant Guide says to click or paste was corrected to what the product actually shows: Exercise 0's server-side scan prompt (Bob's /init documents only the local workspace, even in IBM i Developer mode), the Object Browser filter fields, the workflow picker and panel for Business Rules Extraction (all six rules found), the approval choices in RPG Modernization (compiled clean on the fifth attempt, which is normal for this program), the runbook (Bob also found the rerun gap in OE010 that the header comment denies) and the audit query (two rows: OE005 and QRPGLESRC). Bob's chat failed twice with "Request Failed, AI_APICallError" on the runbook prompt and succeeded on the third try; the guide tells participants to click Retry.
- Not yet verified: the four screen programs (they need a 5250 session), the Exercise 2 follow-up that asks Bob to check LVLCHK on ORDHDR, and the output of the Exercise 5 comparison prompt (it was run but not captured). The LPAR clock runs on UTC, so "today" in the audit query rolls over at 7 pm US Central; that cannot bite an 11:30 lab and is covered in the guide's troubleshooting table.
- The LPAR in `keys/README.txt` already holds the master DIST400 and participant LAB01 with DIST401, and DIST401 has been through the whole lab, so its OE005 is the recompiled free-format version. Before anyone walks the lab as LAB01 again, run `scripts/reset_dist400_user.sh 01` as ITZUSER, or add fresh IDs with the setup script, which skips the ones that exist.
- `keys/` holds private keys to the live lab LPAR, by design, so that every command in the guides works straight from the unzipped folder. Keep the kit inside the team and do not post it anywhere public. If you reserve a new LPAR, replace `keys/itz-admin-key.pem` with that reservation's key and update `keys/README.txt`.

## Quick start by role

**Facilitator standing up a lab.** Follow the Facilitator Guide in `docs/`, section "Before the lab". The short version, from a terminal on a RHEL VM or a Mac, with the kit unzipped to ~/Downloads/DIST400:

```
chmod 600 ~/Downloads/DIST400/keys/*.pem
scp -i ~/Downloads/DIST400/keys/itz-admin-key.pem -r ~/Downloads/DIST400 ITZUSER@<IP address>:/home/ITZUSER/
ssh -i ~/Downloads/DIST400/keys/itz-admin-key.pem ITZUSER@<IP address>
```

then on the IBM i run

```
/QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/setup_dist400_lab.sh -f /home/ITZUSER/DIST400/DIST400.savf -n 23 --keys
```

for 20 participants and 3 spares. It restores the master, creates LAB01 to LAB23 and DIST401 to DIST423, prints the participant table and writes one key file per person into `/home/ITZUSER/DIST400/scripts/keys/`. TechZone IBM i images ship with SSH password login off, so keys are the default; the script prints how to enable passwords if you prefer. Then, from your own terminal again, copy the keys back into the kit; they land in `keys/participants/`, one LABnn.pem per person, which is what you hand out:

```
scp -i ~/Downloads/DIST400/keys/itz-admin-key.pem -r ITZUSER@<IP address>:/home/ITZUSER/DIST400/scripts/keys ~/Downloads/DIST400/keys/participants
```

The script makes a key only for a participant that does not exist yet and never overwrites one, so rerunning it after adding IDs is safe and the copy-back picks up every key, old and new. On the LPAR in `keys/README.txt`, LAB01 already exists and its key is the `keys/LAB01.pem` shipped in the kit.

**Facilitator walking the lab before running it.** Reset LAB01 first, or take a fresh ID. In Bob, open an empty folder as the workspace, connect as LABnn with that key, and follow the Participant Guide from Exercise 0; the Facilitator Guide is only for the setup above. Each exercise says what a good answer looks like, and the Troubleshooting table at the end covers everything that went wrong on 2026-10-08.

**Developer changing the application.** Edit the generators in `guide-source/` and rerun them, or edit the members in `src/` directly (then the generators are stale; say so in a commit). Run `python3 guide-source/xref.py` to catch undefined fields. Copy the kit to the IBM i and run `scripts/build_dist400.sh` under the PASE bash, detached with nohup; it compiles in dependency order, stops at the first failure with the diagnostic lines, loads the data and saves. Then run `scripts/smoke.sh` the same way and compare with the numbers above. Anything the guides quote (seeded rows, counts, the 17 objects, the six rules, the cutoff numbers) must still hold, or the guides must change.

**AI assistant asked to work on this.** Read `guide-source/lab.md` first; its What to expect sections and the FACILITATOR notes in the source say what is planted in the code and what Bob should find. The conventions above are not optional; RPG III column positions and the packed-versus-zoned rule are where every previous failure came from. All verification is scripted: `smoke.sh` for behaviour, `xref.py` for references, the row counts for data. The IBM i quirks below are real and will cost you a session if ignored.

## Working on the LPAR over SSH

Learned on the TechZone box, 2026-10-07:

- The login shell is the old Bourne shell. Run every script with `/QOpenSys/pkgs/bin/bash`.
- Every `system` call is a forked child job, so a `CHGLIBL` inside one call does not carry to the next. The scripts use the PASE bash builtin `liblist -a LIB` in the parent shell instead; children inherit it.
- An attached ssh session tends to drop right after the first `system` call that follows `liblist`. The same script started with `nohup /QOpenSys/pkgs/bin/bash script.sh > /tmp/x.log 2>&1 < /dev/null &` runs to completion. Launch build, smoke, reseed and setup that way and read the log afterwards.
- Bursts of separate ssh or scp connections make port 22 unreachable for a few minutes. Use one multiplexed connection (`ControlMaster auto` with a short `ControlPath` under `~/.ssh`) for everything.
- `/usr/bin/db2` cannot be executed from PASE bash. Query with `qsh -c 'db2 "SELECT ..."'`.
- RPG/400 compiler messages are in `QDEVTOOLS/QRPGMSG`: `system "DSPMSGD RANGE(QRG2014) MSGF(QDEVTOOLS/QRPGMSG) DETAIL(*FULL)"`.
- `system` copies any spooled output of the command to stdout and deletes it, so compile listings are in the captured output and route sheets print to the terminal when the cutoff is run that way. In a 5250 or submitted job they are held as ROUTESHEET.
- Completion messages from called programs do not show through `system`; TSTPRC writes its result to data area TSTPRC for that reason.
- Password rules on the TechZone image: level 4, minimum 15 characters, profile name not allowed inside; the setup script's default `Foodservice-2026-nn` complies. Quote passwords with hyphens in CL.
- PASE `grep` has no `-o`; use `awk`. The login shell cannot do `$((n+1))` arithmetic either, so feed multi-line work to `/QOpenSys/pkgs/bin/bash -s <<'EOF'` over ssh.
- The system clock is UTC. Catalogue timestamps and "today" in SQL follow it, not your laptop.

## Build the master from source

```
/QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/build_dist400.sh
```

Creates DIST400 and its six source files, uploads every member from `src/`, compiles PF, LF, DSPF, PRTF, RPG, RPGLE and CLP in that order, creates the data areas, runs the loader, prints the row counts and saves to `DIST400.savf`. On a failure it prints the error lines from the listing and stops; fix the member and rerun, everything already built is replaced.

## Smoke test

```
nohup /QOpenSys/pkgs/bin/bash /home/ITZUSER/DIST400/scripts/smoke.sh > /tmp/smoke.out 2>&1 < /dev/null &
```

Expected in `/tmp/smoke.out`: five TSTPRC lines ending `PRICE=0004250 SRC=C`, `PRICE=0007184 SRC=P`, `PRICE=0063469 SRC=P`, `PRICE=0008377 SRC=P`, `PRICE=0000000 SRC=X`; then "Cutoff complete for delivery date 261008", 135 orders in status R, 658 shipped, 17 short, 1 substitution, 657 items allocated, data area 261008, and "Cutoff already run" on the second call. Afterwards run `scripts/reseed_dist400.sh` to put the master back and re-save.

The screen programs need a 5250 session (Bob's terminal or any emulator): `ADDLIBLE DIST400`, then `CALL OE001` (customer 100230, item 201410, qty 5, F6: 42.50 source C), `CALL OE020`, `CALL IN001`, `CALL CM001`.

## Set up a lab and reset participants

See Quick start above. Reset one participant: `/QOpenSys/pkgs/bin/bash scripts/reset_dist400_user.sh 07`, or `ALL`. Rerunning setup is safe: existing participants are skipped with their passwords and keys untouched, so `-n 24` after `-n 23` adds only number 24; `--pwreset` issues passwords again; `--force` rebuilds existing participant libraries.

## Rebuilding the guides

Edit `guide-source/lab.md` only; the Word, PDF and Markdown files are generated from it. Line tags: `$$` a terminal command box, `>>` a prompt box to paste into the Bob chat, `==` an expected-output box, `!!` a callout, `✓` a checkpoint, `??` an italic scenario line, `---` a page break, `|` table rows. Audience regions: `%par` to `%end` is participant-only, `%fac` to `%end` facilitator-only, and any callout starting `!! **FACILITATOR` is facilitator-only. The Facilitator Guide is the setup document: the builder stops it at the heading "Key concept: modes", so nothing from the exercises onward appears in it and it does not change when the exercises do. The `%fac` regions inside the exercises are kept in the source as notes only and render nowhere.

Build with Node and version 9 of the `docx` package (`npm install docx@9` in `guide-source/`, or in a scratch folder holding copies of the two files; version 8 writes files that Word flags for repair):

```
node build2.js lab.md "Bob4i - Foodservice Distribution Use Case - Participant Guide.docx" participant
node build2.js lab.md "Bob4i - Foodservice Distribution Use Case - Facilitator Guide.docx" facilitator
python3 gen_prompts.py lab.md "Bob4i - Foodservice Distribution Use Case - Prompts and Commands.txt"
python3 gen_md.py lab.md "Bob4i - Foodservice Distribution Use Case - Participant Guide.md" participant
python3 gen_md.py lab.md "Bob4i - Foodservice Distribution Use Case - Facilitator Guide.md" facilitator
```

Convert to PDF with LibreOffice (`soffice --headless --convert-to pdf`), check that no page is nearly empty, and copy all seven files into `docs/`. The Markdown editions need no packages: `gen_md.py` reads `lab.md` with the same audience rules as `build2.js`, so each says exactly what its Word file says, with prompts and commands in fenced blocks under the same captions. The prompts file is for the room: it lists only the `$$` and `>>` lines participants see, from "Key concept: modes" onward and outside `%fac` regions, grouped by heading, so it changes only when a participant command or prompt does.

## Dry run checklist for a new facilitator

- Run every prompt in the Participant Guide in a fresh DIST4nn as a LABnn profile, not as admin, from an empty workspace folder in Bob.
- Record where the Exercise 0 overview and the two workflows write their files. On 2026-10-08 that was AGENTS.md in the workspace, the rules report under `/home/LABnn/dist4nn/docs/business-rules/` on the IFS, and member OE005 in QRPGLESRC; if anything lands elsewhere, add it to the reset script.
- Confirm Business Rules Extraction lists the six rules in the guide's Exercise 4 expectations, especially the class S discount (it did on 2026-10-08).
- Confirm RPG Modernization writes OE005 to QRPGLESRC and compiles with severity 00. Five attempts is normal: the one-field parameter data structures clash with the procedure-interface names until Bob renames them.
- Confirm the Exercise 6 audit prompt returns two rows, OE005 created by the participant's profile and QRPGLESRC changed today.
- Fix the guide where Bob's real output differs, rebuild the Participant Guide, and leave the Facilitator Guide alone unless a setup step changed.
