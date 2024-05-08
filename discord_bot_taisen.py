import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.all()
intents.reactions = True
intents.guilds = True

bot = commands.Bot(command_prefix='/', intents=intents)

participants = []
match_mem = []
current_index = 0
waiting_for_start = False

TOKEN = ''
CHAT_CHANNEL = ''

named_table = []
match_num = 0
total_num = 1
match_history = []

match_table2 = [
    [0, 1], [1, 0]
]
match_table3 = [
    [0, 1], [2, 0], [1, 2],
    [1, 0], [0, 2], [2, 1]
]

match_table4 = [
    [0, 1], [2, 3], [2, 0], [3, 1], [0, 3], [1, 2],
    [1, 0], [3, 2], [0, 2], [1, 3], [3, 0], [2, 1]
]

match_table5 = [
    [0, 1], [2, 3], [4, 0], [1, 2], [3, 4], [0, 2], [1, 3], [2, 4], [0, 3], [1, 4],
    [1, 0], [3, 2], [0, 4], [2, 1], [4, 3], [2, 0], [3, 1], [4, 2], [3, 0], [4, 1]
]

def table_make(match_table, participants):
    named_table = []
    for match_ind in match_table:
        if (participants[match_ind[0]][1] == 'R') or (participants[match_ind[1]][1] == 'L'):
            #右固定または左固定がいる場合　左右を入れ替える
            named_table.append([participants[match_ind[0]][0], participants[match_ind[1]][0]])

        else:
            named_table.append([participants[match_ind[0]][0], participants[match_ind[1]][0]])

    return named_table


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
            await botRoom.send('**' + before.channel.name + '** から、__' + member.display_name + '__  が抜けました！')
            for name_index, member_name in enumerate(participants):
                if member_name == member.display_name:
                    del participants[name_index]

        # 入室通知
        if after.channel is not None and after.channel.id in announceChannelIds:
            await botRoom.send('**' + after.channel.name + '** に、__' + member.display_name + '__  が参加しました！')
            member_info = [member.display_name, 'LR']
            participants.append(member_info)

@bot.command()
async def change(ctx, num, lr):
    num = int(num)
    if participants:
        if len(participants) > num:
            if lr == 'L':
                participants[num][1] = 'L'
                await ctx.send(f'{participants[num][0]}が左固定になりました')
            elif lr == 'R':
                participants[num][1] = 'R'
                await ctx.send(f'{participants[num][0]}:が右固定になりました')
            elif lr == 'LR':
                participants[num][1] = 'LR'
                await ctx.send(f'{participants[num][0]}:が固定解除されました')
            else:
                await ctx.send('L、R、LRのいずれかを大文字で入力してください')
        else:
            await ctx.send('メンバーのインデックス番号と合いません。/list_memで確認してください')

    else:
        await ctx.send('メンバーが参加していません。/join_memで登録してください')

@bot.command()
async def join(ctx, name):
    for join_name in participants:
        if name not in join_name:
            # 登録時は左右どちらでも可として登録
            member_info = [name, 'LR']
            participants.append(member_info)


@bot.command()
async def leave(ctx, num):
    if participants:
        if len(participants) <= int(num):
            await ctx.send('メンバーのインデックス番号と合いません。/list_memで確認してください')
        else:
            await ctx.send(f'{participants[int(num)][0]} を削除しました。')
            del participants[int(num)]
    else:
        await ctx.send('メンバーが参加していません。/join_memで登録してください')

@bot.command()
async def list_mem(ctx):
    if participants:
        mem_list_mes = '参加者リスト:\n''
        for mem_index, mem_info in enumerate(participants):
            mem_list_mes += str(mem_index) + ":\t" + mem_info[0] + ":" + mem_info[1] + "\n"
        await ctx.send(mem_list_mes)
    else:
        await ctx.send('メンバーが参加していません。/join_memで登録してください')

@bot.command()
async def hqstart(ctx):
    global named_table, match_num, total_num
    match_num = 0
    member_num = len(participants)
    if member_num == 2:
        named_table = table_make(match_table2, participants)
    elif member_num == 3:
        named_table = table_make(match_table2, participants)
    elif member_num == 4:
        named_table = table_make(match_table2, participants)
    elif member_num == 5:
        named_table = table_make(match_table2, participants)
    else:
        await ctx.send('メンバーが足りないか、多すぎます\n２～５人までしか対応していないため参加者を増やすか減らすかしてください')
        return
    #対戦表作成後、最初の1試合はここで通知
    await ctx.send('M' + str(total_num) + ': ' + named_table[match_num][0] + ' vs ' + named_table[match_num][1])
    match_history.append(named_table[match_num])
    match_num += 1
    total_num += 1

@bot.command()
async def next(ctx):
    global match_num, total_num, match_history
    await ctx.send('M' + str(total_num) + ': ' + named_table[match_num][0] + ' vs ' + named_table[match_num][1])
    match_history.append(named_table[match_num])
    if named_table >= len(named_table):
        match_num += 1
    total_num += 1

@bot.command()
async def join_mem(ctx):
    # ボイスチャットに参加しているメンバーを取得
    voicechat_members = [i.display_name for i in ctx.author.voice.channel.members]
    if participants:
        #既にメンバーが登録されている場合は足りない人のみ追加
        for member_name in voicechat_members:
            for join_name in participants:
                if member_name not in join_name:
                    #登録時は左右どちらでも可として登録
                    member_info = [member_name, 'LR']
                    participants.append(member_info)
                    await ctx.send(f'{member_name}が参加しました。')
    else:
        #メンバーが登録されてない場合は新規で全員追加
        for member_name in voicechat_members:
            #登録時は左右どちらでも可として登録
            member_info = [member_name, 'LR']
            participants.append(member_info)
            await ctx.send(f'{member_name}が参加しました。')#    await bot.process_commands(message)

# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)