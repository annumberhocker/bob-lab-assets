     H***TEXT:Inventory inquiry
     H*
     H* IN001  - INVENTORY INQUIRY                      TMORALES   09/14/04
     H* REWRITTEN IN ILE RPG (STILL FIXED FORMAT) WHEN WE MOVED TO V5R3.
     H* USES THE Z LOGICALS BECAUSE THE BINARY FIELDS GAVE THE OLD CODE FITS.
     H*
     FIN001DF   CF   E             WORKSTN
     FITEMMSZ   IF   E           K DISK
     FINVBALZ   IF   E           K DISK
     DWWHSE            S              2A   INZ('01')
     C     IVKEY         KLIST
     C                   KFLD                    WWHSE
     C                   KFLD                    SITEM
     C                   DOW       *IN03 = *OFF
     C                   EXFMT     IN001R1
     C                   EVAL      SMSG = *BLANKS
     C                   IF        *IN03 = *OFF
     C     SITEM         CHAIN     ITEMMSZ                            90
     C                   IF        *IN90
     C                   EVAL      SMSG = 'ITEM NOT FOUND'
     C                   ELSE
     C                   EVAL      SIDESC = IDESC
     C                   EVAL      SZONE = IZONE
     C                   EVAL      SUNITP = UNITPK
     C                   EVAL      SSHELF = SHELFL
     C     IVKEY         CHAIN     INVBALZ                            91
     C                   IF        NOT *IN91
     C                   EVAL      SONHND = ONHAND
     C                   EVAL      SALLOC = ALLOC
     C                   EVAL      SAVAIL = ONHAND - ALLOC
     C                   ELSE
     C                   EVAL      SONHND = 0
     C                   EVAL      SALLOC = 0
     C                   EVAL      SAVAIL = 0
     C                   ENDIF
     C                   ENDIF
     C                   ENDIF
     C                   ENDDO
     C                   EVAL      *INLR = *ON
