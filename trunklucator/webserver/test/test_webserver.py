import pytest
from trunklucator.webserver.server import WebServer
from aiohttp import web
import json
import asyncio
import aiohttp
from pprint import pprint
from unittest.mock import patch
import uuid

import trunklucator.const.msg as const_msg
import trunklucator.const.task_types as const_ttype
import trunklucator.protocol.dto as dto

WS_URL = '/trunklucator/v1.0'

PRINT_MSG = True

def prt_msg(str_:str):
    print("<-- {}".format(str_))
    return str_

def jd(msg : dto.Message):
    if PRINT_MSG:
        return prt_msg(json.dumps(msg.to_dict()))
    return json.dumps(msg.to_dict())

def fake_uuid():
    return patch.object(uuid, 'uuid4', side_effect=['15bfcc21-de44-47d9-9189-1f9f91453311'])

def get_id():
    with fake_uuid():
        return dto.get_id()

def create_task():
    X = [[1,2],[3,4],[5,6]]
    y = [0,1,0]
    label_name = ['Y', 'N']
    return dto.Data(get_id(), X, None)

def create_solution():
    y = [0,1,1]
    return dto.Solution(get_id(), y)

def parse_msg(data) -> dto.Message:
    try:
        data_ = json.loads(data)
        return dto.Message(**data_)
    except TypeError as e:
        raise e
    except Exception as e:
        raise e


async def read_msg(ws, proto_msg_type: str, ws_msg_type: int = web.WSMsgType.text):
    ws_msg = await ws.receive()
    if PRINT_MSG:
        print("\n--> {}".format(ws_msg))
    assert ws_msg.type == ws_msg_type
    msg = parse_msg(ws_msg.data)
    assert msg.type == proto_msg_type
    return msg

async def test_push_task(aiohttp_client, loop):
    ws = WebServer(loop=loop)
    task1 = create_task()
    #await ws.add_task(task1)
    ws.app["task"] = task1
    app = ws.app
    client = await aiohttp_client(app)
    async with client.ws_connect(WS_URL) as ws:
        solution_id = dto.get_id()
        #wait for task meassage
        msg1 = await read_msg(ws, const_msg.TYPE_TASK)
        task2 = dto.Data(**msg1.payload)
        assert task1.task_id == task2.task_id
        assert len(task1.x) == len(task2.x)
        #wait for update meassage
        msg2 = await read_msg(ws, const_msg.TYPE_UPDATE)
        #send solution
        await ws.send_str(jd(dto.Message(const_msg.TYPE_SOLUTION, create_solution(), msg_id=solution_id)))
        #wait for ask
        msg3 = await read_msg(ws, const_msg.TYPE_ACK)
        assert msg3.reply_id == solution_id
        await ws.close() #?
