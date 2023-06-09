import aiohttp
import more_itertools
from fitparse import FitFile
from config import Config
from telebot.async_telebot import AsyncTeleBot
bot = AsyncTeleBot(Config.BOT_TOKEN)


async def upload_message(session, url, message, device_id):
    message_dict = {
        "id": device_id,
        "timestamp": message["timestamp"],
        "lat": message['position_lat']['value'],
        "lon": message['position_long']['value'],
        "speed": message['enhanced_speed']['value'],
        "altitude": message['altitude']['value'],
        "temperature": message['temperature']['value']
    }
    async with session.post(url, params=message_dict) as resp:
        return await resp.text()


async def export_messages(messages, server_address, device_id):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for message in messages:
            tasks.append(asyncio.ensure_future(upload_message(session, f"http://{server_address}", message, device_id)))
        await asyncio.gather(*tasks)


def parse_fit_file(file):
    fitfile = FitFile(file)
    # Get all data messages that are of type record
    messages = []
    for record in fitfile.get_messages('record'):
        message = {"timestamp": int(record.get("timestamp").value.timestamp())}
        # message["timestamp"] = record.get("timestamp")
        for record_data in record:
            if record_data.units:
                message[record_data.name] = {
                    "value": record_data.value,
                    "units": record_data.units
                }
                if record_data.units == "semicircles":
                    message[record_data.name]["value"] = record_data.value * (180.0 / (2 ** 31))
                    message[record_data.name]["units"] = "deg"

                if record_data.units == "m/s":
                    message[record_data.name]["value"] = record_data.value * 3.6
                    message[record_data.name]["units"] = "km/h"

            messages.append(message)
    return messages


@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """
Hi there, I am Xoss Fit Files import bot.
Send me a *.fit files for export points by OsmAnd protocol to external server
""")


@bot.message_handler(func=lambda message: message.document.file_name.find('.fit'), content_types=['document'])
async def handle_fit_file(message):
    file_info = await bot.get_file(message.document.file_id)
    fit_file = await bot.download_file(file_info.file_path)
    messages = parse_fit_file(fit_file)
    chunk_messages = more_itertools.batched(messages, 10)
    for chunk in chunk_messages:
        await export_messages(chunk, Config.SERVER_ADDRESS, Config.DEVICE_ID)
    await bot.reply_to(message, "Uploaded")


if __name__ == '__main__':
    import asyncio
    asyncio.run(bot.polling())
