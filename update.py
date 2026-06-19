import requests

TOKEN = "YOUR_TOKEN"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

with open("urls.txt", "r") as f:
    urls = [x.strip() for x in f if x.strip()]

with open("gists.txt", "r") as f:
    gists = [x.strip() for x in f if x.strip()]

count = min(len(urls), len(gists))

for i in range(count):
    url = urls[i]
    gist_id = gists[i]

    try:
        text = requests.get(url, timeout=20).text

        # تغییر اصلی تو
        text = text.replace("AAA", "BBB")

        requests.patch(
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

    except Exception as e:
        print("error:", url, e)
