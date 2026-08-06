"""websocket_client.py - Image2Forms client"""
import base64,json,mimetypes,os,requests,websockets,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from Config.config import LOCAL_AUTH_URL,DEV_AUTH_URL,LOCAL_IMAGE_WS_URL,DEV_IMAGE_WS_URL,LOCAL_HTML_WS_URL,DEV_HTML_WS_URL,REFRESH_TOKEN_LOCAL,REFRESH_TOKEN_DEV

def get_access_token(environment):
    url=LOCAL_AUTH_URL if environment.lower()=="local" else DEV_AUTH_URL
    if environment.lower() == "local":
        payload={"refresh_token":REFRESH_TOKEN_LOCAL,"token_type":"Bearer","expires_in":300}
    else:
        payload={"refresh_token":REFRESH_TOKEN_DEV,"token_type":"Bearer","expires_in":300}
        
    r=requests.post(url,json=payload);r.raise_for_status();return r.json()["access_token"]

async def connect(url): return await websockets.connect(url)
async def disconnect(ws):
    if ws: await ws.close()
async def send(ws,payload): await ws.send(json.dumps(payload))

async def receive(ws):
    while True:
        m=json.loads(await ws.recv())
        if m.get("stage")=="ping":
            await ws.send(json.dumps({"stage":"pong"}));continue
        return m

def _image_payload(path):
    with open(path,"rb") as f:b64=base64.b64encode(f.read()).decode()
    return {"filename":os.path.basename(path),"content_type":mimetypes.guess_type(path)[0] or "application/octet-stream","data":b64}

async def upload_image(image_path,environment):
    token=get_access_token(environment)
    base=LOCAL_IMAGE_WS_URL if environment.lower()=="local" else DEV_IMAGE_WS_URL
    ws=await connect(f"{base}?token={token}")
    try:
        await send(ws,_image_payload(image_path))
        while True:
            msg=await receive(ws)
            if msg.get("stage")=="error": return {"status":"error","message":msg}
            if msg.get("stage")=="done": return {"status":"success","result":msg.get("result")}
    finally:
        await disconnect(ws)

async def upload_html_css(html_path,css_path,environment):
    token=get_access_token(environment)
    base=LOCAL_HTML_WS_URL if environment.lower()=="local" else DEV_HTML_WS_URL
    with open(html_path,"r",encoding="utf-8") as f: html=f.read()
    css=""
    if css_path:
        with open(css_path,"r",encoding="utf-8") as f: css=f.read()
    ws=await connect(f"{base}?token={token}")
    try:
        await send(ws,{"html":html,"css":css})
        while True:
            msg=await receive(ws)
            if msg.get("stage")=="error": return {"status":"error","message":msg}
            if msg.get("stage")=="done": return {"status":"success","result":msg.get("result")}
    finally:
        await disconnect(ws)