
import pymysql
import re
f = open("dict.txt")
db=pymysql.connect("localhost","root","123456")
cursor = db.cursor()
for line in f:
    l = re.split(r"\s+",line)
    word = l[0]
    interpret = " ".join(l[1:])
    try:
        cursor.execute("use dict;")
        cursor.execute("insert into words(word,interpret) values('%s','%s');" % (word,interpret))
        db.commit()
    except:
        db.rollback()
cursor.close()
f.close()