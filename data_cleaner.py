import json, sys
def clean_old_novels(arg):
    save_file = open('data/novel_data.json', 'r', encoding='utf-8')
    content = save_file.read()
    save_file.close()
    data_list =  json.loads(content)
    delist = []
    for index, novel in enumerate(data_list):
        if novel['publish_time'].startswith(arg):
            print('delete' + str(novel))
            delist.append(novel)
    print(len(delist))
    for i in delist:
        data_list.remove(i)
    write_file = open('data/novel_data.json', 'w', encoding='utf-8')
    write_file.write(json.dumps(data_list, ensure_ascii=False))
    write_file.close()


if __name__ == '__main__':
    arg = sys.argv
    print(f'clean novel in: {arg[1]}')
    clean_old_novels(arg[1])