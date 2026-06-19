import os
import sys
import base64
import requests
from datetime import datetime, timezone

# ---------- تنظیمات ----------
TOKEN = "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"
DATA_FILE = "data.txt"          # فایل شامل URL و Gist ID
TARGET_FILENAME = "gistfile1.txt"
OLD_TEXT = "Nova"
NEW_TEXT = "MOR VPN"
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


# ---------- خواندن data.txt ----------
def parse_data_file(path):
    """
    فرمت فایل:

    URL
    GIST_ID

    URL
    GIST_ID
    """

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
    pairs = []

    for idx, block in enumerate(blocks, start=1):
        lines = [line.strip() for line in block.splitlines() if line.strip()]

        if len(lines) < 2:
            log_warn(f"بلوک {idx} ناقص است و رد شد")
            continue

        url = lines[0]
        gist_id = lines[1]

        pairs.append((url, gist_id))

    return pairs


# ---------- پردازش محتوا ----------
def process_content(encoded_text):
    # Base64 Decode
    text = base64.b64decode(encoded_text).decode("utf-8")

    # تبدیل به لیست کانفیگ‌ها
    configs = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # حذف اولین کانفیگ
    if configs:
        configs.pop(0)

    text = "\n".join(configs)

    # جایگزینی Nova با MOR VPN
    text = text.replace(OLD_TEXT, NEW_TEXT)

    return text


# ---------- برنامه اصلی ----------
def main():
    log_info("شروع اجرا")

    if not TOKEN or TOKEN == "YOUR_GITHUB_TOKEN":
        log_error("توکن GitHub تنظیم نشده است")
        sys.exit(1)

    if not os.path.exists(DATA_FILE):
        log_error(f"فایل {DATA_FILE} پیدا نشد")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    pairs = parse_data_file(DATA_FILE)

    success_count = 0
    fail_count = 0

    for index, (url, gist_id) in enumerate(pairs, start=1):

        log_info(
            f"[{index}/{len(pairs)}] URL={url} | GIST={gist_id}"
        )

        try:
            # دانلود
            response = requests.get(
                url,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()

            encoded_text = response.text.strip()

            # پردازش
            content = process_content(encoded_text)

            # آپدیت Gist
            update_response = requests.patch(
                f"https://api.github.com/gists/{gist_id}",
                headers=headers,
                json={
                    "files": {
                        TARGET_FILENAME: {
                            "content": content
                        }
                    }
                },
                timeout=REQUEST_TIMEOUT
            )

            if update_response.status_code == 200:
                log_success(
                    f"[{index}/{len(pairs)}] آپدیت شد"
                )
                success_count += 1
            else:
                log_error(
                    f"[{index}/{len(pairs)}] خطا: "
                    f"{update_response.status_code}"
                )
                log_error(update_response.text)
                fail_count += 1

        except Exception as e:
            log_error(str(e))
            fail_count += 1

    log_info("=" * 50)
    log_info(
        f"موفق: {success_count} | "
        f"ناموفق: {fail_count} | "
        f"کل: {len(pairs)}"
    )

    if fail_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
