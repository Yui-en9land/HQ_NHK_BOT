import discord
import datetime
import asyncio
import token_id
import os
from discord.ext import commands
# from discord import app_commands
from discord import Option

intents = discord.Intents.all()
intents.reactions = True
intents.guilds = True
intents.message_content = True

bot = discord.Bot(intents=intents)

client = commands.Bot(command_prefix='/', intents=intents)

guild_id = token_id.guild_id

member_list1 = []
member_list2 = []
match_num1 = 0
match_num2 = 0
total_num1 = 1
total_num2 = 1
named_table1 = []
named_table2 = []
match_history1 = []
match_history2 = []

match_table2 = [
    [1, 0], [0, 1]
]
match_table3 = [
    [2, 1], [0, 2], [1, 0],
    [1, 2], [2, 0], [0, 1]
]

match_table4 = [
    [3, 2], [1, 0], [1, 3], [0, 2], [3, 0], [2, 1],
    [2, 3], [0, 1], [3, 1], [2, 0], [0, 3], [1, 2]
]

match_table5 = [
    [4, 3], [2, 1], [0, 4], [3, 2], [1, 0], [4, 2], [3, 1], [2, 0], [4, 1], [3, 0],
    [3, 4], [1, 2], [4, 0], [2, 3], [0, 1], [2, 4], [1, 3], [0, 2], [1, 4], [0, 3]
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


def timefile(total_num, named_table, match_num, channel_num):
    d_today = datetime.date.today()
    str_today = d_today.strftime('%Y%m%d')
    # 対戦履歴を現在の日付でテキストに格納
    with open(str_today + '_' + str(channel_num) + '_' + 'result.txt', 'a') as file:
        file.write('M{:02d}: {} vs {}\n'.format(total_num, named_table[match_num][0], named_table[match_num][1]))

        
def inout_announce(channel_id, participants, member, before, after):
    # 入退室を監視する対象のボイスチャンネル（チャンネルIDを指定）
    announce_channel_id = [channel_id]
    send_str = ''
    # 退室通知
    if before.channel is not None and before.channel.id in announce_channel_id:
        send_str = '**' + before.channel.name + '** から、__' + member.display_name + '__  が抜けました！'
        for name_index, member_name in enumerate(participants):
            if member_name[0] == member.display_name:
                del participants[name_index]

    # 入室通知
    if after.channel is not None and after.channel.id in announce_channel_id:
        send_str = '**' + after.channel.name + '** に、__' + member.display_name + '__  が参加しました！'
        check_name = []
        for join_name in participants:
            # リストからメンバー名だけを取り出す
            check_name.append(join_name[0])
        # メンバーリストに参加者名が無い場合はメンバーリストに追加
        if member.display_name not in check_name:
            # 登録時は左右どちらでも可として登録
            member_info = [member.display_name, 'LR']
            participants.append(member_info)
    return participants, send_str


def change_member(participants, num, lr):
    num = int(num)
    if participants:
        if len(participants) > num:
            if lr == 'L':
                participants[num][1] = 'L'
                send_str = (f'{participants[num][0]}が左固定になりました')
            elif lr == 'R':
                participants[num][1] = 'R'
                send_str = (f'{participants[num][0]}:が右固定になりました')
            elif lr == 'LR':
                participants[num][1] = 'LR'
                send_str = (f'{participants[num][0]}:が固定解除されました')
            else:
                send_str = ('L、R、LRのいずれかを大文字で入力してください')
        else:
            send_str = ('メンバーのインデックス番号と合いません。/list_memで確認してください')

    else:
        send_str = ('メンバーが参加していません。/join_memで登録してください')
    return participants, send_str


def join_member(participants, name):
    check_name = []
    send_str = name + "は既にメンバーにいます"
    for join_name in participants:
        check_name.append(join_name[0])
    if name not in check_name:
        # 登録時は左右どちらでも可として登録
        member_info = [name, 'LR']
        participants.append(member_info)
        send_str = name + 'を追加しました'
    return participants, send_str


@bot.event
async def on_ready():
    print('Bot is ready.')


@bot.event
async def on_voice_state_update(member, before, after):
    global member_list1, member_list2
    # チャンネルへの入室ステータスが変更されたとき（ミュートON、OFFに反応しないように分岐）
    if before.channel != after.channel:
        # 通知メッセージを書き込むテキストチャンネル（チャンネルIDを指定）
        botroom = bot.get_channel(token_id.CHANNEL_ID1)
        [member_list1, send_str] = inout_announce(token_id.CHANNEL_ID1, member_list1, member, before, after)
        if send_str:
            await botroom.send(send_str)

        botroom = bot.get_channel(token_id.CHANNEL_ID2)
        [member_list2, send_str] = inout_announce(token_id.CHANNEL_ID2, member_list2, member, before, after)
        if send_str:
            await botroom.send(send_str)


@bot.slash_command(description="指定番号の参加者の左右の固定有無を設定します", guild_ids=guild_id)
async def change(ctx, num, lr):
    global member_list1, member_list2
    if ctx.channel_id == token_id.CHANNEL_ID1:
        [member_list1, send_str] = change_member(member_list1, num, lr)
        await ctx.respond(send_str)
    if ctx.channel_id == token_id.CHANNEL_ID2:
        [member_list2, send_str] = change_member(member_list2, num, lr)
        await ctx.respond(send_str)


@bot.slash_command(description="手動で参加者を追加します", guild_ids=guild_id)
async def join(ctx, name):
    global member_list1, member_list2
    if ctx.channel_id == token_id.CHANNEL_ID1:
        [member_list1, send_str] = join_member(member_list1, name)
        await ctx.respond(send_str)
    if ctx.channel_id == token_id.CHANNEL_ID2:
        [member_list2, send_str] = join_member(member_list2, name)
        await ctx.respond(send_str)


@bot.slash_command(description="指定番号の参加者を削除します", guild_ids=guild_id)
async def leave(ctx, num):
    global member_list1, member_list2

    def leave_member(num, participants):
        if participants:
            if len(participants) <= int(num):
                send_str = 'メンバーのインデックス番号と合いません。/list_memで確認してください'
            else:
                send_str = f'{participants[int(num)][0]} を削除しました。'
                del participants[int(num)]
        else:
            send_str = 'メンバーが参加していません。/join_memで登録してください'
        return participants, send_str

    if ctx.channel_id == token_id.CHANNEL_ID1:
        [member_list1, send_str] = leave_member(num, member_list1)
        await ctx.respond(send_str)
    if ctx.channel_id == token_id.CHANNEL_ID2:
        [member_list2, send_str] = leave_member(num, member_list2)
        await ctx.respond(send_str)


@bot.slash_command(description="参加者と番号、左右固定有無を表示します", guild_ids=guild_id)
async def list_mem(ctx):
    global member_list1, member_list2

    def member_list(participants):
        if participants:
            mem_list_mes = '参加者リスト:\n'
            for mem_index, mem_info in enumerate(participants):
                mem_list_mes += str(mem_index) + ":\t" + mem_info[0] + ":" + mem_info[1] + "\n"
            send_str = mem_list_mes
        else:
            send_str = 'メンバーが参加していません。/join_memで登録してください'
        return participants, send_str

    if ctx.channel_id == token_id.CHANNEL_ID1:
        [member_list1, send_str] = member_list(member_list1)
        await ctx.respond(send_str)
    if ctx.channel_id == token_id.CHANNEL_ID2:
        [member_list2, send_str] = member_list(member_list2)
        await ctx.respond(send_str)


@bot.slash_command(description="対戦表を作成し試合を開始します。人数が変わった場合も実行してください",
                   guild_ids=guild_id)
async def hqstart(ctx):
    global member_list1, member_list2
    global named_table1, named_table2, match_num1, match_num2, total_num1, total_num2

    def match_make(participants):
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
            send_str = 'メンバーが足りないか、多すぎます\n２～５人までしか対応していないため参加者を増やすか減らすかしてください'
            return [], send_str
        send_str = '対戦表を作成しました。'
        return named_table, send_str

    if ctx.channel_id == token_id.CHANNEL_ID1:
        match_num1 = 0
        [named_table1, send_str] = match_make(member_list1)
        await ctx.respond(send_str)
    if ctx.channel_id == token_id.CHANNEL_ID2:
        match_num2 = 0
        [named_table2, send_str] = match_make(member_list2)
        await ctx.respond(send_str)


def next_match(match_num, total_num, named_table, match_history, channel_num):
    # 全試合数をオーバーしていないか判定　超えた場合は最初(0)に戻る
    if match_num >= len(named_table):
        match_num = 0
    if match_num < 0:
        match_num = len(named_table) - 1
    send_str = ('# M{:02d}: {} vs {}'.format(total_num, named_table[match_num][0], named_table[match_num][1]))
    # 対戦履歴を格納(未使用)
    match_history.append(named_table[match_num])
    timefile(total_num, named_table, match_num, channel_num)
    match_num += 1
    total_num += 1
    return match_num, total_num, named_table, match_history, send_str


@bot.slash_command(description="次の試合のアナウンスをします", guild_ids=guild_id)
async def next(ctx):
    global member_list1, match_num1, total_num1, match_history1, named_table1
    if ctx.channel_id == token_id.CHANNEL_ID1:
        [match_num1, total_num1, named_table1, match_history1, send_str] = next_match(match_num1, total_num1,
                                                                                      named_table1, match_history1, 1)
        await ctx.respond(send_str)

    global member_list2, match_num2, total_num2, match_history2, named_table2
    if ctx.channel_id == token_id.CHANNEL_ID2:
        [match_num2, total_num2, named_table2, match_history2, send_str] = next_match(match_num2, total_num2,
                                                                                      named_table2, match_history2, 2)
        await ctx.respond(send_str)


@bot.event
async def on_message(message):
    global member_list1, match_num1, total_num1, match_history1
    if message.author.name == bot.user.name:
        return

    if "nx" in message.content.lower():
        global member_list1, match_num1, total_num1, match_history1, named_table1
        if message.channel.id == token_id.CHANNEL_ID1:
            [match_num1, total_num1, named_table1, match_history1, send_str] = next_match(match_num1, total_num1,
                                                                                          named_table1, match_history1, 1)
            await message.channel.send(send_str)

        global member_list2, match_num2, total_num2, match_history2, named_table2
        if message.channel.id == token_id.CHANNEL_ID2:
            [match_num2, total_num2, named_table2, match_history2, send_str] = next_match(match_num2, total_num2,
                                                                                          named_table2, match_history2, 2)
            await message.channel.send(send_str)


@bot.slash_command(description="ルームにいるメンバー全員を参加させます", guild_ids=guild_id)
async def join_mem(ctx):

    def member_join(participants, voicechat_members):
        join_members = []
        joins = ''
        send_str = '既に全員登録されています'
        if participants:
            # 既にメンバーが登録されている場合は足りない人のみ追加
            for member_name in voicechat_members:
                for join_name in participants:
                    join_members.append(join_name[0])
                if member_name not in join_members:
                    # 登録時は左右どちらでも可として登録
                    member_info = [member_name, 'LR']
                    participants.append(member_info)
                    joins = member_name + ',' + joins
                    send_str = (f'{joins}が参加しました。')
        else:
            if voicechat_members:
                # メンバーが登録されてない場合は新規で全員追加
                for member_name in voicechat_members:
                    # 登録時は左右どちらでも可として登録
                    member_info = [member_name, 'LR']
                    participants.append(member_info)
                    joins = member_name + ',' + joins
                send_str = (f'{joins}が参加しました。')
            else:
                send_str = 'ルームにメンバーがいません'
        return participants, send_str

    global member_list1
    if ctx.channel_id == token_id.CHANNEL_ID1:
        # ボイスチャットに参加しているメンバーを取得
        voicechat_members1 = [i.display_name for i in ctx.channel.members]
        [member_list1, send_str] = member_join(member_list1, voicechat_members1)
        await ctx.respond(send_str)

    global member_list2
    if ctx.channel_id == token_id.CHANNEL_ID2:
        # ボイスチャットに参加しているメンバーを取得
        voicechat_members2 = [i.display_name for i in ctx.channel.members]
        [member_list2, send_str] = member_join(member_list2, voicechat_members2)
        await ctx.respond(send_str)


@bot.slash_command(description="再戦(re)するか次の対戦をパス(pass)します", guild_ids=guild_id)
async def match_ctrl(ctx, re_or_pass):
    global match_num, total_num
    def match_control(re_or_pass, match_num, total_num, channel_num):
        if re_or_pass == 're':
            match_num = match_num - 1
            send_str = ('もう一度対戦します(/nextまたはnxを入力してください)')
        elif re_or_pass == 'pass':
            # ナンバリングを一つ戻してテキストファイルから最終行を削除する
            total_num = max(total_num - 1, 1)
            d_today = datetime.date.today()
            str_today = d_today.strftime('%Y%m%d')
            filename = str_today + '_' + str(channel_num) + '_' + 'result.txt'
            with open(filename, 'r+') as file:
                filelist = file.readlines()
                file.seek(0)
                file.truncate()
                del filelist[len(filelist) - 1]
                file.writelines(filelist)
            send_str = ('上記の対戦をパスしました')
        else:
            send_str = ('reまたはpassを入力してください')
        return match_num, total_num, send_str
      
      
    global match_num1, total_num1
    if ctx.channel_id == token_id.CHANNEL_ID1:
        [match_num1, total_num1, send_str] = match_control(re_or_pass, match_num1, total_num1, 1)
        await ctx.respond(send_str)
    global match_num2, total_num2
    if ctx.channel_id == token_id.CHANNEL_ID2:
        [match_num2, total_num2, send_str] = match_control(re_or_pass, match_num2, total_num2, 2)
        await ctx.respond(send_str)

@bot.slash_command(description="対戦履歴をクリアします 全て:all １試合:1", guild_ids=guild_id)
async def clear(ctx, all_or_1):
    global match_num, total_num

    def clear_match(channel_num, total_num, match_num):
        d_today = datetime.date.today()
        str_today = d_today.strftime('%Y%m%d')
        filename = str_today + '_' + str(channel_num) + '_' + 'result.txt'
        if os.path.isfile(filename):
            if all_or_1 == 'all':
                # ナンバリングを0にしてテキストファイルを削除する
                total_num = 1
                match_num = 1
                os.remove(filename)
                send_str = ('全てのデータをクリアしました')
            elif all_or_1 == '1':
                # ナンバリングを一つ戻してテキストファイルから最終行を削除する
                total_num = max(total_num - 1, 1)
                with open(filename, 'r+') as file:
                    filelist = file.readlines()
                    file.seek(0)
                    file.truncate()
                    del filelist[len(filelist) - 1]
                    file.writelines(filelist)
                    send_str = ('1試合分のデータをクリアしました')
        else:
            send_str = ('本日の履歴は存在しません')
        return total_num, match_num, send_str

    global match_num1, total_num1
    if ctx.channel_id == token_id.CHANNEL_ID1:
        [total_num1, match_num1, send_str] = clear_match(1, total_num1, match_num1)
        await ctx.respond(send_str)
    global match_num2, total_num2
    if ctx.channel_id == token_id.CHANNEL_ID2:
        [total_num2, match_num2, send_str] = clear_match(2, total_num2, match_num2)
        await ctx.respond(send_str)

@bot.slash_command(description="試合結果をテキストファイルで出力します", guild_ids=guild_id)
async def write(ctx, yyyymmdd):
    if ctx.channel_id == token_id.CHANNEL_ID1:
        filename = yyyymmdd + '_' + str(1) + '_' + 'result.txt'
        if os.path.isfile(filename):
            await ctx.respond('ファイルを出力しました')
            await bot.get_channel(token_id.CHANNEL_ID1).send(file=discord.File(filename))
        else:
             await ctx.respond('その日付のファイルは存在しません')

    if ctx.channel_id == token_id.CHANNEL_ID2:
        filename = yyyymmdd + '_' + str(2) + '_' + 'result.txt'
        if os.path.isfile(filename):
            await ctx.respond('ファイルを出力しました')
            await bot.get_channel(token_id.CHANNEL_ID2).send(file=discord.File(filename))
        else:
             await ctx.respond('その日付のファイルは存在しません')

# Botの起動とDiscordサーバーへの接続
bot.run(token_id.TOKEN)
