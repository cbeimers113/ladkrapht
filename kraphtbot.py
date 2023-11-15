import os
import discord
import time
from discord.ext import tasks
from dotenv import load_dotenv
from mcstatus import JavaServer

intents = discord.Intents.default()
intents.message_content = True


class Client(discord.Client):


    def __init__(self):
        """Instantiate the bot client."""
        super().__init__(intents=intents)
        load_dotenv()
        self._discord_token = os.getenv("DISCORD_TOKEN")
        self._running = False
        self._empty = False
        self._first_empty_time = 0
        self._last_backup_time = time.time_ns()
        self._status_file = ".status"
        self._status = ""
        self._ip_file = ".ip"
        self._ip = ""
        self.run(self._discord_token)


    async def on_ready(self):
        self.update_status.start()


    @tasks.loop(seconds=1)
    async def update_status(self):
        """Update the status either from the status file or the server status."""
        channel = discord.utils.get(self.get_all_channels(), name="general")

        if os.path.exists(self._ip_file):
            ip = ""
            with open(self._ip_file, 'r') as f:
                ip = f.read().strip()

            if ip and ip != self._ip:
                self._ip = ip
                await channel.send(f"IP: `{self._ip}:25565`", delete_after=600)
                await channel.edit(topic=f"🌎 {self._ip}:25565")

        elif self._ip:
            await channel.edit(topic="")
            self._ip = ""

        if os.path.exists(self._status_file):
            status = ""
            with open(self._status_file, 'r') as f:
                status = f.read().strip()

            if status:
                await self.set_status(status, discord.Status.dnd)
        else:
            await self.player_monitor()

        # Perform a backup every 5 minutes
        if time.time_ns() - self._last_backup_time > 1_000_000_000 * 60 * 5:
            self.backup_server()
            self._last_backup_time = time.time_ns()


    async def set_status(self, status, online_status):
        """Update the server description and bot status."""
        if status == self._status:
            return

        # Get the status indicator associated with this online status
        indicators = {
                        discord.Status.online: "🟢",
                        discord.Status.idle: "🔴",
                        discord.Status.dnd: "🟡"
                     }
        indicator = indicators[online_status]

        # Update the bot status
        await self.change_presence(status=online_status, activity=discord.Game(f'{indicator}{status}'))
        self._status = status


    async def player_monitor(self):
        """Check for if players are offline and the server can be shut down."""
        try:
            server = JavaServer.lookup(f"{self._ip}:25565")
            status = server.status()
            players = status.players.online
            max_players = status.players.max
            await self.set_status(f'Tekxit 3.14π, {players}/{max_players}', discord.Status.online)

            if players == 0:
                if not self._empty:
                    self._first_empty_time = time.time_ns()
                self._empty = True

                # If the server has been empty for 1 x 10^9 nanoseconds/s * 60 s/m * 10 = 10 minutes
                if time.time_ns() - self._first_empty_time > 1_000_000_000 * 60 * 10:
                    self.stop_server()
            else:
                self._empty = False

        except Exception as e:
            await self.set_status(f'Server is down', discord.Status.idle)
            with open(".ex", "w") as f:
                f.write(str(e))


    async def on_message(self, message):
        """Listen for and process commands."""
        if message.content == ".start":
            await message.channel.send(f"Starting server, this will take a few minutes...", delete_after=600)
            self.start_server()
            await message.delete()

        # Don't use
        elif message.content == ".stop":
            await message.channel.send("Stopping the server...", delete_after=600)
            self.stop_server()
            await message.channel.send("Server stopped", delete_after=600)
            await message.delete()


    def start_server(self):
        """Start the Minecraft server."""
        if self.running() or self.stopping() or self.backing_up():
            return
        os.system("./deploy &")
        self._first_empty_time = time.time_ns()


    def backup_server(self):
        """Backup the Minecraft server on external storage."""
        if not self.running() or self.stopping() or self.backing_up():
            return
        os.system("./backup &")


    def stop_server(self):
        """Gracefully stop the Minecraft server."""
        if not self.running() or self.stopping() or self.backing_up():
            return
        os.system("./teardown &")


    def running(self):
        """Check if the server is runnning."""
        return os.path.exists(".running")


    def stopping(self):
        """Check if the server is stopping."""
        return os.path.exists(".stopping")


    def backing_up(self):
        """Check if the server is being backed up."""
        return os.path.exists(".backup")


def start():
    try:
        Client()
    except:
        start()


start()

