import dearpygui.dearpygui as dpg
from sqlalchemy import String, Column,Text, Integer,MetaData,engine, text
import sqlalchemy as sql
import re

engine = sql.create_engine('sqlite:///bd.sqlite',echo=True)
connection = engine.connect()
metadata = MetaData()
metadata.create_all(engine)

dpg.create_context()

big_let_start = 0x00C0  # Capital "A" in cyrillic alphabet
big_let_end = 0x00DF  # Capital "Я" in cyrillic alphabet
small_let_end = 0x00FF  # small "я" in cyrillic alphabet
remap_big_let = 0x0410  # Starting number for remapped cyrillic alphabet
alph_len = big_let_end - big_let_start + 1  # adds the shift from big letters to small
alph_shift = remap_big_let - big_let_start  # adds the shift from remapped to non-remapped


with dpg.font_registry():
    with dpg.font("NotoMono-Regular.ttf", 20) as font1:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        dpg.bind_font(font1)       
        biglet = remap_big_let  # Starting number for remapped cyrillic alphabet
        for i1 in range(big_let_start, big_let_end + 1):  # Cycle through big letters in cyrillic alphabet
            dpg.add_char_remap(i1, biglet)  # Remap the big cyrillic letter
            dpg.add_char_remap(i1 + alph_len, biglet + alph_len)  # Remap the small cyrillic letter
            biglet += 1  # choose next letter

table_list_tag = ['GR_KONK','GR_PROJ','VUZ']
table_list_name_size = [['gr_konk',9],['gr_proj',16],['vuz',11]]
GR_KONK_label_list = [' ', 'k2', 'codkon', 'k12', 'k4', 'k41', 'k42', 'k43', 'k44', 'npr']
GR_PROJ_label_list = [' ', 'g1', 'codkon', 'codvuz', 'z2', 'g7', 'g5', 'g2', 'g21', 'g22', 'g23', 'g24', 'g6', 'g8', 'g9', 'g10', 'g11']
VUZ_label_list = [' ', 'codvuz', 'z1', 'z1full','z2','region', 'city', 'status', 'obl','oblname','gr_ved','prof']
window_specs = [['GR_KONK',0], ['GR_PROJ',1], ['VUZ',2]]

table_name_id = []

high_list = []
res_mas = []

specs_filter_list = []
filter_mas_1 = []
combo_id_mas = []

VUZ_row_num_list = []
GR_KONK_row_num_list = []
GR_PROJ_row_num_list = []

filter_string_VUZ  = ''
filter_string_GR_PROJ  = ''
filter_string_GR_KONK  = ''


def row_counter():
    result = connection.execute(text("SELECT ROW_NUMBER() OVER (ORDER BY " + k2 +") RowNum FROM " + info[1]))
    for row in result:
        eval(info[1].upper()+'_row_num_list').append([int(x) for x in row])
    for i in range(len(eval(info[1].upper()+'_row_num_list')+1)):
        eval(info[1].upper()+'_row_num_list')[i] = eval(info[1].upper()+'_row_num_list')[i][0]


def edit_callback(sender):
    print('hello')
    


def to_cyr(instr):  # conversion function
        out = []  # start with empty output
        for i in range(0, len(instr)):  # cycle through letters in input string
            if ord(instr[i]) in range(big_let_start, small_let_end + 1):  # check if the letter is cyrillic
                out.append(chr(ord(instr[i]) + alph_shift))  # if it is change it and add to output list
            else:
                out.append(instr[i])  # if it isn`t don`t change anything and just add it to output list
        return ''.join(out)  # convert list to string


def table_creation(info):
    result = connection.execute(text("SELECT * FROM " + info[0]))
    for row in result:
        with dpg.table_row():
            for j in range(-1,info[1]):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = info[1]+2)
                else:
                    dpg.add_text(f"{row[j]}")

def highlight_rows(sender, specs, user_data):
    _row = dpg.get_item_parent(sender)
    print(_row)
    _table = dpg.get_item_parent(_row)
    first_row = dpg.get_item_children(_table, 1)[0]
    print(first_row)
    _row_ = int((_row-first_row)/user_data)
    print(_row_)
    if(specs):
        if(len(high_list)==0):
            dpg.highlight_table_row(table = _table, row = _row_, color = (0,0,100))
            high_list.append([sender,_row_,_table])
            print(high_list)
        else:
            dpg.unhighlight_table_row(table = high_list[0][2], row = high_list[0][1])
            dpg.set_value(high_list[0][0],False)
            high_list.clear()
            dpg.highlight_table_row(table = _table, row = _row_, color = (0,0,100))
            high_list.append([sender,_row_,_table])
            print(high_list)
    else:
        dpg.unhighlight_table_row(table = _table, row = _row_)
        high_list.clear()
        print(high_list)

def sort_algo(col_id, s_dir, row, sender, ran):
    if(dpg.get_item_label(sender) == 'gr_konk'):
        info = table_list_name_size[0]
    elif(dpg.get_item_label(sender) == 'gr_proj'):
        info = table_list_name_size[1]
    else:
        info = table_list_name_size[2]
    
    col_id = [x-row for x in col_id]
    sorting_string = ""
    counter = 1
    for id,dir in zip(col_id, s_dir):
        print(id, dir)
        sorting_string += eval(dpg.get_item_label(sender).upper() + "_label_list[id]")
        if(dir == 1):
            sorting_string += " ASC"
        else:
            sorting_string += " DESC"
        if (len(s_dir)-counter>0): 
            sorting_string += ", "
        counter +=1

    result = connection.execute(text("SELECT * FROM (SELECT ROW_NUMBER() OVER (ORDER BY " + sorting_string +") RowNum, * FROM " + dpg.get_item_label(sender) +")" ))
    results_arr = []
    for _row in result:
        results_arr.append(list(_row))
    for i in range(len(results_arr)):
        for j in range(1,len(results_arr[0])):
            results_arr[i][j] = str(results_arr[i][j])
    mmas_1 = []
    mmas_2 = []
    for i in range(len(results_arr)):
        mmas_1.append(results_arr[i][0])
        mmas_2.append(results_arr[i][1:len(results_arr)])

    for i in zip(mmas_1,mmas_2):
        res_mas.append(i)
    for i in range(len(res_mas)):
        res_mas[i] = list(res_mas[i]) 

    result = connection.execute(text("SELECT * FROM (SELECT ROW_NUMBER() OVER (ORDER BY " + sorting_string +") RowNum, * FROM " + dpg.get_item_label(sender) +")" ))
    dpg.delete_item(sender, children_only=True)
    exec("for _label in " + dpg.get_item_label(sender).upper() + "_label_list: dpg.add_table_column(parent = sender,label=_label)")
    for _row in result:
        with dpg.table_row(parent = sender):
            for j in range(0,ran+1):
                if (j==0):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = info[1]+2)
                else:
                    dpg.add_text(f"{_row[j]}")

def sort_callback(sender, sort_specs):
    print(sort_specs)

    if(dpg.get_item_label(sender) == 'gr_konk'):
        info = table_list_name_size[0]
    elif(dpg.get_item_label(sender) == 'gr_proj'):
        info = table_list_name_size[1]
    else:
        info = table_list_name_size[2]
    
    if sort_specs is None: return
    if len(dpg.get_item_label(sort_specs[0][0]))==1: 
        for i in table_name_id:
            if i[1] == dpg.get_item_label(sender):
                dpg.delete_item(i[0], children_only=True)
                exec("for _label in " + dpg.get_item_label(sender).upper() + "_label_list: dpg.add_table_column(parent = i[0],label=_label)")
                result = connection.execute(text("SELECT * FROM " + info[0]))
                for _row in result:
                    with dpg.table_row(parent = i[0]):
                        for j in range(-1,len(_row)):
                            if (j==-1):
                                dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = info[1]+2)
                            else:
                                dpg.add_text(f"{_row[j]}")
        return
    
    if len(high_list)==1:
        dpg.unhighlight_table_row(table = high_list[0][2], row = high_list[0][1])
        dpg.set_value(high_list[0][0],False)
        high_list.clear()
    
    column_id = []
    direction = []
    if(len(sort_specs)==1):
        column_id.append(sort_specs[0][0])
        direction.append(sort_specs[0][1])
    else:
        for i in sort_specs:
            column_id.append(i[0])
            direction.append(i[1])

    row = dpg.get_item_children(sender, 1)[0]
    if(dpg.get_item_label(sender) == "gr_proj"):
        row-=17
        ran = 16
    elif(dpg.get_item_label(sender) == 'vuz'):
        row-=12
        ran = 11
    elif(dpg.get_item_label(sender) =='gr_konk'):
        row-=10
        ran = 9

    sort_algo(column_id, direction, row, sender, ran)
    res_mas.clear()
    column_id.clear()
    direction.clear()

def gr_konk_viz(sender):
    dpg.show_item('GR_KONK')

def gr_proj_viz(sender):
    dpg.show_item('GR_PROJ')


def closing_filter_window(sender):
    dpg.delete_item('filter_combo_input')

def closing_inst_window(sender):
    dpg.delete_item('INS')

def reset_filter(sender, specs,user_data):
    for i in combo_id_mas:
        dpg.delete_item(i, children_only=False)

    specs_filter_list.clear()
    combo_id_mas.clear()

    if(user_data == 'gr_konk'):
        info = table_list_name_size[0]
    elif(user_data == 'gr_proj'):
        info = table_list_name_size[1]
    else:
        info = table_list_name_size[2]

    if len(high_list)==1:
        dpg.unhighlight_table_row(table = high_list[0][2], row = high_list[0][1])
        dpg.set_value(high_list[0][0],False)
        high_list.clear()

    for i in table_list_name_size:
            if i[0] == user_data:
                for j in range(i[1]):
                    result = connection.execute(text("SELECT DISTINCT " + eval(i[0].upper() + '_label_list[j+1]') + " FROM " + user_data))
                    for row in result:
                        filter_mas_1.append([str(x) for x in row])
                    for c in range(len(filter_mas_1)):
                        filter_mas_1[c] = filter_mas_1[c][0]
                    combo = dpg.add_combo(parent = 'filter_combo_input', label = eval(i[0].upper() + '_label_list[j+1]') , callback = filtering,
                                                                user_data = [user_data,eval("filter_string_" + i[0].upper())], items = filter_mas_1)
                    combo_id_mas.append(combo)
                    filter_mas_1.clear()
    
    for i in table_name_id:
        if i[1] == user_data:
            dpg.delete_item(i[0], children_only=True)
            exec("for _label in " + user_data.upper() + "_label_list: dpg.add_table_column(parent = i[0],label=_label)")
            result = connection.execute(text("SELECT * FROM " + info[0]))
            for _row in result:
                with dpg.table_row(parent = i[0]):
                    for j in range(-1,len(_row)):
                        if (j==-1):
                            dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = info[1]+2)
                        else:
                            dpg.add_text(f"{_row[j]}")
    

def vuz_viz(sender):
    dpg.show_item('VUZ')

def combo_win_select(sender, specs):
    specs_filter_list.clear()
    combo_id_mas.clear()
    print(specs)
    if(not dpg.does_item_exist('filter_combo_input')):
        with dpg.window(tag = 'filter_combo_input', width = 300, height = 200, no_title_bar = True, no_resize = True):
            dpg.set_item_pos('filter_combo_input', (25, 450))
            dpg.add_button(label = 'Сброс фильтра', callback = reset_filter, user_data = specs)
            for i in table_list_name_size:
                    if (specs == i[0]):
                        for j in range(i[1]):
                            if len(eval("filter_string_" + i[0].upper())) == 0:
                                result = connection.execute(text("SELECT DISTINCT " + eval(i[0].upper() + '_label_list[j+1]') + " FROM " + specs))
                            for row in result:
                                filter_mas_1.append([str(x) for x in row])
                            for c in range(len(filter_mas_1)):
                                filter_mas_1[c] = filter_mas_1[c][0]
                            combo = dpg.add_combo(label = eval(i[0].upper() + '_label_list[j+1]') , callback = filtering,
                                                         user_data = [specs,eval("filter_string_" + i[0].upper())], items = filter_mas_1)
                            combo_id_mas.append(combo)
                            filter_mas_1.clear()
    else:
        dpg.delete_item('filter_combo_input')
        with dpg.window(tag = 'filter_combo_input', width = 300, height = 200, no_title_bar = True, no_resize = True):
            dpg.set_item_pos('filter_combo_input', (25, 450))
            dpg.add_button(label = 'Сброс фильтра', callback = reset_filter, user_data = specs)
            for i in table_list_name_size:
                    if (specs == i[0]):
                        for j in range(i[1]):
                            if len(eval("filter_string_" + i[0].upper())) == 0:
                                result = connection.execute(text("SELECT DISTINCT " + eval(i[0].upper() + '_label_list[j+1]') + " FROM " + specs))
                            for row in result:
                                filter_mas_1.append([str(x) for x in row])
                            for c in range(len(filter_mas_1)):
                               filter_mas_1[c] = filter_mas_1[c][0]
                            combo = dpg.add_combo(label = eval(i[0].upper() + '_label_list[j+1]') , callback = filtering,
                                                         user_data = [specs,eval("filter_string_" + i[0].upper())], items = filter_mas_1)
                            combo_id_mas.append(combo)
                            filter_mas_1.clear()

def filtering(sender,specs, user_data):
    print(specs, dpg.get_item_label(sender))
    print(user_data)

    if len(high_list)==1:
        dpg.unhighlight_table_row(table = high_list[0][2], row = high_list[0][1])
        dpg.set_value(high_list[0][0],False)
        high_list.clear()

    cheker = False
    specs = to_cyr(specs)
    if [dpg.get_item_label(sender),specs] not in specs_filter_list:
            if(len(specs_filter_list)==0):
                specs_filter_list.append([dpg.get_item_label(sender), specs])
            elif(len(specs_filter_list)!=0):
                for i in range(0,len(specs_filter_list)):
                    if(dpg.get_item_label(sender) == specs_filter_list[i][0] and specs != specs_filter_list[i][1]):
                        specs_filter_list[i][1] = specs
                        cheker = True
                        break
                if(not cheker):
                    specs_filter_list.append([dpg.get_item_label(sender), specs])
    print(specs_filter_list)
    
    if(user_data[1].find(dpg.get_item_label(sender)) == -1):
        counter = 1
        for i in specs_filter_list:
            user_data[1]  += i[0] + '=' + "'"+ i[1] + "' "
            if len(specs_filter_list) - counter != 0:
                user_data[1] += ' AND '
                counter+=1
    else:
        result = re.search(r'' +dpg.get_item_label(sender) + '.*\s' , user_data[1])
        result = result.group(0)
        user_data[1] = user_data[1].replace(result,'')
        counter = 1
        for i in specs_filter_list:
            user_data[1]  += i[0] + '=' + "'"+ i[1] + "' "
            if len(specs_filter_list) - counter != 0:
                    user_data[1] += ' AND '
                    counter+=1

    print(user_data[1])

    if(user_data[0] == 'gr_konk'):
        info = table_list_name_size[0]
    elif(user_data[0] == 'gr_proj'):
        info = table_list_name_size[1]
    else:
        info = table_list_name_size[2]
    

    for i in table_list_name_size:
        if (user_data[0] == i[0]):
            for j in range(i[1]):
                result = connection.execute(text("SELECT DISTINCT " + eval(i[0].upper() + '_label_list[j+1]') + " FROM " + i[0] + " WHERE " + user_data[1]))
                for row in result:
                    filter_mas_1.append([str(x) for x in row])
                for c in range(len(filter_mas_1)):
                    filter_mas_1[c] = filter_mas_1[c][0]
                a=0
                for x in specs_filter_list:
                    if(dpg.get_item_label(combo_id_mas[j]) != x[0]):
                        a+=1
                if a == len(specs_filter_list):
                    dpg.delete_item(combo_id_mas[j])
                    combo_id_mas[j] = dpg.add_combo(parent = 'filter_combo_input', label = eval(i[0].upper() + '_label_list[j+1]') , callback = filtering,
                                                                user_data = [user_data[0],eval("filter_string_" + i[0].upper())], items = filter_mas_1)
                else:
                    dpg.disable_item(combo_id_mas[j])
                filter_mas_1.clear()
    

    if(len(specs_filter_list)==0):
        for i in table_name_id:
            if i[1] == user_data[0]:
                dpg.delete_item(i[0], children_only=True)
                exec("for _label in " + user_data[0].upper() + "_label_list: dpg.add_table_column(parent = i[0],label=_label)")
                result = connection.execute(text("SELECT * FROM " + info[0]))
                for _row in result:
                    with dpg.table_row(parent = i[0]):
                        for j in range(-1,len(_row)):
                            if (j==-1):
                                dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = info[1]+2)
                            else:
                                dpg.add_text(f"{_row[j]}")
    else:
        for i in table_name_id:
            if i[1] == user_data[0]:
                dpg.delete_item(i[0], children_only=True)
                exec("for _label in " + user_data[0].upper() + "_label_list: dpg.add_table_column(parent = i[0],label=_label)")
                result = connection.execute(text("SELECT * FROM " + user_data[0] + " WHERE " + user_data[1]))
                user_data[1] = ''
                for _row in result:
                    with dpg.table_row(parent = i[0]):
                        for j in range(-1,len(_row)):
                            if (j==-1):
                                dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = info[1]+2)
                            else:
                                dpg.add_text(f"{_row[j]}")


def filter_btn(sender):
    if(not dpg.does_item_exist('FILTER')):
        with dpg.window(tag = 'FILTER', label = "Фильтр", width = 350, height = 300, on_close = closing_filter_window):
            dpg.set_item_pos('FILTER', (25, 350))
            combo = dpg.add_combo(items = ("gr_konk","gr_proj","vuz"), callback = combo_win_select)
    dpg.show_item('FILTER')

def delete_btn(sender):
    if(not dpg.does_item_exist('DELETE')):
        with dpg.window(tag = 'DELETE', label = "Удаление", width = 200, height = 200, modal = True):
            dpg.add_input_text()
    dpg.show_item('DELETE')

def edit_btn(sender):
    if(not dpg.does_item_exist('EDIT')):
        with dpg.window(tag = 'EDIT', label = "Редактирование", width = 400, height = 400):
            dpg.add_text()
            for i in range(16):
                dpg.add_input_text(label = GR_PROJ_label_list[i+1])

    dpg.show_item('EDIT')

def add_row_btn(sender):
    if(not dpg.does_item_exist('ADD_ROW')):
        with dpg.window(tag = 'ADD_ROW', label = "Добавить строку", width = 200, height = 200, modal = True):
            dpg.add_input_text()
    dpg.show_item('ADD_ROW')

def add_copy_btn(sender):
    if(not dpg.does_item_exist('COPY')):
        with dpg.window(tag = 'COPY', label = "Скопировать выделенное", width = 200, height = 200, modal = True):
            dpg.add_input_text()
    dpg.show_item('COPY')

def inst_window(sender):
    with dpg.window(tag = 'INS', label = "Инструменты", width = 200, height = 200, on_close = closing_inst_window):
        dpg.set_item_pos("INS",(25,50))
        dpg.add_button(label = 'Фильтр', callback = filter_btn)
        dpg.add_button(label = 'Удалить', callback =  delete_btn)
        dpg.add_button(label = 'Редактировать', callback = edit_btn)
        dpg.add_button(label = 'Копировать', callback = add_copy_btn)
        dpg.add_button(label = 'Добавить в конец', callback = add_row_btn)
        

with dpg.window(tag = 'Main Window', height = 720, width = 1280):
    dpg.set_primary_window("Main Window", True)
    with dpg.viewport_menu_bar():
        with dpg.menu(label="Таблицы"):
            dpg.add_menu_item(label="gr_konk" , callback = gr_konk_viz)
            dpg.add_menu_item(label="gr_proj", callback = gr_proj_viz)
            dpg.add_menu_item(label="vuz", callback = vuz_viz)
        with dpg.menu(label="Экспорт"):
            dpg.add_menu_item(label="Экспорт в файл")
        with dpg.menu(label="Инструменты"):
            dpg.add_menu_item(label="Для работы с таблицами", callback = inst_window)
        for i in window_specs:
            with dpg.window(tag = i[0], label  = i[0], width = 820, height = 660, show = False):
                dpg.set_item_pos(i[0],(400,50))
                with dpg.table(label = i[0].lower(),header_row=True, row_background=True,
                            borders_innerH=True, borders_outerH=True, borders_innerV=True,
                            borders_outerV=True, resizable = False, width = 800,height = 600, scrollX=True, scrollY=True, no_keep_columns_visible=True, 
                            policy = dpg.mvTable_SizingFixedFit, sortable = True, callback=sort_callback, sort_multi=True):
                    table_name_id.append([dpg.last_item(), i[0].lower()])
                    for _label in eval( i[0] + '_label_list'):
                        dpg.add_table_column(label=_label)

                    table_creation(table_list_name_size[i[1]])

dpg.create_viewport(title='Custom Title')
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
    