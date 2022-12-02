#!/usr/bin/env python3
# coding=utf-8

from dataclasses import dataclass
from time import sleep
from urllib.parse import urlparse
import ffmpeg
import fire
import requests
import yaml
from os.path import dirname, join, realpath
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Page
from utilities import logger
from os.path import basename

# read config.yml file using yaml
with open(
    join(dirname(realpath(__file__)), "config.yml"),
    mode="r",
    encoding="utf-8",
) as file:
    config = yaml.safe_load(file)

logger.info(f"load config: {config}")

headless: bool = config['playwright']['headless']
slow_mo: int = config['playwright']['slow_mo']
download_location: str = config['common']['download_location']
convert_to_mp3: bool = config['common']['convert_to_mp3']
player_wait_seconds: int = config['common']['player_wait_seconds']


@dataclass
class Music:
    url: str = None
    original_file_name: str = None
    title: str = None
    artist: str = None
    album: str = None


class QQMusicDownloader:
    def __init__(self):
        ...

    @staticmethod
    def parse(song_id: str):
        with sync_playwright() as p:
            browser = p.chromium.launch(
                channel="chrome", headless=headless, slow_mo=slow_mo)
            context = browser.new_context()
            page: Page = context.new_page()
            page.goto(f'https://y.qq.com/n/ryqq/songDetail/{song_id}')
            title = page.locator(
                '#app > div > div.main > div.mod_data > div > div.data__name > h1').inner_text()
            artist = page.locator(
                '#app > div > div.main > div.mod_data > div > div.data__singer > a').inner_text()
            album = page.locator(
                '#app > div > div.main > div.mod_data > div > ul > li:nth-child(1) > a').inner_text()
            music = Music(title=title, artist=artist, album=album)
            # intercept m4a request, save to local

            def handle_route(route):
                url = route.request.url
                logger.info(f'intercepted {url}')
                # get filename from url using urllib.parse
                music.url = url
                music.original_file_name = basename(urlparse(url).path)
                # we don't download music file here. we just save the url
                # response = page.request.fetch(url)
                # result = response.body()
                # logger.info(f"response: {result}")
                # route.fulfill(status=200, body=result)
                route.continue_()

            context.route("/**/*.mp3?*", handle_route)
            context.route("/**/*.m4a?*", handle_route)
            with context.expect_page() as new_page_info:
                logger.info(f'click play button')
                # document.querySelector('div.data__actions > a.mod_btn_green')
                page.click('div.data__actions > a.mod_btn_green')

            page.close()
            page = new_page_info.value
            logger.info(f'get new_page_info: {new_page_info}')
            # sometimes, the popup will not shonw up, the music played inmediately
            # page.wait_for_selector('body > div > div.yqq-dialog-root')
            # page.click('div.yqq-dialog-wrap div.yqq-dialog-content  div.popup__ft > button')
            # wait for a few monments
            # sleep(player_wait_seconds)
            page.wait_for_selector(
                '#app > div.mod_player > div.player__ft > a.btn_big_play.btn_big_play--pause')
            browser.close()
            return music

    @staticmethod
    def download(music: Music):
        logger.info(f'try to download {music.url}')
        content = requests.get(music.url, allow_redirects=True).content
        logger.info(f'download done')
        original_extension = music.original_file_name.split('.')[-1]
        # warning the user if the file extension is not m4a, maybe the music is vip only
        if original_extension != 'm4a':
          logger.warning(f'The music may be vip only!')
        music_file_name = f'{music.title}-{music.artist}.{original_extension}'
        saved_file = join(download_location, music_file_name)
        with open(saved_file, 'wb') as f:
            logger.info(f'saved to {saved_file}')
            f.write(content)
        if convert_to_mp3:
            if original_extension == 'mp3':
                logger.info(f'no need to convert to mp3')
                return
            logger.info(
                f'try to convert to mp3 using ffmpeg-python, please install ffmpeg first')
            stream = ffmpeg.input(music_file_name)
            stream = ffmpeg.hflip(stream)
            stream = ffmpeg.output(stream, f'{music.title}-{music.artist}.mp3')
            ffmpeg.run(stream)


def main(song_id: str = '000Z9mNt109oQd'):
    '''
    song_id: QQ音乐歌曲ID, 例如 https://y.qq.com/n/ryqq/songDetail/000Z9mNt109oQd 中的 000Z9mNt109oQd
    '''
    # qq_music_downloader = QQMusicDownloader()
    logger.info(f'start to parse the music ...')
    music = QQMusicDownloader.parse(song_id)
    logger.info(f'parsed music: {music}')
    logger.info(f'try to download music ...')
    QQMusicDownloader.download(music)


if __name__ == "__main__":
    fire.core.Display = lambda lines, out: print(*lines, file=out)
    fire.Fire(main)
