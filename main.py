from fastapi import FastAPI, WebSocket, APIRouter, WebSocketDisconnect  # type: ignore

app = FastAPI()

clients = set()
msghistory = list([])
currMember = {}
@app.get('/implapi/membernum')
def read_root():
    return { 'clientsnum': len(clients) }


# router = APIRouter(prefix="/implapi")
# @router.websocket('/ws')
@app.websocket('/implapi/ws')
async def websocket_savews(websocket: WebSocket):
    print('前端连接了捏=================>')
    await websocket.accept()
    clients.add(websocket)
    # 到这里位置是前端new WebSocket，然后开始给所有在线的人发当前人数
    # 但是前端进来就会执行send，所以会走到while True，然后当join的时候就触发返回


    await cast_num()
    try:
        while True:
            data = await websocket.receive_json()
            print(f'进来力看看data=========>{ data }')
            print(f"看看type=========>{ data.get('msgtype') }")
            # 进来的时候给自己返回历史信息
            if data.get('msgtype') == 'join':
                print(f'join进来=============>')
                # currMember.append(data)
                currMember[websocket] = data
                # for client in clients:
                    # 自己也要接收的
                    # if client == websocket:
                        # await client.send_text(data)
                await websocket.send_json({ 'msghistory': msghistory, 'msgtype': 'history' })
                await cast_user()
                # print(f"看看currMember=========>{ currMember }")
            
            # elif data.get('msgtype) == 'exit:
            #     print(f'exit进来=============>')
            #     for item in currMember[:]:
            #         if item['id'] == data.get("id"):
            #             currMember.remove(item)
            #     # currMember = templist
            #     print(f'删完了捏=============>{ currMember }')
            #     clients.remove(websocket)

            #     await cast_user()
            #     if len(clients) == 0:
            #         print(f'没有人了捏=============>')
            #         # msghistory = []

            # 发送消息的时候给所有人返回历史信息
            elif data.get('msgtype') == 'msg':
                print(f'msg进来=============>')
                msghistory.append(data)
                print(f'看看msghistory=========>{ msghistory }')
                for client in clients:
                    # 自己也要接收的
                    await client.send_json({ 'msghistory': msghistory, 'msgtype': 'history' })

    except WebSocketDisconnect as e:
        print(f'客户断开链接======>{e}')
        print(f'exit进来=============>')
        currMember.pop(websocket, None)
        # currMember = templist
        print(f'删完了捏=============>{ currMember }')
        clients.remove(websocket)

        await cast_user()
        await cast_num()
        if len(clients) == 0:
            print(f'没有人了捏=============>')
            msghistory.clear()
    finally:
        if websocket in clients:
            clients.remove(websocket)
            currMember.pop(websocket, None)
            await cast_user()
            await cast_num()
        # currMember.remove
        # for client in clients:
        #     # 离开时人数去除
        #     await client.send_json({ "clientsnum": len(clients), "msgtype": "num" })

async def cast_user():
    user_list = list(currMember.values())
    for client in clients:
        await client.send_json({ 'userlist': user_list, 'msgtype': 'users' })

async def cast_num():
    for client in clients:
        # 进来时返回人数
        await client.send_json({ 'clientsnum': len(clients), 'msgtype': 'num' })