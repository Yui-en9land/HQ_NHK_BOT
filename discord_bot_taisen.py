import discord
import datetime
import asyncio
import token_id
import os
from discord.ext import commands
#from discord import app_commands
from discord import Option

intents = discord.Intents.all()
intents.reactions = True
intents.guilds = True
intents.message_content=True

bot = discord.Bot(intents=intents)

client = commands.Bot(command_prefix='/', intents=intents)

participants = []
match_mem = []
current_index = 0
waiting_for_start = False
named_table = []
match_num = 0
total_num = 1
match_history = []
guild_id = token_id.guild_id


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
            # 1P側に右固定または2P側に左固定がいる場合　左右を入れ替える
            named_table.append([participants[match_ind[1]][0], participants[match_ind[0]][0]])

        else:
            named_table.append([participants[match_ind[0]][0], participants[match_ind[1]][0]])

    return named_table


def timefile(total_num, named_table, match_num):
    d_today = datetime.date.today()
    str_today = d_today.strftime('%Y%m%d')
    # 対戦履歴を現在の日付でテキストに格納
    with open(str_today + 'timestamps.txt', 'a') as file:
        file.write('M{:02d}: {} vs {}\n'.format(total_num, named_table[match_num][0], named_table[match_num][1]))


@bot.event
async def on_ready():
    print('Bot is ready.')


@bot.event
async def on_voice_state_update(member, before, after):
    global participants
    # チャンネルへの入室ステータスが変更されたとき（ミュートON、OFFに反応しないように分岐）
    if before.channel != after.channel:
        # 通知メッセージを書き込むテキストチャンネル（チャンネルIDを指定）
        botRoom = bot.get_channel(token_id.CHANNEL_ID1)

        # 入退室を監視する対象のボイスチャンネル（チャンネルIDを指定）
        announceChannelIds = [token_id.CHANNEL_ID1]

        # 退室通知
        if before.channel is not None and before.channel.id in announceChannelIds:
            await botRoom.send('**' + before.channel.name + '** から、__' + member.display_name + '__  が抜けました！')
            for name_index, member_name in enumerate(participants):
                if member_name[0] == member.display_name:
                    del participants[name_index]

        # 入室通知
        if after.channel is not None and after.channel.id in announceChannelIds:
            await botRoom.send('**' + after.channel.name + '** に、__' + member.display_name + '__  が参加しました！')
            check_name = []
            for join_name in participants:
                check_name.append(join_name[0])
            if member.display_name not in check_name:
                # 登録時は左右どちらでも可として登録
                member_info = [member.display_name, 'LR']
                participants.append(member_info)


@bot.slash_command(description="指定番号の参加者の左右の固定有無を設定します", guild_ids=guild_id)
async def change(ctx, num, lr):
    global participants
    num = int(num)
    if participants:
        if len(participants) > num:
            if lr == 'L':
                participants[num][1] = 'L'
                await ctx.respond(f'{participants[num][0]}が左固定になりました')
            elif lr == 'R':
                participants[num][1] = 'R'
                await ctx.respond(f'{participants[num][0]}:が右固定になりました')
            elif lr == 'LR':
                participants[num][1] = 'LR'
                await ctx.respond(f'{participants[num][0]}:が固定解除されました')
            else:
                await ctx.respond('L、R、LRのいずれかを大文字で入力してください')
        else:
            await ctx.respond('メンバーのインデックス番号と合いません。/list_memで確認してください')

    else:
        await ctx.respond('メンバーが参加していません。/join_memで登録してください')


@bot.slash_command(description="手動で参加者を追加します", guild_ids=guild_id)
async def join(ctx, name):
    global participants
    check_name = []
    for join_name in participants:
        check_name.append(join_name[0])
    if name not in check_name:
        # 登録時は左右どちらでも可として登録
        member_info = [name, 'LR']
        participants.append(member_info)
        await ctx.respond(name + 'を追加しました')


@bot.slash_command(description="指定番号の参加者を削除します", guild_ids=guild_id)
async def leave(ctx, num):
    global participants
    if participants:
        if len(participants) <= int(num):
            await ctx.respond('メンバーのインデックス番号と合いません。/list_memで確認してください')
        else:
            await ctx.respond(f'{participants[int(num)][0]} を削除しました。')
            del participants[int(num)]
    else:
        await ctx.respond('メンバーが参加していません。/join_memで登録してください')


@bot.slash_command(description="参加者と番号、左右固定有無を表示します", guild_ids=guild_id)
async def list_mem(ctx):
    global participants
    if participants:
        mem_list_mes = '参加者リスト:\n'
        for mem_index, mem_info in enumerate(participants):
            mem_list_mes += str(mem_index) + ":\t" + mem_info[0] + ":" + mem_info[1] + "\n"
        await ctx.respond(mem_list_mes)
    else:
        await ctx.respond('メンバーが参加していません。/join_memで登録してください')


@bot.slash_command(description="対戦表を作成し試合を開始します。人数が変わった場合も実行してください", guild_ids=guild_id)
async def hqstart(ctx):
    global participants
    global named_table, match_num, total_num
    match_num = 0
    member_num = len(participants)
    if member_num == 2:
        named_table = table_make(match_table2, participants)
    elif member_num == 3:
        named_table = table_make(match_table3, participants)
    elif member_num == 4:
        named_table = table_make(match_table4, participants)
    elif member_num == 5:
        named_table = table_make(match_table5, participants)
    else:
        await ctx.respond(
            'メンバーが足りないか、多すぎます\n２～５人までしか対応していないため参加者を増やすか減らすかしてください')
        return
    # 対戦表作成後、最初の1試合はここで通知
    await ctx.respond('対戦表を作成しました。')


@bot.slash_command(description="次の試合のアナウンスをします", guild_ids=guild_id)
async def next(ctx):
    global participants
    global match_num, total_num, match_history
    # 全試合数をオーバーしていないか判定　超えた場合は最初(0)に戻る
    if match_num >= len(named_table):
        match_num = 0
    await ctx.respond('# M{:02d}: {} vs {}'.format(total_num, named_table[match_num][0], named_table[match_num][1]))
    # 対戦履歴を格納(未使用)
    match_history.append(named_table[match_num])
    timefile(total_num, named_table, match_num)
    match_num += 1
    total_num += 1


@bot.event
async def on_message(message):
    global participants
    global match_num, total_num, match_history
    if message.author.bot:
        return
    if "nx" in message.content.lower():
        # 全試合数をオーバーしていないか判定　超えた場合は最初(0)に戻る
        if match_num >= len(named_table):
            match_num = 0
        await message.channel.send('# M{:02d}: {} vs {}'.format(total_num, named_table[match_num][0], named_table[match_num][1]))
        # 対戦履歴を格納(未使用)
        match_history.append(named_table[match_num])
        timefile(total_num, named_table, match_num)
        match_num += 1
        total_num += 1

@bot.slash_command(description="ルームにいるメンバー全員を参加させます", guild_ids=guild_id)
async def join_mem(ctx):
    global participants
    # ボイスチャットに参加しているメンバーを取得
    voicechat_members = [i.display_name for i in ctx.author.voice.channel.members]
    if participants:
        # 既にメンバーが登録されている場合は足りない人のみ追加
        for member_name in voicechat_members:
            for join_name in participants:
                if member_name not in join_name:
                    # 登録時は左右どちらでも可として登録
                    member_info = [member_name, 'LR']
                    participants.append(member_info)
                    await ctx.respond(f'{member_name}が参加しました。')
    else:
        # メンバーが登録されてない場合は新規で全員追加
        for member_name in voicechat_members:
            # 登録時は左右どちらでも可として登録
            member_info = [member_name, 'LR']
            participants.append(member_info)
            await ctx.respond(f'{member_name}が参加しました。')


@bot.slash_command(description="対戦履歴をクリアします 全て:all １試合:1", guild_ids=guild_id)
async def clear(ctx, allor1):
    global match_num, total_num
    d_today = datetime.date.today()
    str_today = d_today.strftime('%Y%m%d')
    filename = str_today + 'timestamps.txt'
    if os.path.isfile(filename):
        if allor1 == 'all':
            # ナンバリングを0にしてテキストファイルを削除する
            total_num = 0
            os.remove(filename)
        elif allor1 == '1':
            # ナンバリングを一つ戻してテキストファイルから最終行を削除する
            total_num -= 1
            with open(filename, 'w') as file:
                filelist = file.readlines()
                del filelist[len(filelist)-1]
    else:
        await ctx.respond('本日の履歴は存在しません')


@bot.slash_command(description="試合結果をテキストファイルで出力します", guild_ids=guild_id)
async def write(ctx, yyyymmdd):
    filename = yyyymmdd + 'timestamps.txt'
    if os.path.isfile(filename):
        await ctx.respond('ファイルを出力しました')
        await bot.get_channel(token_id.CHANNEL_ID1).send(file=discord.File(filename))
    else:
        await ctx.respond('その日付のファイルは存在しません')


# Botの起動とDiscordサーバーへの接続
bot.run(token_id.TOKEN)
