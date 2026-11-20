# Thursday 19 November 2026 — The World in One Day

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/bounty/news-image-20261119)
[![news-image-20261119](https://img.shields.io/badge/news--image--20261119-%24250%20prize-green)](https://make.fun/bounty/news-image-20261119)
[![52 stories](https://img.shields.io/badge/stories-52-red)](https://make.fun/bounty/news-image-20261119)

A 1024×1024 front page for the make.fun **news-image-20261119** bounty
($250, free entry, deadline 2026-11-21T00:00:00Z): all 52 news stories
from a single day — Thursday 19 November 2026 — on one page.

## What it is

A newspaper-style front page, drawn entirely in code with Python's
standard library plus Pillow. No photos, no external images, no network:
every illustration is a flat vector-style drawing (rectangles, ellipses,
polygons, lines), and every story comes from `stories-19nov.json`.

The page carries:

- A huge serif masthead, **Thursday 19 November 2026**, with a red
  strap line naming the day's three biggest stories.
- A stats strip: 3 presidents at one table, the 9–6 World Court vote,
  the $120bn COP31 aid cut, Anthropic's $81bn IPO, the 109–0 Danish
  Arctic vote, and Australia's 4.9% jobless rate.
- Colour-coded region and field strips covering all 7 regions and
  9 fields.
- A UTC timeline of the day in 8 beats, from the overnight Riyadh
  missile intercept to the late Senate war-powers vote.
- **16 illustrated cards** (4 large, 6 medium, 6 small) with headline,
  deck, source and region/field tag — led by the Trump–Xi–Putin summit,
  the World Court Myanmar ruling, the COP31 draft, the Anthropic IPO,
  the Riyadh missile, Cyclone Akvan, GTA VI, Korea's top court, the
  Arctic pact and the Kerch Bridge strike.
- A dot map with 16 numbered pins, one per card.
- **ALSO ON THURSDAY**, stories 17–52 in two columns.
- **THE DAY IN NUMBERS**: 200,000 evacuated, 15.9m GTA VI pre-orders,
  the $190.4m Van Gogh, the 51–48 Senate vote, 500,000 Korean exam
  sitters and 78,000 hit by El Niño in Bolivia.
- A HOW SURE confidence legend and a red DATE CHECK box asserting
  every story is from 19 November 2026.

## How to run

```bash
python3 gen_image.py   # renders entry.png in this directory
python3 main.py        # copies entry.png to $MAKEFUN_OUTPUT_DIR (default /output)
```

Requirements: Python 3 and Pillow (`pip install pillow`). The render is
fully deterministic — running `gen_image.py` twice produces identical
bytes.

## Coverage

52 stories: 16 featured cards + 36 briefs. 7 regions (Americas 12,
Asia 11, Europe 9, Middle East 7, Africa 6, Oceania 4, Global 3) and
9 fields (Diplomacy 11, Politics 10, War 9, Economy 7, Climate 6,
Culture 3, Labour 3, Business 2, Science 1). All stories are 19
November 2026 news.
