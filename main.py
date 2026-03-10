import os
import asyncio
import aiohttp
import re
import sys
import threading
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

config = {
  'cookies': [],
  'post': ''
}

os.system('cls' if os.name == 'nt' else 'clear')

print("\033[92mEnter cookies one by one. Type 'done' when finished.\033[0m")
while True:
  cookie = input(f"\033[0mCOOKIE #{len(config['cookies']) + 1} (or 'done'): \033[92m").strip()
  if cookie.lower() == 'done':
    if len(config['cookies']) == 0:
      print("\033[91mAt least one cookie required!\033[0m")
      continue
    break
  if cookie:
    config['cookies'].append(cookie)

config['post'] = input("\033[0mPOST LINK : \033[92m").strip()
share_count = int(input("\033[0mSHARE COUNT (per cookie): \033[92m"))

if not config['post'].startswith('https://'):
  print("Invalid post link")
  sys.exit()
elif not share_count:
  print("No count provided")
  sys.exit()

os.system('cls' if os.name == 'nt' else 'clear')

headers_template = {
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

# Global counters
global_lock = threading.Lock()
global_success = 0
global_failed = 0
cookie_stats = {}

for i, c in enumerate(config['cookies']):
  cookie_stats[i] = {'success': 0, 'failed': 0, 'status': 'waiting', 'token': ''}

console = Console()

def build_table():
  total_target = share_count * len(config['cookies'])
  table = Table(title=f"[bold cyan]SpamShare - Global: {global_success}/{total_target} | Failed: {global_failed}[/bold cyan]", 
                border_style="cyan", expand=True)
  table.add_column("Cookie #", style="bold white", justify="center", width=10)
  table.add_column("Token Preview", style="dim white", width=20)
  table.add_column("Success", style="bold green", justify="center", width=10)
  table.add_column("Failed", style="bold red", justify="center", width=10)
  table.add_column("Status", justify="center", width=15)

  for i, stats in cookie_stats.items():
    status_color = {
      'waiting': 'yellow',
      'running': 'cyan',
      'done': 'green',
      'blocked': 'red',
      'error': 'red'
    }.get(stats['status'], 'white')

    token_preview = stats['token'][:15] + '...' if stats['token'] else 'N/A'
    table.add_row(
      f"#{i+1}",
      token_preview,
      str(stats['success']),
      str(stats['failed']),
      f"[{status_color}]{stats['status'].upper()}[/{status_color}]"
    )
  return table

class Share:
  async def get_token(self, session, cookie):
    hdrs = headers_template.copy()
    hdrs['cookie'] = cookie
    try:
      async with session.get('https://business.facebook.com/content_management', headers=hdrs) as response:
        data = await response.text()
        match = re.search('EAAG(.*?)","', data)
        if not match:
          return None, cookie
        access_token = 'EAAG' + match.group(1)
        return access_token, cookie
    except Exception:
      return None, cookie

  async def share_worker(self, session, token, cookie, cookie_index, live):
    global global_success, global_failed
    hdrs = headers_template.copy()
    hdrs['accept-encoding'] = 'gzip, deflate'
    hdrs['host'] = 'b-graph.facebook.com'
    hdrs['cookie'] = cookie

    cookie_stats[cookie_index]['status'] = 'running'
    cookie_stats[cookie_index]['token'] = token

    while cookie_stats[cookie_index]['success'] < share_count:
      try:
        async with session.post(
          f'https://b-graph.facebook.com/me/feed?link=https://mbasic.facebook.com/{config["post"]}&published=0&access_token={token}',
          headers=hdrs
        ) as response:
          data = await response.json()
          with global_lock:
            if 'id' in data:
              global_success += 1
              cookie_stats[cookie_index]['success'] += 1
            else:
              global_failed += 1
              cookie_stats[cookie_index]['failed'] += 1
              cookie_stats[cookie_index]['status'] = 'blocked'
              live.update(build_table())
              return
          live.update(build_table())
      except Exception:
        with global_lock:
          global_failed += 1
          cookie_stats[cookie_index]['failed'] += 1
        live.update(build_table())

    cookie_stats[cookie_index]['status'] = 'done'
    live.update(build_table())

async def run_cookie(cookie, cookie_index, live):
  async with aiohttp.ClientSession() as session:
    share = Share()
    token, ck = await share.get_token(session, cookie)
    if not token:
      cookie_stats[cookie_index]['status'] = 'error'
      live.update(build_table())
      return
    await share.share_worker(session, token, ck, cookie_index, live)

def thread_runner(cookie, cookie_index, live, loop):
  asyncio.run_coroutine_threadsafe(run_cookie(cookie, cookie_index, live), loop).result()

async def main():
  loop = asyncio.get_event_loop()
  with Live(build_table(), console=console, refresh_per_second=10) as live:
    threads = []
    for i, cookie in enumerate(config['cookies']):
      t = threading.Thread(target=thread_runner, args=(cookie, i, live, loop))
      t.start()
      threads.append(t)
    for t in threads:
      t.join()

  total_target = share_count * len(config['cookies'])
  print(f"\n\033[32m[*] \033[0mAll done! Global shares: {global_success}/{total_target}")

asyncio.run(main())
