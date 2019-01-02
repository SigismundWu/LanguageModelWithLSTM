# -*- coding:utf-8 -*-
from collections import Counter, OrderedDict


class RegexPattern(object):
    """
    A configuration type class, to store the regex pattern
    As the regex part was designed for VOA(news), some of it processing the gutenburg might not needed
    so annotated them, you can dis-annotated them
    """
    # re_lists
    re_first = [
        ['\<', ''], ['\>', ''],
    ]
    re_first = OrderedDict(re_first)

    re_dict = [
        # 无意义的标题或词汇行
        # ['\n.{1,300}?\.\n', ''], ['\\bclick to see content\s*:\s*[\w_]\\b', ''],
        # ['\\bfollow\s[\w\s]+on\stwitter\s@\w+BBC\\b', ''], ['\\b\d{1,2}\.\s', '. '],
        # ['\\bclick to see content:\s+', ''], ['&amp;', ' '], ['&nbsp;', ' '],
        ['\\bby.{2,40}?\d{1,2}\sjanuary\s\d{4}|\\bby.{2,40}?\d{1,2}\sfebruary\s\d{4}|\\bby.{2,40}?\d{1,2}\smarch\s\d{4}|\\bby.{2,40}?\d{1,2}\sapril\s\d{4}|\\bby.{2,40}?\d{1,2}\smay\s\d{4}|\\bby.{2,40}?\d{1,2}\sjune\s\d{4}|\\bby.{2,40}?\d{1,2}\sjuly\s\d{4}|\\bby.{2,40}?\d{1,2}\saugust\s\d{4}|\\bby.{2,40}?\d{1,2}\sseptember\s\d{4}|\\bby.{2,40}?\d{1,2}\soctober\s\d{4}|\\bby.{2,40}?\d{1,2}\snovember\s\d{4}|\\bby.{2,40}?\d{1,2}\sdecember\s\d{4}|', ''],
        # 缩写
        ['\\bd\.c\.', 'dc'], ['\\bu\.s\.', 'america'], ['\\bu\.n\.', 'un'],
        ['\\bdr\.', 'dr'], ['\\bmr\.', 'mr'], ['\\bms\.', 'ms'],
        ['\\b(\w\s+\.){1, 4}', '<abbr> '], ['\\bpres\.', 'president'],
        ['\\bjan\.|\\bjan\\b', 'january'], ['\\bfeb\.|\\bfeb\\b', 'february'],
        ['\\bmar\.|\\bmar\\b', 'march'], ['\\bapr\.|\\bapr\\b', 'april'],
        ['\\bjun\.|\\bjun\\b', 'june'], ['\\bjul\.|\\bjul\\b', 'july'],
        ['\\baug\.|\\baug\\b', 'august'], ['\\bsep\.|\\bsep\\b', 'september'],
        ['\\boct\.|\\boct\\b', 'october'], ['\\bnov\.|\\bnov\\b', 'november'],
        ['\\bdec\.|\\bdec\\b', 'december'],
        ['\\bsec\.', 'secretary'],
        # 简写
        ['(?<=\\bit)[’\']s\\b|(?<=\\bhe)[’\']s\\b|(?<=\\bshe)[’\']s\\b|(?<=\\bthat)[’\']s\\b|(?<=\\bthis)[’\']s\\b|(?<=\\bthere)[’\']s\\b|(?<=\\bhere)[’\']s\\b', ' is'],
        ['(?<=[a-zA-Z])[’\']re\\b', ' are'], ['(?<=[a-zA-Z])[’\']d\\b', ' would'],
        ['(?<=[a-zA-Z])[’\']ve\\b', 'have'], ["(?<=[a-zA-Z])n[’\']t\\b", ' not'],
        ['(?<=[a-zA-Z])[’\']m\\b', ' am'],  ['[’\']ll\\b', ' will'],
        # 货币
        ['[\$￡]*\s*\d[\s,\d\.]{0,10}\s*bn*\\b', '<money> billion'],
        ['[\$￡]\s*\d[\s,\d\.]{0,10}\s*m\\b', '<money> million'],
        ['[\$￡]*\s*\d[\s,\d\.]{0,10}\s*tr*n\\b|[\$￡]*\s*\d[\s,\d\.]{0,10}\s*tr\\b', '<money> trillion'],
        ['\$￡]\s*\d[\s,\d\.]{0,10}\s*k\\b', '<money> thousand'],
        ['[\$￡]\s*\d[\s,\d\.]{0,10}\\b', '<money> '], # $10
        # date
        # month-day-year
        ['\\bjanuary[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bfebruary[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bmarch[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bapril[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bmay[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bjune[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bjuly[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\baugust[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bseptember[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\boctober[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bnovember[,\s-]+\d{1,2}[,\s-]+\d{4}\\b|\\bdecember[,\s-]+\d{1,2}[,\s-]+\d{4}\\b', '<month> <day> <year>'], # May 15, 1864
        ['\\b\d{1,2}\s+january\s+\d{4}\\b|\\b\d{1,2}\s+february\s+\d{4}\\b|\\b\d{1,2}\s+march\s+\d{4}\\b|\\b\d{1,2}\s+april\s+\d{4}\\b|\\b\d{1,2}\s+may\s+\d{4}\\b|\\b\d{1,2}\s+june\s+\d{4}\\b|\\b\d{1,2}\s+july\s+\d{4}\\b|\\b\d{1,2}\s+august\s+\d{4}\\b|\\b\d{1,2}\s+september\s+\d{4}\\b|\\b\d{1,2}\s+october\s+\d{4}\\b|\\b\d{1,2}\s+november\s+\d{4}\\b|\\b\d{1,2}\s+december\s+\d{4}\\b', '<day> <month> <year>'],
        # month-year
        ['\\bjanuary\s+\d{4}\\b|\\bfebruary\s+\d{4}\\b|\\bmarch\s+\d{4}\\b|\\bapril\s+\d{4}\\b|\\bmay\s+\d{4}\\b|\\bjune\s+\d{4}\\b|\\bjuly\s+\d{4}\\b|\\baugust\s+\d{4}\\b|\\bseptember\s+\d{4}\\b|\\boctober\s+\d{4}|november\s+\d{4}\\b|\\bdecember\s+\d{4}\\b', '<month> <year>'], # march 2017
        # month-day
        ['\\bjanuary\s+\d{1,2}\\b|\\bfebruary\s+\d{1,2}\\b|\\bmarch\s+\d{1,2}\\b|\\bapril\s+\d{1,2}\\b|\\bmay\s+\d{1,2}\\b|\\bjune\s+\d{1,2}\\b|\\bjuly\s+\d{1,2}\\b|\\baugust\s+\d{1,2}\\b|\\bseptember\s+\d{1,2}\\b|\\boctober\s+\d{1,2}|november\s+\d{1,2}\\b|\\bdecember\s+\d{1,2}\\b', '<month> <day>'],
        # day-month
        ['\\b\d{1,2}\s+junuary\\b|\\b\d{1,2}\s+february\\b|\\b\d{1,2}\s+march\\b|\\b\d{1,2}\s+april\\b|\\b\d{1,2}\s+may\\b|\\b\d{1,2}\s+june\\b|\\b\d{1,2}\s+july\\b|\\b\d{1,2}\s+august\\b|\\b\d{1,2}\s+september\\b|\\b\d{1,2}\s+october\\b|\\b\d{1,2}\s+november\\b|\\b\d{1,2}\s+december\\b', '<day> <month>'],
        # generation
        ['\\b\d{4}s\s+&\s+\d{2,4}s\\b|\\b\d{4}s\s+and\s+\d{2,4}s\\b|\\b\d{4}s\s+&\s+early\s+\d{2,4}s\\b|\\b\d{4}s\s+&\s+late\d{2,4}s\\b|\\b\d{4}s\s+and\s+early\d{2,4}s\\b|\\b\d{4}s\s+and\s+late\d{2,4}s\\b', '<generation>'],
        ['\\bearly\s+\d{2,4}s\\b|\\blate\s+\d{2,4}s\\b', '<generation>'],
        ['\\b\d{2,4}s\\b', '<generation>'],
        # year
        ['\\byear\s+\d{4}[,\s-]+year\s+\d{4}\\b|\\byear\s+\d{4}[,\s-]+\d{4}\\b', '<year>'], # year 2017-2018
        ['\\byear[,\s-]+\d{4}\\b', '<year>'], # year 2017
        ['\\bby\s\d{4}-\d{2,4}\\b|\\bfrom\s\d{4}-\d{2,4}\\b|\\bduring\s\d{4}-\d{2,4}\\b', '<year>'], # by 2017-19
        ['(?<=\\bafter\sthe\s)d{4}\\b|(?<=\\bafter\s)\d{4}\\b|(?<=\\bbefore\sthe\s)d{4}\\b|(?<=\\bbefore\s)\d{4}\\b', '<year>'],
        ['(?<=\\bpost)[,\s-]+\d{4}\\b|(?<=\\bpre)[,\s-]+\d{4}\\b|(?<=\\blate)[,\s-]+\d{4}\\b|(?<=\\bearly)[,\s-]+\d{4}\\b', '<year>'], # post 2017
        ['(?<=\\bby\s)\d{4}\\b|(?<=\\bof\s)\d{4}\\b|(?<=\\bin\s)\d{4}\\b|(?<=\\bsince\s)\d{4}\\b|(?<=\\buntil\s)\d{4}\\b|(?<=\\blast\s)\d{4}\\b|(?<=\\bbetween\s)\d{4}\s+&\s+\d{4}\\b|(?<=\\bbetween\s)\d{4}\s+and\s+\d{4}\\b', '<year>'],
        ['(?<=\\bin\s)t*h*e*\s+[12]\d{3}\\b|(?<=\\buntil\s)t*h*e*\s+[12]\d{3}\\b|(?<=\\bsince\s)t*h*e*\s+[12]\d{3}\\b', '<year>'], #  in 2017
        # month
        ['\\bjanuary\\b|\\bfebruary\\b|march\\b|\\bapril\\b|\\bjune\\b|\\bjuly\\b|\\baugust\\b|\\bseptember|\\boctober\\b|\\bnovember\\b|\\bdecember\\b', '<month>'], # march
        # 百分比
        ['%', ' percent'],
        # 单位
        ['\\b\d{1,4}x\d{1,4}\s*m\\b', '<noxno> m'],
        ['\\b\d[\d,\.]{0,10}sq\s*feet\\b', '<no> sq feet'], ['\\b\d[\d,\.]{0,10}hrs*\\b', '<no> hour'],
        # ['\\b\d[\d,\.]{0,10}mmhg\\b', '<no> mmhg'], ['\\b\d[\d,\.]{0,10}mbps\s\\b', '<no> mbps'],
        ['\\b\d[\d,\.]{0,10}gbps\\b', '<no> gbps'], ['\\b\d[\d,\.]{0,10}sq\s*rt\\b', '<no> sqft'],
        ['\\b\d[\d,\.]{0,10}gbz\\b', '<no> gbz'], ['\\b\d[\d,\.]{0,10}sq\s*m\\b', '<no> sqm'],
        # ['\\b\d[\d,\.]{0,10}kwh\\b', '<no> kwh'], ['\\b\d[\d,\.]{0,10}sq\s*km\\b', '<no> sqkm'],
        # ['\\b\d[\d,\.]{0,10}ers\\b', '<no> ers'], ['\\b\d[\d,\.]{0,10}lbn\\b', '<no> lbn'],
        # ['\\b\d[\d,\.]{0,10}ins\\b', '<no> ins'], ['\\b\d[\d,\.]{0,10}mph\\b', '<no> mph'],
        # ['\\b\d[\d,\.]{0,10}msv\\b', '<no> msv'], ['\\b\d[\d,\.]{0,10}kmh\\b', '<no> kmh'],
        # ['\\b\d[\d,\.]{0,10}pph\\b', '<no> pph'], ['\\b\d[\d,\.]{0,10}lbs\\b', '<no> lbs'],
        # ['\\b\d[\d,\.]{0,10}mdb\\b', '<no> mdb'], ['\\b\d[\d,\.]{0,10}mmt\\b', '<no> mmt'],
        # ['\\b\d[\d,\.]{0,10}mg\\b', '<no> mg'], ['\\b\d[\d,\.]{0,10}kb\\b', '<no> kb'],
        # ['\\b\d[\d,\.]{0,10}kw\\b', '<no> kw'], ['\\b\d[\d,\.]{0,10}gb\\b', '<no> gb'],
        ['\\b\d[\d,\.]{0,10}km\\b', '<no> km'], ['\\b\d[\d,\.]{0,10}ft\\b', '<no> ft'],
        ['\\b\d[\d,\.]{0,10}kg\\b', '<no> kg'], ['\\b\d[\d,\.]{0,10}ml\\b', '<no> ml'],
        # ['\\b\d[\d,\.]{0,10}cm\\b', '<no> cms'], ['\\b\d[\d,\.]{0,10}lb\\b', '<no> lb'],
        # ['\\b\d[\d,\.]{0,10}in\\b', '<no> in'], ['\\b\d[\d,\.]{0,10}tb\\b', '<no> tb'],
        # ['\\b\d[\d,\.]{0,10}cc\\b', '<no> cc'],
        ['\\b\d[\d,\.]{0,10}mm\\b', '<no> mm'],
        # ['\\b\d[\d,\.]{0,10}mw\\b', '<no> mw'], ['\\b\d[\d,\.]{0,10}nm\\b', '<no> nm'],
        ['\\b\d[\d,\.]{0,10}m\\b', '<no> m'],
        # ['\\b\d[\d,\.]{0,10}c\\b', '<no> c'],
        # ['\\b\d[\d,\.]{0,10}f\\b', '<no> f'], ['\\b\d[\d,\.]{0,10}p\\b', '<no> p'],
        # ['\\b\d[\d,\.]{0,10}g\\b', '<no> g'], ['\\b\d[\d,\.]{0,10}v\\b', '<no> v'],
        # 时间
        ['\\b\d{1,2}\s*:\s*\d{1,2}GMT\\b', '<time> GMT'],
        ['\\b\d{1,2}\s*:\s*\d{1,2}\\b', '<time>'], # 7:05
        ['\\b\d[:\d]*[ap]m\\b', '<time>'],
        # 邮箱
        # ['\\b[\w\d_\.]+@[\w\d_\.]+\\b', '<mail address>'],
        # 其他
        ['\\b3\s*-\s*d\\b', '3d'], ['\.\.\.', ' '], ['wi - fi', 'wifi'],
        # 网址
        # ['\\bh*t*t*p*:*/*/*www\.[\w\d\.]+\\b', '<url>'],
        # ['\s[\w\d\.]+com\\b|[\w\d\.]+cn\\b', ' <url>'],
        # 电话
        # ['\+\s*\d{1,4}[\d\(\)\s-]{4,12}\\b', '<tele no>'],
        # 型号
        # ['\\bmi\d{1,4}\\b|\\bitv\d{1,4}\\b|\\b\ds\\b|\\bp\d{1,4}\\b', '<brand type>'],
        # ['\\bmate\d{1,4}\\b|\\bps\d{1,4}\\b', '<brand type>'],
        # 还原
        # ['\\bh1[\s-]*b\\b', 'h1-b'],
        ['<money> million <money> million', '<money> million'],
        ['\.\s\.', '.'],
        # ['h & m', 'h&m'],
    ]
    re_dict = OrderedDict(re_dict)

    re_symb = [
        # 符号
        ['‘', '\''], ['//', ''], ['”', ' " '], ['，', ' , '], ['：', ' : '], ['…', ''], ['–', ' - '],
        ['-[\s-]+-', '-'], ['"', ' " '], ['\#', ' # '], ['\%', ' % '], ['&', ' & '], ['\!', ' . '],
        ['\'', ' \' '], ['\(', ''], ['\)', ''], ['\*', ' * '], ['\+', ' + '], [',', ' , '],
        ['-', ' - '], ['\.', ' . '], ['/', ' / '], [':', ' : '], [';', ' ; '], ['“', ' " '],
        ['=', ' = '], ['\?', ' . '], ['@', ' @ '], ['\[', ''], ['\]', ''], ['\$', ' $ '],
        ['\^', ' ^ '], ['_', ' _ '], ['`', ' ` '], ['\{', ' { '], ['\|', ' | '], ['\}', ' } '],
        ['—', ' — '], ['\s+', ' '], ['’', " ' "], ["' s", "'s"], ["\\'s", "'s"]
    ]
    re_symb = OrderedDict(re_symb)

    re_number = [
        # 数字
        ['\\b\d+x\d+\\b', '<no>x<no>'],
        ['\\b\d+rd|\d+th|\d+st\\b|\\b\d+nd\\b', '<num>'],  # 23rd
        ['\\b\d[\d,\s\.]+\\b', '<no> '], # 300
        ['\\b\d\\b', '<no>']  # 单独一个数字: 5
    ]
    re_number = OrderedDict(re_number)
