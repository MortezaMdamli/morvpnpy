import os
import sys
import requests
from datetime import datetime, timezone

# ---------- تنظیمات ----------
# هشدار: قرار دادن توکن مستقیم در کد ناامن است.
# اگر این فایل به ریپازیتوری (مخصوصاً public) Push شود، توکن لو می‌رود.
# توصیه می‌شود به‌جای این روش از GitHub Secrets استفاده شود.
TOKEN = "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"
URLS_FILE = "urls.txt"
GISTS_FILE = "gists.txt"
TARGET_FILENAME = "gistfile1.txt"   # نام فایل داخل Gist
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


def main():
    log_info("شروع اجرای اسکریپت update.py")

    # بررسی وجود توکن
    if not TOKEN or TOKEN == "PASTE_YOUR_TOKEN_HERE":
        log_error("توکن تنظیم نشده است. مقدار TOKEN را در بالای فایل جایگزین کنید.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # خواندن urls.txt
    if not os.path.exists(URLS_FILE):
        log_error(f"فایل {URLS_FILE} پیدا نشد.")
        sys.exit(1)
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    log_info(f"{len(urls)} لینک از {URLS_FILE} خوانده شد.")

    # خواندن gists.txt
    if not os.path.exists(GISTS_FILE):
        log_error(f"فایل {GISTS_FILE} پیدا نشد.")
        sys.exit(1)
    with open(GISTS_FILE, "r", encoding="utf-8") as f:
        gists = [line.strip() for line in f if line.strip()]
    log_info(f"{len(gists)} Gist ID از {GISTS_FILE} خوانده شد.")

    if len(urls) != len(gists):
        log_warn(
            f"تعداد URL ها ({len(urls)}) با تعداد Gist ID ها ({len(gists)}) برابر نیست. "
            f"فقط {min(len(urls), len(gists))} مورد پردازش می‌شود."
        )

    count = min(len(urls), len(gists))
    success_count = 0
    fail_count = 0

    for i in range(count):
        url = urls[i]
        gist_id = gists[i]
        log_info(f"[{i+1}/{count}] در حال پردازش -> URL: {url} | Gist: {gist_id}")

        try:
            # دریافت متن از URL
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            text = resp.text
            log_info(f"[{i+1}/{count}] دانلود موفق ({len(text)} کاراکتر دریافت شد)")

            # اعمال تغییرات
            occurrences = text.count(OLD_TEXT)
            text = text.replace(OLD_TEXT, NEW_TEXT)
            log_info(f"[{i+1}/{count}] {occurrences} مورد '{OLD_TEXT}' با '{NEW_TEXT}' جایگزین شد")

            # بروزرسانی Gist
            update_resp = requests.patch(
                f"https://api.github.com/gists/{gist_id}",
                headers=headers,
                json={"files": {TARGET_FILENAME: {"content": text}}},
                timeout=REQUEST_TIMEOUT
            )

            if update_resp.status_code == 200:
                log_success(f"[{i+1}/{count}] Gist با موفقیت آپدیت شد: {gist_id}")
                success_count += 1
            else:
                log_error(
                    f"[{i+1}/{count}] آپدیت Gist ناموفق بود ({update_resp.status_code}): {gist_id}"
                )
                log_error(f"پاسخ سرور: {update_resp.text}")
                fail_count += 1

        except requests.exceptions.RequestException as e:
            log_error(f"[{i+1}/{count}] خطای شبکه برای {url}: {e}")
            fail_count += 1
        except Exception as e:
            log_error(f"[{i+1}/{count}] خطای غیرمنتظره برای {url}: {e}")
            fail_count += 1

    # ---------- خلاصه نهایی ----------
    log_info("=" * 50)
    log_info(f"خلاصه اجرا: {success_count} موفق | {fail_count} ناموفق | {count} کل")
    log_info("پایان اجرای اسکریپت")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
