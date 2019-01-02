# deprecated code for gutenberg crawler

def get_urls(url):
    print(url)
    print('----------')
    # headers good, can be used
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}

    request = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(request, timeout=60).read()
    # 上面两行就是读取出上面get_urls异步的那个网页结果而已，一直到response这边的事情都能做就好办了

    time.sleep(random.random() * 2)
    # get hyperlinks
    # absolute url
    websites = []
    for itm in links:
        web = urlparse.urljoin('http://gutenberg.net.au/index.html', itm.get('href'))
        websites.append(web)
    return list(set(websites))


def get_suburls(itm):
    links = []
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}
    request = urllib2.Request(itm, None, headers)
    try:
        response = urllib2.urlopen(request, timeout=60).read()
        time.sleep(random.random() * 2)
        soup = BeautifulSoup(response)
        res = soup.find_all('a', href=re.compile('ebooks.*\d{3,9}.*\.html'))
        for unt in res:
            web = urlparse.urljoin(itm, unt.get('href'))
            links.append(web)
        return list(set(links))
    except Exception:
        print(itm, 'failed')
        return


def get_text(self, i, q, lock):
    url = q.get(True)
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}
    request = urllib2.Request(url, None, headers)
    try:
        response = urllib2.urlopen(request, timeout=60).read()
        time.sleep(random.random() * 2)
        lock.acquire()
        q.put(response)
        lock.release()
        if i % 50 == 0:
            print('task %s (%s) success' % (i, os.getpid()))
        return
    except Exception:
        if i % 50 == 0:
            print('task %s (%s) fail' % (i, os.getpid()))
        return


def get_story(self, i, response):
    # get story id
    # try:
    #     pattern = re.compile('eBook\s+No\.:\s+[\w\d]+\.html', re.I)
    #     id = re.search(pattern, response).group()
    #     id = id.replace('eBook No.:', '')
    #     id = id.replace('.html', '')
    #     id = id.replace(' ', '')
    # except Exception:
    #     id = 'sequence no_' + str(i) + str(time.ctime())

    # sequence story id
    id = 'sequence no_' + str(i) + str(time.ctime())

    # get texts
    story = []
    pattern = re.compile('<p>[^<>]*?</p>', re.S)
    res = re.findall(pattern, response)
    for itm in res:
        itm = itm.replace('<p>', '')
        itm = itm.replace('</p>', '')
        story.append(itm)
    story = ' '.join(story)
    story = re.sub('\s+', ' ', story)
    story = re.sub('\n', ' ', story)

    try:
        file = open('/Users/roger.zhou/Downloads/Project_Gutenberg/a/' + id + '.txt', 'w')
        file.write(story.decode('utf-8'))
        file.close()
        # return story
        return
    except Exception:
        # print(id, 'extracting failed')
        return
    # return


if __name__ == "__main__":
    start = time.time()

    lists = ['a']
    websites = []
    for itm in lists:
        # get hyperlinks
        url = 'http://gutenberg.net.au/titles-' + itm + '.html'
        res = get_urls(url)
        websites.extend(res)

    ####
    # websites = websites[0: 1]
    ####

    links = []
    for i, itm in enumerate(websites):
        print(i, itm)
        res = get_suburls(itm)
        try:
            links.extend(res)
        except Exception:
            pass
    print('-----hyper links finished-----')

    out_links = '!'.join(links)
    file = open('/Users/roger.zhou/Downloads/Project_Gutenberg/' + 'a' + '_links.txt', 'w')
    file.write(out_links)
    file.close()












    # load crawled links
    links = []
    f = open('/Users/roger.zhou/Downloads/Project_Gutenberg/' + 'a' + '_links.txt', 'r')
    for line in f.readlines():
        links.append(line)
    links = ''.join(links)
    links = links.split('!')
    print('-----links loaded-----')

    #####
    links = links[150000: 180000]
    #####

    # get response
    print('total links no:', len(links))

    manager = multiprocessing.Manager()
    q = manager.Queue()
    lock = manager.Lock()
    print
    'Parent process %s.' % os.getpid()
    pool = Pool(50)

    # 这个links获取
    # itm是来自于links的
    for i, itm in enumerate(links):
        q.put(itm)
        pool.apply_async(get_text, args=(i, q, lock))
    pool.close()
    pool.join()

    responses = []
    while True:
        if not q.empty():
            value = q.get(True)
            responses.append(value)
        else:
            break
    print('total response:', len(responses))

    # get story
    stories = []
    print('-----extracting story-----')
    # texts = []
    for i, itm in enumerate(responses):
        if i % 1000 == 0:
            print(i, 'done')
        res = get_story(i, itm)
        # stories.append(res)
    # stories = ' '.join(stories)
    # file = open('/Users/roger.zhou/Downloads/Project_Gutenberg/total/' + 'c_utf' + '_total.txt', 'w')
    # file.write(stories)
    # file.close()
    print('all done')
    end = time.time()
    print((end - start) / 3600)
