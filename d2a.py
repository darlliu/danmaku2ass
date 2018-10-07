import os
import sys
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import sqlite3
from difflib import SequenceMatcher as SM
from dataclasses import dataclass
import argparse

@dataclass
class danmaku:
    index: int
    date: str
    uid: str
    pos: int #this is the relative timestamp
    tag: str
    content: str

class dmdb(object):
    """
    simple sqlite db to store the danmaku
    one table per file, completely flat   
    """
    def __init__(self, dbpath="./db.sqlite"):
        self.dbpath = dbpath
        self.conn = sqlite3.connect(dbpath)
        self.conn.row_factory = sqlite3.Row
        self.curr = self.conn.cursor()
        return
    def __enter__(self):
        # self.curr.execute("""
        # DROP TABLE meta;
        # """)
        self.curr.execute("""
        CREATE TABLE IF NOT EXISTS meta
        (fname text unique primary key, name text, ext text, series text, episode integer, source text, keywords text);
        """)
        self.conn.commit()
        print ("Initialized db at {}".format(self.dbpath))
        return self

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

    def add(self, fpath, res):
        basename = os.path.basename(os.path.abspath(fpath))
        name, ext = os.path.splitext(basename)
        self.curr.execute("""
        insert or replace into meta (fname, name, ext, series, episode, source, keywords) values
        ("{basename}","{name}", "{ext}", "{series}", {episode}, "{source}", "{keywords}");
        """.format(
            basename = basename,
            name = name,
            ext = ext,
            series = "unknown",
            episode = -1,
            source = "ひまわり",
            keywords = ""
        ))
        # self.curr.execute("select count (*) from meta")
        # row = self.curr.fetchone()
        # print ("inserted meta info, which currently has {} rows".format(row[0]))
        self.curr.execute("DROP TABLE IF EXISTS \"{}\"".format(basename))
        self.curr.execute("""
        CREATE TABLE "{}"
        (originalIdx integer, originalDate text, userId text, originalPos integer, originalTag text, content text) ; 
        """.format(basename))
        for idx, date, uid, vpos, tag, text in res:
            self.curr.execute("""
            insert into "{basename}" values (
                {idx}, "{date}", "{uid}", {vpos}, "{tag}", "{text}"
            )
            """.format(
                basename=basename,
                text = str(text).replace("None","").replace("\"","").replace("\'",''),
                tag = tag,
                idx = idx,
                date= date,
                uid = uid,
                vpos = vpos
            ))
        self.conn.commit()
        # self.curr.execute("select count(*) from \"{}\"".format(basename))
        # for row in self.curr.fetchone():
        #     print ("Inserted a table {} with {} rows".format(basename, row))
        return
    
    def __getitem__(self, key):
        self.curr.execute("select * from meta;")
        fnames = [r for r in self.curr.fetchall()]
        scores = [SM(None, key, r[1]).ratio() for r in fnames]
        idx = scores.index(max(scores))
        print ("Keyword based search -- keyword: {}, selected {}".format(key, fnames[idx][1]))
        self.curr.execute("select * from \"{}\"".format(fnames[idx][0]))
        return fnames[idx][1], self.curr

    def __iter__(self):
        self.curr.execute("select * from meta;")
        for row in self.curr.fetchall():
            self.curr.execute("select * from \"{}\"".format(row[0]))
            yield row[1], self.curr

class renderer(object):
    HEADER = u"""\ufeff
[Script Info]
Title:NicoScript
Original Script: NicoNico or else
ScriptType: v4.00
Collisions: Normal
PlayResX: {resX}
PlayResY: {resY}
PlayDepth: 32
Timer: 100.0000
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColor, BackColour, Bold, \
Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, \
Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Meiryo Bold,80,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,1,0.00,1,1,0,10,30,30,30,1
Style: Static,Meiryo Bold,80,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,2,0.00,1,1,0,2,0,0,0,1
Style: Scroll,Meiryo Bold,80,11861244,11861244,0,-2147483640,-1,0,0,0,100,100,2,0.00,1,1,0,2,0,0,0,1
[Events]
Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
    """
    EVENT = u"""
Dialogue: Marked=0,{tstart},{tend},Scroll,NicoChu,0000,0000,0000,,{{\\a6\\move(1150,{startpos},0,{endpos})\c&HFFFFFF\\fs25}}{content}
    """
    resX = 640
    resY = 360
    delay = 400
    stepSize = 20
    def __init__(self,x=640,y=360, delay=500, stepSize=20):
        self.resX = x
        self.resY = y
        self.delay = delay
        self.stepSize =stepSize
    def convert(self,timepos):
        TIMESTR = u"{hour:02d}:{minute:02d}:{second:02.2f}"
        timepos /= 100.0
        hh = int(timepos / 3600)
        mm = int((timepos - hh*3600)/60)
        ss = round((timepos - hh*3600 - mm*60), 2)
        return TIMESTR.format(hour = hh,
                              minute=mm, second=ss)
    def __call__(self, res):
        ss = self.HEADER.format(resX = self.resX, resY = self.resY)
        rows = [danmaku(*row) for row in res]
        pos = 1
        if not rows: return ss
        told = rows[0].pos - self.delay
        for d in sorted(rows, key = lambda x: x.pos):
            if told+self.delay < d.pos or pos >= self.resY:
                pos = 1
                told += self.delay
            ss += self.EVENT.format(
                tstart = self.convert(d.pos),
                tend = self.convert(d.pos + self.delay),
                startpos = pos,
                endpos = pos,
                content = d.content
            )
            pos += self.stepSize
        return ss
        

def scan(dirpath="./"):
    for fpath in os.listdir(dirpath):
        if os.path.splitext(fpath)[1] == ".xml":
            yield os.path.join(dirpath, fpath)

def parseXmlHimawari(fname):
    """
    himawari xmls sometimes are misformatted
    """
    parser = ET.XMLParser(encoding ="utf-8")
    s = open(fname, encoding = "utf-8").read().replace("\x08","")
    try:
        root = ET.fromstring(s, parser=parser)
    except ET.ParseError as e:
        e.what = s[e.position[-1]]
        print ("Got error: around location {} with string ({})".format(e.position, e.what), file=sys.stderr)
        raise e
    for child in root:
        yield child.attrib["no"], child.attrib["date"], child.attrib["user_id"],\
        int(child.attrib["vpos"]), child.tag, child.text

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Convert himado danmaku xml to .ass for local play!")
    parser.add_argument("--db", default =None , help="Path of the sqlite db, leave default to use ./db.sqlite")
    parser.add_argument("--out", default = "./" , help="Directory to output the .ass file/s")
    parser.add_argument("--input", default ="./" , help="Directory to scan for .xml files")
    parser.add_argument("--keyword", default ="ep1" , help="A keyword to search an entry for, will always return one file.")
    parser.add_argument("--mode", default ="all" , help="""Mode of action: 
    all  -- scan for xml, store and convert.
    scan -- scan for xml, store.
    list -- list all entries in the db.
    output -- provide a keyword for an entry, output that """)
    args = parser.parse_args()
    if args.mode not in ["all","scan","list","output"]:
        raise ValueError("--most must be one of all, scan, list, or output")
    if args.db is not None:
        dbp = args.db
    else:
        dbp = "./db.sqlite"

    with dmdb(dbp) as db:
        if args.mode == "list":
            for idx, (fname, _) in enumerate(db):
                print ("Entry {} : {}".format(idx+1, fname))
            sys.exit(0)
        r = renderer()
        if args.mode == "output":
            fname, res = db[args.keyword]
            open(os.path.join(args.out, fname+".ass"),"wb").write(r(res).encode())
            sys.exit(0)
        for fname in scan(args.input):
            try:
                db.add(fname, parseXmlHimawari(fname))
                print ("Added {}".format(fname))
            except ET.ParseError as e:
                continue
        if args.mode == "scan":
            sys.exit(0)
        if args.mode == "all":
            for fname, res in db:
                open(os.path.join(args.out, fname+".ass"),"wb").write(r(res).encode())
            sys.exit(0)

