from psycopg2 import OperationalError
from dotenv import load_dotenv
import fastnanoid
import psycopg2
import os

load_dotenv()


conn_auth = {
    "database": os.getenv("DB"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_KEY"),
    "host": 'localhost'
}


def generatetinyUrl(long_url):

    """
    Function to create a UUID for Url and Maps into Database
    """
    conn, cur = connectDb()

    if (isUrlExists(long_url)):

        nanoId = cur.execute(""""SELECT nanoId FROM tinyurl WHERE longurl = %s""", (long_url,))
        return nanoId
    
    nanoId = fastnanoid.generate(size=6)

    if (isNanoIdExists(nanoId)):
        
        generatetinyUrl(long_url)
    else:
        
        cur.execute("""INSERT INTO tinyUrl (nanoId, longUrl) VALUES (%s, %s)""", (nanoId, long_url))
        conn.commit()
        print(f'Tiny Url created Successfully, {long_url}: {nanoId}')
    
    conn.close()
    return nanoId
        

def isNanoIdExists(nanoId):
    
    '''
    Function used to check whether Unique NanoIds already exists or not, 
    
    used to get avoid collision
    '''

    conn, cur = connectDb()
    
    cur.execute("""SELECT * FROM tinyUrl WHERE nanoId=%s""", (nanoId,))
    
    isnanoIdExists = cur.fetchall()
    
    if isnanoIdExists:
        conn.close()
        return True
    
    conn.close()
    return False


def isUrlExists(long_url):
    
    '''Çhecks whether long url already exists in the database'''

    try:
        conn, cur = connectDb()
        cur.execute("""SELECT * FROM tinyUrl WHERE longurl=%s""", (long_url,))
        
        isUrlExists = cur.fetchone()
        
        if (isUrlExists):
            return True
        
        return False
        
    except OperationalError as e:

        raise e

    finally: 
        conn.close()


def connectDb():

    '''
    Function connectDB used to connect to the PostGreSQL application

    and can able to access the TinyUrls database...
    '''
    
    try:
        conn = psycopg2.connect(**conn_auth)
    
        cur = conn.cursor()
        return conn, cur
        
    except OperationalError as e:
    
        print(f'Error occured in Database connection {e}')


def main():

    long_url = input('Enter url: ')
    
    tiny_url = generatetinyUrl(long_url)
    print(tiny_url)


if __name__ == '__main__':
    main()