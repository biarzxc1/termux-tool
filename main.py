import os
import asyncio
import aiohttp
import re
import sys
import threading
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live

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

# ── Shared state ──────────────────────────────────────────────
lock = threading.Lock()
global_success = 0
global_failed  = 0
cookie_stats   = {
  i: {'success': 0, 'failed': 0, 'status': 'waiting', 'token': ''}
  for i in range(len(config['cookies']))
}
done_event = threading.Event()

console = Console()

# ── Table builder ─────────────────────────────────────────────
def build_table():
  total = share_count * len(config['cookies'])
  table = Table(
    title=f"[bold cyan]SpamShare  Global: {global_success}/{total}  Failed: {global_failed}[/bold cyan]",
    border_style="cyan", expand=True
  )
  table.add_column("Cookie #",      style="bold white",  justify="center", width=10)
  table.add_column("Token Preview", style="dim white",   width=22)
  table.add_column("Success",       style="bold green",  justify="center", width=10)
  table.add_column("Failed",        style="bold red",    justify="center", width=10)
  table.add_column("Status",        justify="center",    width=12)

  color_map = {
    'waiting': 'yellow', 'running': 'cyan',
    'done':    'green',  'blocked': 'red', 'error': 'red'
  }
  for i, s in cookie_stats.items():
    c = color_map.get(s['status'], 'white')
    tok = (s['token'][:18] + '...') if s['token'] else 'N/A'
    table.add_row(
      f"#{i+1}", tok,
      str(s['success']), str(s['failed']),
      f"[{c}]{s['status'].upper()}[/{c}]"
    )
  return table

# ── Display thread ────────────────────────────────────────────
def display_loop(live):
  while not done_event.is_set():
    live.update(build_table())
    time.sleep(0.3)
  live.update(build_table())   # final refresh

# ── Per-cookie async worker (runs in its own thread+loop) ─────
async def run_cookie(cookie, idx):
  global global_success, global_failed

  hdrs = HEADERS.copy()
  hdrs['cookie'] = cookie

  # 1. get token
  try:
    async with aiohttp.ClientSession() as session:
      async with session.get(
        'https://business.facebook.com/content_management', headers=hdrs
      ) as resp:
        text  = await resp.text()
        match = re.search('EAAG(.*?)","', text)
        if not match:
          with lock:
            cookie_stats[idx]['status'] = 'error'
          return
        token = 'EAAG' + match.group(1)

    with lock:
      cookie_stats[idx]['token']  = token
      cookie_stats[idx]['status'] = 'running'

    # 2. share loop — no sleep, no delay
    share_hdrs = HEADERS.copy()
    share_hdrs.update({
      'accept-encoding': 'gzip, deflate',
      'host':   'b-graph.facebook.com',
      'cookie': cookie
    })

    connector = aiohttp.TCPConnector(limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
      while True:
        with lock:
          done = cookie_stats[idx]['success'] >= share_count
        if done:
          break

        try:
          async with session.post(
            f'https://b-graph.facebook.com/me/feed'
            f'?link=https://mbasic.facebook.com/{config["post"]}'
            f'&published=0&access_token={token}',
            headers=share_hdrs
          ) as resp:
            data = await resp.json(content_type=None)
            with lock:
              if 'id' in data:
                global_success               += 1
                cookie_stats[idx]['success'] += 1
              else:
                global_failed               += 1
                cookie_stats[idx]['failed'] += 1
                cookie_stats[idx]['status'] = 'blocked'
                return
        except Exception:
          with lock:
            global_failed               += 1
            cookie_stats[idx]['failed'] += 1

    with lock:
      cookie_stats[idx]['status'] = 'done'

  except Exception as e:
    with lock:
      cookie_stats[idx]['status'] = 'error'

def thread_entry(cookie, idx):
  """Each cookie runs its own event loop — safe in Termux."""
  asyncio.run(run_cookie(cookie, idx))

# ── Main ──────────────────────────────────────────────────────
def main():
  threads = [
    threading.Thread(target=thread_entry, args=(ck, i), daemon=True)
    for i, ck in enumerate(config['cookies'])
  ]

  with Live(build_table(), console=console, refresh_per_second=0) as live:
    disp = threading.Thread(target=display_loop, args=(live,), daemon=True)
    disp.start()

    for t in threads:
      t.start()
    for t in threads:
      t.join()

    done_event.set()
    disp.join()

  total = share_count * len(config['cookies'])
  print(f"\n\033[32m[✓]\033[0m Done! {global_success}/{total} shares sent.")

main()
