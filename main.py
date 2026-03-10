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
  "version": '1',
}


config = {
  'cookies': '',
  'post': ''
}


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
config['cookies'] = input("\033[0mCOOKIE : \033[92m")
config['post'] = input("\033[0mPOST LINK : \033[92m")
share_count = int(input("\033[0mSHARE COUNT : \033[92m"))


if not config['post'].startswith('https://'):
  print("Invalid post link")
  sys.exit()
elif not share_count:
  print("Invalid share count")
  sys.exit()


os.system('cls' if os.name == 'nt' else 'clear')
print("\033[33m[*] \033[0mChecking your inputs, please wait...")
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


class Share:
  async def get_token(self, session):
    headers['cookie'] = config['cookies']
    async with session.get('https://business.facebook.com/content_management', headers=headers) as response:
      data = await response.text()
      access_token = 'EAAG' + re.search('EAAG(.*?)","', data).group(1)
      return access_token, headers['cookie']


  async def share(self, session, token, cookie):
    headers['accept-encoding'] = 'gzip, deflate'
    headers['host'] = 'b-graph.facebook.com'
    headers['cookie'] = cookie
    count = 1
    console = Console()
    os.system('cls' if os.name == 'nt' else 'clear')
    with console.status("[bold green]Sharing facebook post...") as stats:
      while count < share_count + 1:
        async with session.post(
          f'https://b-graph.facebook.com/me/feed?link=https://mbasic.facebook.com/{config["post"]}&published=0&access_token={token}',
          headers=headers) as response:
          data = await response.json()
          if 'id' in data:
            console.log(f"{count}/{share_count} Complete")
            count += 1
          else:
            console.log("[red]Cookie is blocked, CTRL+C to exit !!!")
            console.log(f"Total success: {count}")
            break
    print(f"\033[32m[*] \033[0mSharing post done!!")
    exit()


async def main(num_tasks):
  async with aiohttp.ClientSession() as session:
    share = Share()
    token, cookie = await share.get_token(session)
    tasks = []
    for i in range(num_tasks):
      task = asyncio.create_task(share.share(session, token, cookie))
      tasks.append(task)
    await asyncio.gather(*tasks)


asyncio.run(main(1))
