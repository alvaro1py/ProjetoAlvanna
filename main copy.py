import discord
from discord.ext import commands
import youtube_dl
import asyncio
import yt_dlp



intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print("Bot inicializado com sucesso!")

@bot.command()
async def falar(ctx):
    nome = ctx.author.name
    await ctx.reply(f"Oii {nome}! Tudo bem? Qual a boa de hoje?")

@bot.command()
async def oi(ctx):
    await ctx.reply("Oi! Espero que você esteja tendo um ótimo dia! 😊")

@bot.command()
async def calculadora(ctx):
    nome = ctx.author.name
    await ctx.reply(f"Certo! Vamos calcular {nome}. Escolha a operação: +, -, *, /")
    
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content in ['+', '-', '*', '/']
    
    try:
        op_msg = await bot.wait_for("message", check=check, timeout=30.0)
        operacao = op_msg.content
    except:
        await ctx.send("Tempo esgotado! Tente novamente.")
        return
    
    await ctx.send("Digite o primeiro número:")
    
    def check_number(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.replace('.', '', 1).isdigit()
    
    try:
        num1_msg = await bot.wait_for("message", check=check_number, timeout=30.0)
        num1 = float(num1_msg.content)
    except:
        await ctx.send("Entrada inválida! Tente novamente.")
        return
    
    await ctx.send("Digite o segundo número:")
    
    try:
        num2_msg = await bot.wait_for("message", check=check_number, timeout=30.0)
        num2 = float(num2_msg.content)
    except:
        await ctx.send("Entrada inválida! Tente novamente.")
        return
    
    if operacao == '+':
        resultado = num1 + num2
    elif operacao == '-':
        resultado = num1 - num2
    elif operacao == '*':
        resultado = num1 * num2
    elif operacao == '/':
        if num2 == 0:
            await ctx.send("Erro: Divisão por zero não é permitida!")
            return
        resultado = num1 / num2
    
    await ctx.send(f"O resultado de {num1} {operacao} {num2} é: {resultado}")

@bot.command()
async def avatar(ctx, user: discord.Member = None):
    
    if user is None:
        user = ctx.author

    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url

    embed = discord.Embed(
        title=f"Avatar de {user.name}",
        color=discord.Color.blue()
    )
    embed.set_image(url=avatar_url)

    await ctx.reply(embed=embed)


# Fila de músicas
queues = {}

# Configuração do yt-dlp com pesquisa automática no YouTube
yt_dl_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch',  # Agora permite buscas no YouTube
    'noplaylist': True  # Evita que o bot tente baixar playlists inteiras
}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

# Função para tocar a próxima música
async def play_next(ctx):
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        url = queues[ctx.guild.id].pop(0)
        await play_music(ctx, url)
    else:
        await ctx.voice_client.disconnect()
        await ctx.send("Fila de músicas acabou. Saindo do canal de voz! 🎶")

# Função para tocar uma música
async def play_music(ctx, search):
    try:
        voice_channel = ctx.author.voice.channel
        if not voice_channel:
            await ctx.send("Você precisa estar em um canal de voz para pedir músicas!")
            return

        # Conecta ao canal de voz se ainda não estiver conectado
        if ctx.voice_client is None:
            await voice_channel.connect()

        # Se for um link do YouTube, usa diretamente; senão, faz uma busca automática
        info = ytdl.extract_info(search, download=False)
        if "entries" in info:
            info = info["entries"][0]  # Pega o primeiro resultado da busca

        audio_url = info['url']
        title = info['title']

        # Reproduz o áudio
        ctx.voice_client.stop()
        ctx.voice_client.play(
            discord.FFmpegPCMAudio(audio_url, executable="ffmpeg"),
            after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        )

        await ctx.send(f"🎶 Tocando agora: **{title}**")

    except yt_dlp.utils.DownloadError as e:
        if "DRM" in str(e):
            await ctx.send("🚫 Este vídeo possui **proteção DRM** e não pode ser reproduzido.")
        else:
            await ctx.send(f"❌ Erro ao tentar tocar música: {e}")

# Comando para tocar música e adicionar à fila
@bot.command()
async def play(ctx, *, search: str):
    """Toca uma música do YouTube pelo nome ou URL"""
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []

    if ctx.voice_client and ctx.voice_client.is_playing():
        queues[ctx.guild.id].append(search)
        await ctx.send(f"📌 Música adicionada à fila!")
    else:
        await play_music(ctx, search)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

@bot.command()
async def ajuda(ctx):
    comandos = {
        ".falar": "O bot cumprimenta você 👋",
        ".oi": "Receba uma saudação especial do bot 😊",
        ".calculadora": "Calculadora interativa para somar, subtrair, multiplicar ou dividir 🔢",
        ".avatar [usuário]": "Veja o avatar de um usuário específico ou o seu próprio 🖼️",
        ".ping": "Responde 'Pong!' para testar a latência do bot 🏓"
    }
    
    mensagem = "**🤖 Lista de Comandos Disponíveis:**\n\n"
    for cmd, desc in comandos.items():
        mensagem += f"🔹 `{cmd}` - {desc}\n"

    await ctx.send(mensagem)

bot.run("")