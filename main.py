from fastapi import FastAPI, HTTPException
import aiohttp
from dotenv import load_dotenv
import os, time
from aiocache import cached

load_dotenv()

app = FastAPI()
session = aiohttp.ClientSession()
TOKEN = os.environ['TOKEN']
BASE = 'https://discord.com/api'







@app.on_event("startup")
async def startup_event():
    # cache
    await staff()

@cached()
async def get(url):
    headers = {'content-type': 'application/json', 'Authorization': 'Bot ' + TOKEN}
    async with session.get(BASE+url,headers=headers) as resp:
        data = await resp.json()
        if not resp.status == 200:
            raise HTTPException(status_code=resp.status, detail=data['message'])

    return data

@cached()
async def get_all_members():
    members = await get('/guilds/681882711945641997/members?limit=1000')
    for _ in range(5):
        last = members[-1]['user']['id']
        new = await get(f'/guilds/681882711945641997/members?limit=1000&after={last}')
        members.extend(new)
    return members

def set_postion(member: dict):
    roles = {
        '681895373454835749': 'Owner',
        '725899526350831616': 'Administrator',
        '795136568805294097': 'Head Moderator',
        '729530191109554237': 'Senior Moderator',
        '681895900070543411': 'Moderator',
        '783909939311280129': 'Head Helper',
        '726650418444107869': 'Official Helper',
    }
    for role_id in roles:
        if role_id in member['roles']:
            member['position'] = roles[role_id]
            break
    return member

@app.get("/")
async def root():
    return await get('/guilds/681882711945641997')

@app.get("/staff")
async def staff():
    start = time.time()
    staff_role = '795145820210462771'
    members = await get_all_members()
        
    staff = [x for x in members if staff_role in x['roles']]
    staff = list(map(set_postion, staff))
    print('Elapsed time:', time.time()-start)
    return staff


@app.get("/allstaff")
async def allstaff():
    staff_role = '795145820210462771'
    helper = '726650418444107869'
    trainee = '729537643951554583'
    roles = [helper,staff_role, trainee]
    members = await get_all_members()
    staff = [x for x in members if any(r in x['roles'] for r in roles)]
    staff = list(map(set_postion, staff))
    return staff

@app.get("/user/{id}")
async def user(id:int):
    return await get(f'/users/{id}')

@app.on_event("shutdown")
async def shutdown_event():
    await session.close()
