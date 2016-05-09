# from os import getenv
import pymssql
import csv



csvfile = file('tags_text.csv', 'rb')
reader = csv.reader(csvfile)
d ={}
for line in reader:
    d[line[2]]=line[1]
# print d
csvfile.close()




conn = pymssql.connect("172.19.131.17", "sa", "System!102", "TJURFID")
cursor = conn.cursor()
for k in d:
    print k,d[k]
    cursor.execute("update T_CJXX set BQ = %s where CJBSF =%s",(d[k],k))
conn.commit()
conn.close()





# cursor.execute('SELECT * FROM T_CJXX')
# row = cursor.fetchone()
# while row:
# for row in cursor:
    # print('row = %s' % row['CJBSF'])
    # if row[0] in d :
        # cursor.execute("update T_cjxx set BQ = '%s' where CJBSF ='%s'", [d[row[0]],row[0]])
# cursor.execute("""
# IF OBJECT_ID('persons', 'U') IS NOT NULL
    # DROP TABLE persons
# CREATE TABLE persons (
    # id INT NOT NULL,
    # name VARCHAR(100),
    # salesrep VARCHAR(100),
    # PRIMARY KEY(id)
# )
# """)
# cursor.executemany(
    # "INSERT INTO persons VALUES (%d, %s, %s)",
    # [(1, 'John Smith', 'John Doe'),
     # (2, 'Jane Doe', 'Joe Dog'),
     # (3, 'Mike T.', 'Sarah H.')])
# # you must call commit() to persist your data if you don't set autocommit to True
# conn.commit()

# row = cursor.fetchone()
# while row:
    # print("ID=%s, Name=%s" % (row[0], row[1]))
    # row = cursor.fetchone()

