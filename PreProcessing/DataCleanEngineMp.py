# -*- coding: utf-8 -*-
import multiprocessing as mp

from PreProcessing.DataCleanComponents import DataCleanComponents


class DataCleanEngineMp(DataCleanComponents):
    """Data clean Engine of the nlp data for the Language Model"""
    def __init__(self):
        super(DataCleanEngineMp, self).__init__()
        # Cpu intensive tasks，so Ncpu + 1
        self.cpu_cores = mp.cpu_count() + 1

    def mp_main_data_process(self, lst: list) -> list:
        final_processed_texts_list = list()
        for task_path in lst:
            print(task_path)
            with open(task_path, 'r', encoding='utf-8') as to_process_file:
                single_text = to_process_file.read()
                processed_text = self.clean_data_with_re_patterns(single_text)
            final_processed_texts_list.append(processed_text)

        return final_processed_texts_list

    def mp_based_the_clean_engine_core(self):
        # get the mission list
        task_paths_list = self.divide_the_lst_into_counts(self.get_the_training_data(), self.cpu_cores)
        # depends on your cores
        # usually: 4，depends on the cpu
        process_pool = mp.Pool(self.cpu_cores)
        # unnecessary to work in sequence, async it to make it quicker
        final_result = process_pool.map(self.mp_main_data_process, task_paths_list)
        process_pool.close()
        process_pool.join()

        return final_result


if __name__ == "__main__":
    instance_to_use = DataCleanEngineMp()
    result = instance_to_use.mp_based_the_clean_engine_core()
    print(result)
    print(len(result))
    print(result[2])
    print(result[4])
    print(result[4][0])
