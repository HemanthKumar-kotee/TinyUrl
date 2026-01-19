from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from psycopg2 import OperationalError
from pydantic import BaseModel
import redis

from generateURL import generatetinyUrl as tinyUrl
from generateURL import connectDb
from urlDB import getUrls

class UrlRequest(BaseModel):

    '''Pydantic model to validate the incoming long_url data'''
    
    long_url: str

class CredentialRequest(BaseModel):

    '''Pydantic model to validate the incoming credentials data'''
    
    email: str
    password: int



app = FastAPI()
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post('/signup')
def signup(credentials: CredentialRequest):

    '''Function to signup user with email and password'''
    
    conn, cur = connectDb()
    
    email, password = credentials.email, credentials.password
    
    print(email, password)
    if (not email) or (not password):
        return False
    
    try:
    
        cur.execute('INSERT INTO users (email, password) VALUES (%s, %s)', (email, password))
        
        conn.commit()
        print('User Created Successfully')
        
        response  = {
            'isSignedUp': True 
        }
        
        return response

    except OperationalError as e:

        print('Unable to create user', e)
        return {'isSignedUp': False, 'error': str(e)}
        
    finally:
        conn.close()



@app.post('/login')
def login(credentials: CredentialRequest):

    ''''Function to login user with email and password'''
    conn, cur = connectDb()
    
    email, password = credentials.email, credentials.password

    if (not email) or (not password):
        return False
    
    try:
        cur.execute('SELECT * FROM users WHERE email=%s AND password=%s', (email, str(password)))
        res = cur.fetchone()

        if (res):
            if (res[1] != email) or (res[2] != str(password)):
                print('Invalid Credentials')
                response  = {
                    'isLoggedIn': False
                }
                return response
            
        response  = {
            'isLoggedIn': bool(res)
        }

        return response
    finally:
        conn.close()


@app.post('/submit-url')
def createTinyUrl(data: UrlRequest):
    
    """
    Path route used to submit long url and 
    
    returns NanoId for the long url
    """

    long_url = data.long_url
    
    try:
        '''Try to reduce database hit'''

        nanoId = redis_client.hget(name='UrlToTinyUrl',
                      key=long_url)
        
        if nanoId is not None:
            print('Redis cache Hit')
            return {'data': nanoId}

        else:
            print('Redis cache miss')
        
    except redis.DataError as e:
        print('Redis cache miss')

    nanoId = tinyUrl(long_url)
    
    if nanoId:
        response = {
            'data': nanoId,
        }
        redis_client.hsetex(name='UrlToTinyUrl',
                            key=long_url,
                            value=nanoId,
                            ex=1800)
        return response
    else:
        return {'error': 'Database error'}


@app.get('/get-urls')
def getData(defaultValue: int = Query(...)):
    
    """
    params: defaultValue: int, to fetch default number of rows from DB.

    Path route used to fetch data from DB and gives it to the React JS frontend
    """
    
    response = getUrls(defaultValue)

    if response:

        print('Urls fetched successfully')
        return {'urls': response}
    else:
        return {'error': 'Database error, Urls cannot be fetched'}


@app.get('/')
def root():
    return {"message": "Welcome to the URL Shortener API"}
    