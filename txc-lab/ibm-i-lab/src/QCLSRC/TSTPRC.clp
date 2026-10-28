/* **TEXT:Test harness - call OE005 price lookup                               */
/*                                                                             */
/*  TSTPRC - CALL THE PRICE LOOKUP FROM A COMMAND LINE                         */
/*  CALL TSTPRC PARM('100230' '201410' '00005' '261015')                       */
/*  ALL PARAMETERS ARE CHARACTER DIGITS BECAUSE OE005 EXPECTS ZONED NUMERICS.  */
/*  ANSWERS WITH A COMPLETION MESSAGE AND WRITES THE SAME TEXT TO DATA AREA    */
/*  TSTPRC SO A BATCH CALLER CAN READ IT:  PRICE=0004250 SRC=C  (42.50)        */
             PGM        PARM(&CUST &ITEM &QTY &DATE)
             DCL        VAR(&CUST)  TYPE(*CHAR) LEN(6)
             DCL        VAR(&ITEM)  TYPE(*CHAR) LEN(6)
             DCL        VAR(&QTY)   TYPE(*CHAR) LEN(5)
             DCL        VAR(&DATE)  TYPE(*CHAR) LEN(6)
             DCL        VAR(&PRICE) TYPE(*CHAR) LEN(7) VALUE('0000000')
             DCL        VAR(&SRC)   TYPE(*CHAR) LEN(1) VALUE(' ')
             DCL        VAR(&MSG)   TYPE(*CHAR) LEN(80)
             CALL       PGM(OE005) PARM(&CUST &ITEM &QTY &DATE &PRICE &SRC)
             CHGVAR     VAR(&MSG) VALUE('OE005 CUST=' *CAT &CUST *CAT +
                        ' ITEM=' *CAT &ITEM *CAT ' QTY=' *CAT &QTY *CAT +
                        ' DATE=' *CAT &DATE *CAT ' PRICE=' *CAT &PRICE +
                        *CAT ' SRC=' *CAT &SRC)
             CHGDTAARA  DTAARA(TSTPRC) VALUE(&MSG)
             MONMSG     MSGID(CPF0000)
             SNDPGMMSG  MSG(&MSG) MSGTYPE(*COMP)
             ENDPGM
