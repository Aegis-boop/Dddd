import os
import json
import discord
from discord import app_commands
from discord.ext import commands
import datetime
import asyncio

# ─── SECURE STORAGE ENGINE ───────────────────────────────────────────────────
DATA_FILE = "security_database.json"

def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f: 
                return json.load(f)
        except Exception: 
            pass
    return {"recent_flags": []}

def save_db(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f: 
            json.dump(data, f, indent=4)
    except Exception: 
        pass

def add_flag_log(reason):
    db = load_db()
    log_entry = f"[{datetime.datetime.utcnow().strftime('%H:%M:%S')}] {reason}"
    db["recent_flags"].append(log_entry)
    if len(db["recent_flags"]) > 10: 
        db["recent_flags"].pop(0)
    save_db(db)

# ─── CORE BOT DEFINITION ─────────────────────────────────────────────────────
class HybridSecurityBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        intents.message_content = True  # Added to clear configuration warnings
        super().__init__(command_prefix="!", intents=intents)
        self.join_tracker = []
        self.raid_mode_active = False

bot = HybridSecurityBot()

@bot.event
async def on_ready():
    print(f'🚨 Aegis Security Matrix Engaged: {bot.user.name}')
    try: 
        await bot.tree.sync()
        print("✅ Global slash commands synchronized successfully.")
    except Exception as e:
        print(f"❌ Failed to sync slash commands: {e}")

# ─── DISCORD SLASH COMMANDS ──────────────────────────────────────────────────
@bot.tree.command(name="help", description="Get information about Aegis.")
async def web_help(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🛡️ **Aegis Security Framework Mainframe**\n"
        f"Active perimeter monitoring is online. Use structural commands to manage your server sectors.\n\n"
        f"⚙️ **Available Commands:** `/kick`, `/ban`, `/timeout` \n"
        f"🔗 **Command Node Portal:** https://aegisbott.netlify.app", 
        ephemeral=True
    )

@bot.tree.command(name="kick", description="Kick a disruptive user from the server sector.")
@app_commands.checks.has_permissions(kick_members=True)
async def kick_admin(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if member.top_role >= interaction.user.top_role: 
        return await interaction.response.send_message("❌ Error: Target user has matching or higher role hierarchy clearance.", ephemeral=True)
    await member.kick(reason=reason)
    add_flag_log(f"Staff ({interaction.user.name}) kicked user: {member.name}")
    await interaction.response.send_message(f"👢 **{member.name}** has been removed from the server zone.")

@bot.tree.command(name="ban", description="Permanently blacklist a threat actor.")
@app_commands.checks.has_permissions(ban_members=True)
async def ban_admin(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if member.top_role >= interaction.user.top_role: 
        return await interaction.response.send_message("❌ Error: Target user has matching or higher role hierarchy clearance.", ephemeral=True)
    await member.ban(reason=reason)
    add_flag_log(f"Staff ({interaction.user.name}) banned user: {member.name}")
    await interaction.response.send_message(f"🔨 **{member.name}** has been blacklisted permanently.")

@bot.tree.command(name="timeout", description="Isolate a member inside communication channels.")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout_admin(interaction: discord.Interaction, member: discord.Member, minutes: int):
    if member.top_role >= interaction.user.top_role: 
        return await interaction.response.send_message("❌ Error: Target user has matching or higher role hierarchy clearance.", ephemeral=True)
    await member.timeout(datetime.timedelta(minutes=minutes))
    add_flag_log(f"Staff ({interaction.user.name}) isolated user: {member.name} for {minutes}m")
    await interaction.response.send_message(f"🤫 **{member.name}** has been placed in communication isolation for {minutes} minutes.")

# ─── AUTOMATED SHIELDS (BACKGROUND SYSTEM INTERCEPTS) ───────────────────────
@bot.event
async def on_member_join(member):
    now = datetime.datetime.utcnow()
    bot.join_tracker = [t for t in bot.join_tracker if (now - t).total_seconds() < 10]
    bot.join_tracker.append(now)
    if len(bot.join_tracker) > 5 and not bot.raid_mode_active:
        bot.raid_mode_active = True
        add_flag_log("Join Traffic Spike - Anti-Raid Perimeter Locked Down")
    if bot.raid_mode_active:
        try: 
            await member.kick(reason="Aegis Core Defense: Automated Traffic Mitigation")
        except Exception: 
            pass

@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
        if entry.user.id == bot.user.id or entry.user.id == channel.guild.owner_id: 
            return
        if isinstance(entry.user, discord.Member) and entry.user.top_role < channel.guild.me.top_role:
            try:
                roles = [r for r in entry.user.roles if r.name != "@everyone" and r < channel.guild.me.top_role]
                await entry.user.remove_roles(*roles, reason="Aegis Intercept: Revoked credentials.")
                add_flag_log(f"Blocked unauthorized structural channel wipe by {entry.user.name}")
            except Exception: 
                pass

# ─── RUN BOT ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    token = os.environ.get('TOKEN')
    if not token:
        print("❌ CRITICAL ERROR: 'TOKEN' Environment Variable is completely missing.")
    else:
        bot.run(token)
    
