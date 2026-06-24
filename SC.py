import asyncio
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import json
import random
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl
from colorama import Fore, Style, init

init(autoreset=False)

api_id   = 25187675
api_hash = '3d9f5672b62ac793fd07c18b3a3999b7'
SESSION_FILE = "v2ray_session"

# ── تنظیمات Gist ──────────────────────────────
GIST_TOKEN       = "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"
GIST_ID_CONFIGS  = "df9b838003979b88e37310e0ee90bcfe"   # گیست کانفیگ‌ها
GIST_ID_PROXIES  = "b5048513069ca4f51a1f436a5aad4f8a"   # گیست پروکسی‌ها
GIST_FILE_CONFIGS = "MORVPN_configs.txt"
GIST_FILE_PROXIES = "MORVPN_proxy.txt"

CONCURRENCY  = 10   # تعداد کانال‌های همزمان
HOURS_BACK   = 24

channels = [
    "prrofile_purple", "v2line", "v2ray1_ng", "v2ray_swhil", "v2rayng_fast",
    "v2raytz", "vmessorg", "ISVvpn", "forwardv2ray",
    "PrivateVPNs", "VlessConfig", "V2pedia", "v2rayNG_Matsuri", "proxystore11",
    "DirectVPN", "OutlineVpnOfficial", "networknim", "beiten", "MsV2ray",
    "DailyV2RY", "yaney_01", "EliV2ray", "ServerNett",
    "v2rayng_fa2", "v2rayng_org", "V2rayNGvpni", "v2rayNG_VPNN",
    "FreeVlessVpn", "freeland8", "vmessiran", "V2rayNG3",
    "ShadowsocksM", "ShadowSocks_s", "VmessProtocol", "Easy_Free_VPN",
    "V2RAY_VMESS_free", "v2ray_for_free", "V2rayN_Free",
    "free4allVPN", "configV2rayForFree", "FreeV2rays", "DigiV2ray", "v2rayNG_VPN",
    "freev2rayssr", "v2rayn_server", "iranvpnet", "vmess_iran", "configV2rayNG",
    "vpn_proxy_custom", "vpnmasi", "ViPVpn_v2ray", "vip_vpn_2022", "FOX_VPN66",
    "ultrasurf_12", "frev2rayng", "FreakConfig", "Awlix_ir",
    "arv2ray", "flyv2ray", "free_v2rayyy", "ip_cf", "mehrosaboran",
    "oneclickvpnkeys", "outline_vpn", "outlinev2rayng", "outlinevpnofficial",
    "v2rayngvpn", "V2raNG_DA", "configshub2",
    "v2ray_configs_pool", "hope_net", "everydayvpn", "v2nodes", "shadowproxy66",
    "free_nettm", "VConfing", "CONFIG_TotFarangi", "npvv2rayn", "mitivpn",
    "XpnTeam", "proxymtprotoir", "NetAccount", "VpnPinks", "planB_net",
    "V2rayNG_Cafe", "V2rayBaaz", "phv2ray_config", "PhantomNett", "Filter_breaker",
    "FREE_VPN02", "meliproxyy", "EmKavpn", "Free_World2", "vmesc", "Hope_Net",
    "wedbazgap", "ConfigX2ray", "free_v22", "arisping", "aryaeeconfig",
    "Kia_Net", "configraygan", "sudoflux", "Maznet", "ipV2Ray",
    "IRVIVPN", "VpnMaan", "Merlin_ViP", "ITSecurityComputer", "AstroVPN_official",
    "PewezaVPN", "VPNCUSTOMIZE", "zedmodeonvpn", "V2RAY_SPATIAL", "VIPV2rayNGNP",
    "Vpn_Shield", "acccrd", "vpnfun", "v2ra_config", "beshcan", "V2Ray_Tz",
    "AmyraxVPN", "Eag1e_YT", "kurdivpn", "cooonfig", "ChinaPortGFW",
    "V2rayEnglish", "v2rayNGcloud", "TeleProxyTele", "proxy_yam",
    "sogoandfuckyourlove", "v2rayng_vpnrog",
]

SUB_LINKS_FILE  = "Create subSC.txt"
V2RAY_PREFIXES  = ("vless://", "vmess://", "trojan://", "ss://", "hy2://", "hysteria2://", "tuic://", "wireguard://")
PROXY_PREFIXES  = ("tg://py",)


# ─── Sub URL fetch ────────────────────────────

def _encode_url(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((
        p.scheme, p.netloc,
        urllib.parse.quote(p.path, safe="/:@!$&'()*+,;="),
        urllib.parse.quote(p.query, safe="=&+%"),
        p.fragment,
    ))

def fetch_sub_url(url):
    import base64
    configs = []
    try:
        req = urllib.request.Request(_encode_url(url), headers={"User-Agent": "v2rayNG/1.8.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
        try:
            decoded = base64.b64decode(raw + b"==").decode("utf-8", errors="ignore")
            text = decoded if any(p in decoded for p in V2RAY_PREFIXES) else raw.decode("utf-8", errors="ignore")
        except Exception:
            text = raw.decode("utf-8", errors="ignore")
        configs = [l.strip() for l in text.splitlines() if l.strip().startswith(V2RAY_PREFIXES)]
    except Exception as e:
        print(Fore.RED + f"\n  [sub] {url[:55]}: {e}" + Style.RESET_ALL)
    return configs

def load_and_fetch_subs(path):
    if not os.path.exists(path):
        return []
    urls = [l.strip() for l in open(path, encoding="utf-8")
            if l.strip() and not l.startswith("#") and l.strip().startswith("http")]
    if not urls:
        return []
    print(Fore.CYAN + f"  [*] Fetching {len(urls)} sub URLs..." + Style.RESET_ALL)
    all_configs = []
    for i, url in enumerate(urls, 1):
        sys.stdout.write(Fore.CYAN + f"\r  [{i}/{len(urls)}] {url[:60]}" + Style.RESET_ALL)
        sys.stdout.flush()
        all_configs.extend(fetch_sub_url(url))
    print()
    return all_configs


# ─── Gist upload ─────────────────────────────

def gist_update(content, token, gist_id, filename):
    if "YOUR_" in token or "YOUR_" in gist_id:
        print(Fore.YELLOW + f"  [!] Gist not configured — skip ({filename})" + Style.RESET_ALL)
        return
    payload = json.dumps({"files": {filename: {"content": content or " "}}}).encode()
    req = urllib.request.Request(
        f"https://api.github.com/gists/{gist_id}",
        data=payload, method="PATCH",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "v2ray-scraper/2.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        raw = data["files"][filename]["raw_url"]
        print(Fore.GREEN + f"  [✓] Gist updated: {raw}" + Style.RESET_ALL)
    except urllib.error.HTTPError as e:
        print(Fore.RED + f"  [!] Gist error {e.code}: {e.read().decode()[:120]}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"  [!] Gist error: {e}" + Style.RESET_ALL)


# ─── Telegram scan (concurrent) ───────────────

async def scan_channel(client, target, since_time, sem, v2ray_set, proxy_set, counter, total):
    async with sem:
        try:
            async for msg in client.iter_messages(target, wait_time=0):
                if msg.date.replace(tzinfo=None) < since_time:
                    break
                if msg.text:
                    for line in msg.text.splitlines():
                        line = line.strip()
                        if line.startswith(V2RAY_PREFIXES):
                            v2ray_set.add(line)
                        if line.startswith(PROXY_PREFIXES):
                            proxy_set.add(line)
                if msg.entities:
                    for ent in msg.entities:
                        if isinstance(ent, MessageEntityTextUrl) and ent.url.startswith(PROXY_PREFIXES):
                            proxy_set.add(ent.url)
                        elif isinstance(ent, MessageEntityUrl):
                            url = msg.text[ent.offset: ent.offset + ent.length]
                            if url.startswith(PROXY_PREFIXES):
                                proxy_set.add(url)
        except Exception as e:
            pass  # skip dead channels silently
        finally:
            counter[0] += 1
            pct = int(counter[0] / total * 100)
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            sys.stdout.write(Fore.CYAN + f"\r  [{bar}] {pct:3d}%  {counter[0]}/{total}" + Style.RESET_ALL)
            sys.stdout.flush()


# ─── MAIN ─────────────────────────────────────

async def main():
    t0 = time.time()
    since_time = datetime.now() - timedelta(hours=HOURS_BACK)

    # sub URLs
    sub_configs = load_and_fetch_subs(SUB_LINKS_FILE)

    # Telegram
    targets = list(dict.fromkeys(channels))
    total   = len(targets)
    print(Fore.GREEN + f"\n  [+] Scanning {total} channels (concurrency={CONCURRENCY})...\n" + Style.RESET_ALL)

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.start()
    if not await client.is_user_authorized():
        print(Fore.RED + "  [!] Not authorized." + Style.RESET_ALL)
        return

    v2ray_set  = set()
    proxy_set  = set()
    counter    = [0]
    sem        = asyncio.Semaphore(CONCURRENCY)

    tasks = [
        scan_channel(client, t, since_time, sem, v2ray_set, proxy_set, counter, total)
        for t in targets
    ]
    await asyncio.gather(*tasks)
    print()
    await client.disconnect()

    # merge + dedup
    all_configs = list(v2ray_set | set(sub_configs))
    all_proxies = list(proxy_set)

    elapsed = round(time.time() - t0, 1)
    print(Fore.GREEN + f"""
  ╔══════════════════════════════════════╗
  ║  DONE in {elapsed}s
  ║  Configs : {len(all_configs)}
  ║  Proxies : {len(all_proxies)}
  ╚══════════════════════════════════════╝""" + Style.RESET_ALL)

    # upload
    print(Fore.CYAN + "\n  Uploading to Gist..." + Style.RESET_ALL)
    gist_update("\n".join(all_configs), GIST_TOKEN, GIST_ID_CONFIGS, GIST_FILE_CONFIGS)
    gist_update("\n".join(all_proxies), GIST_TOKEN, GIST_ID_PROXIES, GIST_FILE_PROXIES)

    print(Fore.YELLOW + "\n  All done.\n" + Style.RESET_ALL)


if __name__ == "__main__":
    asyncio.run(main())
