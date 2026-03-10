import os
import asyncio
import aiohttp
import re
import sys
from rich.console import Console

info = {
  "owner": 'Astro Ksks',
  "facebook": 'https://www.facebook.com/christhenoob13',
  "tool": 'Spamshare',
  "version": '2',
}

config = {
  'cookies': [],
  'post': ''
}

global_count = 0
lock = asyncio.Lock()

os.system('cls' if os.name == 'nt' else 'clear')


def banner():
  bannir = f"""
\033[1;97m=============================================================
  OWNER: \033[32m{info['owner']}\033[0m
  FACEBOOK: {info['facebook']}
  TOOL: {info['tool']}
  VERSION: {info['version']}
=============================================================
  """
  print(bannir)


banner()

print("\033[0mEnter cookies one per line. Type \033[92mdone\033[0m when finished:")
cookie_num = 1
while True:
  cookie = input(f"\033[0mCOOKIE {cookie_num}: \033[92m")
  if cookie.lower() == 'done':
    break
  if cookie.strip():
    config['cookies'].append(cookie.strip())
    cookie_num += 1

if not config['cookies']:
  print("\033[31m[!] No cookies provided.\033[0m")
  sys.exit()

print(f"\033[33m[*] \033[0mLoaded \033[92m{len(config['cookies'])}\033[0m cookies")

config['post'] = input("\033[0mPOST LINK : \033[92m")
share_count = int(input("\033[0mSHARE COUNT (per cookie) : \033[92m"))

if not config['post'].startswith('https://'):
  print("Invalid post link")
  sys.exit()
elif not share_count:
  print("Invalid share count")
  sys.exit()

os.system('cls' if os.name == 'nt' else 'clear')

headers = {
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

console = Console()
total_target = share_count * len(config['cookies'])


async def get_token(session, cookie):
  h = headers.copy()
  h['cookie'] = cookie
  async with session.get('https://business.facebook.com/content_management', headers=h) as response:
    data = await response.text()
    match = re.search('EAAG(.*?)","', data)
    if not match:
      return None, cookie
    return 'EAAG' + match.group(1), cookie


async def share_worker(session, token, cookie, cookie_id):
  global global_count
  h = headers.copy()
  h['accept-encoding'] = 'gzip, deflate'
  h['host'] = 'b-graph.facebook.com'
  h['cookie'] = cookie
  local_count = 0

  while local_count < share_count:
    try:
      async with session.post(
        f'https://b-graph.facebook.com/me/feed?link=https://mbasic.facebook.com/{config["post"]}&published=0&access_token={token}',
        headers=h) as response:
        data = await response.json()
        if 'id' in data:
          local_count += 1
          async with lock:
            global_count += 1
            console.log(f"\033[92m[Cookie {cookie_id}] \033[0m{local_count}/{share_count} | \033[97mGlobal: {global_count}/{total_target}\033[0m")
        else:
          console.log(f"\033[31m[Cookie {cookie_id}] Blocked or expired. Stopping this cookie.\033[0m")
          break
    except Exception as e:
      console.log(f"\033[31m[Cookie {cookie_id}] Error: {e}\033[0m")
      break

  return local_count


async def main():
  global global_count
  connector = aiohttp.TCPConnector(limit=0)
  async with aiohttp.ClientSession(connector=connector) as session:
    print("\033[33m[*] \033[0mGetting tokens for all cookies...")

    token_tasks = [get_token(session, cookie) for cookie in config['cookies']]
    results = await asyncio.gather(*token_tasks)

    valid = []
    for i, (token, cookie) in enumerate(results):
      if token:
        valid.append((token, cookie, i + 1))
        console.log(f"\033[92m[Cookie {i + 1}] Token OK\033[0m")
      else:
        console.log(f"\033[31m[Cookie {i + 1}] Failed - expired or invalid\033[0m")

    if not valid:
      print("\033[31m[!] No valid cookies. Exiting.\033[0m")
      sys.exit()

    print(f"\n\033[33m[*] \033[0mStarting shares with \033[92m{len(valid)}\033[0m valid cookies | Target: \033[92m{total_target}\033[0m total shares\n")

    share_tasks = [share_worker(session, token, cookie, cid) for token, cookie, cid in valid]
    results = await asyncio.gather(*share_tasks)

    print(f"\n\033[32m[*] \033[0mDone! Total shares: \033[92m{global_count}/{total_target}\033[0m")


asyncio.run(main())
