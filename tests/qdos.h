/* Host-only stand-ins: exercise application logic, not QDOS traps. */
#include <stdio.h>
typedef long chanid_t;
struct QLRECT { unsigned short q_width, q_height, q_x, q_y; };
struct qdirect {
    unsigned long d_length;
    unsigned char d_access, d_type;
    unsigned long d_datalen;
    long d_reserved;
    unsigned short d_szname;
    char d_name[36];
    long d_update;
    union { long d_refdate; struct { unsigned short d_version, d_fileno; } v2; } u;
    long d_backup;
};
#define QF_DIR_TYPE 255
#define CST_DIR_TYPE 4
#define THOR_DIR_TYPE 3
#define RED_M4 2
#define ERR_BP -15
#define ERR_NC -1
#define ERR_FE -16
#define ERR_OM -3
#define OLD_EXCL 0
#define DIROPEN 4
long fgetchid(FILE *);
int iscon(long,int);
int isnoclose(int);
int sd_wdef(long,int,int,int,struct QLRECT *);
int sd_clear(long,int);
int sd_chenq(long,int,struct QLRECT *);
int sd_cure(long,int);
int sd_curs(long,int);
int io_fbyte(long,int,char *);
long io_open(const char *,int);
int io_close(long);
long open_qdir(const char *);
int read_qdir(long,char *,char *,struct qdirect *,int);
char *cn_date(char *,long);
