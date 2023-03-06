import json
def clean_old_novels():
    save_file = open('data/novel_data.json', 'r', encoding='utf-8')
    content = save_file.read()
    save_file.close()
    data_list =  json.loads(content)
    delist = []
    for index, novel in enumerate(data_list):
        if novel['publish_time'].startswith('2022-12'):
            print('delete' + str(novel))
            delist.append(novel)
    print(len(delist))
    for i in delist:
        data_list.remove(i)
    write_file = open('data/novel_data.json', 'w', encoding='utf-8')
    write_file.write(json.dumps(data_list, ensure_ascii=False))
    write_file.close()
clean_old_novels()