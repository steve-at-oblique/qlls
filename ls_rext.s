; Copyright (c) 2026 Steve Jennen
; SPDX-License-Identifier: BSD-2-Clause
; Resident SuperBASIC LS command. Motorola 68000, position independent.
; Load once per boot with LRESPR. Uses only QDOS traps and ROM vectors.
; Workspace: header[64], command[260], file/job/base, argument offsets,
; and inherited #1 channel ID (352 bytes). Up to 16 separate arguments.
; Waits for completion and leaves SuperBASIC #1 open.
        .sect .text
        .extern ls_init
ls_init:
        lea ls_table(pc),a1
        move.w 0x110,a2
        jmp (a2)
ls_table:
        .data2 2
ls_slot:
        .data2 ls_command-ls_slot
        .data1 2,0x4c,0x53,0
ls_use_slot:
        .data2 ls_use-ls_use_slot
        .data1 6
        .ascii "LS_USE"
        .data1 0
        .data2 0,0,0
; LS_USE takes a string expression containing the full executable filename.
ls_use:
        move.l a5,d0
        sub.l a3,d0
        cmp.l #8,d0
        bne ls_bad
        move.w 0x116,a2
        jsr (a2)
        tst.l d0
        bne ls_use_return
        moveq #0,d1
        move.w 0(a6,a1.l),d1
        addq.l #2,a1
        move.l a1,d0
        add.l d1,d0
        addq.l #1,d0
        and.l #-2,d0
        move.l d0,0x58(a6)
        tst.w d1
        beq ls_bad
        cmp.w #255,d1
        bhi ls_bad
        lea ls_program(pc),a0
        move.w d1,(a0)+
        subq.w #1,d1
ls_use_copy:
        move.b 0(a6,a1.l),(a0)+
        addq.l #1,a1
        dbra d1,ls_use_copy
        moveq #0,d0
ls_use_return:
        rts
ls_command:
        move.l a5,d7
        sub.l a3,d7
        move.l d7,d0
        and.l #7,d0
        bne ls_bad
        cmp.l #128,d7
        bhi ls_bad
ls_alloc:
        move.l #352,d1
        moveq #-1,d2
        moveq #0x18,d0
        trap #1
        tst.l d0
        bne ls_return
        move.l a0,a4
        clr.l 324(a4)
        move.l #-1,328(a4)
        clr.w 64(a4)
        move.l a3,336(a4)
        move.l a5,340(a4)
ls_next:
        move.l 336(a4),a3
        cmp.l 340(a4),a3
        beq ls_channels
        lea 8(a3),a5
; A string variable/expression is fetched by CA.GTSTR. Otherwise use the
; parameter's name-list entry, so LS win1_ works without quotes.
        cmp.b #1,1(a6,a3.l)
        bne ls_name
        move.b 0(a6,a3.l),d0
        and.b #15,d0
        cmp.b #1,d0
        beq ls_string
        tst.l 4(a6,a3.l)
        bmi ls_name
ls_string:
        move.w 0x116,a2
        jsr (a2)
        tst.l d0
        bne ls_clean
        moveq #0,d6
        move.w 0(a6,a1.l),d6
        addq.l #2,a1
        move.l a1,d0
        add.l d6,d0
        addq.l #1,d0
        and.l #-2,d0
        move.l d0,0x58(a6)
        bra ls_arg
ls_name:
; A procedure parameter contains a name-TABLE index, not a name-list offset.
; Resolve the original eight-byte entry before reading its name-list offset.
        moveq #0,d0
        move.w 2(a6,a3.l),d0
        tst.w d0
        bmi ls_param
        lsl.l #3,d0
        add.l 0x18(a6),d0
        move.l d0,a1
        moveq #0,d0
        move.w 2(a6,a1.l),d0
        add.l 0x20(a6),d0
        move.l d0,a1
        moveq #0,d6
        move.b 0(a6,a1.l),d6
        addq.l #1,a1
ls_arg:
        cmp.l #255,d6
        bhi ls_param
        moveq #0,d5
        move.w 64(a4),d5
        lea 66(a4),a2
        add.l d5,a2
        tst.l d5
        beq ls_first
        move.b #32,(a2)+
        addq.l #1,d5
ls_first:
        add.l d6,d5
        addq.l #2,d5
        cmp.l #255,d5
        bhi ls_param
        move.w d5,64(a4)
        move.b #34,(a2)+
        tst.l d6
        beq ls_endquote
        subq.w #1,d6
ls_copy:
        move.b 0(a6,a1.l),d0
        cmp.b #34,d0
        beq ls_param
        cmp.b #32,d0
        blo ls_param
        move.b d0,(a2)+
        addq.l #1,a1
        dbra d6,ls_copy
ls_endquote:
        move.b #34,(a2)+
        clr.b (a2)
        addq.l #8,336(a4)
        bra ls_next
ls_channels:
; Resolve SuperBASIC #1. Table entries are $28 bytes; ID is at offset zero.
; Resolve after CA.GTSTR, which may relocate the SuperBASIC area.
        move.l 0x30(a6),d0
        add.l #40,d0
        move.l d0,d1
        add.l #40,d1
        cmp.l 0x34(a6),d1
        bhi ls_badchannel
        move.l d0,a0
        move.l 0(a6,a0.l),d0
        bmi ls_badchannel
        move.l d0,344(a4)
ls_open:
        lea ls_program(pc),a0
        moveq #-1,d1
        moveq #1,d3
        moveq #1,d0
        trap #2
        tst.l d0
        bne ls_clean
        move.l a0,324(a4)
        move.l a4,a1
        moveq #64,d2
        moveq #-1,d3
        moveq #0x47,d0
        trap #3
        tst.l d0
        bne ls_clean
        cmp.b #1,5(a4)
        bne ls_notexec
        move.l (a4),d2
        cmp.l #48,d2
        blo ls_notexec
        move.l 6(a4),d3
        tst.l d3
        ble ls_notexec
; Extra room keeps the command string outside the compiler's dataspace.
        add.l #336,d3
        moveq #0,d1
        sub.l a1,a1
        moveq #1,d0
        trap #1
        tst.l d0
        bne ls_clean
        move.l d1,328(a4)
        move.l a0,332(a4)
        move.l a0,a1
        move.l 324(a4),a0
        move.l (a4),d2
        moveq #-1,d3
        moveq #0x48,d0
        trap #3
        tst.l d0
        bne ls_clean
; The inactive job's saved A7 is at -12 from its code base (JCB + $5c).
; Set up the standard EX stack: channel-count=3 (#1 for stdin/stderr/stdout), string length, text.
        move.l 332(a4),a5
        move.l -12(a5),a2
        moveq #0,d0
        move.w 64(a4),d0
        add.l #17,d0
        and.l #-2,d0
        sub.l d0,a2
        move.l a2,-12(a5)
        move.w #3,(a2)+
        move.l 344(a4),(a2)+
        move.l 344(a4),(a2)+
        move.l 344(a4),(a2)+
        lea 64(a4),a1
        moveq #0,d0
        move.w (a1),d0
        addq.w #1,d0
ls_stack:
        move.b (a1)+,(a2)+
        dbra d0,ls_stack
        move.l 324(a4),a0
        moveq #2,d0
        trap #2
        clr.l 324(a4)
        tst.l d0
        bne ls_clean
        move.l 328(a4),d1
        moveq #32,d2
        moveq #-1,d3
        moveq #10,d0
        trap #1
        tst.l d0
        bne ls_clean
        move.l #-1,328(a4)
        moveq #0,d0
        bra ls_clean
ls_badchannel:
        moveq #-6,d0
        bra ls_clean
ls_notexec:
        moveq #-15,d0
        bra ls_clean
ls_param:
        moveq #-15,d0
ls_clean:
        move.l d0,d7
        move.l 324(a4),d0
        beq ls_nochan
        move.l d0,a0
        moveq #2,d0
        trap #2
ls_nochan:
        move.l 328(a4),d1
        bmi ls_nojob
        moveq #-1,d3
        moveq #5,d0
        trap #1
ls_nojob:
        move.l a4,a0
        moveq #0x19,d0
        trap #1
        move.l d7,d0
ls_return:
        rts
ls_bad:
        moveq #-15,d0
        rts
ls_program:
        .data2 7
        .ascii "snl4_ls"
        .space 248
        .align 2
