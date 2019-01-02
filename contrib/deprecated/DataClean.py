# -*- coding:utf-8 -*-
"""
deprecated functions in old single process DataClean class
"""


def get_the_train_data() -> str:
    path = '/Users/roger.zhou/Downloads/Project_Gutenberg/'

    subfolder = 'c'
    file_name = []
    texts = []
    k = 0
    for parent, subfolders, files in os.walk(path + subfolder + '/'):
        for i, unt in enumerate(files):
            unt = os.path.join(parent, unt)
            if (unt.find('DS_Store') < 0) & (os.path.getsize(unt) > 0):
                file_name.append(unt)
                if i % 1000 == 0:
                    print('processing task:', i)
                try:
                    with open(unt, 'r', encoding='utf-8') as f:
                        for line in f:
                            texts.append(line)
                    f.close()
                except Exception:
                    print(unt, 'failed')
                    k += 1
    print('processing finished...')
    texts = ' '.join(texts)
    print('total files:', len(file_name))
    print('failed:', k)
    print(texts[0: 1500])

    return texts
