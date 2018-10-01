import os
import re
import requests


class Spider:

    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

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
            resp = requests.get(url, headers=self.headers, stream=True, timeout=10)
            with open(f'videos\{name}.ts', 'wb') as f:
                f.write(resp.content)
        except requests.exceptions:
            print(f'下载错误!!: {name}')
            pass

    def get_urls(self, url):
        """获取视频列表"""
        name = Spider.get_name(url)
        self.downloader(url) # 下载M3U8文件, 即视频列表
        with open(f'videos\{name}.ts', 'r') as f:
            urls = []
            for i in f.readlines():
                ts = re.search(r'https://.*?\.ts', i)
                if ts:
                    urls.append(ts.group())
            return urls

    def get_videos(self, urls):
        """下载视频"""
        for url in urls:
            self.downloader(url)
        self.merge_videos()

    def merge_videos(self):
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

    def run(self):
        if not os.path.exists('videos'):
            os.mkdir('videos')
        url_list = self.get_urls(URL)
        self.get_videos(url_list)
        print('finish')


if __name__ == '__main__':
    # 播放视频的原网址
    SOURCE_URL = 'https://avgle.com/video/CYGlilf1AlC/kbj-irene-6-kbj-pw'
    # 关闭广告后的302网址, 利用抓包获取, key根据video_id生成且有时效性
    URL = 'https://cdn.qooqlevideo.com/key=IzvvoXcywPywB+OIdQu8BQ,end=1538381800,limit=2/referer=force,.avgle.com/data=1538381800/media=hlsA/127683.mp4'

    HEADERS = {
        'authority': 'ip54177648.ahcdn.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'referer': SOURCE_URL,
    }

    main = Spider(URL, HEADERS)
    main.run()