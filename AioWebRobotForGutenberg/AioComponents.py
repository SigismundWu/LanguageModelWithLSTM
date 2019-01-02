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
        self.download_list = ["a"]
        self.sub_urls_pattern = 'ebooks.*\d{3,9}.*\.html'
        self.storage_path = "../Data/gutenburg/"

    # async parts
    async def __fetch(self, session, url):
        async with session.get(url, headers=self.headers) as response:
            return await response.text()

    async def _get_urls(self, url):
        # initial the ClientSession Class as session
        async with aiohttp.ClientSession() as session:
            response_html = await self.__fetch(session, url)
            soup_object = BeautifulSoup(response_html)
            # sleep for 2 secs for each html to protect the server
            await asyncio.sleep(2)
            links = soup_object.find_all('a', href=re.compile('#'))
            # get the websites list
            websites = [
                parse.urljoin('http://gutenberg.net.au/index.html', item.get('href')) for item in links
            ]
            websites_list = list(set(websites))

            return websites_list

    async def _get_sub_urls(self, item):
        # init the links, avoiding the unassinged issues
        links = list()
        try:
            async with aiohttp.ClientSession() as session:
                response_html = await self.__fetch(session, item)
                await asyncio.sleep(2)
                soup_objcet = BeautifulSoup(response_html)
                # compile and find the rules of websites by regex
                res = soup_objcet.find_all('a', href=re.compile(self.sub_urls_pattern))
                links = [
                    parse.urljoin(item, unt.get('href')) for unt in res
                ]
        except Exception as e:
            logging.exception(e)

        return links

    def _build_url_lists(self):
        # The lists decides which of the first_lettered articles would be downloaded
        first_letter_list = self.download_list
        # Get the url from the main page, statically have the gutengbery.net url rules down below as shown
        tasks_get_first_letter_links = [
            self._get_urls("".join(['http://gutenberg.net.au/titles-', url, '.html'])) for url in first_letter_list
        ]
        loop_get_first_letter = asyncio.get_event_loop()
        # The arg for gather must be passed as a discomposed struct
        first_letter_url_list = loop_get_first_letter.run_until_complete(
            asyncio.gather(*tasks_get_first_letter_links)
        )
        loop_get_first_letter.close()
        # Get the set-result of the urls that you need
        # each first letter has its own list in the larger list

        # process the first_letter_url_list to make it unique
        def __manage_the_first_letter_url_list(lst):
            managed_lst = list()
            for index in range(len(lst)):
                cache = lst.pop()
                managed_lst.extend(cache)
            # drop the duplications with set func
            managed_lst_set = set(managed_lst)
            managed_lst = list(managed_lst_set)

            return managed_lst

        unique_first_letter_url_list = __manage_the_first_letter_url_list(first_letter_url_list)
        # size_control_test, temporarily, step 2
        unique_first_letter_url_list = unique_first_letter_url_list[0:1]
        # if only single url, then do the check
        if not isinstance(unique_first_letter_url_list, list):
            cache_list = list()
            cache_list.append(unique_first_letter_url_list)
            unique_first_letter_url_list = cache_list

        tasks_get_hyper_links = [
            self._get_sub_urls(url) for url in unique_first_letter_url_list
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
