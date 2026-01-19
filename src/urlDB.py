from generateURL import connectDb
from psycopg2 import OperationalError

def getUrls(defaultValue):
    
    '''
    Function used to get records from Database table
    
    specifically from tinyUrls table
    '''
    
    try:
        conn, cur = connectDb()
    
        cur.execute('SELECT COUNT(*) FROM tinyUrl')
        totalRecords = cur.fetchone()[0]

        if (totalRecords < defaultValue):
    
            cur.execute('SELECT nanoid, longurl FROM tinyUrl')

        else:
            cur.execute('SELECT nanoid, longurl FROM tinyUrl ORDER BY RANDOM() LIMIT %s', (defaultValue,))
    
        res = cur.fetchall()
    
        return res

    except OperationalError as e:
        raise e
    
    finally:
        conn.close()


def main():
    print(getUrls(10))


if __name__ == '__main__':
   
    main()