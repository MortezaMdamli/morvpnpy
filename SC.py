import asyncio
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import json
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl
from colorama import Fore, Style, init

init(autoreset=False)

api_id   = 25187675
api_hash = '3d9f5672b62ac793fd07c18b3a3999b7'
SESSION_FILE = "v2ray_session"

# ── تنظیمات Gist ──────────────────────────────
GIST_TOKEN        = "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"
GIST_ID_CONFIGS   = "df9b838003979b88e37310e0ee90bcfe"
GIST_ID_PROXIES   = "b5048513069ca4f51a1f436a5aad4f8a"
GIST_FILE_CONFIGS = "MORVPN_configs.txt"
GIST_FILE_PROXIES = "MORVPN_proxy.txt"

CONCURRENCY = 10
HOURS_BACK  = 24

# ── لیست sub لینک‌ها ──
SUB_URLS = [
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/mix/sub.html",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/vless.html",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/vmess.html",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/trojan.html",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/ss.html",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/refs/heads/main/hy2.html",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/AT%20%F0%9F%87%A6%F0%9F%87%B9.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/AU%20%F0%9F%87%A6%F0%9F%87%BA.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/BE%20%F0%9F%87%A7%F0%9F%87%AA.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/CA%20%F0%9F%87%A8%F0%9F%87%A6.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/CH%20%F0%9F%87%A8%F0%9F%87%AD.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/CL%20%F0%9F%87%A8%F0%9F%87%B1.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/CO%20%F0%9F%87%A8%F0%9F%87%B4.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/DE%20%F0%9F%87%A9%F0%9F%87%AA.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/ES%20%F0%9F%87%AA%F0%9F%87%B8.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/FI%20%F0%9F%87%AB%F0%9F%87%AE.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/FR%20%F0%9F%87%AB%F0%9F%87%B7.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/HK%20%F0%9F%87%AD%F0%9F%87%B0.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/HU%20%F0%9F%87%AD%F0%9F%87%BA.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/GB%20%F0%9F%87%AC%F0%9F%87%A7.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/IE%20%F0%9F%87%AE%F0%9F%87%AA.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/IL%20%F0%9F%87%AE%F0%9F%87%B1.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/IN%20%F0%9F%87%AE%F0%9F%87%B3.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/IT%20%F0%9F%87%AE%F0%9F%87%B9.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/MX%20%F0%9F%87%B2%F0%9F%87%BD.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/NL%20%F0%9F%87%B3%F0%9F%87%B1.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/PH%20%F0%9F%87%B5%F0%9F%87%AD.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/PL%20%F0%9F%87%B5%F0%9F%87%B1.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/RO%20%F0%9F%87%B7%F0%9F%87%B4.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/RU%20%F0%9F%87%B7%F0%9F%87%BA.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/SK%20%F0%9F%87%B8%F0%9F%87%B0.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/TH%20%F0%9F%87%B9%F0%9F%87%AD.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/TR%20%F0%9F%87%B9%F0%9F%87%B7.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/TW%20%F0%9F%87%B9%F0%9F%87%BC.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/US%20%F0%9F%87%BA%F0%9F%87%B8.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/XX%20%E2%9D%93.txt",
    "https://raw.githubusercontent.com/arshiacomplus/v2rayExtractor/main/loc/ZA%20%F0%9F%87%BF%F0%9F%87%A6.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile-2.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS_mobile.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/Mosifree/-FREE2CONFIG/refs/heads/main/FRAGMENT",
    "https://raw.githubusercontent.com/ShadowException/VPN/refs/heads/main/configs/VPN-cat",
    "https://raw.githubusercontent.com/F0rc3Run/F0rc3Run/main/splitted-by-protocol/vless.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/Sub2.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Config/main/Sub3.txt",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/refs/heads/main/V2Ray-Config-By-EbraSha.txt",
    "https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/subscriptions/all.txt",
    "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray.txt",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt",
    "https://mifa.world/ss",
    "https://mifa.world/trojan",
    "https://mifa.world/hysteria",
    "https://mifa.world/other",
    "https://mifa.world/vmess",
    "https://mifa.world/vless",
    "https://raw.githubusercontent.com/ThomasJasperthecat/sub/main/sublist1.txt",
    "https://raw.githubusercontent.com/masir-sefid/Sub/main/@Masir_Sefid.txt",
    "https://sub.iampedi5.live/sub/base64.txt",
    "https://raw.githubusercontent.com/masir-sefid/Sub/main/Telegram-Channel-@Masir_Sefid.txt",
    "https://raw.githubusercontent.com/AmyraxVPN-Main/AmyraxVPN/refs/heads/main/AmyraxVPN.txt",
    "https://raw.githubusercontent.com/MahsaNetConfigTopic/config/refs/heads/main/xray_final.txt",
]

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

V2RAY_PREFIXES = ("vless://", "vmess://", "trojan://", "ss://", "hy2://", "hysteria2://", "tuic://", "wireguard://")
PROXY_PREFIXES = ("tg://py",)


# ─── Sub URL fetch ────────────────────────────

def fetch_sub_url(url):
    import base64
    configs = []
    try:
        p = urllib.parse.urlsplit(url)
        safe = urllib.parse.urlunsplit((
            p.scheme, p.netloc,
            urllib.parse.quote(p.path, safe="/:@!$&'()*+,;="),
            urllib.parse.quote(p.query, safe="=&+%"),
            p.fragment,
        ))
        req = urllib.request.Request(safe, headers={"User-Agent": "v2rayNG/1.8.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read()
        try:
            decoded = base64.b64decode(raw + b"==").decode("utf-8", errors="ignore")
            text = decoded if any(x in decoded for x in V2RAY_PREFIXES) else raw.decode("utf-8", errors="ignore")
        except Exception:
            text = raw.decode("utf-8", errors="ignore")
        configs = [l.strip() for l in text.splitlines() if l.strip().startswith(V2RAY_PREFIXES)]
        tag = Fore.GREEN + f"✓ {len(configs):>5}" if configs else Fore.YELLOW + "    0"
        print(f"  {tag}{Style.RESET_ALL}  {url[:65]}")
    except Exception as e:
        print(Fore.RED + f"  ✗      {url[:60]}  ({type(e).__name__})" + Style.RESET_ALL)
    return configs


def fetch_all_subs():
    if not SUB_URLS:
        return []
    print(Fore.CYAN + "\n  [*] Fetching " + str(len(SUB_URLS)) + " sub URLs...\n" + Style.RESET_ALL)
    all_configs = []
    for i, url in enumerate(SUB_URLS, 1):
        sys.stdout.write(Fore.CYAN + "  [" + str(i).rjust(2) + "/" + str(len(SUB_URLS)) + "] " + Style.RESET_ALL)
        sys.stdout.flush()
        found = fetch_sub_url(url)
        all_configs.extend(found)
    print(Fore.GREEN + "\n  [+] Sub total: " + str(len(all_configs)) + " configs از " + str(len(SUB_URLS)) + " لینک" + Style.RESET_ALL)
    return all_configs


# ─── Gist upload (Bearer برای fine-grained PAT) ──

def gist_update(content, token, gist_id, filename):
    payload = json.dumps({"files": {filename: {"content": content or " "}}}).encode()
    # هم Bearer هم token رو امتحان میکنه
    for auth in (f"Bearer {token}", f"token {token}"):
        req = urllib.request.Request(
            f"https://api.github.com/gists/{gist_id}",
            data=payload, method="PATCH",
            headers={
                "Authorization": auth,
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
                "User-Agent": "v2ray-scraper/2.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
            raw = data["files"][filename]["raw_url"]
            print(Fore.GREEN + f"  [✓] {filename} → {raw}" + Style.RESET_ALL)
            return  # موفق شد، خروج
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 401:
                continue  # روش دیگه رو امتحان کن
            print(Fore.RED + f"  [!] Gist {e.code}: {body[:120]}" + Style.RESET_ALL)
            return
        except Exception as e:
            print(Fore.RED + f"  [!] Gist error: {e}" + Style.RESET_ALL)
            return
    print(Fore.RED + "  [!] Gist: هر دو روش auth ناموفق بود" + Style.RESET_ALL)


# ─── Telegram scan ────────────────────────────

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
                        elif isinstance(ent, MessageEntityUrl) and msg.text:
                            url = msg.text[ent.offset: ent.offset + ent.length]
                            if url.startswith(PROXY_PREFIXES):
                                proxy_set.add(url)
        except Exception:
            pass
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

    sub_configs = fetch_all_subs()

    targets = list(dict.fromkeys(channels))
    total   = len(targets)
    print(Fore.GREEN + f"\n  [+] Scanning {total} channels...\n" + Style.RESET_ALL)

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.start()
    if not await client.is_user_authorized():
        print(Fore.RED + "  [!] Not authorized." + Style.RESET_ALL)
        return

    v2ray_set = set()
    proxy_set = set()
    counter   = [0]
    sem       = asyncio.Semaphore(CONCURRENCY)

    await asyncio.gather(*[
        scan_channel(client, t, since_time, sem, v2ray_set, proxy_set, counter, total)
        for t in targets
    ])
    print()
    await client.disconnect()

    tg_configs  = list(v2ray_set)
    all_configs = list(v2ray_set | set(sub_configs))
    all_proxies = list(proxy_set)
    elapsed = round(time.time() - t0, 1)

    print(Fore.GREEN + f"""
  ╔══════════════════════════════════════════╗
  ║  DONE in {elapsed}s
  ╠══════════════════════════════════════════╣
  ║  کانفیگ از تلگرام : {len(tg_configs):<6}
  ║  کانفیگ از ساب    : {len(sub_configs):<6}
  ║  مجموع کانفیگ     : {len(all_configs):<6}  (بعد از dedup)
  ║  پروکسی تلگرام   : {len(all_proxies):<6}
  ╚══════════════════════════════════════════╝""" + Style.RESET_ALL)

    print(Fore.CYAN + "\n  Uploading to Gist..." + Style.RESET_ALL)
    gist_update("\n".join(all_configs), GIST_TOKEN, GIST_ID_CONFIGS, GIST_FILE_CONFIGS)
    gist_update("\n".join(all_proxies), GIST_TOKEN, GIST_ID_PROXIES, GIST_FILE_PROXIES)

    print(Fore.YELLOW + "\n  All done.\n" + Style.RESET_ALL)


if __name__ == "__main__":
    asyncio.run(main())
