from config import *
import json, httpx, time, random
from pyquery import PyQuery as pq
from playwright.sync_api import sync_playwright
from apscheduler.schedulers.blocking import BlockingScheduler

def main():
    print('tick')
    # get novel list
    save_file = open('data/novel_data.json', 'r+', encoding='utf-8')
    content = save_file.read()
    save_file.close()
    data_list = []
    if content == '':
        data_list = init_data()
    else:
        data_list =  json.loads(content)
    if len(data_list) == 0:
        data_list = init_data()
    # decide which novel which chapter
    selected_novel, novel_detail = select_novel(data_list, 0)
    current_chap = selected_novel['current_chap']
    selected_novel['current_chap'] += 1
    select_chap = novel_detail['chap_list'][current_chap]
    # grab content
    post_content = ''
    if selected_novel != None:
        post_content = f'#{selected_novel["title"]}# by {selected_novel["author"]}  收藏数：{novel_detail["collection_count"]}\n'
    if len(novel_detail["tags"]) > 0:
        for t in novel_detail["tags"]:
            post_content += f'#{t}#  '
        post_content += '\n'
    if select_chap != None:
        post_content += f'第{current_chap+1}章 发表于{select_chap["time"]}\n'
        chapter_content = get_chapter_content(select_chap['url'])
        # in case content is too long
        if len(chapter_content) > 4500:
            post_content += chapter_content[:4500] + '...'
        else:
            post_content += chapter_content
        post_content += f'\n阅读原文：{selected_novel["url"]}'
    # post weibo
    if post_content != '':
        post_weibo(post_content)
        # update novel data
        new_data = append_data(data_list)
        write_file = open('data/novel_data.json', 'w', encoding='utf-8')
        write_file.write(json.dumps(new_data, ensure_ascii=False))
        write_file.close()

def select_novel(data_list, retry):
    if retry > 10:
        print(f'尝试次数={retry}, return None')
        return None, None
    selected_novel = random.choice(data_list)
    print(f'尝试次数={retry}, try{selected_novel["title"]}')
    current_chap = selected_novel['current_chap']
    novel_detail = get_detail_page(selected_novel['url'])
    if novel_detail == None:
        retry += 1
        return select_novel(data_list, retry)
    print(f'尝试次数={retry}, 获取章节{novel_detail}')
    if current_chap >= novel_detail['chap_count']:
        print(f'{selected_novel["title"]}章节数不足')
        if novel_detail['status'] != '连载':
            data_list.remove(selected_novel)
        retry += 1
        return select_novel(data_list, retry)
    elif (novel_detail['vip_chap_id'] != None and current_chap >= novel_detail['vip_chap_id'] - 1) or novel_detail == None:
        print(f'{selected_novel["title"]}入V或锁文')
        data_list.remove(selected_novel)
        retry += 1
        return select_novel(data_list, retry)
    else:
        # update chap count
        print(f'选中{selected_novel}\n章节{novel_detail}')
        return selected_novel, novel_detail


search_url = 'https://www.jjwxc.net/bookbase.php?xx3=3&sortType=3&isfinish=1&page={}'

def append_data(old_data):
    page = 1
    exist = False
    new_novel_list = []
    old_titles = [i['title'] for i in old_data]
    while not exist:
        res = httpx.get(search_url.format(page), headers={'Cookie': jjwxc_cookies})
        res.encoding = 'gb2312'
        doc = pq(res.text)
        trs = list(doc('table.cytable tr').items())
        for tr in trs[1:]:
            tds = list(tr('td').items())
            author = tds[0].text()
            title = tds[1].text()
            url = 'https://www.jjwxc.net/' + tds[1]('a').attr('href')
            wordcount = tds[4].text()
            publish_time = tds[6].text()
            # print(author, title, url, wordcount, publish_time)
            # novel_data = get_detail_page(url)
            if title in old_titles:
                exist = True
                break
            new_novel_list.append({
                'title': title,
                'author': author,
                'url': url,
                'wordcount': wordcount,
                'publish_time': publish_time,
                'current_chap': 0
            })
    # with open('data/novel_data.json', 'w', encoding='utf-8') as save:
    #     save.write(json.dumps(new_novel_list, ensure_ascii=False))
    return old_data + new_novel_list


def init_data():
    page = 1
    delta_days = 0
    new_novel_list = []
    while delta_days < 10.0:
        res = httpx.get(search_url.format(page), headers={'Cookie': jjwxc_cookies})
        res.encoding = 'gb2312'
        doc = pq(res.text)
        trs = list(doc('table.cytable tr').items())
        for tr in trs[1:]:
            tds = list(tr('td').items())
            author = tds[0].text()
            title = tds[1].text()
            url = 'https://www.jjwxc.net/' + tds[1]('a').attr('href')
            wordcount = tds[4].text()
            publish_time = tds[6].text()
            # print(author, title, url, wordcount, publish_time)
            # novel_data = get_detail_page(url)
            print(title)
            new_novel_list.append({
                'title': title,
                'author': author,
                'url': url,
                'wordcount': wordcount,
                'publish_time': publish_time,
                'current_chap': 0
            })
            # 2022-12-20 08:58:15
            time_stamp = time.mktime(time.strptime(publish_time,"%Y-%m-%d %H:%M:%S"))
            delta_time = time.time() - time_stamp
            delta_days = delta_time // (24*3600)
        print(delta_days)
        page += 1
    with open('data/novel_data.json', 'w', encoding='utf-8') as save:
        save.write(json.dumps(new_novel_list, ensure_ascii=False))
    return new_novel_list


def get_detail_page(url):
    detail_res = httpx.get(url)
    detail_res.encoding = 'gb2312'
    doc = pq(detail_res.text)
    chap_table = doc('#oneboolt')
    if chap_table == None: # locked
        return None
    bid = url.split('=')[-1]
    tag_items = doc('div.smallreadbody a').items()
    tag_dict = {
        item.text(): item.attr('href') for item in tag_items
    }
    tag_remove_list = []
    for i in tag_dict.keys():
        if '?bq=' not in tag_dict[i] or len(i) > 4:
            tag_remove_list.append(i)
    for i in tag_remove_list:
        tag_dict.pop(i)
    tags = [i.strip() for i in tag_dict.keys() if len(i.strip()) > 0]
    try:
        httpx.get(f'https://fun.zhufree.fun/book/update/{bid}') # update book to baihehub btw
    except Exception as e:
        pass
    finally:
        pass
    chapters = chap_table('tr[itemprop~=chapter]').items()
    chap_list = []
    vip_chap_id = None
    for chap in chapters:
        chap_tds = list(chap('td').items())
        chap_id = chap_tds[0].text().strip()
        chap_title = chap_tds[1].text()
        if chap_title == '等待进入网审' or chap_title == '[屏蔽中]':
            continue
        if '[VIP]' in chap_title:
            vip_chap_id = int(chap_id)
            continue
        chap_desc = chap_tds[2].text()
        chap_time = chap_tds[5]('span:first-child').text()
        chap_list.append({
            'id': chap_id,
            'title': chap_title,
            'url': chap_tds[1]('a').attr('href').replace('http://', 'https://'),
            'desc': chap_desc,
            'time': chap_time
        })
    genre = doc('span[itemprop=genre]').text()
    if genre != None and len(genre.split('-')) > 2:
        tags.append(genre.split('-')[2])
    return {
        'collection_count': doc('span[itemprop=collectedCount]').text(),
        'type': genre,
        'style': doc('.rightul li:nth-child(3) span').text(),
        'tags': tags,
        'status': doc('span[itemprop=updataStatus]').text(),
        'chap_count': len(chap_list),
        'vip_chap_id': vip_chap_id,
        'chap_list': chap_list
    }


def get_chapter_content(url):
    detail_res = httpx.get(url)
    detail_res.encoding = 'gb2312'
    doc = pq(detail_res.text)
    div = doc('.novelbody:nth-child(2) > div')
    div.remove('div:first-child')
    div.remove('div[align=right]')
    content = div.text()
    return content


def post_weibo(content):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(storage_state='weibo_state.json')
        page = context.new_page()
        page.goto("https://weibo.com/")
        page.get_by_placeholder("有什么新鲜事想分享给大家？").click()
        page.get_by_placeholder("有什么新鲜事想分享给大家？").fill(content)
        # 粉见
        # page.get_by_text("公开").click()
        # page.get_by_role("button", name="粉丝").click()
        page.get_by_role("button", name="发送").click()
        time.sleep(1)
        page.close()
        context.storage_state(path='weibo_state.json')
        context.close()
        browser.close()
# scheduler.add_job(ru:n_every_day_from_program_start, "interval", days=1, id="xxx")
# import asyncio
# asyncio.run(main())

if __name__ == '__main__':
    # init_data()
    # main()
    scheduler = BlockingScheduler()
    scheduler.add_job(main, "cron", hour='7-23', minute='0,20,40', jitter=20, id="novel_bot", max_instances=100)
    scheduler.start()