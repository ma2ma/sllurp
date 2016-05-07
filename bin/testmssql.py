from os import getenv
import pymssql


conn = pymssql.connect("172.19.131.17", "sa", "System!102", "TJURFID")
cursor = conn.cursor(as_dict=True)
cursor.execute('SELECT * FROM T_CJXX where BQ is not null')
for row in cursor:
    print('row = %s' % row['CJBSF'])
conn.close()







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

