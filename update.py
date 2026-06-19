import requests

# توکن GitHub
TOKEN = "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"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# خواندن URL ها
with open("urls.txt", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

# خواندن Gist ID ها
with open("gists.txt", "r", encoding="utf-8") as f:
    gists = [line.strip() for line in f if line.strip()]

# تعداد URL و Gist باید برابر باشد
count = min(len(urls), len(gists))

for i in range(count):
    url = urls[i]
    gist_id = gists[i]

    try:
        print(f"Reading: {url}")

        # دریافت متن از URL
        text = requests.get(url, timeout=30).text

        # تغییرات دلخواه
        text = text.replace("AAA", "BBB")

        # بروزرسانی Gist
        response = requests.patch(
            f"https://api.github.com/gists/{gist_id}",
            headers=headers,
            json={
                "files": {
                    "file.txt": {
                        "content": text
                    }
                }
            }
        )

        if response.status_code == 200:
            print(f"Gist updated: {gist_id}")
        else:
            print(f"Failed: {gist_id}")
            print(response.text)

    except Exception as e:
        print(f"Error in {url}")
        print(e)
