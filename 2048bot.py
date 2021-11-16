import logging
import random
import copy
import math
import dico
import traceback
import sys
import ssl
from dico_interaction import InteractionClient, InteractionContext, InteractionWebserver


class UndefinedDirectionError(Exception):
    def __init__(self):
        super().__init__('UndefinedDirectionError')


class FinishedGameError(Exception):
    def __init__(self):
        super().__init__('The game has already over.')


class Class2048:
    def __init__(self, msg_id, author_id):
        self.sq = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.score = 0
        self.over = False
        self.__random_spawn()
        self.__random_spawn()

        self.bot_msg_id = msg_id
        self.author_id = author_id

    def __is_game_over(self):
        cnt = 0
        sw = [0, 1, -1]
        ne = [0, 1, -1]

        for i in range(0, 4):
            for j in range(0, 4):
                tmp_cnt, tmp_chk = 0, 0
                for x in range(0, 3):
                    for y in range(0, 3):
                        if -1 < sw[x] + i < 4 and -1 < ne[y] + j < 4 and abs(sw[x]) + abs(ne[y]) == 1:
                            tmp_cnt += 1
                            if self.sq[sw[x] + i][ne[y] + j] != self.sq[i][j] and self.sq[sw[x] + i][ne[y] + j] != 0:
                                tmp_chk += 1
                if tmp_chk == tmp_cnt:
                    cnt += 1
        if cnt == 16:
            return True
        return False

    def __random_spawn(self):
        while True:
            a, b = random.randrange(0, 4), random.randrange(0, 4)
            spawn = [2, 2, 2, 2, 2, 2, 2, 2, 2, 4]
            if self.sq[a][b] == 0:
                self.sq[a][b] = random.choice(spawn)
                break

    def __sub_merge_up(self):
        for i in range(0, 4):
            line = []
            for j in range(0, 4):
                line.append(self.sq[j][i])
            cnt = 0
            for x in range(0, 4):
                if line[x] != 0:
                    line[cnt] = line[x]
                    if cnt != x:
                        line[x] = 0
                    cnt += 1
            for x in range(0, 3):
                if line[x] == line[x + 1]:
                    line[x], line[x + 1] = line[x] + line[x + 1], 0
                    self.score += line[x]
            cnt = 0
            for x in range(0, 4):
                if line[x] != 0:
                    line[cnt] = line[x]
                    if cnt != x:
                        line[x] = 0
                    cnt += 1
            for j in range(0, 4):
                self.sq[j][i] = line[j]

    def __sub_merge_down(self):
        for i in range(0, 4):
            line = []
            for j in range(0, 4):
                line.append(self.sq[j][i])
            cnt = 3
            for x in range(3, -1, -1):
                if line[x] != 0:
                    line[cnt] = line[x]
                    if cnt != x:
                        line[x] = 0
                    cnt -= 1
            for x in range(3, 0, -1):
                if line[x] == line[x - 1]:
                    line[x], line[x - 1] = line[x] + line[x - 1], 0
                    self.score += line[x]
            cnt = 3
            for x in range(3, -1, -1):
                if line[x] != 0:
                    line[cnt] = line[x]
                    if cnt != x:
                        line[x] = 0
                    cnt -= 1
            for j in range(0, 4):
                self.sq[j][i] = line[j]

    def __sub_merge_left(self):
        for i in range(0, 4):
            line = self.sq[i]
            cnt = 0
            for x in range(0, 4):
                if line[x] != 0:
                    line[cnt] = line[x]
                    if cnt != x:
                        line[x] = 0
                    cnt += 1
            for x in range(0, 3):
                if line[x] == line[x + 1]:
                    line[x], line[x + 1] = line[x] + line[x + 1], 0
                    self.score += line[x]
            cnt = 0
            for x in range(0, 4):
                if line[x] != 0:
                    line[cnt] = line[x]
                    if cnt != x:
                        line[x] = 0
                    cnt += 1
            self.sq[i] = line

    def __sub_merge_right(self):
        for i in range(0, 4):
            line = self.sq[i]
            cnt = 3
            for x in range(3, -1, -1):
                if line[x] != 0:
                    line[cnt] = line[x]
                    if cnt != x:
                        line[x] = 0
                    cnt -= 1
            for x in range(3, 0, -1):
                if line[x] == line[x - 1]:
                    line[x], line[x - 1] = line[x] + line[x - 1], 0
                    self.score += line[x]
            cnt = 3
            for x in range(3, -1, -1):
                if line[x] != 0:
                    line[cnt] = line[x]
                    if cnt != x:
                        line[x] = 0
                    cnt -= 1
            self.sq[i] = line

    def merge(self, direction):
        if self.over:
            raise FinishedGameError
        if direction == 'up':
            prv = copy.deepcopy(self.sq)
            self.__sub_merge_up()
            if not prv == self.sq:
                self.__random_spawn()
        elif direction == 'down':
            prv = copy.deepcopy(self.sq)
            self.__sub_merge_down()
            if not prv == self.sq:
                self.__random_spawn()
        elif direction == 'left':
            prv = copy.deepcopy(self.sq)
            self.__sub_merge_left()
            if not prv == self.sq:
                self.__random_spawn()
        elif direction == 'right':
            prv = copy.deepcopy(self.sq)
            self.__sub_merge_right()
            if not prv == self.sq:
                self.__random_spawn()
        else:
            raise UndefinedDirectionError

        if self.__is_game_over():
            self.over = True
            return -1

        return 0


# Bot Area

with open('token.txt', 'r') as f:
    token = f.read()

with open('public_key.txt', 'r') as f:
    public_key = f.read()

logger = logging.getLogger('dicobot')
logging.basicConfig(level=logging.DEBUG)  # DEBUG/INFO/WARNING/ERROR/CRITICAL
handler = logging.FileHandler(filename=f'dicobot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

interaction = InteractionClient(respond_via_endpoint=False)
server = InteractionWebserver(token, public_key, interaction, application_id=789491883755831318)


def create_msg(m):
    buffer = ""
    emojis = ['',
              '<:2:904349077746118706>',
              '<:4:904349077750292520>',
              '<:8:904349078345895946>',
              '<:16:904349077737734144>',
              '<:32:904349077674786816>',
              '<:64:904349077716738068>',
              '<:128:904349077960028191>',
              '<:256:904349077813219328>',
              '<:512:904349078421377044>',
              '<:1024:904349077788049428>',
              '<:2048:904349077062447114>']
    for i in range(0, 4):
        for j in range(0, 4):
            if m[i][j] == 0:
                buffer += '⬛'
            else:
                buffer += emojis[int(math.log2(m[i][j]))]
        buffer += '\n'
    return buffer


emoji_left = "<left:909659546081959956>"
emoji_up = "<up:909659546304249867>"
emoji_down = "<down:909659546182631476>"
emoji_right = "<right:909659546295869450>"
emoji_cancel = "✖"


def create_buttons(message_id, disabled=False):
    left_button = dico.Button(style=dico.ButtonStyles.PRIMARY, emoji=emoji_left, custom_id=f"left{message_id}",
                              disabled=disabled)
    up_button = dico.Button(style=dico.ButtonStyles.PRIMARY, emoji=emoji_up, custom_id=f"up{message_id}",
                            disabled=disabled)
    down_button = dico.Button(style=dico.ButtonStyles.PRIMARY, emoji=emoji_down, custom_id=f"down{message_id}",
                              disabled=disabled)
    right_button = dico.Button(style=dico.ButtonStyles.PRIMARY, emoji=emoji_right, custom_id=f"right{message_id}",
                               disabled=disabled)
    cancel_button = dico.Button(style=dico.ButtonStyles.DANGER, emoji=emoji_cancel, custom_id=f"cancel{message_id}",
                                disabled=disabled)
    row = dico.ActionRow(left_button, up_button, down_button, right_button, cancel_button)
    return row


games = {}


async def game_over(inter, game):
    await inter.send(create_msg(game.sq) + '\nGame Over! Your final score is: ' + str(game.score),
                     components=[create_buttons(inter.message.id, disabled=True)], update_message=True)
    del games[int(inter.message.id)]


async def on_interaction_error(_, inter: InteractionContext, ex: Exception):
    if isinstance(ex, KeyError):
        await inter.send("Invalid game session. Start new game.", ephemeral=True)
    else:
        tb = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        title = f"Exception while executing command {inter.data.name}" if inter.type.application_command else \
            f"Exception while executing callback of {inter.data.custom_id}"
        print(f"{title}:\n{tb}", file=sys.stderr)


interaction.execute_error_handler = on_interaction_error


@interaction.component_callback("cancel")
async def cancel_callback(ctx: InteractionContext):
    game = games[int(ctx.message.id)]
    if ctx.author.id != game.author_id:
        return await ctx.send("This is not your session!", ephemeral=True)
    game = games.pop(int(ctx.message.id))
    await ctx.send(create_msg(game.sq) + '\nThis game is cancelled. Score: ' + str(game.score),
                   update_message=True, components=[create_buttons(ctx.message.id, disabled=True)])


@interaction.component_callback("left")
async def left_callback(ctx: InteractionContext):
    if not ctx.data.component_type.button:
        return
    game = games[int(ctx.message.id)]
    if ctx.author.id != game.author_id:
        return await ctx.send("This is not your session!", ephemeral=True)
    res = game.merge('left')
    if res == -1:
        await game_over(ctx, game)
    else:
        await ctx.send(create_msg(game.sq), update_message=True)


@interaction.component_callback("up")
async def up_callback(ctx: InteractionContext):
    if not ctx.data.component_type.button:
        return
    game = games[int(ctx.message.id)]
    if ctx.author.id != game.author_id:
        return await ctx.send("This is not your session!", ephemeral=True)
    res = game.merge('up')
    if res == -1:
        await game_over(ctx, game)
    else:
        await ctx.send(create_msg(game.sq), update_message=True)


@interaction.component_callback("down")
async def down_callback(ctx: InteractionContext):
    if not ctx.data.component_type.button:
        return
    game = games[int(ctx.message.id)]
    if ctx.author.id != game.author_id:
        return await ctx.send("This is not your session!", ephemeral=True)
    res = game.merge('down')
    if res == -1:
        await game_over(ctx, game)
    else:
        await ctx.send(create_msg(game.sq), update_message=True)


@interaction.component_callback("right")
async def right_callback(ctx: InteractionContext):
    if not ctx.data.component_type.button:
        return
    game = games[int(ctx.message.id)]
    if ctx.author.id != game.author_id:
        return await ctx.send("This is not your session!", ephemeral=True)
    res = game.merge('right')
    if res == -1:
        await game_over(ctx, game)
    else:
        await ctx.send(create_msg(game.sq), update_message=True)


@interaction.slash(name="start", description="Starts a new game.")
async def start(ctx: InteractionContext):
    await ctx.defer()
    msg = await ctx.request_original_response()
    games[int(msg)] = Class2048(int(msg), int(ctx.author))
    await ctx.send(create_msg(games[int(msg)].sq))
    await ctx.edit_original_response(content=create_msg(games[int(msg)].sq), components=[create_buttons(int(msg))])


ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain("cert.pem", "privkey.pem")
server.run(host='0.0.0.0', port=1337, ssl_context=ssl_context)
