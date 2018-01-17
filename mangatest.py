import sqlite3
import feedparser
import pprint
import re
import time

ms_feed_URL = 'https://readms.net/rss'
jb_feed_URL = 'https://jaiminisbox.com/reader/feeds/rss'
jb_parse = feedparser.parse(jb_feed_URL)
ms_parse = feedparser.parse(ms_feed_URL)

the_db = sqlite3.connect('mangatest.db')


# create mangastream table
the_db.execute("""CREATE TABLE IF NOT EXISTS \
             ms_table (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                         title TEXT UNIQUE, \
                         latest_chap INTEGER, \
                         chap_URL TEXT, \
                         chap_desc TEXT\
                         )""")

# create jaiminibox table
the_db.execute("""CREATE TABLE IF NOT EXISTS \
             jb_table (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                         title TEXT UNIQUE, \
                         latest_chap INTEGER, \
                         chap_URL TEXT, \
                         chap_desc TEXT\
                         )""")


##TODO: create table for manga thumbnails and description

# create user table
the_db.execute("""CREATE TABLE IF NOT EXISTS \
             user_table (id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, \
                         discord_id TEXT UNIQUE, \
                         notify INTEGER \
                         )""")

#create user_manga link table
the_db.execute("""CREATE TABLE IF NOT EXISTS \
             user_manga_link (discord_id TEXT, \
                              manga_title TEXT  \
                              )""")

#create and initialise key value store
the_db.execute("""CREATE TABLE IF NOT EXISTS \
             kvs (property TEXT UNIQUE, \
                              value TEXT  \
                              )""")
the_db.execute("INSERT OR IGNORE INTO kvs VALUES ('ms_updated', '0')")
the_db.execute("INSERT OR IGNORE INTO kvs VALUES ('jb_updated', '0')")
the_db.commit()


dbc = the_db.cursor() # database cursor

# add a manga to table
def addMangaMS(table):
    dbc.execute("INSERT OR IGNORE INTO ms_table VALUES (null, ?, 0, null, null)", (table,))
    the_db.commit()
    
## i know this is retarded but it won't work otherwise
def addMangaJB(table):
    dbc.execute("INSERT OR IGNORE INTO jb_table VALUES (null, ?, 0, null, null)", (table,))
    the_db.commit()

### add a discord user to user_table
##def addUser(discord_id):
##    dbc.execute("INSERT OR IGNORE INTO user_table VALUES (null, ?, 0)", (discord_id,))
##    the_db.commit()

# return all manga_title user is subbed to
def checkSubs(discord_id):
    aa = dbc.execute("SELECT manga_title FROM user_manga_link WHERE discord_id==?", (discord_id,)).fetchall()
    bb=[]
    for i in aa:
        bb.append(i[0])
    return bb

# return all discord_id subbed to the manga
def checkSubbers(title):
    aa = dbc.execute("SELECT discord_id FROM user_manga_link WHERE manga_title==?", (title,)).fetchall()
    bb=[]
    for i in aa:
        bb.append(i[0])
    return bb


# create a relationship
def createSub(discord_id, manga_title):
    if manga_title not in checkSubs(str(discord_id)):
        the_db.execute("INSERT INTO user_manga_link VALUES (?, ?)", (discord_id, manga_title))
        the_db.commit()

# deletes a relationship
def delSub(discord_id, manga_title):
    if manga_title in checkSubs(str(discord_id)):
        the_db.execute("DELETE FROM user_manga_link WHERE discord_id=? AND manga_title=?", (discord_id, manga_title))
        the_db.commit()

# updates the manga table with mangastream rss
# TODO create generic RSS updater
#needs to somehow return all mangas updated
def updateMS(ms_parse):  #### parse object dict: ms_parse = feedparser.parse(ms_feed_URL)
    update_list = [] #list of updated mangas in this update
    ms_reg = re.compile(r'(.+?) (\d*$)')  #MS regex to search for chapter and name in title
                                          #group(1) = title, group(2) = chapter number

    #add non-existent entries to manga_table
    for i in ms_parse.entries:            ##loops through i, which is each rss feed entry
        
        mo = ms_reg.search(i.title)   ##mo.group(1) = manga title, mo.group(2) = manga chapter
        tt = dbc.execute("SELECT * FROM ms_table WHERE title=?", (mo.group(1),)).fetchone()
        ## tt will be a tuple of (manga.id, manga.title , latest chapter number, chapter URL, chap desc) from the DB
        if not tt:
            addMangaMS(mo.group(1))
            tt = dbc.execute("SELECT * FROM ms_table WHERE title=?", (mo.group(1),)).fetchone()
        if int(mo.group(2)) > tt[2]:
            dbc.execute("UPDATE ms_table SET latest_chap=? WHERE id=?", (mo.group(2), tt[0]))
            dbc.execute("UPDATE ms_table SET chap_URL=? WHERE id=?", (i.link, tt[0]))
            dbc.execute("UPDATE ms_table SET chap_desc=? WHERE id=?", (i.summary, tt[0]))
            update_list.append(mo.group(1))
    the_db.execute("UPDATE kvs SET value=? WHERE property=?", (str(time.time()),'ms_updated'))
    the_db.commit()

    return update_list

    
# updates the manga_table with jaimini box rss
def updateJB(jb_parse):  #### parse object dict: jb_parse = feedparser.parse(jb_feed_URL)
    update_list = [] #list of updated mangas in this update
##    jb_chapreg = re.compile(r'(\d*): (.*$)')  #JB regex to search for chapter number in title group(1), group(2) for desc
##    jb_titlereg = re.compile(r'.+?(?=( Chapter| Page)?( )?(\.|\d)*:)') #JB regex to search for manga name in title group()
    jb_reg = re.compile(r'(?P<title>.*?)\s?(Chapter|Page|Question|Anno Radix)?\s?([^\d\s]*(?P<chapter_num>\d+)\:)\s?(?P<chapter_name>.*)')  ##credit to HY

    #add non-existent entries to manga_table
    for i in jb_parse.entries:            ##loops through i, which is each rss feed entry
        
        mo = jb_reg.search(i.title)   ##mo.group('title'), mo.group('chapter_num'), mo.group('chapter_name')

        
        tt = dbc.execute("SELECT * FROM jb_table WHERE title=?", (mo.group('title'),)).fetchone()
        ## tt will be a tuple of (manga.id, manga.title , latest chapter number, chapter URL, chap desc) from the DB
        if not tt:
            addMangaJB(mo.group('title'))
            tt = dbc.execute("SELECT * FROM jb_table WHERE title=?", (mo.group('title'),)).fetchone()
        if int(mo.group('chapter_num')) > tt[2]:
            dbc.execute("UPDATE jb_table SET latest_chap=? WHERE id=?", (mo.group('chapter_num'), tt[0]))
            dbc.execute("UPDATE jb_table SET chap_URL=? WHERE id=?", (i.link, tt[0]))
            dbc.execute("UPDATE jb_table SET chap_desc=? WHERE id=?", (mo.group('chapter_name'), tt[0]))
            update_list.append(mo.group('title'))
            
    the_db.execute("UPDATE kvs SET value=? WHERE property=?", (str(time.time()),'jb_updated'))
    the_db.commit()

    return update_list

#todo
##      let's make it return: [{ms_title, ms_chap, ms_link, ms_desc},{jb_title, jb_chap, jb_link, jb_desc}]
def checkManga(title):

    ms_tuple = dbc.execute("SELECT * FROM ms_table WHERE title=?", (title,)).fetchone()
    if ms_tuple:
        ms_dict = {'title':ms_tuple[1], 'latest_chap':ms_tuple[2], 'chap_URL':ms_tuple[3], 'chap_desc':ms_tuple[4]}
    else:
        ms_dict = {}
    
    jb_tuple = dbc.execute("SELECT * FROM jb_table WHERE title=?", (title,)).fetchone()
    if jb_tuple:
        jb_dict = {'title':jb_tuple[1], 'latest_chap':jb_tuple[2], 'chap_URL':jb_tuple[3], 'chap_desc':jb_tuple[4]}
    else:
        jb_dict = {}

    if ms_dict == {} and jb_dict == {}:
        return []
    else:
        return [ms_dict, jb_dict]


#returns [ms_parse, jb_parse] the parsed dicts
def arigatou_mr_parsebotto():
    jb_parse = feedparser.parse(jb_feed_URL)
    ms_parse = feedparser.parse(ms_feed_URL)

#when this function is called, bot will reparse, and tell bot to update
def updatedMangaList():
    arigatou_mr_parsebotto()
    list_update = updateMS(ms_parse) + updateJB(jb_parse)
    return list_update


##debuggingggg

##createSub('1','1')
##createSub('1','2')
##createSub('2','1')
##createSub('2','3')
##createSub('2','5')
##createSub('3','5')
##addManga('One Piece')
##addManga('Tokyo Ghoul')
##addManga('Bleach')
##addManga('One Punch Man')
##addUser('sjmc')
##addUser('hy')
##addUser('k-dawg')

updateJB(jb_parse)
dd = dbc.execute("SELECT * FROM jb_table").fetchall()
updateMS(ms_parse)
cc = dbc.execute("SELECT * FROM ms_table").fetchall()





## the_db.close()
