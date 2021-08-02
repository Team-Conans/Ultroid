# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

"""

import os

import requests

from . import *


@ultroid_cmd(pattern="addnsfw ?(.*)", admins_only=True)
async def addnsfw(e):
    action = e.pattern_match.group(1)
    if not action or ("ban" or "kick" or "mute") not in action:
        action = "mute"
    nsfw_chat(e.chat_id, action)
    await eor(e, "Added This Chat To Nsfw Filter")


@ultroid_cmd(pattern="remnsfw", admins_only=True)
async def remnsfw(e):
    rem_nsfw(e.chat_id)
    await eor(e, "Removed This Chat from Nsfw Filter.")


NWARN = {}


@ultroid_bot.on(events.NewMessage(incoming=True))
async def checknsfw(e):
    chat = e.chat_id
    action = is_nsfw(chat)
    if action and udB.get("DEEP_API") and e.media:
        pic, name, nsfw = "", "", 0
        try:
            pic = await ultroid_bot.download_media(e.media, thumb=-1)
        except BaseException:
            pass
        if e.file:
            name = e.file.name
        if name and check_profanity(name):
            nsfw += 1
        if pic and not nsfw:
            r = requests.post(
                "https://api.deepai.org/api/nsfw-detector",
                files={
                    "image": open(pic, "rb"),
                },
                headers={"api-key": udB["DEEP_API"]},
            )
            k = float((r.json()["output"]["nsfw_score"]))
            score = int(k * 100)
            if score > 45:
                nsfw += 1
            os.remove(pic)
        if nsfw:
            await e.delete()
            if NWARN.get(e.sender_id):
                count = NWARN[e.sender_id] + 1
                if count < 3:
                    NWARN.update({e.sender_id: count})
                    return await ultroid_bot.send_message(
                        e.chat_id,
                        f"**NSFW Warn {count}/3** To [{e.sender.first_name}](tg://user?id={e.sender_id})\nDon't Send NSFW stuffs Here Or You will Be Get {action}",
                    )
                if "mute" in action:
                    try:
                        await ultroid_bot.edit_permissions(
                            e.chat_id, e.sender_id, until_date=None, send_messages=False
                        )
                    except BaseException:
                        pass
                elif "ban" in action:
                    try:
                        await ultroid_bot.edit_permissions(
                            e.chat_id, e.sender_id, view_messages=False
                        )
                    except BaseException:
                        pass
                elif "kick" in action:
                    try:
                        await ultroid_bot.kick_participant(e.chat_id, e.sender_id)
                    except BaseException:
                        pass
                NWARN.pop(e.sender_id)
            else:
                NWARN.update({e.sender_id: 1})
                return await ultroid_bot.send_message(
                    e.chat_id,
                    f"**NSFW Warn 1/3** To [{e.sender.first_name}](tg://user?id={e.sender_id})\nDon't Send NSFW stuffs Here Or You will Be Get {action}",
                )
