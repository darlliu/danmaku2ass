### Danmaku2Ass  Convert danmaku to .ass files

A brief visit to an old exercise. Now rewritten with some more modern python.

```bash
PS C:\Users\darlliu\Desktop\danmaku2ass> python .\d2a.py --help
usage: d2a.py [-h] [--db DB] [--out OUT] [--input INPUT] [--keyword KEYWORD]              [--mode MODE]

Convert himado danmaku xml to .ass for local play!

optional arguments:
  -h, --help         show this help message and exit
  --db DB            Path of the sqlite db, leave default to use ./db.sqlite
  --out OUT          Directory to output the .ass file/s
  --input INPUT      Directory to scan for .xml files
  --keyword KEYWORD  A keyword to search an entry for, will always return one
                     file.
  --mode MODE        Mode of action: all -- scan for xml, store and convert.
                     scan -- scan for xml, store. list -- list all entries in
                     the db. output -- provide a keyword for an entry, output
                     that

# After some imports

PS C:\Users\darlliu\Desktop\danmaku2ass> python .\d2a.py --mode list
Initialized db at ./db.sqlite
Entry 1 : Persona4 the Golden 第8話 「Not So Holy Christmas Eve」
Entry 2 : PSYCHO-PASS2 第4話 蒸気さん200追加「ヨブの救済」
...
# 
PS C:\Users\darlliu\Desktop\danmaku2ass> python .\d2a.py --mode output --keyword　少女05
Initialized db at ./db.sqlite
Keyword based search -- keyword: 少女05, selected 少女☆歌劇　レヴュースタァライト #05 『キラめきのありか』
```

```conf
[Script Info]
Title:NicoScript
Original Script: NicoNico or else
ScriptType: v4.00
Collisions: Normal
PlayResX: 640
PlayResY: 360
PlayDepth: 32
Timer: 100.0000
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColor, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Meiryo Bold,80,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,1,0.00,1,1,0,10,30,30,30,1
Style: Static,Meiryo Bold,80,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,2,0.00,1,1,0,2,0,0,0,1
Style: Scroll,Meiryo Bold,80,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,2,0.00,1,1,0,2,0,0,0,1
[Events]
Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
    
Dialogue: Marked=0,00:00:1.29,00:00:6.29,Scroll,NicoChu,0000,0000,0000,,{\a6\move(1150,1,0,1)\c&HFFFFFF\fs25}うぽつなのだー
    
Dialogue: Marked=0,00:00:2.59,00:00:7.59,Scroll,NicoChu,0000,0000,0000,,{\a6\move(1150,21,0,21)\c&HFFFFFF\fs25}This+is
```

result :

![demo](./demo.JPG)
