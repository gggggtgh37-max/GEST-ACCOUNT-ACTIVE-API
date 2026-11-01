"""
FF GUEST ACTIVATOR — Vercel Serverless API
"""
import asyncio
import json
import uuid
import time
import base64
import ssl
from datetime import datetime
from typing import Optional

import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mangum import Mangum

AES_KEY   = b'Yg&tc%DEuh6%Zc^8'
AES_IV    = b'6oyZDr22E3ychjM%'
LOGIN_URL = "https://loginbp.ppmainecoonghj.com"
VERSION_URL = "https://version.ggwhitehawk.com/live/ver.php"

app = FastAPI(title="FF Guest Activator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ActivateRequest(BaseModel):
    uid: str
    password: str


# ==================== PROTO HELPERS ====================
def encode_varint(n):
    if n < 0: return b''
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)


def build_proto_str(fields):
    parts = []
    for k, v in fields.items():
        k = int(k)
        if isinstance(v, dict):
            nested = build_proto_str(v)
            parts.append(encode_varint((k << 3) | 2) + encode_varint(len(nested)) + nested)
        elif isinstance(v, int):
            parts.append(encode_varint((k << 3) | 0) + encode_varint(v))
        elif isinstance(v, (str, bytes)):
            ev = v.encode() if isinstance(v, str) else v
            parts.append(encode_varint((k << 3) | 2) + encode_varint(len(ev)) + ev)
    return b''.join(parts)


def decode_varint(data, pos):
    result = 0; shift = 0
    while True:
        b = data[pos]
        result |= (b & 0x7F) << shift
        pos += 1
        if not (b & 0x80): break
        shift += 7
    return result, pos


def parse_proto_manual(data):
    fields = {}; pos = 0
    while pos < len(data):
        try: tag, pos = decode_varint(data, pos)
        except: break
        fn = tag >> 3; wt = tag & 7
        if wt == 0:
            v, pos = decode_varint(data, pos); fields[fn] = v
        elif wt == 2:
            ln, pos = decode_varint(data, pos)
            raw = data[pos:pos + ln]; pos += ln
            try:
                s = raw.decode('utf-8')
                fields[fn] = s if (s.isprintable() and len(s) > 0) else raw
            except: fields[fn] = raw
        elif wt == 5: pos += 4
        elif wt == 1: pos += 8
        else: break
    return fields


def decode_jwt_payload(jwt_token):
    try:
        parts = jwt_token.split(".")
        b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(b64))
    except: return {}


async def encrypted_proto(encoded_bytes):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(encoded_bytes, AES.block_size))


async def enc_packet(data_hex, key, iv):
    try:
        data = bytes.fromhex(data_hex)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.encrypt(pad(data, AES.block_size)).hex()
    except: return data_hex


# ==================== OAUTH ====================
async def generate_access(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"
    }
    data = {
        "uid": uid, "password": password,
        "response_type": "token", "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    for _ in range(3):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        d = await response.json()
                        oid = d.get("open_id"); tok = d.get("access_token")
                        if oid and tok: return oid, tok
                    elif response.status == 429:
                        await asyncio.sleep(10); continue
        except: pass
        await asyncio.sleep(2)
    return None, None


# ==================== VERSION ====================
async def get_version_config():
    try:
        url = (f"{VERSION_URL}?version=1.132.8&lang=hi&device=android&channel=android"
               "&appstore=googleplay&region=ID&whitelist_version=1.3.0&whitelist_sp_version=1.0.0")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 200:
                    data = await r.json(content_type=None)
                    return (data.get("latest_release_version", "OB55"),
                            data.get("remote_version", "1.132.11"))
    except: pass
    return "OB55", "1.132.11"


# ==================== MAJOR LOGIN ====================
async def encrypt_major_login(open_id, access_token, client_version):
    payload_dict = {
        3: str(datetime.now())[:-7], 4: "free fire", 5: "1",
        7: str(client_version), 8: "Android OS 15 / API-35",
        9: "Handheld", 10: "Airtel", 11: "CarrierDataNetwork",
        12: "1639", 13: "720", 14: "320",
        15: "ARM64 FP ASIMD AES | 2000 | 8", 16: "5653",
        17: "Mali-G52 MC2",
        18: "OpenGL ES 3.2 v1.r49p1-03bet0.19498e0ae1d5dac223383c39a2e58f04",
        19: f"Google|{uuid.uuid4()}", 20: "182.5.135.225",
        21: "en", 22: str(open_id), 23: "4", 24: "Handheld",
        25: "Xiaomi 2409BRN2CY", 26: "IND",
        29: str(access_token), 30: "1", 41: "Airtel", 42: "4G",
        57: "7428b253defc164018c604a1ebbfebdf",
        60: "109278", 61: "55402", 62: "868",
        64: "55927", 65: "109278", 66: "55927", 67: "109278", 73: "2",
        74: "/data/app/~~6Cw028g_ld-8Z0z2qhrOLA==/com.dts.freefireth-i3wiaEmpx8CbiRVhUMx_ag==/lib/arm64",
        76: "1",
        77: "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~6Cw028g_ld-8Z0z2qhrOLA==/com.dts.freefireth-i3wiaEmpx8CbiRVhUMx_ag==/base.apk",
        78: "3", 79: "2", 81: "64", 83: "2019121229",
        85: "3", 86: "OpenGLES2", 87: "8191", 88: "4",
        90: "Mumbai", 91: "MH", 92: "14466", 93: "android",
        94: "KqsHTyb7yHjsAiyNWUUZa0DSOD6U0AhDQ76smAo1WeHHHpSmJ8KMRyRrxb2ttgJqO9YOqO/K6AORAvDMAX/qBS8+JahIkrM7kHfzlfULbgRAoZ9r",
        95: "111207",
        96: '{"cur_rate":[60,90,120],"support_etc2":false}',
        97: "1", 98: "1", 99: "4", 100: "4",
        102: "D]C\x15\x05T\x0eU3", 103: "1", 104: "52837", 105: "1",
        106: "https://dl.gmc.freefiremobile.com/live/ABHotUpdates/|https://core-gmc.freefiremobile.com/live/ABHotUpdates/|211c933168f55902c7dfbfd8c4e2957d",
        107: "1.3fb8adbf45f44ce9",
    }
    raw = build_proto_str(payload_dict)
    return await encrypted_proto(raw)


async def major_login(payload, release_version):
    url = f"{LOGIN_URL.rstrip('/')}/MajorLogin"
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; SM-G998B Build/TP1A.220624.014)",
        'Connection': "Keep-Alive", 'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'X-Unity-Version': "2018.4.12f1", 'X-GA': "v1 1",
        'X-Ga-Sv': str(int(time.time())),
        'ReleaseVersion': release_version,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_ctx) as response:
            if response.status == 200:
                return await response.read()
    return None


def decode_majorlogin(response_bytes):
    if not response_bytes: return None
    for offset in [64, 48, 32, 128, 16, 0]:
        if len(response_bytes) <= offset: continue
        try:
            fields = parse_proto_manual(response_bytes[offset:])
            jwt_token = fields.get(8)
            if not isinstance(jwt_token, str):
                try: jwt_token = jwt_token.decode('utf-8', errors='replace')
                except: continue
            if not jwt_token.startswith('eyJ') or len(jwt_token) < 100: continue
            key = fields.get(22); iv = fields.get(23)
            if not isinstance(key, bytes) or len(key) != 16: key = b'\x00' * 16
            if not isinstance(iv, bytes) or len(iv) != 16:  iv  = b'\x00' * 16
            url = fields.get(10)
            if not isinstance(url, str) or not url.startswith('http'): url = LOGIN_URL
            jwt_payload = decode_jwt_payload(jwt_token)
            return {
                "token": jwt_token, "url": url,
                "account_uid": jwt_payload.get("account_id"),
                "region": jwt_payload.get("lock_region", "BD"),
                "key": key, "iv": iv,
            }
        except: continue
    return None


# ==================== GET LOGIN DATA ====================
async def get_login_data(base_url, payload, token, release_version):
    if not base_url or not isinstance(base_url, str): base_url = LOGIN_URL
    url = f"{base_url.rstrip('/')}/GetLoginData"
    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    headers = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 13; SM-G998B Build/TP1A.220624.014)",
        'Connection': "Keep-Alive", 'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'X-Unity-Version': "2018.4.12f1", 'X-GA': "v1 1",
        'ReleaseVersion': release_version,
        'Authorization': f'Bearer {token}',
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers, ssl=ssl_ctx) as response:
            if response.status == 200:
                return await response.read()
    return None


def find_ip_ports(data):
    fields = parse_proto_manual(data)
    return [(fn, v) for fn, v in fields.items()
            if isinstance(v, str) and ":" in v and v.count(".") >= 3]


# ==================== AUTH + TCP ====================
async def build_auth_packet(target, token, timestamp, key, iv):
    try: target_int = int(target)
    except: return None
    uid_hex = hex(target_int)[2:]
    uid_len = len(uid_hex)
    enc_ts  = hex(int(timestamp))[2:].zfill(8)
    enc_tok = token.encode().hex()
    enc_pkt = await enc_packet(enc_tok, key, iv)
    enc_len = hex(len(enc_pkt) // 2)[2:]
    pad_map = {9: '0000000', 8: '00000000', 10: '000000', 7: '000000000'}
    hdrs    = pad_map.get(uid_len, '0000000')
    return f"0115{hdrs}{uid_hex}{enc_ts}00000{enc_len}{enc_pkt}"


async def tcp_activate(ip, port, auth):
    try:
        reader, writer = await asyncio.open_connection(ip, int(port))
        writer.write(bytes.fromhex(auth))
        await writer.drain()
        try:
            data = await asyncio.wait_for(reader.read(9999), timeout=5.0)
            if data: return True, data.hex()
        except asyncio.TimeoutError:
            return True, ""
        try: writer.close(); await writer.wait_closed()
        except: pass
    except Exception as e:
        return False, str(e)
    return True, ""


# ==================== CORE ====================
async def run_activation(uid, password):
    open_id, access_token = await generate_access(uid, password)
    if not open_id:
        return {"success": False, "error": "OAuth failed — invalid UID or password"}

    release_version, client_version = await get_version_config()

    encrypted = await encrypt_major_login(open_id, access_token, client_version)
    response  = await major_login(encrypted, release_version)
    if not response:
        return {"success": False, "error": "MajorLogin failed"}

    decoded = decode_majorlogin(response)
    if not decoded or not decoded.get('token'):
        return {"success": False, "error": "No JWT in MajorLogin response"}

    account_uid = decoded['account_uid']
    if not account_uid:
        return {"success": False, "error": "No account_uid in JWT"}

    login_data = await get_login_data(decoded['url'], encrypted, decoded['token'], release_version)
    if not login_data:
        return {"success": False, "error": "GetLoginData failed"}

    ip_ports = find_ip_ports(login_data)
    if len(ip_ports) < 2:
        return {"success": False, "error": f"Not enough servers: {len(ip_ports)} found"}

    chat_ip,   chat_port   = ip_ports[0][1].split(":")
    online_ip, online_port = ip_ports[1][1].split(":")

    timestamp = int(time.time())
    auth = await build_auth_packet(account_uid, decoded['token'], timestamp, decoded['key'], decoded['iv'])
    if not auth:
        return {"success": False, "error": "Auth packet build failed"}

    ok1, resp1 = await tcp_activate(chat_ip, int(chat_port), auth)
    await asyncio.sleep(0.5)
    ok2, resp2 = await tcp_activate(online_ip, int(online_port), auth)

    return {
        "success": True,
        "account_uid":     account_uid,
        "region":          decoded['region'],
        "chat_server":     f"{chat_ip}:{chat_port}",
        "online_server":   f"{online_ip}:{online_port}",
        "chat_response":   resp1[:80] if resp1 else ("OK" if ok1 else "FAILED"),
        "online_response": resp2[:80] if resp2 else ("OK" if ok2 else "FAILED"),
    }


# ==================== ROUTES ====================
@app.get("/")
async def root():
    return {"status": "online", "service": "FF Guest Activator API"}


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": int(time.time())}


@app.post("/activate")
async def activate(req: ActivateRequest):
    if not req.uid or not req.password:
        raise HTTPException(status_code=400, detail="uid and password required")
    result = await run_activation(req.uid, req.password)
    return JSONResponse(content=result, status_code=200 if result["success"] else 400)


# ==================== /bind — Bot Compatible (GET with query params) ====================
# Bot calls: GET /bind?uid=xxx&password=xxx&region=BD
# Bot checks response for: "success" | "activated" | "true"
@app.get("/bind")
async def bind(uid: str = "", password: str = "", region: str = "BD"):
    if not uid or not password:
        return JSONResponse(
            content={"success": False, "activated": False, "message": "uid and password required"},
            status_code=400
        )

    result = await run_activation(uid, password)

    if result.get("success"):
        return JSONResponse(
            content={
                "success": True,
                "activated": True,
                "status": "activated",
                "account_uid":    result.get("account_uid", uid),
                "region":         result.get("region", region),
                "chat_server":    result.get("chat_server", ""),
                "online_server":  result.get("online_server", ""),
                "chat_response":  result.get("chat_response", ""),
                "online_response": result.get("online_response", ""),
                "message": "Account activated successfully"
            },
            status_code=200
        )
    else:
        return JSONResponse(
            content={
                "success": False,
                "activated": False,
                "message": result.get("error", "Activation failed")
            },
            status_code=400
        )


# ==================== VERCEL HANDLER ====================
handler = Mangum(app, lifespan="off")
