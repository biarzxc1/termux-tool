import os
import asyncio
import aiohttp
import re
import sys
import threading
from rich.console import Console
from rich.live import Live
from rich.table import Table

config = {
    'cookies': [],
    'post': ''
}

share_lock = threading.Lock()
global_count = 0
cookie_stats = {}

os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    print("""
\033[1;97m=============================================================
  TOOL: Spamshare Multi-Cookie
=============================================================
    """)

banner()

print("\033[0mEnter cookies one per line. Type \033[92mDONE\033[0m when finished:\n")
cookie_num = 1
while True:
    cookie = input(f"\033[0mCOOKIE {cookie_num}: \033[92m").strip()
    if cookie.upper() == 'DONE':
        break
    if cookie:
        config['cookies'].append(cookie)
        cookie_num += 1

if not config['cookies']:
    print("\033[31mNo cookies provided!\033[0m")
    sys.exit()

config['post'] = input("\n\033[0mPOST LINK : \033[92m").strip()
share_count = int(input("\033[0mSHARE COUNT (per cookie) : \033[92m"))

if not config['post'].startswith('https://'):
    print("\033[31mInvalid post link\033[0m")
    sys.exit()
if not share_count:
    print("\033[31mNo share count provided\033[0m")
    sys.exit()

total_target = share_count * len(config['cookies'])
os.system('cls' if os.name == 'nt' else 'clear')
print(f"\033[33m[*] \033[0mLoaded {len(config['cookies'])} cookies | Target: {total_target} total shares\n")

headers_base = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "Windows",
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1'
}

async def get_token(session, cookie):
    headers = {**headers_base, 'cookie': cookie}
    async with session.get('https://business.facebook.com/content_management', headers=headers) as response:
        data = await response.text()
        match = re.search('EAAG(.*?)","', data)
        if not match:
            return None
        return 'EAAG' + match.group(1)

async def share_worker(cookie_index, cookie):
    global global_count
    console = Console()
    label = f"Cookie-{cookie_index + 1}"

    async with aiohttp.ClientSession() as session:
        token = await get_token(session, cookie)
        if not token:
            console.log(f"[red][{label}] Failed to get token - cookie may be invalid")
            cookie_stats[label] = {'status': 'FAILED', 'count': 0}
            return

        headers = {
            **headers_base,
            'accept-encoding': 'gzip, deflate',
            'host': 'b-graph.facebook.com',
            'cookie': cookie
        }

        local_count = 0
        cookie_stats[label] = {'status': 'ACTIVE', 'count': 0}

        tasks = []
        for _ in range(share_count):
            tasks.append(do_share(session, headers, token, label))

        results = await asyncio.gather(*tasks)

        for success in results:
            if success:
                local_count += 1
                with share_lock:
                    global_count += 1
                cookie_stats[label]['count'] = local_count

        cookie_stats[label]['status'] = 'DONE'
        console.log(f"[green][{label}] Finished: {local_count}/{share_count} shares")

async def do_share(session, headers, token, label):
    try:
        url = f'https://b-graph.facebook.com/me/feed?link=https://mbasic.facebook.com/{config["post"]}&published=0&access_token={token}'
        async with session.post(url, headers=headers) as response:
            data = await response.json()
            if 'id' in data:
                return True
            return False
    except:
        return False

def run_cookie(cookie_index, cookie):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(share_worker(cookie_index, cookie))
    loop.close()

threads = []
for i, cookie in enumerate(config['cookies']):
    t = threading.Thread(target=run_cookie, args=(i, cookie))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

os.system('cls' if os.name == 'nt' else 'clear')
print("\n\033[1;97m====================== RESULTS ======================\033[0m")
for label, stats in cookie_stats.items():
    status_color = "\033[32m" if stats['status'] == 'DONE' else "\033[31m"
    print(f"  {label}: {status_color}{stats['status']}\033[0m — {stats['count']} shares")
print(f"\n  \033[1;36mGLOBAL TOTAL: {global_count}/{total_target} shares\033[0m")
print("\033[1;97m=====================================================\033[0m\n")
