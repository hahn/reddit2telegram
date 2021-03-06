# encoding: utf-8

import logging

from pytgbot.bot import Bot
from pytgbot.exceptions import TgApiException

from utils import get_url


logger = logging.getLogger(__name__)


subreddit = 'unexpected'
t_channel = '@r_unexpected'


NSFW_emoji = u'\U0001F51E'


def send_post(submission, r2t):
    bot = r2t.telepot_bot
    bot_old = bot
    bot = Bot(bot_old._token)
    what, gif_url, ext = get_url(submission)
    if what != 'gif':
        return False

    if r2t.dup_check_and_mark(gif_url) is True:
        return False

    title = submission.title
    link = submission.shortlink

    if submission.over_18:
        url = submission.url
        text = '{emoji}NSFW\n{url}\n{title}\n\n{link}\n\nby {channel}'.format(
            emoji=NSFW_emoji, url=url, title=title, link=link, channel=t_channel
        )
        bot.send_message(t_channel, text, disable_web_page_preview=True)
        return True
    text = '{title}\n{link}\n\nby {channel}'.format(title=title, link=link, channel=t_channel)
    logger.info("{channel} Posting {gif_url}:\n{text}".format(channel=t_channel, gif_url=gif_url, text=text))
    try:
        # try sending as gif
        return send_gif(bot, t_channel, gif_url, caption=text, ext=ext)
    except Exception:
        # sending it link-only
        text = '{url}\n{title}\n\n{link}\n\nby {channel}'.format(
            url=gif_url, title=title, link=link, channel=t_channel
        )
        bot.send_message(t_channel, text, disable_web_page_preview=False)
    return True
# end def send_post


def send_gif(bot, channel, url, caption, ext):
    import pytgbot
    from magic import MagicException

    assert isinstance(bot, pytgbot.bot.Bot)
    assert isinstance(url, str)
    assert isinstance(caption, str)

    # Fo not need code below because of it should be .mp4 if possible itself.
    # if url.endswith(".gif"):
    #     url_mp4 = url[:-4] + ".mp4"
    #     try:
    #         return send_gif(bot, channel, url_mp4, caption)
    #     except:
    #         pass
    #         # end try
    # # end if

    try:
        bot.send_document(channel, document=url, caption=caption)
        return True
    except TgApiException:
        logger.warning("Gif via Telegram failed: {url}\n{caption}".format(url=url, caption=caption))
    # end try
    from pytgbot.api_types.sendable.files import InputFileFromURL, InputFileFromDisk
    try:
        bot.send_document(channel, document=InputFileFromURL(url), caption=caption)
        return True
    except (TgApiException, MagicException):
        logger.warning("Gif via InputFileFromURL failed: {url}\n{caption}".format(url=url, caption=caption))
        import os
        from utils import download_file, TELEGRAM_AUTOPLAY_LIMIT
        filename = '{channel}.{suffix}'.format(channel=channel, suffix=ext)
        if not download_file(url, filename):
            return False
        if os.path.getsize(filename) > TELEGRAM_AUTOPLAY_LIMIT:
            return False
        bot.send_document(channel, InputFileFromDisk(file_path=filename, file_name=filename, file_mime="image/gif" if url.endswith(".gif") else "video/mp4"), caption=caption)
        return True
    # end try
# end def send_gif
