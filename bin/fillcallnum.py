# from os import getenv
import pymssql
import csv



csvfile = file('byybook.csv', 'rb')
reader = csv.reader(csvfile)
d ={}
for line  in reader:
    if line[5] not in d:
        d[line[5]]=line[2].strip('[').strip(']')
# print d
csvfile.close()




conn = pymssql.connect("172.19.131.17", "sa", "System!102", "TJURFID")
cursor = conn.cursor()
for k in d:
    # print k,d[k]
    cursor.execute("update T_CJXX set GCBSF = %s where FIRSTCALLNUM =%s",(d[k],k))
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

