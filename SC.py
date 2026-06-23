import asyncio
import os
import sys
import time
import socket
import threading
import urllib.request
import urllib.parse
import random
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl
from colorama import Fore, Style, init

init(autoreset=False)

api_id = 25187675
api_hash = '3d9f5672b62ac793fd07c18b3a3999b7'
SESSION_FILE = "v2ray_session"

# Channels with confirmed errors removed
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

SUB_LINKS_FILE = "Create subSC.py"
BASE_DIR = "mor"
V2RAY_PREFIXES = ("vless://", "vmess://", "trojan://", "ss://", "hy2://", "hysteria2://", "tuic://", "wireguard://")
PROXY_PREFIXES = ("tg://py",)
NPVT_EXT = ".nt"
HAT_EXT = ".hat"


# ─────────────────────────────────────────────
#  CONFIG RENAME
# ─────────────────────────────────────────────

def rename_config(cfg: str) -> str:
    new_tag = f"MOR VPN - {random.randint(1000, 9999)}"
    if "#" in cfg:
        cfg = cfg[:cfg.index("#")]
    return f"{cfg}#{urllib.parse.quote(new_tag)}"


# ─────────────────────────────────────────────
#  FETCH SUB URL  (fixed: proper URL encoding)
# ─────────────────────────────────────────────

def _encode_url(url: str) -> str:
    """Encode non-ASCII / space characters in URL path while keeping scheme+host intact."""
    parsed = urllib.parse.urlsplit(url)
    # encode path: spaces → %20, emoji → %XX, keep slashes
    encoded_path = urllib.parse.quote(parsed.path, safe="/:@!$&'()*+,;=")
    encoded_query = urllib.parse.quote(parsed.query, safe="=&+%")
    return urllib.parse.urlunsplit((
        parsed.scheme,
        parsed.netloc,
        encoded_path,
        encoded_query,
        parsed.fragment,
    ))


def fetch_sub_url(url: str) -> list[str]:
    import base64
    configs = []
    try:
        safe_url = _encode_url(url)
        req = urllib.request.Request(safe_url, headers={"User-Agent": "v2rayNG/1.8.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()

        # Try base64 decode first (standard sub format)
        try:
            decoded = base64.b64decode(raw + b"==").decode("utf-8", errors="ignore")
            if any(p in decoded for p in V2RAY_PREFIXES):
                raw_text = decoded
            else:
                raw_text = raw.decode("utf-8", errors="ignore")
        except Exception:
            raw_text = raw.decode("utf-8", errors="ignore")

        for line in raw_text.splitlines():
            line = line.strip()
            if line.startswith(V2RAY_PREFIXES):
                configs.append(line)

    except Exception as e:
        short_url = url[:60] + ".." if len(url) > 60 else url
        print(Fore.RED + f"\n  [!] Failed to fetch {short_url}: {e}" + Style.RESET_ALL)

    return configs


def load_and_fetch_subs(path: str) -> list[str]:
    if not os.path.exists(path):
        print(Fore.YELLOW + f"  [!] {path} not found, skipping." + Style.RESET_ALL)
        return []

    urls = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and line.startswith("http"):
                urls.append(line)

    if not urls:
        print(Fore.YELLOW + f"  [!] No URLs found in {path}" + Style.RESET_ALL)
        return []

    print(Fore.CYAN + f"  [*] Fetching {len(urls)} sub URLs..." + Style.RESET_ALL)
    all_configs = []
    for i, url in enumerate(urls, 1):
        display = url[:65] + ".." if len(url) > 65 else url
        sys.stdout.write(Fore.CYAN + f"\r  [{i:>2}/{len(urls)}] {display:<67}" + Style.RESET_ALL)
        sys.stdout.flush()
        found = fetch_sub_url(url)
        if found:
            all_configs.extend(found)

    print(Fore.GREEN + f"\n  [+] Sub URLs yielded {len(all_configs)} configs" + Style.RESET_ALL)
    return all_configs


# ─────────────────────────────────────────────
#  PING / TEST
# ─────────────────────────────────────────────

def parse_host_port(config: str):
    try:
        for prefix in V2RAY_PREFIXES:
            if config.startswith(prefix):
                rest = config[len(prefix):]
                if "#" in rest:
                    rest = rest[:rest.index("#")]
                if "@" in rest:
                    at = rest.rfind("@")
                    hostpart = rest[at + 1:].split("/")[0].split("?")[0]
                    if ":" in hostpart:
                        host, port_s = hostpart.rsplit(":", 1)
                        return host.strip("[]"), int(port_s)
                try:
                    import base64, json
                    padded = rest + "=" * (-len(rest) % 4)
                    decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")
                    obj = json.loads(decoded)
                    return obj.get("add", ""), int(obj.get("port", 0))
                except Exception:
                    pass
    except Exception:
        pass
    return None, None


def tcp_ping(host: str, port: int, timeout: float) -> float | None:
    try:
        start = time.perf_counter()
        sock = socket.create_connection((host, port), timeout=timeout)
        elapsed = (time.perf_counter() - start) * 1000
        sock.close()
        return round(elapsed, 1)
    except Exception:
        return None


def _print_test_row(i, total, cfg, latency, status):
    short = cfg[:55] + "..." if len(cfg) > 55 else cfg
    if status == "OK":
        lat_str = Fore.GREEN + f"{latency} ms" + Style.RESET_ALL
        tag = Fore.GREEN + "[OK]" + Style.RESET_ALL
    elif status == "ERR":
        lat_str = Fore.YELLOW + "parse err" + Style.RESET_ALL
        tag = Fore.YELLOW + "[??]" + Style.RESET_ALL
    else:
        lat_str = Fore.RED + "timeout" + Style.RESET_ALL
        tag = Fore.RED + "[--]" + Style.RESET_ALL
    print(f"  {tag} [{i:>4}/{total}] {Fore.CYAN}{short:<57}{Style.RESET_ALL}  {lat_str}")


def test_configs(configs: list[str], timeout: float, batch_size: int | None) -> list[dict]:
    targets = configs[:batch_size] if batch_size else list(configs)
    total = len(targets)
    print(Fore.CYAN + f"\n  Testing {total} configs...\n" + Style.RESET_ALL)
    results = []
    for i, cfg in enumerate(targets, 1):
        host, port = parse_host_port(cfg)
        if not host or not port:
            results.append({"config": cfg, "latency": None, "status": "PARSE_ERR"})
            _print_test_row(i, total, cfg, None, "ERR")
            continue
        latency = tcp_ping(host, port, timeout)
        status = "OK" if latency is not None else "DEAD"
        results.append({"config": cfg, "latency": latency, "status": status})
        _print_test_row(i, total, cfg, latency, status)
    return results


def test_configs_parallel(configs: list[str], timeout: float) -> list[dict]:
    results = [None] * len(configs)
    lock = threading.Lock()
    done = [0]
    total = len(configs)
    print(Fore.CYAN + f"\n  Parallel testing {total} configs...\n" + Style.RESET_ALL)

    def worker(idx, cfg):
        host, port = parse_host_port(cfg)
        if not host or not port:
            res = {"config": cfg, "latency": None, "status": "PARSE_ERR"}
        else:
            latency = tcp_ping(host, port, timeout)
            res = {"config": cfg, "latency": latency, "status": "OK" if latency else "DEAD"}
        with lock:
            results[idx] = res
            done[0] += 1
            pct = int((done[0] / total) * 100)
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            sys.stdout.write(Fore.CYAN + f"\r  [{bar}] {pct:3d}%  {done[0]}/{total}" + Style.RESET_ALL)
            sys.stdout.flush()

    threads = [threading.Thread(target=worker, args=(i, c), daemon=True) for i, c in enumerate(configs)]
    for t in threads: t.start()
    for t in threads: t.join()
    print()
    return [r for r in results if r]


# ─────────────────────────────────────────────
#  MENUS
# ─────────────────────────────────────────────

def ask(prompt: str, valid: list[str]) -> str:
    while True:
        sys.stdout.write(Fore.GREEN + f"\n  {prompt}: " + Style.RESET_ALL)
        sys.stdout.flush()
        ans = input().strip()
        if ans in valid:
            return ans
        print(Fore.RED + f"  [!] Enter one of: {', '.join(valid)}" + Style.RESET_ALL)


def ask_test_menu() -> bool:
    print(Fore.YELLOW + """
  ╔══════════════════════════════════╗
  ║   PING TEST                      ║
  ║   [1] Yes — run ping test        ║
  ║   [2] No  — save only            ║
  ╚══════════════════════════════════╝""" + Style.RESET_ALL)
    return ask(">", ["1", "2", "yes", "no", "y", "n"]) in ("1", "yes", "y")


def ask_test_mode(total: int) -> tuple[float, int | None, bool]:
    print(Fore.CYAN + f"""
  ╔══════════════════════════════════════╗
  ║   TEST MODE  ({total} configs)
  ║   Timeout:
  ║   [1] Ultra-fast  (1s)
  ║   [2] Fast        (3s)
  ║   [3] Slow        (8s)
  ╚══════════════════════════════════════╝""" + Style.RESET_ALL)
    timeout = {"1": 1.0, "2": 3.0, "3": 8.0}[ask("Timeout [1/2/3]", ["1", "2", "3"])]

    print(Fore.CYAN + f"""
  ║   Batch:
  ║   [1] All ({total})
  ║   [2] 10
  ║   [3] 50
  ║   [4] 100
  ║   [5] All (parallel)""" + Style.RESET_ALL)
    ans = ask("Batch [1/2/3/4/5]", ["1", "2", "3", "4", "5"])
    batch = {"2": 10, "3": 50, "4": 100}.get(ans)
    return timeout, batch, ans == "5"


# ─────────────────────────────────────────────
#  SAVE
# ─────────────────────────────────────────────

def save_test_results(results: list[dict], run_folder: str):
    alive = sorted([r for r in results if r["status"] == "OK"], key=lambda x: x["latency"])
    dead  = [r for r in results if r["status"] == "DEAD"]
    err   = [r for r in results if r["status"] == "PARSE_ERR"]

    path = os.path.join(run_folder, "tested_alive.txt")
    with open(path, "w", encoding="utf-8") as f:
        for r in alive:
            f.write(f"{r['latency']} ms  |  {r['config']}\n")

    print(Fore.GREEN + f"""
  ╔══════════════════════════════════════════╗
  ║   RESULTS                                ║
  ║   OK    : {len(alive):<6}                      ║
  ║   DEAD  : {len(dead):<6}                      ║
  ║   ERROR : {len(err):<6}                      ║
  ╚══════════════════════════════════════════╝
  Saved: {path}""" + Style.RESET_ALL)

    if alive:
        print(Fore.YELLOW + "\n  -- TOP 10 LOWEST LATENCY --" + Style.RESET_ALL)
        for r in alive[:10]:
            print(Fore.GREEN + f"  {r['latency']:>7} ms  " + Fore.CYAN + r['config'][:70] + Style.RESET_ALL)


# ─────────────────────────────────────────────
#  TELEGRAM AUTH  (persistent session — no re-login)
# ─────────────────────────────────────────────

async def get_client() -> TelegramClient:
    """Return an authenticated TelegramClient. Session is saved to disk."""
    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.start()          # re-uses saved session; prompts only on first run
    if not await client.is_user_authorized():
        print(Fore.RED + "  [!] Not authorized. Delete v2ray_session.session and re-run." + Style.RESET_ALL)
        sys.exit(1)
    return client


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

async def main():
    now = datetime.now()
    since_time = now - timedelta(hours=24)
    run_folder = os.path.join(BASE_DIR, now.strftime("%d_%H-%M"))
    npv_folder = os.path.join(run_folder, "NPV")
    hat_folder = os.path.join(run_folder, "HAT")
    for d in (run_folder, npv_folder, hat_folder):
        os.makedirs(d, exist_ok=True)

    v2ray_path = os.path.join(run_folder, "v2ray_configs.txt")
    proxy_path = os.path.join(run_folder, "telegram_proxies.txt")

    # ── Fetch sub URLs ──
    sub_configs = load_and_fetch_subs(SUB_LINKS_FILE)

    # ── Telegram scan ──
    targets = list(dict.fromkeys(channels))   # deduplicate, preserve order
    total = len(targets)
    print(Fore.GREEN + f"  [+] {total} Telegram targets queued\n" + Style.RESET_ALL)

    client = await get_client()

    v2ray_configs = set()
    proxy_configs = set()
    error_channels = []

    for idx, target in enumerate(targets, 1):
        bar_w = 20
        fill = int((idx / total) * bar_w)
        bar = "█" * fill + "░" * (bar_w - fill)
        pct = int((idx / total) * 100)
        sys.stdout.write(
            Fore.CYAN + f"\r  [{idx:>3}/{total}] @{target:<24} [{bar}] {pct:3d}%  " + Style.RESET_ALL
        )
        sys.stdout.flush()

        try:
            async for msg in client.iter_messages(target):
                if msg.date.replace(tzinfo=None) < since_time:
                    break
                if msg.file and msg.file.name:
                    name = msg.file.name.lower()
                    if name.endswith(NPVT_EXT):
                        await msg.download_media(file=os.path.join(npv_folder, msg.file.name))
                    elif name.endswith(HAT_EXT):
                        await msg.download_media(file=os.path.join(hat_folder, msg.file.name))
                if msg.text:
                    for line in msg.text.splitlines():
                        line = line.strip()
                        if line.startswith(V2RAY_PREFIXES):
                            v2ray_configs.add(line)
                        if line.startswith(PROXY_PREFIXES):
                            proxy_configs.add(line)
                if msg.entities:
                    for ent in msg.entities:
                        if isinstance(ent, MessageEntityTextUrl):
                            if ent.url.startswith(PROXY_PREFIXES):
                                proxy_configs.add(ent.url)
                        elif isinstance(ent, MessageEntityUrl):
                            url = msg.text[ent.offset: ent.offset + ent.length]
                            if url.startswith(PROXY_PREFIXES):
                                proxy_configs.add(url)
        except Exception as e:
            error_channels.append(target)
            print(f"\n  [!] Skip {target}: {e}")

    print()
    await client.disconnect()

    # ── Warn about dead channels ──
    if error_channels:
        print(Fore.YELLOW + f"  [!] {len(error_channels)} channels had errors (consider removing):" + Style.RESET_ALL)
        for ch in error_channels:
            print(Fore.YELLOW + f"      - {ch}" + Style.RESET_ALL)

    # ── Merge + rename ──
    all_raw = v2ray_configs | set(sub_configs)
    renamed = [rename_config(c) for c in all_raw]

    if renamed:
        with open(v2ray_path, "w", encoding="utf-8") as f:
            f.write("\n".join(renamed))

    if proxy_configs:
        with open(proxy_path, "w", encoding="utf-8") as f:
            f.write("\n".join(proxy_configs))

    print(Fore.GREEN + f"""
  ╔══════════════════════════════════════════╗
  ║   SCAN COMPLETE                          ║
  ║   Telegram configs : {len(v2ray_configs):<6}              ║
  ║   Sub URL configs  : {len(sub_configs):<6}              ║
  ║   Total (renamed)  : {len(renamed):<6}              ║
  ║   Proxies          : {len(proxy_configs):<6}              ║
  ║   Folder           : {run_folder:<22} ║
  ╚══════════════════════════════════════════╝""" + Style.RESET_ALL)

    if renamed and ask_test_menu():
        timeout, batch, parallel = ask_test_mode(len(renamed))
        results = test_configs_parallel(renamed, timeout) if parallel else test_configs(renamed, timeout, batch)
        save_test_results(results, run_folder)

    print(Fore.YELLOW + "\n  Done. Ctrl+C to exit.\n" + Style.RESET_ALL)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
