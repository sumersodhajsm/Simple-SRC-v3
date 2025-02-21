import os as O, re as R
from pyrogram import Client as C, filters as F
from pyrogram.types import Message as M

A, H, T, S = O.getenv("API_ID"), O.getenv("API_HASH"), O.getenv("BOT_TOKEN"), O.getenv("SESSION")
X, Y = C("X", api_id=A, api_hash=H, bot_token=T), C("Y", api_id=A, api_hash=H, session_string=S)
Z, W = {}, {}

def E(L):
    P, Q = R.match(r"https://t\.me/([^/]+)/(\d+)", L), R.match(r"https://t\.me/c/(\d+)/(\d+)", L)
    return (P.group(1), int(P.group(2)), "public") if P else (f"-100{Q.group(1)}", int(Q.group(2)), "private") if Q else (None, None, None)

async def J(C, U, I, D, L):
    try:
        return await C.get_messages(I, D) if L == "public" else await U.get_messages(I, D)
    except Exception as e:
        print(f"Error: {e}")
        return None

async def K(c, t, C, h, m):
    p = (c / t) * 100
    await C.edit_message_text(h, m, f"Progress: {p:.2f}%")

async def V(C, U, m, d, l, u):
    try:
        if m.media:
            if l == "private":
                P = await C.send_message(d, "Downloading...")
                W[u] = {"cancel": False, "progress": P.id}
                F = await U.download_media(m, progress=K, progress_args=(C, d, P.id))
                if W.get(u, {}).get("cancel"):
                    await C.edit_message_text(d, P.id, "Canceled.")
                    if O.path.exists(F): O.remove(F)
                    del W[u]
                    return "Canceled."
                if not F:
                    await C.edit_message_text(d, P.id, "Failed.")
                    del W[u]
                    return "Failed."
                await C.edit_message_text(d, P.id, "Uploading...")
                th = "v3.jpg"
                if m.video: await C.send_video(d, video=F, caption=m.caption, thumb=th, progress=K, progress_args=(C, d, P.id))
                elif m.photo: await C.send_photo(d, photo=F, caption=m.caption, progress=K, progress_args=(C, d, P.id))
                elif m.document: await C.send_document(d, document=F, caption=m.caption, progress=K, progress_args=(C, d, P.id))
                O.remove(F)
                await C.delete_messages(d, P.id)
                del W[u]
                return "Done."
            else:
                await m.copy(chat_id=d)
                return "Copied."
        elif m.text:
            await (C.send_message(d, text=m.text) if l == "private" else m.copy(chat_id=d))
            return "Sent."
    except Exception as e:
        return f"Error: {e}"

@X.on_message(F.command("batch"))
async def B(C, m: M):
    U = m.from_user.id
    Z[U] = {"step": "start"}
    await m.reply_text("Send start link.")

@X.on_message(F.command("cancel"))
async def N(C, m: M):
    U = m.from_user.id
    if U in W:
        W[U]["cancel"] = True
        await m.reply_text("Cancelling...")
    else:
        await m.reply_text("No active task.")

@X.on_message(F.text & ~F.command)
async def H(C, m: M):
    U = m.from_user.id
    if U not in Z:
        return
    S = Z[U].get("step")
    if S == "start":
        L = m.text
        I, D, L = E(L)
        if not I or not D:
            await m.reply_text("Invalid.")
            del Z[U]
            return
        Z[U].update({"step": "count", "cid": I, "sid": D, "lt": L})
        await m.reply_text("How many?")
    elif S == "count":
        if not m.text.isdigit():
            await m.reply_text("Enter a number.")
            return
        Z[U].update({"step": "dest", "num": int(m.text)})
        await m.reply_text("Send destination ID.")
    elif S == "dest":
        D = m.text
        Z[U].update({"step": "process", "did": D})
        I, S, N, L = Z[U]["cid"], Z[U]["sid"], Z[U]["num"], Z[U]["lt"]
        R = 0
        await m.reply_text("Processing...")
        for i in range(N):
            M = S + i
            msg = await J(C, Y, I, M, L)
            if msg:
                res = await V(C, Y, msg, D, L, U)
                await m.reply_text(f"{i+1}/{N}: {res}")
                if "Done" in res: R += 1
            else:
                await m.reply_text(f"{M} not found.")
        await m.reply_text(f"Completed. {R}/{N} done.")
        del Z[U]

if __name__ == "__main__":
    Y.start()
    X.run()
