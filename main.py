import discord

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="ping", description="Show Latency")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond(f"Pong! Now Latency is: {bot.latency}")

bot.run('MTIzOTAwMzE0OTQ5NTQzNTI5Ng.Ga_qc2.ExgN91es6jvn4tR6HwmCjSf5u9wf63uWx0IBjM')