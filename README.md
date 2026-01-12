# Cyber Chat - TCP/IP Network Project

**מגישים:** אדיר בוסקילה 209487727 וליאב ויצמן 324926898  
**קורס:** רשתות תקשורת מחשבים  
**תאריך:** ינואר 2026

---

## סקירת הפרויקט

פרויקט זה מדגים הבנה מעשית של תקשורת TCP/IP ומחולק לשני חלקים:

1. **חלק 1:** אריזת מנות - בניית חבילות TCP/IP ולכידה ב-Wireshark
2. **חלק 2:** יישום צ'אט - מערכת צ'אט מרובת לקוחות עם GUI

---

## מבנה הפרויקט

| קובץ | תיאור |
|------|-------|
| **חלק 1 - אריזת מנות** ||
| `group209487727_http_input.csv` | קובץ CSV עם 20 הודעות HTTP/DNS |
| `raw_tcp_ip_notebook_fallback_annotated-v1.ipynb` | מחברת Jupyter לאריזת מנות |
| `part1.pcap` | לכידת Wireshark של חלק 1 |
| **חלק 2 - יישום צ'אט** ||
| `main.py` | נקודת כניסה - בחירת שרת/לקוח |
| `server.py` | שרת TCP - תומך ב-50+ לקוחות |
| `client.py` | לקוח TCP עם ממשק גרפי |
| `config.py` | הגדרות ופרמטרים |
| `utils.py` | פונקציות עזר, לוגים, ולידציה |
| `ui_components.py` | רכיבי UI לשימוש חוזר |
| `part2.pcap` | לכידת Wireshark של תעבורת הצ'אט |
| **תיעוד** ||
| `דוח_מסכם.md` | דוח חלק 1 - אריזת מנות |
| `דוח_מסכם_חלק_2.md` | דוח חלק 2 - יישום וניתוח |
| `Screenshot_1-4.png` | צילומי מסך |

---

## התקנה והרצה

### חלק 1: אריזת מנות
```bash
pip install pandas scapy
jupyter notebook raw_tcp_ip_notebook_fallback_annotated-v1.ipynb
```

### חלק 2: יישום צ'אט
```bash
# GUI Launcher
python main.py

# או ישירות
python main.py server    # הפעלת שרת
python main.py client    # הפעלת לקוח
```

---

## חלק 1 - אריזת מנות

### קובץ CSV
הקובץ `group209487727_http_input.csv` מכיל 20 הודעות עם השדות:
- `msg_id`, `app_protocol`, `src_app`, `dst_app`, `message`, `timestamp`

### תהליך
1. טעינת ההודעות מה-CSV
2. בניית IP Header
3. בניית TCP Header
4. שליחה באמצעות Scapy
5. לכידה ב-Wireshark

### לכידה ב-Wireshark
- ממשק: Npcap Loopback Adapter
- מסנן: `tcp.port == 12345`
- קובץ: `part1.pcap`

---

## חלק 2 - יישום צ'אט

### דרישות טכניות שמומשו

| דרישה | מימוש |
|-------|-------|
| פרוטוקול TCP | `socket.SOCK_STREAM` |
| תקשורת דו-כיוונית | שרת ↔ מספר לקוחות |
| 5+ לקוחות במקביל | `MAX_CLIENTS = 50` עם Threading |
| שרת כמתווך | Broadcast + הודעות פרטיות |
| Sockets בלבד | ספריית `socket` |
| טיפול בשגיאות | Try/except + ניקוי |
| קוד מתועד | 6 קבצים מודולריים |
| **בונוס: GUI** | ממשק Tkinter מלא |

### תכונות השרת
- סטטיסטיקות בזמן אמת
- לוגים צבעוניים
- בקרת מנהל (kick, broadcast)
- ייצוא לוגים

### תכונות הלקוח
- ממשק Cyberpunk
- סטטוס משתמש (Online/Away/Busy)
- הודעות פרטיות
- בחירת אימוג'ים
- פקודות צ'אט (`/help`, `/status`, `/dm`, `/clear`, `/save`)

---

## פקודות

| פקודה | תיאור |
|-------|-------|
| `/help` | הצגת פקודות |
| `/status <online\|away\|busy>` | שינוי סטטוס |
| `/dm <user> <msg>` | הודעה פרטית |
| `/clear` | ניקוי חלון |
| `/save` | ייצוא היסטוריה |

---

## הגדרות

ניתן לשנות ב-`config.py`:

```python
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 12345
MAX_CLIENTS = 50
BUFFER_SIZE = 4096
```

---

## ארכיטקטורה

```
┌─────────────────────────────────────────────────┐
│                    main.py                       │
│                 (Launcher GUI)                   │
└──────────────────┬──────────────┬───────────────┘
                   │              │
       ┌───────────▼────┐   ┌─────▼──────────┐
       │   server.py    │   │   client.py    │
       │  (TCP Server)  │   │  (TCP Client)  │
       └───────────┬────┘   └─────┬──────────┘
                   │              │
       ┌───────────▼──────────────▼───────────┐
       │         ui_components.py              │
       │        (Styled Widgets)               │
       └───────────────────┬──────────────────┘
                           │
       ┌───────────────────▼──────────────────┐
       │     config.py     │     utils.py      │
       └──────────────────────────────────────┘
```

---

## תוצרים להגשה

### חלק 1
- [x] `group209487727_http_input.csv`
- [x] `raw_tcp_ip_notebook_fallback_annotated-v1.ipynb`
- [x] `part1.pcap`
- [x] `דוח_מסכם.md`

### חלק 2
- [x] `server.py`, `client.py`, `main.py`, `config.py`, `utils.py`, `ui_components.py`
- [x] `part2.pcap`
- [x] `דוח_מסכם_חלק_2.md`

---

## שימוש ב-AI

הפרויקט פותח בסיוע Claude (Anthropic) עבור:
- תכנון הקוד
- דיבוג
- עיצוב UI
- תיעוד

כל הקוד נבדק והובן על ידי הסטודנטים.

---

## מגישים

**אדיר בוסקילה 209487727**  
**ליאב ויצמן 324926898**

קורס רשתות תקשורת מחשבים, ינואר 2026
good luck