# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/aufaakmalbunaya/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/aufaakmalbunaya/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Tuesday 24 November 2026 world news in one image: a dense newspaper front page drawn by a single Python file — masthead, a 7-number markets strip, the lead story of Jensen Huang returning as Nvidia chief as Wall Street roars back, world / sport / tech and markets columns, a sketch world map with eight pins, a day-in-numbers panel, and a culture row. 45 stories, all verified from Tuesday's news.

## How it is built

`main.py` uses only the Python standard library. It draws the whole page on its own pixel canvas with its own 5x7 letter alphabet, and writes the PNG with its own encoder (zlib + struct). No network, no clock, no randomness: two runs write byte-identical files.

## Run it

```sh
python3 main.py
```

The image is written to `$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output/entry.png`).

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
