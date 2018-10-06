import asyncio
import os
import random
import re
from time import sleep
import aiofiles
import aiohttp
import requests
from fake_useragent import UserAgent


class Spider:

    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.retry_list = []

    @staticmethod
    def get_name(url):
        """文件名字"""
        pattern = re.compile(r'([\w-]+)\..[ts|mp4]+$')
        name = pattern.findall(url)[-1]
        return name

    def downloader(self, url):
        """下载器"""
        name = Spider.get_name(url)
        print(f'正在下载: {name}')
        try:
            resp = requests.get(url, headers=self.headers, stream=True, timeout=30)
            with open(f'videos\{name}.ts', 'wb') as f:
                f.write(resp.content)
        except:
            print(f'下载错误!!: {name}')

    async def fetch(self, url, session):
        """异步下载器"""
        try:
            async with session.get(url, headers=HEADERS, timeout=60) as resp:
                print(url, '请求成功!!')
                name = self.get_name(url)
                f = await aiofiles.open(f'videos\{name}.ts', 'wb')
                await f.write(await resp.read())
                await f.close()
        except Exception:
            print('下载超时!!')
            self.retry_list.append(url)
            pass

    async def adownloader(self, urls):
        """设置异步下载任务"""
        async with aiohttp.ClientSession() as session:
            print('正在请求')
            tasks = [asyncio.ensure_future(self.fetch(url, session)) for url in urls]
            return await asyncio.gather(*tasks)

    def get_urls(self, url):
        """获取视频列表"""
        name = Spider.get_name(url)
        self.downloader(url) # 下载M3U8文件, 即视频列表
        try:
            with open(f'videos\{name}.ts', 'r') as f:
                urls = []
                for i in f.readlines():
                    ts = re.search(r'https://.*?\.ts', i)
                    if ts:
                        urls.append(ts.group())
                if not urls:
                    print('没有获取到视频列表!!')
            return urls
        except FileNotFoundError:
            print('没有下载列表文件')


    def merge_videos(self):
        print('稍等片刻...') # 下载完再合并, 不要马上合并
        sleep(3)
        print('正在合并视频..')
        videos = os.listdir('videos')
        videos.sort(key=len)
        q = (f"file '{video}'" for video in videos[1:])
        with open('videos/videos.txt', 'w') as f:
            for i in q:
                f.write(i+'\n')
        name = Spider.get_name(self.url)
        os.system(f'cd videos && ffmpeg -f concat -i videos.txt -c copy {name}.mp4')
        self.delete()

    def delete(self):
        name = self.get_name(self.url)
        print('正在删除碎片视频..')
        l = os.listdir('videos')
        [os.system(f'cd videos && del {i}') for i in l if f'{name}.mp4' not in i]

    def start_requests(self):
        url_list = self.get_urls(URL)
        if url_list:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.adownloader(url_list))
            while self.retry_list: # 失败重试
                tasks = self.retry_list
                self.retry_list = []
                loop.run_until_complete(self.adownloader(tasks))
            else:
                loop.close()

    def run(self):
        if not os.path.exists('videos'):
            os.mkdir('videos')
        self.start_requests()
        self.merge_videos()
        print('finish')


if __name__ == '__main__':
    # 播放视频的原网址
    SOURCE_URL = 'https://avgle.com/video/5nzxkxfbGx5/kolvr-013-vr-%E5%A5%B3%E9%81%94%E3%81%AE%E3%83%8F-%E3%83%88%E3%83%AB%E9%96%8B%E5%A7%8B-%E8%A3%9C%E7%BF%92%E4%B8%AD%E3%81%AB%E6%80%9D%E3%81%84%E3%81%8B-%E3%81%91%E3%81%99-%E3%83%8F%E3%83%BC%E3%83%AC%E3%83%A0%E3%83%95-%E3%83%AC%E3%82%A4'
    # 关闭广告后的302网址, 利用抓包获取, key根据video_id生成且有时效性
    URL = 'https://cdn.qooqlevideo.com/key=5LACOPNa4-xdA4sRE-f2Ng,end=1538805966,limit=2/referer=force,.avgle.com/data=1538805966/media=hlsA/146431.mp4'

    HEADERS = {
        'Origin': 'https://avgle.com',
        'authority': 'ip54177648.ahcdn.com',
        'user-agent': UserAgent().random,
        'referer': SOURCE_URL,
    }

    main = Spider(URL, HEADERS)
    main.run()