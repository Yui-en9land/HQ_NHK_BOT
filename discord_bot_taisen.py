import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.all()
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix='/', intents=intents)

participants = []
participantslr = []
match_mem = []
current_index = 0
waiting_for_start = False

TOKEN = ''
CHAT_CHANNEL = ''

@bot.event
async def on_ready():
    print('Bot is ready.')



@bot.event
async def on_voice_state_update(member, before, after):

    # チャンネルへの入室ステータスが変更されたとき（ミュートON、OFFに反応しないように分岐）
    if before.channel != after.channel:
        # 通知メッセージを書き込むテキストチャンネル（チャンネルIDを指定）
        botRoom = bot.get_channel(CHAT_CHANNEL)

        # 入退室を監視する対象のボイスチャンネル（チャンネルIDを指定）
        announceChannelIds = [CHAT_CHANNEL]

        # 退室通知
        if before.channel is not None and before.channel.id in announceChannelIds:
            await botRoom.send("**" + before.channel.name + "** から、__" + member.display_name + "__  が抜けました！")
            participants.remove(member.display_name)

        # 入室通知
        if after.channel is not None and after.channel.id in announceChannelIds:
            await botRoom.send("**" + after.channel.name + "** に、__" + member.display_name + "__  が参加しました！")
            participants.append(member.display_name)

@bot.command()
async def join_members(ctx):
    voicechat_members = [i.display_name for i in ctx.author.voice.channel.members]
    for member_name in voicechat_members:
        if member_name not in participants:
            participants.append(member_name)
            await ctx.send(f'{member_name}が参加しました。')

@bot.command()
async def join(ctx, name, lr):
    if name not in participants:
        participants.append(name)
        participantslr.append(lr)
        if lr == 'l':
            await ctx.send(f'{name}が左固定になりました')
        elif lr == 'r':
            await ctx.send(f'{name}:が右固定になりました')
        else:
            await ctx.send(f'{name}が参加しました。')
    else:
        await ctx.send(f'{name} は既に参加しています。')

@bot.command()
async def leave(ctx, name):
    if name not in participants:
        await ctx.send(f'{name} は既にいません。')
    else:
        participants.remove(name)
        await ctx.send(f'{name} を削除しました。')

@bot.command()
async def list_participants(ctx):
    if participants:
        await ctx.send("参加者リスト:\n" + "\n".join(participants))
    else:
        await ctx.send("参加者はいません。")

@bot.command()
async def hqstart(ctx):
    global waiting_for_start
    waiting_for_start = True
    member = len(participants)
    if member == 3:
        match_mem.append('#' + participants[0] + " vs " + participants[1])
        match_mem.append('#' + participants[0] + " vs " + participants[2])
        match_mem.append('#' + participants[2] + " vs " + participants[1])
        match_mem.append('#' + participants[1] + " vs " + participants[0])
        match_mem.append('#' + participants[2] + " vs " + participants[0])
        match_mem.append('#' + participants[1] + " vs " + participants[2])
    await ctx.send("Enter キーを押すと参加者が表示されます。")

@bot.command()
async def aaa(ctx):
    global current_index, waiting_for_start,match_mem
    if waiting_for_start:
        if match_mem:
            await ctx.send(match_mem[current_index])
            current_index = (current_index + 1) % len(match_mem)
        else:
            await ctx.send("参加者がいません。")
#    await bot.process_commands(message)

# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)