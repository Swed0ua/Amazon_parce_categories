import json
import xlsxwriter
import time
import datetime
import os

def writer(data, name):
    book = xlsxwriter.Workbook(f'./{name}.xlsx', {'strings_to_numbers': True})
    page = book.add_worksheet('products')

    row = 1
    column = 0
    
    page.set_column("A:A", 30)
    page.set_column("B:B", 30)
    page.set_column("C:C", 30)
    page.set_column("D:D", 30)
    page.set_column("E:E", 30)
    page.set_column("F:F", 30)
    page.set_column("G:G", 30)

    page.write(0, 0, 'node_id')
    page.write(0, 1, 'PATH')
    page.write(0, 2, 'child_nodes')
    page.write(0, 3, 'child_links')
    page.write(0, 4, 'result_default')
    page.write(0, 5, 'result_lows')
    page.write(0, 6, 'result_highs')
    page.write(0, 7, 'LINK')

    count = 0    

    for key in data:
        item = data[key]

        count += 1
        try:
            page.write(row, column, item["node_id"])
        except:
            exec
        try:
            page.write(row, column + 1, item['PATH'])
        except:
            exec
        try:
            page.write(row, column + 2, ','.join(item["child_nodes"]))
        except:
            exec
        try:
            page.write(row, column + 3, ','.join(item["child_links"]))
        except:
            exec
        try:
            page.write(row, column + 4, str(item['results']['default']))
        except:
            exec
        try:
            page.write(row, column + 5, str(item['results']['lows']))
        except:
            exec
        try:
            page.write(row, column + 6, str(item['results']['highs']))
        except:
            exec
        try:
            page.write(row, column + 7, item['link'])
        except:
            exec
        row += 1

    book.close()

def get_json_data(name, path = './'):
    with open(f'{path}{name}', 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def set_json_data(data, name_ind, path = './'):
    with open(f'{path}{name_ind}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

def main_writer(tp = False):
    folder_path = './4'
    file_list = os.listdir(folder_path)
    
    main_data = {}
    count = 1
    if tp:
        triger = "PATH"
    else:
        triger = "node_id"
    for file in file_list:
        print(f'file_name {file} // {count}')
        dt  = get_json_data(file, f'{folder_path}/')
        
        
        input_string = dt['PATH']
        middle = len(input_string) // 2
        first_half = input_string[:middle]
        second_half = input_string[middle:]

        if first_half == second_half:
            dt['PATH'] = first_half
        else:
            exec

        main_data[dt['node_id']] = dt
        count += 1
        # if count>10:
        #     break
    writer(main_data,'res_4')
    print(len(main_data))
    # set_json_data(main_data, 'ids', './names/')

main_writer(True)