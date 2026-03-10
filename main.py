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

os.system('clear')

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
if not share_count:
  print("No count provided")
  sys.exit()

os.system('clear')

HEADERS = {
  'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
  'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-platform': "Android",
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1'
}

# Global state
lock = threading.Lock()
global_success = 0
global_failed = 0
cookie_stats = {
  i: {'success': 0, 'failed': 0, 'status': 'waiting', 'token': ''}
  for i in range(len(config['cookies']))
}

console = Console()

def build_table():
  total_target = share_count * len(config['cookies'])
  table = Table(
    title=f"[bold cyan]SpamShare | Total: {global_success}/{total_target} | Failed: {global_failed}[/bold cyan]",
    border_style="cyan", expand=True
  )
  table.add_column("Cookie", style="bold white", justify="center")
  table.add_column("Token", style="dim white")
  table.add_column("OK", style="bold green", justify="center")
  table.add_column("Fail", style="bold red", justify="center")
  table.add_column("Status", justify="center")

  status_colors = {
    'waiting': 'yellow', 'running': 'cyan',
    'done': 'green', 'blocked': 'red', 'error': 'red'
  }
  for i, s in cookie_stats.items():
    color = status_colors.get(s['status'], 'white')
    token = (s['token'][:14] + '...') if s['token'] else 'N/A'
    table.add_row(
      f"#{i+1}", token,
      str(s['success']), str(s['failed']),
      f"[{color}]{s['status'].upper()}[/{color}]"
    )
  return table

async def get_token(cookie):
  hdrs = HEADERS.copy()
  hdrs['cookie'] = cookie
  try:
    async with aiohttp.ClientSession() as session:
      async with session.get(
        'https://business.facebook.com/content_management',
        headers=hdrs, timeout=aiohttp.ClientTimeout(total=30)
      ) as resp:
        text = await resp.text()
        match = re.search(r'EAAG(.*?)","', text)
        if match:
          return 'EAAG' + match.group(1)
  except Exception:
    pass
  return None

async def do_shares(cookie, cookie_index, live):
  global global_success, global_failed

  token = await get_token(cookie)
  if not token:
    with lock:
      cookie_stats[cookie_index]['status'] = 'error'
    live.update(build_table())
    return

  with lock:
    cookie_stats[cookie_index]['token'] = token
    cookie_stats[cookie_index]['status'] = 'running'
  live.update(build_table())

  hdrs = HEADERS.copy()
  hdrs['accept-encoding'] = 'gzip, deflate'
  hdrs['host'] = 'b-graph.facebook.com'
  hdrs['cookie'] = cookie

  async with aiohttp.ClientSession() as session:
    while True:
      with lock:
        done = cookie_stats[cookie_index]['success'] >= share_count
      if done:
        break
      try:
        url = (
          f'https://b-graph.facebook.com/me/feed'
          f'?link=https://mbasic.facebook.com/{config["post"]}'
          f'&published=0&access_token={token}'
        )
        async with session.post(url, headers=hdrs, timeout=aiohttp.ClientTimeout(total=30)) as resp:
          data = await resp.json()
          with lock:
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
      except Exception as e:
        with lock:
          global_failed += 1
          cookie_stats[cookie_index]['failed'] += 1
        live.update(build_table())
        await asyncio.sleep(0.5)

  with lock:
    cookie_stats[cookie_index]['status'] = 'done'
  live.update(build_table())

def run_thread(cookie, cookie_index, live):
  # Each thread runs its own isolated event loop — Termux safe
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  try:
    loop.run_until_complete(do_shares(cookie, cookie_index, live))
  finally:
    loop.close()

def main():
  with Live(build_table(), console=console, refresh_per_second=15) as live:
    threads = []
    for i, cookie in enumerate(config['cookies']):
      t = threading.Thread(target=run_thread, args=(cookie, i, live), daemon=True)
      t.start()
      threads.append(t)
    for t in threads:
      t.join()

  total = share_count * len(config['cookies'])
  print(f"\n\033[32m[✓] Done! Shares: {global_success}/{total} | Failed: {global_failed}\033[0m")

main()
