# music_downloader
Simple downloader for music from https://y.qq.com/, https://music.163.com/, https://www.kuwo.cn/ and so on.

### What's it

It's a simple python script which parses the music using `playwright` instead of normally `request` (so no need to inspect the devtools anymore!), then download, convert to mp3.

It's just for personal usage.

### How to run it

1. git clone https://github.com/liudonghua123/music_downloader.git
2. cd music_downloader
3. pip install -r requirements.txt 
4. change configurations in config.yml (optinal)
5. python main.py --help


### Todos

- [x] qq music support
- [ ] package executable support
- [ ] github action ci/cd support
- [ ] search music support
- [ ] 163 music support
- [ ] kuwo music support

### License

MIT License

Copyright (c) 2022 liudonghua