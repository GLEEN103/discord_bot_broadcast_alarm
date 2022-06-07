#로그
import logging
import os
import datetime as dt

#파싱
import requests

#디스코드 봇
import discord
from discord import option

#컨피그
import configparser

#system
import time
import sys
import re
import asyncio
import numpy

#DB
import sqlite3


#logger 세팅
def SetLogger(name=None):
    """메인 Logger 세팅용 클래스

    Args:
        name (_str_, optional): Logger의 이름 Defaults to None.

    Returns:
        _logger_: 로거 반환
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    time = dt.datetime.now()
    if not os.path.isdir("log"):
        os.makedirs("log")
    
    stream_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(filename="log\{0}.log".format(time.strftime("%Y-%m-%d-%H-%M-%S")), encoding='utf-8')
    
    formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    stream_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)
    
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    
    return logger

#컨피그 호출
def ReadConfig():
    """컨피그를 읽어오고 파일이 존재하지 않는다면 생성하고 프로그램을 종료

    Returns:
        _dic_: 컨피그의 정보
    """
    config = configparser.ConfigParser()
    
    if not os.path.isfile("config.ini"):
        Main_logger.warning("config.ini를 찾을 수 없습니다.")
        config['DEFAULT']['TOKEN'] = ''
        config['DEFAULT']['Twitch_Client_ID'] = ''
        config['DEFAULT']['Twitch_Client_Secret'] = ''
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        Main_logger.info("config.ini 생성 완료.")
    
    if_error = False
    config.read('config.ini')
    result = dict()
    try:
        if config["DEFAULT"]['TOKEN']:
            result['TOKEN'] = config["DEFAULT"]['TOKEN']
        else:
            Main_logger.error("type:01 config.ini의 token값이 없습니다.")
            if_error = True
    except:
        Main_logger.error("type:01 config.ini의 token값이 없습니다.")
        config['DEFAULT']['TOKEN'] = ''
        if_error = True
    
    try:
        if config["DEFAULT"]['Twitch_Client_ID']:
            result['Twitch_Client_ID'] = config["DEFAULT"]['Twitch_Client_ID']
        else:
            Main_logger.error("type:02 config.ini의 Twitch_Client_ID값이 없습니다.")
            if_error = True
    except:
        Main_logger.error("type:02 config.ini의 Twitch_Client_ID값이 없습니다.")
        config['DEFAULT']['Twitch_Client_ID'] = ''
        if_error = True
        
    try:
        if config["DEFAULT"]['Twitch_Client_Secret']:
            result['Twitch_Client_Secret'] = config["DEFAULT"]['Twitch_Client_Secret']
        else:
            Main_logger.error("type:03 config.ini의 Twitch_Client_Secret값이 없습니다.")
            if_error = True
    except:
        Main_logger.error("type:03 config.ini의 Twitch_Client_Secret값이 없습니다.")
        config['DEFAULT']['Twitch_Client_Secret'] = ''
        if_error = True
    
    if if_error:
        Main_logger.error("컨피그 에러 발생! 3초 뒤 자동으로 종료됩니다.")
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        time.sleep(3)
        sys.exit()
    else:
        return result
        
class DB():
    def __init__(self, table:str, field_names:list):
        """DB관리 클래스

        Args:
            table (str): table의 이름
            field_names (list): 필드들의 이름을 가진 리스트
        """
        self.table = table
        self.field_names = field_names
        
    async def db_open(self):
        """DB를 열고 conn과 커서를 리턴
        """
        if not os.path.isdir("DB"):
            os.makedirs("DB")
        conn = sqlite3.connect("DB\\DB.db", isolation_level=None)
        cursor = conn.cursor()
        fields = ""
        for field_name in self.field_names:
            fields += f", {field_name} text not null"
        fields = fields[1:]
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table} ({fields})""")
        return conn, cursor
    
    async def list_none(self, data:list):
        T = tuple()
        for i in data:
            if i:
                T += (i)
            else:
                T += tuple()
        return T
    
    async def find_all(self, filter:list , conn=None, cursor=None):
        """DB에서 필터와 같은 값을 가진 데이터를 리스트의 형태로 반환

        Args:
            filter (_list_): 찾을 데이터의 필터 ['찾을 a값','찾을 b값', (조건없을시 None) , ...]의 형식

        Returns:
            _list_: 찾은 데이터를 반환
        """
        open_check = True
        if not conn or not cursor:
            open_check = False
            conn, cursor = await self.db_open()
        text = f'SELECT * FROM {self.table} WHERE'
        prefix = ""
        convert_filter = list()
        count = 0
        for num in range(len(self.field_names)):
            if count > 0:
                prefix = " AND"
            if filter[num] != None:
                text += prefix + f" {self.field_names[num]}=?"
                convert_filter.append(filter[num])
                count += 1
        cursor.execute(text, convert_filter)
        result = cursor.fetchall()
        if not open_check:
            await self.db_close(conn)
        return result
    
    async def find(self, filter:list , conn=None, cursor=None):
        """DB에서 필터와 같은 값을 가진 데이터를 리스트의 형태로 반환

        Args:
            filter (_list_): 찾을 데이터의 필터 ['찾을 a값','찾을 b값', (조건없을시 None) , ...]의 형식

        Returns:
            _list_: 찾은 데이터를 반환
        """
        open_check = True
        if not conn or not cursor:
            opne_check = False
            conn, cursor = await self.db_open()
        text = f'SELECT * FROM {self.table} WHERE'
        prefix = ""
        convert_filter = list()
        count = 0
        for num in range(len(self.field_names)):
            if count > 0:
                prefix = " AND"
            if filter[num] != None:
                text += prefix + f" {self.field_names[num]}=?"
                convert_filter.append(filter[num])
                count += 1
        cursor.execute(text, convert_filter)
        result = cursor.fetchone()
        if not open_check:
            await self.db_close(conn)
        return result
    
    async def add(self, data):
        """DB에 중복되는 데이터가 없다면 추가

        Args:
            data (_list_): 추가하려는 데이터의 리스트 [1, 2, 3, ..]의 형식

        Returns:
            _bool_: 작업의 성공 여부
        """
        conn, cursor = await self.db_open()
        value = await self.find(data, conn=conn, cursor=cursor)
        if not value:
            text = f"INSERT INTO {self.table} "
            fields = ""
            for field in self.field_names:
                fields += f"{field}, "
            fields = fields[:-2]
            values = ""
            for i in self.field_names:
                values += "?,"
            values = values[:-1]
            text += f"({fields}) VALUES({values})"
            cursor.execute(text, tuple(data))
        await self.db_close(conn)
        
        if not value:
            return True
        else:
            return False
        
    async def remove(self, data):
        """DB에 데이터가 존재한다면 제거

        Args:
            data (_str_): 제거할 데이터

        Returns:
            _bool_: 작업의 성공 여부
        """
        conn, cursor = await self.db_open()
        value = await self.find(data, conn=conn, cursor=cursor)
        if value:
            text = f'DELETE FROM {self.table} WHERE'
            prefix = ""
            convert_filter = list()
            count = 0
            for num in range(len(self.field_names)):
                if count > 0:
                    prefix = " AND"
                if data[num] != None:
                    text += prefix + f" {self.field_names[num]}=?"
                    convert_filter.append(data[num])
                    count += 1
            cursor.execute(text, convert_filter)
        await self.db_close(conn)
        
        if value:
            return True
        else:
            return False
        
    async def update(self, find_data:list, data, num):
        """DB의 데이터를 수정하는 함수

        Args:
            find_data (list): 수정하려는 행의 필터. [1, 2, ...] 의 형태. 단 바꾸려는 열의 값은 None이어야만한다
            data (_type_): 변경하려는 값
            num (_type_): 변경하려는 값의 열번호. 주의 : 0부터 카운트

        Returns:
            _bool_: 작업 성공 여부
        """
        conn, cursor = await self.db_open()
        value = await self.find(find_data, conn=conn, cursor=cursor)
        if value:
            text = 'UPDATE {0} SET {1}=? WHERE'.format(self.table, self.field_names[num])
            prefix = ""
            convert_filter = [data]
            count = 0
            for num in range(len(self.field_names)):
                if count > 0:
                    prefix = " AND"
                if find_data[num] != None:
                    text += prefix + f" {self.field_names[num]}=?"
                    convert_filter.append(find_data[num])
                    count += 1
            cursor.execute(text, tuple(convert_filter))
            
        if value:
            return True
        else:
            return False
            
        
    async def get_all(self):
        """DB의 데이터를 전부 가져온다

        Returns:
            _list_: DB의 데이터를 list형태로 반환
        """
        conn, cursor = await self.db_open()
        cursor.execute(f"SELECT * FROM {self.table}")
        result = cursor.fetchall()
        await self.db_close(conn)
        
        return result
    
    async def db_close(self, conn): #DB 쓰고 난 뒤 필수
        """사용된 DB를 처리하는 함수
        db_open과 함께 필수적으로 사용된다

        Args:
            conn : 닫으려는 DB의 conn
        """
        conn.close()
        
        
class simple_embed:
    def __init__(self, title = "", text = "", thumbnail = None, color = 0xFFFFFF, footer = "", ):
        """EMBED를 생성

        Args:
            title (str, optional): 제목. Defaults to "".
            text (str, optional): 설명. Defaults to "".
            thumbnail (_url_, optional): 썸네일. Defaults to None.
            color (optional): 좌측 바 색상. Defaults to 0xFFFFFF.
            footer (str, optional): 하단 footer. Defaults to "".
        """
        self.embed = discord.Embed(title = title, description = text, color = color)
        if thumbnail:
            self.embed.set_thumbnail(url=thumbnail)
        if footer:
            self.embed.set_footer(text=footer)
            
    def add_field(self, name, value, inline = False):
        """embed에 필드를 추가

        Args:
            name (_str_): 제목
            value (_str_): 설명
            inline (bool, optional): 줄바꿈 여부. Defaults to False.
        """
        self.embed.add_field(name = name, value = value, inline = inline)
        
    # async def add_field_list(self, texts, inline = False):
    #     for dic in texts:
    #         await self.add_field(dic['name'], dic['text'],inline=inline)
            
    def get_embed(self):
        return self.embed
        
class channel_embed(simple_embed):
    def __init__(self, data):
        """알림 채널 출력용

        Args:
            data (_list_): DB에서 추출한 데이터 [튜플, 튜플, ...] 의 형태
        """
        description = ""
        i = 1
        for value in data:
            channel = bot.get_channel(int(value[2]))
            description += f"{i}. " + channel.mention + "\n"
            i += 1
            
        super().__init__("이 서버의 알림 채널들", description)

class twitch_api:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.get_token()
    
    def get_token(self):
        """트위치 api 토큰을 받아오는 함수
        """
        oauth_key = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={self.client_id}&client_secret={self.client_secret}&grant_type=client_credentials")
        self.key_json = oauth_key.json()
        self.access_token = self.key_json['access_token']
        # self.token_type = self.key_json['token_type']
        self.authorization = "Bearer " + self.access_token
        self.headers = {'client-id':self.client_id,'Authorization':self.authorization}
        
        Main_logger.info(f"twitch api token : {self.access_token}")
        
    async def get_user(self, twitch_user_name):
        """트위치 api에게 유저데이터를 요청

        Args:
            twitch_user_name (_str_): 요청하려는 유저의 이름

        Returns:
            _dic_: api의 json형식 응답을 dic으로 변환해서 리턴
        """
        response_channel = requests.get(f"https://api.twitch.tv/helix/users?login={twitch_user_name}",headers=self.headers)
        json = response_channel.json()
        return json
    
    async def get_user_by_id(self, user_id):
        """트위치 api에게 유저데이터를 요청

        Args:
            twitch_user_name (_str_): 요청하려는 유저의 ID

        Returns:
            _dic_: api의 json형식 응답을 dic으로 변환해서 리턴
        """
        response_channel = requests.get(f"https://api.twitch.tv/helix/users?id={user_id}",headers=self.headers)
        json = response_channel.json()
        return json
        
    async def get_broadcast_info(self, twitch_user_name):
        response_channel = requests.get(f"https://api.twitch.tv/helix/streams?user_login={twitch_user_name}",headers=self.headers)
        json = response_channel.json()
        return json
    
    async def get_broadcast_info_by_id(self, user_id):
        response_channel = requests.get(f"https://api.twitch.tv/helix/streams?user_id={user_id}",headers=self.headers)
        json = response_channel.json()
        return json
        
    
            
#서버 리스트
# server_list = [348474574666465284, 979042884219174923]
server_list = [979042884219174923]

#최초 설정
Main_logger = SetLogger("main") #메인 로거 설정
Config = ReadConfig() #컨피그 불러오기
db_alarm = DB("alarm_channel", ["guild", "channel"])
db_twitch = DB("twitch_channel", ["guild", "user_id"])
db_broadcast = DB("broadcast", ["user_id", "on_air"])
t_api = twitch_api(Config['Twitch_Client_ID'], Config['Twitch_Client_Secret'])

#봇
# intents = discord.Intents.default()
# intents.members = True
# intents.guilds = True
# bot = discord.Bot(intents=intents)
bot = discord.Bot()

async def if_admin(user):
    """이 유저가 관리자 권한을 갖고있는지 검사

    Args:
        user : 검사할 유저의 유저데이터

    Returns:
        _bool_: 관리자 여부
    """
    result = False
    for role in user.roles:
        if role.permissions.administrator == True:
            result = True
    return result

#명령어 호출 로그 기록
async def command_use(ctx, command_name):
    """명령어를 사용했다는 로그를 기록

    Args:
        ctx : 메시지를 보낼 ctx
        command_name (_str_): 사용한 명령어의 이름
    """
    Main_logger.info(f"{ctx.user} use to /{command_name}")
    
async def command_try(ctx, command_name):
    """명령어를 사용을 시도했다는 로그를 기록
    권한 부족의 경우 사용

    Args:
        ctx : 메시지를 보낼 ctx
        command_name (_str_): 시도한 명령어의 이름
    """
    Main_logger.info(f"{ctx.user} try to /{command_name}")
    
async def admin_command(ctx):
    """관리자 명령어 권한부족 출력용

    Args:
        ctx : 메시지를 출력할 ctx

    Returns:
        _bool_: 명령어 사용자의 관리자 여부
    """
    if await if_admin(ctx.user):
        return True
    else:
        embed = discord.Embed(title="오류!", description="관리자 권한이 없으면 사용할 수 없어요!", color=0xFF0000)
        await ctx.respond(embed=embed, ephemeral=True)
        await command_try(ctx, sys._getframe().f_code.co_name)
        return False
    
async def test_DB():
    """twitch_channel table의 정보를 broadcast table로 변환하는 함수
    """
    data = await db_twitch.get_all()
    channels = list()
    for i in data:
        if not i[1] in channels:
            channels.append(i[1])
    
    for i in channels:
        result = await db_broadcast.find([i ,None])
        if not result:
            await db_broadcast.add([i, False])

async def get_live_loop():
    """2분마다 방송정보를 불러오는 함수
    """
    while True:
        tm = time.localtime()
        if (tm.tm_sec % 10) == 0:
            await test_DB()
            Main_logger.debug("get_live_loop() started")
            
            data = await db_broadcast.get_all()
            for i in data:
                guild_ids = await db_twitch.find_all([None, i[0]])
                if guild_ids:
                    json = await t_api.get_broadcast_info_by_id(i[0])
                    if json['data']:
                        if await db_broadcast.find([i[0], 0]):
                            await db_broadcast.update([i[0], None], True, 1)
                            Main_logger.info('id:{0} is OnAir'.format(i[0]))
                            
                            for guild_id in guild_ids:
                                channel_ids = await db_alarm.find_all([guild_id[0], None])
                                for channel_id in channel_ids:
                                    await bot.get_channel(int(channel_id[2])).send("id:{0}_test".format(i[0]))
                            
                    else:
                        await db_broadcast.update([i[0], None], False, 1)
                else:
                    await db_broadcast.remove([i[0],None])
                            
                
            
        await asyncio.sleep(1)
        

@bot.event
async def on_ready():
    Main_logger.info("Logged on as {0}".format(bot.user))
    await test_DB()
    
    GLL = asyncio.create_task(get_live_loop())
    # await GLL
    
@bot.slash_command(guild_ids = server_list, description="봇의 응답속도 체크")
async def ping(ctx):
    embed = discord.Embed(title="pong!", description=f"Delay: {bot.latency} seconds", color=0xFFFFFF)
    await ctx.respond(embed=embed, ephemeral=True)
    await command_use(ctx, sys._getframe().f_code.co_name)

# --- 알림 채널 관리 커맨드
@bot.slash_command(guild_ids = server_list, description="알림이 올라올 채널을 지정합니다.")
@option("채널", description="알림이 올라올 채널을 지정합니다.",)
async def channel_add(ctx: discord.ApplicationContext,
                          channel : discord.TextChannel,
                          ):
    if await admin_command(ctx):
        if await db_alarm.add([ctx.guild.id, channel.id]):
            embed = discord.Embed(title="설정 완료", description= f"{channel.mention} 채널이 성공적으로 지정되었습니다.", color=0x00FF00)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="오류!", description="이미 추가된 채널입니다.", color=0xFF0000)
            await ctx.respond(embed=embed)
        await command_use(ctx, sys._getframe().f_code.co_name)
        
@bot.slash_command(guild_ids = server_list, description="이 서버에서 알림이 올라오는 채널들의 목록을 출력합니다.")
async def channel_list(ctx):
    if await admin_command(ctx):
        channel_list = await db_alarm.find_all([ctx.guild.id, None])
        embed = channel_embed(channel_list)
        await ctx.respond(embed=embed.get_embed())
        await command_use(ctx, sys._getframe().f_code.co_name)

@bot.slash_command(guild_ids = server_list, description="알림이 올라올 채널을 취소합니다.")
@option("채널", description="취소할 채널을 지정합니다.",)
async def channel_remove(ctx: discord.ApplicationContext,
                       channel : discord.TextChannel,
                       ):
    if await admin_command(ctx):
        if await db_alarm.remove([ctx.guild.id, channel.id]):
            embed = discord.Embed(title="설정 완료", description= f"{channel.mention} 채널이 성공적으로 취소되었습니다.", color=0x00FF00)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="오류!", description="등록되지 않은 채널입니다.", color=0xFF0000)
            await ctx.respond(embed=embed)
        await command_use(ctx, sys._getframe().f_code.co_name)
        
@bot.slash_command(guild_ids = server_list, description="알림을 등록할 트위치 주소를 추가합니다.")
@option("url", description="추가할 채널의 트위치 주소",)
async def twitch_add(ctx: discord.ApplicationContext,
                     url: str
                     ):
    if await admin_command(ctx):
        if re.compile('https://www.twitch.tv/.*').match(url):
            embed = discord.Embed(title="불러오는중...", description="채널의 정보를 불러오는 중입니다.\n잠시만 기다려주세요.", color=0xFFFFFF)
            loding_message = await ctx.respond(embed=embed)
            
            user_name = url.split('https://www.twitch.tv/')[1]
            json = await t_api.get_user(user_name)
            if json['data']:
                user_data = json['data'][0]
                
                await loding_message.delete_original_message()         
                embed = discord.Embed(title=user_data['display_name'], description=user_data['description'], color=0xFFFFFF)
                embed.set_thumbnail(url=user_data['profile_image_url'])
                embed.set_footer(text="추가하려는 채널이 이 채널인가요?")
                
                class Button(discord.ui.View):
                    @discord.ui.button(label="네", style=discord.ButtonStyle.primary)
                    async def yes(self, button: discord.ui.button, interaction: discord.Interaction):
                        if await db_twitch.add([ctx.guild.id, user_data['id']]):
                            embed = discord.Embed(title="설정 완료", description= "채널이 성공적으로 추가되었습니다.", color=0x00FF00)
                            await ctx.respond(embed=embed)
                        else:
                            embed = discord.Embed(title="오류!", description="이미 추가된 채널입니다.", color=0xFF0000)
                            await ctx.respond(embed=embed)
                        self.stop()
                        return
                    
                    @discord.ui.button(label="아니오", style=discord.ButtonStyle.red)
                    async def no(self, button: discord.ui.button, interaction: discord.Interaction):
                        embed = discord.Embed(title="취소", description= "채널 등록이 취소되었습니다.", color=0xFFFFFF)
                        await ctx.respond(embed=embed)
                        self.stop()
                        return
                
                view = Button()
                info_message = await ctx.respond(embed=embed, view=view)
                if await view.wait():
                    embed = discord.Embed(title="취소", description= "시간초과로 입력이 취소되었습니다.", color=0xFFFFFF)
                    await ctx.respond(embed=embed)
                await info_message.delete()
            else:
                embed = discord.Embed(title="오류!", description="올바르지 않은 트위치 주소입니다.", color=0xFF0000)
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="오류!", description="올바르지 않은 트위치 주소입니다.", color=0xFF0000)
            await ctx.respond(embed=embed)
            
        await command_use(ctx, sys._getframe().f_code.co_name)
        
@bot.slash_command(guild_ids = server_list, description="알림등록된 방송들의 리스트를 출력합니다.")
async def twitch_list(ctx):
    if await admin_command(ctx):
        embed = discord.Embed(title="이 서버에 알림등록된 방송들", color=0xFFFFFF)
        channel_list = await db_twitch.find_all([ctx.guild.id, None])
        i = 1
        for user_id in channel_list:
            json = await t_api.get_user_by_id(user_id[1])
            json = json['data'][0]
            embed.add_field(name="{0}. {1}".format(i, json['display_name']),
                            value="{0}\n link : https://www.twitch.tv/{1}".format(json['description'],json['login']), inline=False)
            i += 1
        
        await ctx.respond(embed=embed)
        await command_use(ctx, sys._getframe().f_code.co_name)

@bot.slash_command(guild_ids = server_list, description="알림등록된 트위치 채널을 제거합니다.")
@option("url", description="제거할 채널의 트위치 주소",)
async def twitch_remove(ctx:discord.ApplicationContext,
                        url:str):
    if await admin_command(ctx):
        if re.compile('https://www.twitch.tv/.*').match(url):
            embed = discord.Embed(title="불러오는중...", description="채널의 정보를 불러오는 중입니다.\n잠시만 기다려주세요.", color=0xFFFFFF)
            loding_message = await ctx.respond(embed=embed)
            
            user_name = url.split('https://www.twitch.tv/')[1]
            json = await t_api.get_user(user_name)
            if json['data']:
                user_data = json['data'][0]
                
                await loding_message.delete_original_message()         
                embed = discord.Embed(title=user_data['display_name'], description=user_data['description'], color=0xFFFFFF)
                embed.set_thumbnail(url=user_data['profile_image_url'])
                embed.set_footer(text="정말로 이 채널을 제거할까요?")
                
                class Button(discord.ui.View):
                    @discord.ui.button(label="네", style=discord.ButtonStyle.red)
                    async def yes(self, button: discord.ui.button, interaction: discord.Interaction):
                        if await db_twitch.remove([ctx.guild.id, user_data['id']]):
                            embed = discord.Embed(title="설정 완료", description= "채널이 성공적으로 제거되었습니다.", color=0x00FF00)
                            await ctx.respond(embed=embed)
                        else:
                            embed = discord.Embed(title="오류!", description="존재하지 않는 채널입니다.", color=0xFF0000)
                            await ctx.respond(embed=embed)
                        self.stop()
                        return
                    
                    @discord.ui.button(label="아니오", style=discord.ButtonStyle.gray)
                    async def no(self, button: discord.ui.button, interaction: discord.Interaction):
                        embed = discord.Embed(title="취소", description= "작업을 취소하였습니다.", color=0xFFFFFF)
                        await ctx.respond(embed=embed)
                        self.stop()
                        return
                
                view = Button()
                info_message = await ctx.respond(embed=embed, view=view)
                if await view.wait():
                    embed = discord.Embed(title="취소", description= "시간초과로 입력이 취소되었습니다.", color=0xFFFFFF)
                    await ctx.respond(embed=embed)
                await info_message.delete()
            else:
                embed = discord.Embed(title="오류!", description="올바르지 않은 트위치 주소입니다.", color=0xFF0000)
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="오류!", description="올바르지 않은 트위치 주소입니다.", color=0xFF0000)
            await ctx.respond(embed=embed)
        
        await command_use(ctx, sys._getframe().f_code.co_name)

@bot.slash_command(guild_ids = server_list, description="트위치 채널의 방송정보를 가져옵니다.")
@option("url", description="채널의 트위치 주소",)
async def twitch_info(ctx:discord.ApplicationContext,
                        url:str):
    if await admin_command(ctx):
        if re.compile('https://www.twitch.tv/.*').match(url):
            embed = discord.Embed(title="불러오는중...", description="채널의 정보를 불러오는 중입니다.\n잠시만 기다려주세요.", color=0xFFFFFF)
            loding_message = await ctx.respond(embed=embed)
            
            user_name = url.split('https://www.twitch.tv/')[1]
            json = await t_api.get_user(user_name)
            if json['data']:
                user_data = json['data'][0]
                json = await t_api.get_broadcast_info(user_name)
                
                await loding_message.delete_original_message()
                if json['data']:
                    boradcast_data = json['data'][0]
                    
                    embed = discord.Embed(title="{0}님의 방송정보 입니다.".format(boradcast_data['user_name']), description=boradcast_data['title'], color=0xFFFFFF)
                    embed.add_field(name="지금 {0}님은".format(boradcast_data['user_name']), value="{0}을 플레이 중이에요!".format(boradcast_data['game_name']))
                    embed.set_image(url=boradcast_data['thumbnail_url'].format(width=1920, height=1080))
                    embed.set_thumbnail(url=user_data['profile_image_url'])
                else:     
                    embed = discord.Embed(title="이런!" ,description="{0}님은 현재 방송중이 아닙니다.".format(user_data['display_name']), color=0xFF0000)
                    embed.set_thumbnail(url=user_data['profile_image_url'])
                
                await ctx.respond(embed=embed)
            else:
                embed = discord.Embed(title="오류!", description="올바르지 않은 트위치 주소입니다.", color=0xFF0000)
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="오류!", description="올바르지 않은 트위치 주소입니다.", color=0xFF0000)
            await ctx.respond(embed=embed)
        
        await command_use(ctx, sys._getframe().f_code.co_name)
        
@bot.slash_command(guild_ids = server_list, description="test")
async def test(ctx):
    data = await db_broadcast.get_all()
    for i in data:
        guild_ids = await db_twitch.find_all([None, i[0]])
        if guild_ids:
            for guild_id in guild_ids:
                channel_ids = await db_alarm.find_all([guild_id[0], None])
                for channel_id in channel_ids:
                    Main_logger.info('id : {0} - start'.format(i[0]))
                    json = await t_api.get_user_by_id(i[0])
                    Main_logger.info('id : {0} - end'.format(i[0]))
                    # - 해결해야할 문제 1:
                    # 같은 트위치 id의 정보를 여러번 불러오며
                    # 트위치 API의 반응속도가 많이 느리므로
                    # 트위치 API를 로드하는 비동기 함수를 짜야할 필요성이 있음.
                    if json['data']:
                        user_data = json['data'][0]
                        embed = discord.Embed(title="{0}님의 방송정보 입니다.".format(user_data['display_name']), color=0xFFFFFF)
                        
                        channel = bot.get_channel(int(channel_id[2]))
                        if channel:
                            await channel.send(embed=embed)
                        
        else:
            await db_broadcast.remove([i[0],None])

bot.run(Config['TOKEN'])