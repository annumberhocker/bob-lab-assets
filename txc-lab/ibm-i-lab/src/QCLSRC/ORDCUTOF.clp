/* **TEXT:Nightly order cutoff                                                 */
/*                                                                             */
/*  ORDCUTOF - NIGHTLY ORDER CUTOFF                        DKOWALSKI  06/11/98 */
/*  CALL ORDCUTOF PARM('YYMMDD')      DELIVERY DATE, SIX CHARACTERS            */
/*  1. REFUSE TO RUN TWICE FOR THE SAME DATE (DATA AREA CUTOFF)                */
/*  2. ALLOCATE EVERY OPEN ORDER FOR THE DATE (OE011 -> OE010)                 */
/*  3. PRINT THE ROUTE SHEETS (RP010)                                          */
/*  4. SET THE ORDERS TO ROUTED AND STAMP THE DATA AREA                        */
/*  RERUN AFTER A FAILURE: STEP 2 IS SAFE, OE010 SKIPS ALLOCATED LINES.        */
/*  STEP 3 JUST PRINTS AGAIN. DELETE THE HELD ROUTESHEET SPOOL FILES FIRST.    */
/*  THE DATE IS PASSED AS CHARACTER BECAUSE THE RPG PROGRAMS EXPECT A ZONED    */
/*  6,0 PARAMETER AND CL *DEC VARIABLES ARE PACKED.            DK 06/11/98     */
             PGM        PARM(&DLVDT)
             DCL        VAR(&DLVDT)  TYPE(*CHAR) LEN(6)
             DCL        VAR(&DLVDTN) TYPE(*DEC)  LEN(6 0)
             DCL        VAR(&LAST)   TYPE(*DEC)  LEN(6 0)
             DCL        VAR(&SQL)    TYPE(*CHAR) LEN(256)
             MONMSG     MSGID(CPF0000) EXEC(GOTO CMDLBL(FAILED))

             CHGVAR     VAR(&DLVDTN) VALUE(%DEC(&DLVDT 6 0))

/* STEP 1: HAS CUTOFF ALREADY RUN FOR THIS DELIVERY DATE?                      */
             RTVDTAARA  DTAARA(CUTOFF) RTNVAR(&LAST)
             IF         COND(&LAST *EQ &DLVDTN) THEN(DO)
                SNDPGMMSG  MSGID(CPF9898) MSGF(QCPFMSG) +
                           MSGDTA('Cutoff already run for delivery date' +
                           *BCAT &DLVDT) MSGTYPE(*ESCAPE)
             ENDDO

/* STEP 2: ALLOCATE STOCK TO EVERY OPEN ORDER FOR THE DATE                     */
             CALL       PGM(OE011) PARM(&DLVDT)

/* STEP 3: PRINT ROUTE SHEETS, HELD ON THE JOB OUTQ FOR THE SHIPPING OFFICE    */
             OVRPRTF    FILE(RP010PF) OUTQ(*JOB) HOLD(*YES) +
                        SPLFNAME(ROUTESHEET)
             CALL       PGM(RP010) PARM(&DLVDT)
             DLTOVR     FILE(RP010PF)

/* STEP 4: MARK ALLOCATED ORDERS ROUTED, STAMP THE DATA AREA                   */
             CHGVAR     VAR(&SQL) VALUE('UPDATE ORDHDR SET OSTAT = ''R''' +
                        *BCAT 'WHERE ODLVDT =' *BCAT &DLVDT +
                        *BCAT 'AND OSTAT = ''A''')
             RUNSQL     SQL(&SQL) COMMIT(*NONE) NAMING(*SYS)
             CHGDTAARA  DTAARA(CUTOFF) VALUE(&DLVDTN)
             SNDPGMMSG  MSG('Cutoff complete for delivery date' *BCAT &DLVDT) +
                        MSGTYPE(*COMP)
             RETURN

 FAILED:     SNDPGMMSG  MSGID(CPF9898) MSGF(QCPFMSG) +
                        MSGDTA('Cutoff FAILED for delivery date' *BCAT +
                        &DLVDT *BCAT '- see job log, then rerun') +
                        MSGTYPE(*ESCAPE)
             ENDPGM
