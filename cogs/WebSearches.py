import asyncio
import typing
from datetime import datetime as dt

import aiohttp
import discord
from discord.ext import buttons
from discord.ext import commands


class Paginator(buttons.Paginator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class APICommands(commands.Cog, name='API'):
    """Various API commands for things."""

    def __init__(self, bot):
        self.bot = bot
        self.keys = self.bot.config['api']
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        asyncio.create_task(self.session.close())

    # ------ Methods ------
    # ------ API
    async def request(self, base, params=None, json=True) -> typing.Any:
        async with self.session.get('https://' + base, params=params) as r:
            if not r.raise_for_status():
                if json:
                    return await r.json()
                else:
                    return await r.text()

    async def shorten(self, url):
        base = 'www.tinyurl.com/api-create.php?'
        params = {
            'url': url
        }
        return await self.request(base, params, json=False)

    @staticmethod
    def char_limit(text, saver=False):
        if len(text) > 1024:
            text = text[:1021] + '...'
        if saver:
            text = text.replace('[', '').replace(']', '')
        return text

    # ------ Paginator
    @staticmethod
    async def start_pages(ctx, pages):
        if pages is None:
            return
        display = Paginator(use_defaults=True, extra_pages=pages, timeout=45)
        await display.start(ctx)

    # ------ Embeds
    @staticmethod
    def init_page(title=None, desc=None, color=discord.Color(0x6600ff)):
        return discord.Embed(title=title, description=desc, color=color)

    @staticmethod
    def set_page_author(embed, name=None, icon=None, url=None):
        embed.set_author(name=name, icon_url=icon or '', url=url or '')
        return embed

    @staticmethod
    def set_page_images(embed: discord.Embed, image=None, thumbnail=None):
        embed.set_image(url=image or '')
        embed.set_thumbnail(url=thumbnail or '')
        return embed

    @staticmethod
    def set_page_fields(embed, fields):
        # Pass fields as tuples Ex. ((name, value, False),)
        if fields is None:
            return
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=field[2])
        return embed

    @staticmethod
    def set_page_footer(embed, footer=None, timestamp=None, icon=None):
        embed.set_footer(text=footer, icon_url=icon or '')
        return embed

    @staticmethod
    def set_page_timestamp(embed, timestamp=None):
        if timestamp is not None:
            embed.timestamp = timestamp
        return embed

    def new_page(self, title=None, desc=None, author=None, url=None,
                 author_icon=None, image=None, thumbnail=None,
                 fields: () = None, footer=None, timestamp=None,
                 footer_icon=None):
        """Used to create pages in bulk for pagination"""
        embed = self.init_page(title=title, desc=desc)
        self.set_page_author(embed, name=author, icon=author_icon, url=url)
        self.set_page_images(embed, image=image, thumbnail=thumbnail)
        self.set_page_fields(embed, fields=fields)
        self.set_page_footer(embed, footer=footer, icon=footer_icon)
        self.set_page_timestamp(embed, timestamp=timestamp)
        return embed

    # ------ Checks
    @staticmethod
    def is_restricted(ctx):
        return ctx.guild is not None and ctx.channel.is_nsfw()

    # ------ Commands ------

    @commands.command()
    async def dogs(self, ctx, *, breed=None):
        """View pictures of random or specified breeds of dogs."""
        base = 'dog.ceo/api/breeds/image/random/50'
        if breed is not None:
            breed = breed.replace(' ', '-')
            base = f"dog.ceo/api/breed/{breed}/images/random/50"
        data = await self.request(base)

        items = data['message']

        pages = []
        for item in items:
            breed = f"{item.split('/')[-2].replace('-', ' ').title()}"

            pages.append(self.new_page(
                author='Dogs',
                image=item,
                footer=breed + f' | Image {len(pages) + 1} of {len(items)}.'
            ))
        await self.start_pages(ctx, pages)

    @commands.command(name='tiny')
    async def shorten_url(self, ctx, url):
        """Shorten any long URL into a tiny URL."""
        tiny = await self.shorten(url)
        shortened_by = len(url) - len(tiny)
        if shortened_by <= 0:
            return await ctx.send("That url is already tiny!")
        await ctx.send(f'Shortened by **{shortened_by}** characters: <{tiny}>')

    @commands.command(aliases=['d', 'urban'])
    async def define(self, ctx, *, term):
        """Find definitions for any word/term using Urban Dictionary."""

        base = 'api.urbandictionary.com/v0/define?'
        params = {
            'term': term
        }
        data = await self.request(base, params)
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
                        self.char_limit(item['definition']),
                        False
                    ],
                    [
                        f"⠀",
                        self.char_limit(item['example']),
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

    @commands.command(aliases=['r'])
    async def reddit(self, ctx, subreddit, *, search=None):
        """View photos from a specified subreddit."""

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

        data = await self.request(url, params=params)

        items = data['data']['children']

        if len(items) == 0:
            return await ctx.send('Could not find a subreddit by that name.')

        checked = []
        allowed = 0
        for item in items:
            item = item['data']
            if all([
                item['url'].endswith(('png', 'jpg', 'gif')),
                item['over_18'] <= self.is_restricted(ctx)
            ]):
                checked.append(item)
                if item['over_18'] <= self.is_restricted(ctx):
                    allowed += 1
        if allowed == 0:
            return await ctx.send('Subreddit is NSFW, move to NSFW channel.')

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

    @commands.group(aliases=['g'], invoke_without_command=True)
    async def google(self, ctx, *, search):
        """Search the web with google custom search."""

        base = 'www.googleapis.com/customsearch/v1?'
        params = {
            'key': self.keys['google'],
            'cx': '009522941519100613891:ih0adp90wv4',
            'q': search,
            'safe': 'active',
        }
        if self.is_restricted(ctx):
            params['safe'] = 'off'

        data = await self.request(base, params)

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
                f"About {total} results ({time} seconds)    "
                f"Safesearch {params['safe'].replace('off', 'inactive')}."
            )
        )]
        for item in items:
            pages.append(self.new_page(
                author_icon='https://hmp.me/cjo2',
                author=item['title'] + ':',
                url=item['link'],
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
        """Search for images with google images custom search."""

        base = 'www.googleapis.com/customsearch/v1?'
        params = {
            'key': self.keys['google'],
            'cx': '009522941519100613891:8nyxi_jhyya',
            'q': search,
            'safe': 'active',
            'searchType': 'image'
        }
        if self.is_restricted(ctx):
            params['safe'] = 'off'

        data = await self.request(base, params)

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
                    f"About {total} results ({time} seconds) "
                    f"Safesearch {params['safe'].replace('off', 'inactive')}."
                    f" │ {len(pages) + 1}/{len(items)}."
                )
            ))
        await self.start_pages(ctx, pages)


def setup(bot):
    bot.add_cog(APICommands(bot))
