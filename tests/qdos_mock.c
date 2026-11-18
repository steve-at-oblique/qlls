#include "qdos.h"
#include <stdlib.h>
#include <string.h>
long fgetchid(FILE *f) { return 1; }
int iscon(long c,int t) { return 0; }
int isnoclose(int f) { return getenv("SHARED") ? 1 : 0; }
int sd_wdef(long c,int t,int a,int b,struct QLRECT *r) { return 0; }
int sd_clear(long c,int t) { return 0; }
int sd_chenq(long c,int t,struct QLRECT *r) { r->q_width=80; r->q_x=0; return 0; }
int sd_cure(long c,int t) { return 0; }
int sd_curs(long c,int t) { return 0; }
int io_fbyte(long c,int t,char *b) { *b='\n'; return 0; }
long io_open(const char *s,int m) { return -7; }
int io_close(long c) { return 0; }
static int literal_wildcard;
long open_qdir(const char *s) {
    literal_wildcard = getenv("SNL") && strpbrk(s,"*?[") != NULL;
    return getenv("OPEN_ERROR") ? -7 : 1;
}
char *cn_date(char *s,long d) { sprintf(s,"2026 Nov 16 17:18:12"); return s; }
int read_qdir(long c,char *p,char *n,struct qdirect *d,int type) {
    static int i;
    static FILE *fixture;
    static const char *ql_names[] = {"boot", "boot2", "boot3", "playss", "rn_bas",
        "TK236_bin", "mouse_bin", "proglogic", "sound_run", "bench4_bin", "benchm_bin",
        "catwalk_ub", "pitman_zip", "western_ub", "bintest_bin", "sertest_bas",
        "Min4068_rext", "forgotten_ub", "probe384_bin", "probe512_bin", "qimsikbd_bin",
        "snldriver_asm", "qspread302_zip", "snl_channels_bas", "snldriver239_bin",
        "snl_throughput_bas"};
    static const char *names[] = {"zebra", "Beta", "alpha", "abcdefghijklmnopqrstuvwxyz0123456789"};
    int limit = getenv("MANY") ? 100 : 4;
    if (getenv("QL_NAMES")) limit = sizeof(ql_names) / sizeof(ql_names[0]);
    if (getenv("READ_ERROR")) return -1;
    if (literal_wildcard || getenv("EMPTY") || i == limit) return 0;
    memset(d,0,sizeof(*d));
    if (getenv("SNL_FIXTURE")) {
        unsigned int filetype;
        if (!fixture) fixture = fopen(getenv("SNL_FIXTURE"), "r");
        if (!fixture || fscanf(fixture,"%36s %lu %ld %u",d->d_name,
                              &d->d_length,&d->d_update,&filetype) != 4) return 0;
        d->d_type = filetype;
        d->d_szname = strlen(d->d_name);
        return 1;
    }
    if (getenv("QL_NAMES")) memcpy(d->d_name,ql_names[i],strlen(ql_names[i]));
    else if (limit == 100) sprintf(d->d_name,"file%03d",99-i);
    else memcpy(d->d_name,names[i],strlen(names[i]));
    d->d_szname = getenv("QL_NAMES") ? strlen(ql_names[i]) : limit == 100 ? 7 : strlen(names[i]);
    d->d_length = 64 + (i+1)*100;
    if (getenv("DIRECTORIES")) {
        /* Standard dir, legacy dir, legacy non-dir, max-length Thor dir. */
        static const unsigned char types[] = {255,4,4,3};
        d->d_type = types[i];
        if (i != 2) d->d_length = 128;
    }
    d->d_update = 1000-i;
    if (getenv("NO_DATE")) d->d_update = 0;
    d->d_datalen = 200;
    ++i;
    return 1;
}
