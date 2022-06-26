from discord_webhook import DiscordWebhook, DiscordEmbed
from authentication.models import User
from churchaio.models import Configuration


def successful_checkout(user_id, title):
    try:
        user = User.objects.get(id=user_id)
        config = user.configuration
        webhook_url = config.webhook
    except (User.DoesNotExist, Configuration.DoesNotExist) as ex:
        msg = "user not found"
    else:
        if webhook_url is not None:
            discord_msg = "Successfully Cooked"
            webhook = DiscordWebhook(url=webhook_url)
            embed = DiscordEmbed(title=title, description=discord_msg, color='2f599b')
            # add embed object to webhook
            webhook.add_embed(embed)
            try:
                response = webhook.execute()
            except Exception:
                msg = "webhook failed"
