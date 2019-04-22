import asyncio
import typing
from datetime import datetime as dt

import aiohttp
import discord
from discord.ext import buttons
from discord.ext import commands

import config
from exceptions import *


class Paginator(buttons.Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class APICommands(commands.Cog):
    """Various API commands"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        asyncio.create_task(self.session.close())

    async def fetch(self, base, params=None) -> typing.Dict:
        async with self.session.get(f'https://{base}', params=params) as r:
            if r.status == 200:
                return await r.json()
            elif r.status == 400:
                raise BadRequestError
            elif r.status == 403:
                raise ForbiddenError
            elif r.status == 404:
                raise NotFoundError

    async def shorten(self, url):
        base = 'tinyurl.com/api-create.php?'
        params = {
            'url': url
        }
        async with self.session.get(f'https://{base}', params=params) as r:
            return await r.text()

    @staticmethod
    def is_restricted(ctx):
        return ctx.guild is not None and ctx.channel.is_nsfw()

    @staticmethod
    def new_page(title='', desc='', image='', thumbnail='', author='',
                 author_link='', author_icon='', footer='', footer_icon='',
                 timestamp=None, fields=()):

        embed = discord.Embed(title=title, description=desc)
        embed.colour = discord.Color.from_rgb(0, 100, 225)
        embed.set_image(url=image)
        embed.set_thumbnail(url=thumbnail)
        embed.set_author(name=author, icon_url=author_icon, url=author_link)
        embed.set_footer(text=footer, icon_url=footer_icon)
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=field[2])
        if timestamp is not None:
            embed.timestamp = timestamp

        return embed

    @staticmethod
    async def start_pages(ctx, pages):
        if not pages:
            raise NotFoundError
        display = Paginator(use_defaults=True, extra_pages=pages, timeout=60)
        await display.start(ctx)

    @commands.command()
    async def tiny(self, ctx, url):
        """shorten that long URL into a tiny URL"""

        tiny = await self.shorten(url)
        delta = len(url) - len(tiny)
        if delta < 0:
            return await ctx.send("That is already tiny!")
        await ctx.send(f'Shortened by *{delta}* characters: <{tiny}>')

    @commands.group(aliases=['r'])
    async def reddit(self, ctx, subreddit, *, search=None):
        """View all or specific photos from subreddits """

        base = 'www.reddit.com'
        params = {
            'q': f'subreddit:{subreddit} {search}',
            'limit': 100,
            'restrict_sr': 'True',
            'sort': 'relevance',
            't': 'month'
        }
        if search is None:
            url = f"{base}/r/{subreddit}/hot.json?"
            params = {'limit': 100}
        else:
            url = f"{base}/search.json?"

        data = await self.fetch(url, params=params)

        items = data['data']['children']

        checked = []
        for item in items:
            item = item['data']
            if all([
                item['url'].endswith(('png', 'jpg', 'gif')),
                item['over_18'] <= self.is_restricted(ctx)
            ]):
                checked.append(item)

        pages = []
        for item in checked:
            pages.append(self.new_page(
                title=item['title'],
                image=item['url'],
                author='u/' + item['author'],
                author_icon='https://hmp.me/cjtg',
                footer=(
                    f"r/{item['subreddit']} | "
                    f"{len(pages) + 1}/{len(checked)}"
                )
            ))
        await self.start_pages(ctx, pages)

    @reddit.command(aliases=['u'])
    async def user(self, ctx, user):
        """View photos from a specific reddit user"""
        pass

    @commands.group(aliases=['g'], invoke_without_command=True)
    async def google(self, ctx, *, search):
        """Search the web with google"""

        base = 'www.googleapis.com/customsearch/v1?'
        params = {
            'key': config.google,
            'cx': '009522941519100613891:ih0adp90wv4',
            'q': search,
            'safe': 'active',
        }
        if not self.is_restricted(ctx):
            params['safe'] = 'off'

        data = await self.fetch(base, params)

        if data['searchInformation']['totalResults'] == '0':
            return await ctx.send('No results found.')

        items = data['items']

        total = data['searchInformation']['formattedTotalResults']
        time = data['searchInformation']['formattedSearchTime']

        lines = []
        for item in items:
            lines.append(
                f"◦ *[{item['title']}]({await self.shorten(item['link'])})*"
            )
        results = '\n'.join(lines)

        pages = [self.new_page(
            author='Google Search',
            author_icon='https://hmp.me/cjo2',
            fields=[
                [
                    f"Results for '{search}':",
                    results,
                    True
                ]
            ],
            footer=(
                f"About {total} results ({time} seconds)"
                f"Safesearch {params['safe'].replace('off', 'inactive')}."
            )
        )]
        for item in items:
            pages.append(self.new_page(
                author_icon='https://hmp.me/cjo2',
                author=item['title'] + ':',
                author_link=item['link'],
                desc=item['snippet'],
                footer=(
                    f"About {total} results ({time} seconds) │ "
                    f"Safesearch {params['safe'].replace('off', 'inactive')}."
                    f" │ {len(pages)}/{len(items)}."
                )
            ))
        await self.start_pages(ctx, pages)

    @google.command(aliases=['i'])
    async def images(self, ctx, *, search: str):
        """Search for images with google"""

        base = 'www.googleapis.com/customsearch/v1?'
        params = {
            'key': config.google,
            'cx': '009522941519100613891:8nyxi_jhyya',
            'q': search,
            'safe': 'active',
            'searchType': 'image'
        }
        if not self.is_restricted(ctx):
            params['safe'] = 'off'

        data = await self.fetch(base, params)

        if data['searchInformation']['totalResults'] == '0':
            return await ctx.send('No results found.')

        items = data['items']

        total = data['searchInformation']['formattedTotalResults']
        time = data['searchInformation']['formattedSearchTime']

        pages = []
        for item in items:
            pages.append(self.new_page(
                title=item['title'],
                image=item['link'],
                author=f"Google Images",
                author_icon="https://hmp.me/cjo2",
                footer=(
                    f"About {total} results ({time} seconds)"
                    f"Safesearch {params['safe'].replace('off', 'inactive')}."
                    f" │ {len(pages) + 1}/{len(items)}."
                )
            ))
        await self.start_pages(ctx, pages)

    @staticmethod
    def chop(block):
        if len(block) > 1024:
            block = block[:1021] + '...'
        return block.replace('[', '').replace(']', '')

    @commands.command(name='define', aliases=['d'])
    async def urban(self, ctx, *, term):
        """Find wacky definitions for any word/term"""

        base = 'api.urbandictionary.com/v0/define?'
        params = {
            'term': term
        }
        data = await self.fetch(base, params)
        items = data['list']

        top = 'TOP '
        pages = []
        for item in items:
            pages.append(self.new_page(
                timestamp=dt.fromisoformat(item['written_on'].strip('Z')),
                desc=f"**[{top}DEFINITION]({item['permalink']})**",
                author="Urban Dictionary",
                author_icon="https://hmp.me/cjpn",

                fields=[
                    [
                        f'"{item["word"]}"',
                        self.chop(item['definition']),
                        False
                    ],
                    [
                        f"⠀",
                        self.chop(item['example']),
                        False
                    ]
                ],
                footer=(
                    f"Definition {len(pages) + 1} of {len(items)} │ "
                    f"Defined by: {item['author']}"
                )
            ))
            top = ''
        await self.start_pages(ctx, pages)

    @commands.command(aliases=['dog', 'doggo', 'doggos'])
    async def dogs(self, ctx, *, breed=None):
        """View pictures of random or specific breeds of dogs"""

        base = 'dog.ceo/api/breeds/image/random/50'
        if breed is not None:
            breed = breed.replace(' ', '-')
            base = f"dog.ceo/api/breed/{breed}/images/random/50"
        data = await self.fetch(base)

        items = data['message']

        pages = []
        for item in items:
            breed = f"{item.split('/')[-2].replace('-', ' ').title()}"

            pages.append(self.new_page(
                author='Doggos',
                image=item,
                footer=breed + f' | Image {len(pages) + 1} of {len(items)}.'
            ))
        await self.start_pages(ctx, pages)

    @commands.command(aliases=['y'])
    async def youtube(self, ctx, *, search):
        """Find top results for a search on youtube"""

        base = 'www.googleapis.com/youtube/v3/search?'
        params = {
            'part': 'snippet',
            'order': 'relevance',
            'type': 'video',
            'videoDefinition': 'high',
            'videoEmbeddable': 'true',
            'key': config.youtube,
            'q': search
        }
        data = await self.fetch(base, params)
        items = data['items']

        url = 'https://www.youtube.com/watch?v='

        pages = []
        for item in items:
            pages.append(
                f"{url}{item['id']['videoId']} | "
                f"Result: {len(pages) + 1}/{len(items)}")

        await self.start_pages(ctx, pages)


def setup(bot):
    bot.add_cog(APICommands(bot))
