import os, json, shutil
from mega import Mega
from telethon import TelegramClient, events

# Load Telegram config
bot_token = os.getenv('BOT_TOKEN')
source_chat = int(os.getenv('SOURCE_CHAT_ID'))

# Load MEGA accounts
with open('mega_accounts.json') as f:
    mega_accounts = json.load(f)
mega = Mega()
current = 0

# Branding text file
with open('branding.txt', 'r') as f:
    branding_text = f.read()

# Telegram client
client = TelegramClient('bot', api_id=0, api_hash='unused').start(bot_token=bot_token)

async def rotate_and_upload(folder_path):
    global current
    for i in range(len(mega_accounts)):
        acc = mega_accounts[current]
        m = mega.login(acc['email'], acc['password'])
        try:
            link = m.upload(folder_path)
            return link
        except Exception as e:
            current = (current + 1) % len(mega_accounts)
    raise Exception("All MEGA accounts failed")

def clean_and_brand(source_folder):
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            path = os.path.join(root, file)
            if file.endswith('.txt'):
                os.remove(path)
            else:
                ext = os.path.splitext(file)[1]
                newp = os.path.join(root, f"@OnlyFun_dungeon [Telegram]{ext}")
                os.rename(path, newp)
    # Add branding file
    shutil.copy('branding.txt', source_folder)

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    msg = event.raw_text.strip()
    if 'mega.nz/' in msg:
        # download
        m = mega.login(mega_accounts[0]['email'], mega_accounts[0]['password'])
        path = m.download_url(msg, dest_filename='downloaded_folder')
        clean_and_brand(path)
        new_link = rotate_and_upload(path)
        await event.reply(f"🔁 Rebranded: {new_link}")

client.start()
client.run_until_disconnected()
