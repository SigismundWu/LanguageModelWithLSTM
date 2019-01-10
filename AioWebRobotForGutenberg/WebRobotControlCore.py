# -*- coding: utf-8 -*-
import asyncio
import multiprocessing as mp

from AioWebRobotForGutenberg.AioComponents import AioComponents


class WebRobotControlCore(AioComponents):
    """Control Core using multiprocessing to build the high performance WebRobot"""

    def __init__(self):
        super().__init__()
        # control the tasks that you wanted by slicing the url_list
        # all_text_url_list is like [[link....], [link...]], according to how many main links of articles you chose
        # and this links' sub-links would be crawled with multi-processing
        self.all_text_url_list = self._build_url_lists()
        # set the nums of articles that you need, multiprocessed, so your demands // 2
        self.start_label = 1300
        self.end_label = 1500

    def get_all_text(self, func_mode) -> list:
        """
        whether want to storage the text or use it directly in ram, by the func mode，this is the main control func
        :rtype [[str, str...], [str, str...]...]
        """
        # default to 4, depends on your tasks and core of the CPU of your machine
        cpu_cores = mp.cpu_count()
        process_pool = mp.Pool(cpu_cores)
        # a list of each function return, divide into sub lists and with a high performance
        process_result = process_pool.map_async(func_mode, self.all_text_url_list)
        process_pool.close()
        process_pool.join()

        final_result = process_result.get()

        return final_result

    def _pre_process_the_sub_text_url_list(self, func_to_use, sub_text_url_list):
        """abstract from the previous func, have this func to use like a switch to adapt different funcs"""
        # control the size to crawl
        print(sub_text_url_list)
        if (len(sub_text_url_list) == 0) | (sub_text_url_list is None):
            print("no tasks in this sequences, try next one")
            return []
        else:
            # if not list with list in it like [[link....], [link...]]
            if isinstance(sub_text_url_list[0], str) and len(sub_text_url_list[0]) > 1:
                tasks_get_all_text = [
                    func_to_use(text_url) for text_url in sub_text_url_list
                ]
                print("the tasks:", tasks_get_all_text)
            # if only a str, not even a list, then build a single element list for it
            elif isinstance(sub_text_url_list[0], str) and len(sub_text_url_list[0]) == 1:
                tasks_get_all_text = [func_to_use(sub_text_url_list)]
            # if the self.all_text_url_list is like [[link...], [link...]]
            else:
                tasks_get_all_text = [
                    func_to_use(single_url) for text_url in sub_text_url_list for single_url in text_url
                ]
            # actually how many tasks, divided by 2, usually won't overflow, we usually don't have such a powerful GPU
            # two processes, so actually would be doubled, would warn you never awaited, that's ok, cos you just pick tasks
            tasks_get_all_text = tasks_get_all_text[self.start_label:self.end_label]
            print("actually tasks counts:", len(tasks_get_all_text))

            return tasks_get_all_text

    def get_all_text_core_in_ram_cache(self, sub_text_url_list):
        """return the result directly for other functions to use"""
        tasks_get_all_text = self._pre_process_the_sub_text_url_list(self._get_text, sub_text_url_list)
        # Distribute all tasks to 4 processes, in each sub process can have it's own main event loop
        loop_get_all_text = asyncio.new_event_loop()
        asyncio.set_event_loop(loop_get_all_text)
        all_text = loop_get_all_text.run_until_complete(
            asyncio.gather(*tasks_get_all_text)
        )

        return all_text

    def get_all_text_core_to_files(self, sub_text_url_list):
        """storage the result of lines to files"""
        # set the index slice to control the size of the tasks
        tasks_get_all_text = self._pre_process_the_sub_text_url_list(
            self._get_text_directly_to_file, sub_text_url_list
        )
        # Distribute all tasks to 4 processes, in each sub process can have it's own main event loop
        loop_get_all_text = asyncio.new_event_loop()
        asyncio.set_event_loop(loop_get_all_text)
        all_text = loop_get_all_text.run_until_complete(
            asyncio.gather(*tasks_get_all_text)
        )

        return all_text


if __name__ == "__main__":
    t_use = WebRobotControlCore()
    result = t_use.get_all_text(t_use.get_all_text_core_to_files)
    print(len(result))
    # print(result[0][0])
    # print(type(result[0]))
