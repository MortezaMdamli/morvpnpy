import os
import sys
import requests
from datetime import datetime, timezone

# ---------- تنظیمات ----------
# هشدار: قرار دادن توکن مستقیم در کد ناامن است.
# اگر این فایل به ریپازیتوری Push شود (مخصوصاً public)، توکن لو می‌رود.
TOKEN = "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"
DATA_FILE = "data.txt"          # فایل واحد شامل URL و Gist ID
TARGET_FILENAME = "gistfile1.txt"    # نام فایل داخل Gist
OLD_TEXT = "AAA"
NEW_TEXT = "BBB"
REQUEST_TIMEOUT = 30

# ---------- ابزار لاگ ----------
def log(level, message):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] [{level}] {message}", flush=True)

def log_info(msg):
    log("INFO", msg)

def log_warn(msg):
    log("WARN", msg)

def log_error(msg):
    log("ERROR", msg)

def log_success(msg):
    log("OK", msg)


def parse_data_file(path):
    """
    فایل را بر اساس خط خالی (دو اینتر) به بلوک‌ها تقسیم می‌کند.
    هر بلوک باید دو خط داشته باشد: خط اول URL، خط دوم Gist ID.
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
    pairs = []

    for idx, block in enumerate(blocks, start=1):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            log_warn(f"بلوک شماره {idx} ناقص است و نادیده گرفته شد: {block!r}")
            continue
        url, gist_id = lines[0], lines[1]
        pairs.append((url, gist_id))

    return pairs


def main():
    log_info("شروع اجرای اسکریپت update_combined.py")

    if not TOKEN or TOKEN == "PASTE_YOUR_TOKEN_HERE":
        log_error("توکن تنظیم نشده است. مقدار TOKEN را در بالای فایل جایگزین کنید.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    if not os.path.exists(DATA_FILE):
        log_error(f"فایل {DATA_FILE} پیدا نشد.")
        sys.exit(1)

    pairs = parse_data_file(DATA_FILE)
    log_info(f"{len(pairs)} جفت (URL + Gist) از {DATA_FILE} خوانده شد.")

    success_count = 0
    fail_count = 0
    count = len(pairs)

    for i, (url, gist_id) in enumerate(pairs, start=1):
        log_info(f"[{i}/{count}] در حال پردازش -> URL: {url} | Gist: {gist_id}")

        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            text = resp.text
            log_info(f"[{i}/{count}] دانلود موفق ({len(text)} کاراکتر دریافت شد)")

            occurrences = text.count(OLD_TEXT)
            text = text.replace(OLD_TEXT, NEW_TEXT)
            log_info(f"[{i}/{count}] {occurrences} مورد '{OLD_TEXT}' با '{NEW_TEXT}' جایگزین شد")

            update_resp = requests.patch(
                f"https://api.github.com/gists/{gist_id}",
                headers=headers,
                json={"files": {TARGET_FILENAME: {"content": text}}},
                timeout=REQUEST_TIMEOUT
            )

            if update_resp.status_code == 200:
                log_success(f"[{i}/{count}] Gist با موفقیت آپدیت شد: {gist_id}")
                success_count += 1
            else:
                log_error(f"[{i}/{count}] آپدیت Gist ناموفق بود ({update_resp.status_code}): {gist_id}")
                log_error(f"پاسخ سرور: {update_resp.text}")
                fail_count += 1

        except requests.exceptions.RequestException as e:
            log_error(f"[{i}/{count}] خطای شبکه برای {url}: {e}")
            fail_count += 1
        except Exception as e:
            log_error(f"[{i}/{count}] خطای غیرمنتظره برای {url}: {e}")
            fail_count += 1

    log_info("=" * 50)
    log_info(f"خلاصه اجرا: {success_count} موفق | {fail_count} ناموفق | {count} کل")
    log_info("پایان اجرای اسکریپت")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
