# -*- coding:utf-8 -*-
import asyncio
import re
import logging

import aiohttp
from urllib import parse
from bs4 import BeautifulSoup

import aiofile


class AioComponents(object):
    """A totally async way to build the components to get the data from web site"""
    def __init__(self):
        # please do your configurations about this webrobot down here
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        }
        # Depends on which kind of first-letter-urls you want to download
        self.storage_path = "../Data/gutenburg/"
        self.main_origin_urls = [
            "http://gutenberg.net.au/plusfifty-a-m.html",
            "http://gutenberg.net.au/plusfifty-n-z.html"
        ]
        self.download_size_control = 0

    # async parts
    async def __fetch(self, session, url):
        async with session.get(url, headers=self.headers) as response:
            print("fetched an url:", url)
            return await response.text()

    async def _get_sub_urls(self, item):
        # init the links, avoiding the unassinged issues
        links = list()
        try:
            async with aiohttp.ClientSession() as session:
                response_html = await self.__fetch(session, item)
                print(item)
                await asyncio.sleep(2)
                soup_objcet = BeautifulSoup(response_html, "html.parser")
                # compile and find the rules of websites by regex
                tags_with_href = soup_objcet.find_all('a')
                tags_have_html = list()
                for index, tag in enumerate(tags_with_href):
                    if tag.string is not None:
                        if "HTML" in tag.string:
                            print(tag)
                            tags_have_html.append("http://gutenberg.net.au" + tags_with_href[index]["href"])
                links.append(tags_have_html)
        except Exception as e:
            logging.exception(e)

        print(links)
        return links

    def _build_url_lists(self):
        # Get the set-result of the urls that you need
        # each first letter has its own list in the larger list

        # unique_first_letter_url_list = unique_first_letter_url_list[0:10]

        # if only single url, then do the check
        main_task_list = self.main_origin_urls
        tasks_get_hyper_links = [
            self._get_sub_urls(url) for url in main_task_list
        ]
        # start the get_sub-urls_loop, bring a new one, with new_event_loop and set it global with set_event_loop
        loop_get_suburls = asyncio.new_event_loop()
        asyncio.set_event_loop(loop_get_suburls)
        hyper_links = loop_get_suburls.run_until_complete(
            asyncio.gather(*tasks_get_hyper_links)
        )
        loop_get_suburls.close()
        print("Sets' nums of hyper_links(the articles' links):", len(hyper_links))
        # filter the duplicated list in the main list
        # list is un-hashable, so make it string, and drop the duplicated one
        hyper_links = list(map(eval, set(list(map(str, hyper_links)))))
        print("unique_tasks_sub_lists_num:", len(hyper_links))

        # links are already the websites of articles, unique
        return hyper_links

    @classmethod
    def _get_story(cls, raw_response):
        # get texts
        story = []
        pattern = re.compile('<p>[^<>]*?</p>', re.S)
        res = re.findall(pattern, raw_response)
        for itm in res:
            itm = itm.replace('<p>', '')
            itm = itm.replace('</p>', '')
            story.append(itm)
        story = ' '.join(story)
        story = re.sub('\s+', ' ', story)
        story = re.sub('\n', ' ', story)

        return story

    async def _get_text(self, item):
        try:
            async with aiohttp.ClientSession() as session:
                response_html = await self.__fetch(session, item)
                await asyncio.sleep(2)
            print("task completed:", item)
            return self._get_story(response_html)
        except Exception as e:
            logging.exception(e)

    # not really necessary when your result is not that big, please choose the _get_text, when necessary, use this
    # depends on your result and your machines' RAM, cache
    async def _get_text_directly_to_file(self, item):
        # it's available to have both the choices of directly use the result or write into files
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(item, headers=self.headers) as response:
                    await asyncio.sleep(2)
                    # as returned the text, which is string, shall use 'w' mode
                    # the path is automatically created by item's name, file type default to .txt, you might change it
                    # set the path to storage the data, like: ../data/gutenburg/
                    # storage_path = "../Data/gutenburg/"
                    storage_path = self.storage_path
                    async with aiofile.AIOFile(
                            "".join([storage_path, item.split("/")[-1].split(".")[0], ".txt"]), 'w'
                    ) as afp:
                        writer = aiofile.Writer(afp)
                        # reader = Reader(afp, chunk_size=8)
                        result = await response.text()
                        await writer(self._get_story(result))
                        await afp.fsync()
            print("task completed:", item)
            return
        except Exception as e:
            logging.exception(e)
