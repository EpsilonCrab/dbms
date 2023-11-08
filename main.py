import dearpygui.dearpygui as dpg
from sqlalchemy import String, Column,Text, Integer,MetaData,engine, text
import sqlalchemy as sql
import re
import keyboard

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

def to_cyr(instr):  # conversion function
        out = []  # start with empty output
        for i in range(0, len(instr)):  # cycle through letters in input string
            if ord(instr[i]) in range(big_let_start, small_let_end + 1):  # check if the letter is cyrillic
                out.append(chr(ord(instr[i]) + alph_shift))  # if it is change it and add to output list
            else:
                out.append(instr[i])  # if it isn`t don`t change anything and just add it to output list
        return ''.join(out)  # convert list to string

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
GR_PROJ_label_list = [' ', 'codkon', 'g1','g8','g7','z2','g5','g2','g21','g22','g23','g24','codvuz','g6','g9','g10','g11']
VUZ_label_list = [' ', 'codvuz', 'z1', 'z1full','z2','region', 'city', 'status', 'obl','oblname','gr_ved','prof']
window_specs = [['GR_KONK',0], ['GR_PROJ',1], ['VUZ',2]]

GR_KONK_label_list_ru = [' ', 'Конкурс', 'Код конкурса', 'Плановый объем гранта', 'Фактический объем гранта', '1-ый кв', '2-ой кв', '3-ий кв', '4-ый кв', 'кол-во НИР по грантам']
GR_PROJ_label_list_ru  = [' ','Код конкурса', 'Код НИР', 'Руководитель НИР', 'ГРНТИ','ВУЗ', 'Плановый объем гранта', 'Фактический объем гранта',
 '1-ый кв', '2-ой кв', '3-ий кв', '4-ый кв', 'Код вуза', 'НИР',  'Должность', 'Ученое звание', 'Ученая степень']
VUZ_label_list_ru  = [' ', 'Код вуза', 'ВУЗ', 'Юр наз-ие ВУЗа','Наименование','Фед. округ', 'Город', 'Статус', 'Субъект','Область','gr_ved','Направленность']

VUZ_z2_codvuz_dict = {}

result = connection.execute(text("SELECT DISTINCT z2,codvuz FROM vuz"))
for pairs in result:
    VUZ_z2_codvuz_dict[pairs[0]] = pairs[1]

table_name_id = []

high_list = []
res_mas = []

specs_filter_list = []
filter_mas_1 = []
combo_id_mas = []

VUZ_row_num_list = []
GR_KONK_row_num_list = []
GR_PROJ_row_num_list = []

filter_string = ''
new_formed_filter_string = ''

codkon_list = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17']

def planned_and_actual_financing():
    for i in codkon_list:
        try:
            result = connection.execute(text("SELECT SUM(g5) FROM gr_proj WHERE codkon='" + i + "'"))
            add_mas = []
            for row in result:
                add_mas.append([str(x) for x in row])
            for c in range(len(add_mas)):
                add_mas[c] = add_mas[c][0]
            connection.execute(text("UPDATE gr_konk SET k12=" + add_mas[0] + " WHERE codkon='" + i + "'" ))
            add_mas.clear()
            connection.execute(text("COMMIT"))
        except:
            print("Неверный SQL запрос")
            continue
        try:
            result = connection.execute(text("SELECT SUM(g2) FROM gr_proj WHERE codkon='" + i + "'"))
            for row in result:
                add_mas.append([str(x) for x in row])
            for c in range(len(add_mas)):
                add_mas[c] = add_mas[c][0]
            connection.execute(text("UPDATE gr_konk SET k4=" + add_mas[0]+ " WHERE codkon='" + i + "'"))
            add_mas.clear()
            connection.execute(text("COMMIT"))
        except:
            print("Неверный SQL запрос")

        try:
            result = connection.execute(text("SELECT SUM(g21) FROM gr_proj WHERE codkon='" + i + "'"))
            for row in result:
                add_mas.append([str(x) for x in row])
            for c in range(len(add_mas)):
                add_mas[c] = add_mas[c][0]
            connection.execute(text("UPDATE gr_konk SET k41=" + add_mas[0]+ " WHERE codkon='" + i + "'"))
            add_mas.clear()
            connection.execute(text("COMMIT"))
        except:
            print("Неверный SQL запрос")

        try:
            result = connection.execute(text("SELECT SUM(g22) FROM gr_proj WHERE codkon='" + i + "'"))
            for row in result:
                add_mas.append([str(x) for x in row])
            for c in range(len(add_mas)):
                add_mas[c] = add_mas[c][0]
            connection.execute(text("UPDATE gr_konk SET k42=" + add_mas[0]+ " WHERE codkon='" + i + "'"))
            add_mas.clear()
            connection.execute(text("COMMIT"))
        except:
            print("Неверный SQL запрос")

        try:
            result = connection.execute(text("SELECT SUM(g23) FROM gr_proj WHERE codkon='" + i + "'"))
            for row in result:
                add_mas.append([str(x) for x in row])
            for c in range(len(add_mas)):
                add_mas[c] = add_mas[c][0]
            connection.execute(text("UPDATE gr_konk SET k43=" + add_mas[0]+ " WHERE codkon='" + i + "'"))
            add_mas.clear()
            connection.execute(text("COMMIT"))
        except:
            print("Неверный SQL запрос")

        try:
            result = connection.execute(text("SELECT SUM(g24) FROM gr_proj WHERE codkon='" + i + "'"))
            for row in result:
                add_mas.append([str(x) for x in row])
            for c in range(len(add_mas)):
                add_mas[c] = add_mas[c][0]
            connection.execute(text("UPDATE gr_konk SET k44=" + add_mas[0]+ " WHERE codkon='" + i + "'"))
            add_mas.clear()
            connection.execute(text("COMMIT"))
        except:
            print("Неверный SQL запрос")

    dpg.delete_item(table_name_id[0][0], children_only=True)
    exec("for _label in " + "GR_KONK" + "_label_list_ru: dpg.add_table_column(parent = table_name_id[0][0],label=_label)")
    result = connection.execute(text("SELECT * FROM gr_konk"))
    for row in result:
        with dpg.table_row(parent = table_name_id[0][0]):
            for j in range(-1,9):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = 11)
                else:
                    dpg.add_text(f"{row[j]}")


def codkon_row_counter():
    for i in codkon_list:
        try:
            result = connection.execute(text("SELECT COUNT(*) FROM gr_proj WHERE codkon='" + i + "'"))
            add_mas=[]
            for row in result:
                add_mas.append([str(x) for x in row])
            for c in range(len(add_mas)):
                add_mas[c] = add_mas[c][0]
            connection.execute(text("UPDATE gr_konk SET npr=" + add_mas[0] + " WHERE codkon='" + i + "'"))
            add_mas.clear()
            connection.execute(text("COMMIT"))
        except:
            print("Неверный SQL запрос")
            continue

    dpg.delete_item(table_name_id[0][0], children_only=True)
    exec("for _label in " + "GR_KONK" + "_label_list_ru: dpg.add_table_column(parent = table_name_id[0][0],label=_label)")
    result = connection.execute(text("SELECT * FROM gr_konk"))
    for row in result:
        with dpg.table_row(parent = table_name_id[0][0]):
            for j in range(-1,9):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = 11)
                else:
                    dpg.add_text(f"{row[j]}")

edit_input = []
add_row_input = []
add_row_id = []

def edit_callback(sender,specs):
    sender_label = dpg.get_item_label(sender)
    specs = to_cyr(specs)
    high_list_copy = []
    if sender_label in ['g1','codkon','codvuz','g7','g5','g2','g21','g22','g23','g24']:
        result = re.search(r'' + "[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\/#$%&'\"()*+\\\:;<=>?@[\]\^_`{|}~абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ ]*",specs )
        result = result.group(0)
        print(result)
        if len(result) != len(specs):
            print('Введены недопустимые символы для данного поля')
            edit_btn()
            return

    for i in range(len(high_list[1])):
        high_list_copy.append(high_list[1][i])

    for i in range(0,16):
        if sender_label == GR_PROJ_label_list_ru[i+1]:
            high_list[1][i]=specs
    if sender_label == 'ВУЗ':
        print(VUZ_z2_codvuz_dict[specs])
        high_list[1][11] = str(VUZ_z2_codvuz_dict[specs])

    try:
        connection.execute(text("UPDATE gr_proj SET codkon='"+ high_list[1][0] +"', g1='" + high_list[1][1] + "', g8='" + high_list[1][2] + "', g7='" + high_list[1][3] + 
        "', z2='" + high_list[1][4] + "', g5='" + high_list[1][5] + "', g2='" + high_list[1][6] + "', g21='" + high_list[1][7] + "', g22='" + high_list[1][8] + "', g23='" + high_list[1][9] + 
        "', g24='" + high_list[1][10] + "', codvuz='" + high_list[1][11] + "', g6='" + high_list[1][12] + "', g9='" + high_list[1][13] + "', g10='" + high_list[1][14] + "', g11='" + high_list[1][15]+
        "' WHERE codkon='"+ high_list_copy[0] +"' AND g1='" + high_list_copy[1] + "' AND g8='" + high_list_copy[2] + "' AND g7='" + high_list_copy[3] + 
        "' AND z2='" + high_list_copy[4] + "' AND g5=" + high_list_copy[5] + " AND g2=" + high_list_copy[6] + " AND g21=" + high_list_copy[7] + " AND g22=" + high_list_copy[8] + " AND g23=" + high_list_copy[9] + 
        " AND g24=" + high_list_copy[10] + " AND codvuz='" + high_list_copy[11] + "' AND g6='" + high_list_copy[12] + "' AND g9='" + high_list_copy[13] + "' AND g10='" + high_list_copy[14] + "' AND g11='" + high_list_copy[15]+"'"))
    except:
        print()
        print("Нельзя выполнить SQL запрос")
        
        for i in range(16):
            high_list[1][i] = high_list_copy[i]
        edit_btn()
        return
    connection.execute(text("COMMIT"))
    planned_and_actual_financing()
    codkon_row_counter()
    dpg.delete_item(table_name_id[1][0], children_only=True)
    exec("for _label in " + "GR_PROJ" + "_label_list_ru: dpg.add_table_column(parent = table_name_id[1][0],label=_label)")
    result = connection.execute(text("SELECT codkon, g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11 FROM gr_proj"))
    counter = 0
    for _row in result:
        with dpg.table_row(parent = table_name_id[1][0]):
            for j in range(-1,len(_row)):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = 18)
                    if(counter==high_list[0][1]):
                        high_list[0][0] = dpg.last_item()
                        dpg.highlight_table_row(table = high_list[0][2], row = high_list[0][1], color = (0,0,100))
                        dpg.set_value(dpg.last_item(), True)
                else:
                    dpg.add_text(f"{_row[j]}")
        counter+=1
    
def delete_callback():
    try:
        connection.execute(text("DELETE FROM gr_proj " + "WHERE codkon='"+ high_list[1][0] +"' AND g1='" + high_list[1][1] + "' AND g8='" + high_list[1][2] + "' AND g7='" + high_list[1][3] + 
        "' AND z2='" + high_list[1][4] + "' AND g5=" + high_list[1][5] + " AND g2=" + high_list[1][6] + " AND g21=" + high_list[1][7] + " AND g22=" + high_list[1][8] + " AND g23=" + high_list[1][9] + 
        " AND g24=" + high_list[1][10] + " AND codvuz='" + high_list[1][11] + "' AND g6='" + high_list[1][12] + "' AND g9='" + high_list[1][13] + "' AND g10='" + high_list[1][14] + "' AND g11='" + high_list[1][15]+"'"))
        high_list.clear()
    except:
        print("Неверный SQL запрос")
        return
    connection.execute(text("COMMIT"))
    codkon_row_counter()
    planned_and_actual_financing()
    dpg.delete_item(table_name_id[1][0], children_only=True)
    exec("for _label in " + "GR_PROJ" + "_label_list_ru: dpg.add_table_column(parent = table_name_id[1][0],label=_label)") 
    result = connection.execute(text("SELECT codkon, g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11 FROM gr_proj"))
    for _row in result:
        with dpg.table_row(parent = table_name_id[1][0]):
            for j in range(-1,len(_row)):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = 18)
                else:
                    dpg.add_text(f"{_row[j]}")
    dpg.hide_item("DELETE")

def sorter(info):
    return info[0]

def add_row_callback():
    for c in range(7,12):
        add_row_input.append([c,'0'])
    print(add_row_input)
    if(len(add_row_input)<16):
        print('Введите все значения в поля')
        return
    print(add_row_input)
    add_row_input.sort(key = sorter)
    add_row_string = ''
    for i in range(16):
        if i !=15:
            add_row_string += "'" + add_row_input[i][1] + "'" + ', '
        else:
            add_row_string += "'" + add_row_input[i][1] + "'"

    print(add_row_string)
    try:
        connection.execute(text("INSERT INTO gr_proj (codkon, g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11) VALUES (" + add_row_string + ")"))
    except:
        print('Неверный SQL запрос')
        return

    add_row_input.clear()
    connection.execute(text('COMMIT'))
    planned_and_actual_financing()
    codkon_row_counter()
    dpg.delete_item(table_name_id[1][0], children_only=True)
    exec("for _label in " + "GR_PROJ" + "_label_list_ru: dpg.add_table_column(parent = table_name_id[1][0],label=_label)")
    result = connection.execute(text("SELECT codkon, g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11 FROM gr_proj"))
    for _row in result:
        with dpg.table_row(parent = table_name_id[1][0]):
            for j in range(-1,len(_row)):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = 18)
                else:
                    dpg.add_text(f"{_row[j]}")

def clear_add_row():
    for i in range(len(add_row_id)):
        dpg.delete_item(add_row_id[i])
    add_row_id.clear()
    for i in range(17):
        if i in [0,7,8,9,10,11,12]:
            continue
        else:
            if i == 13:
                add_row_id_1 = dpg.add_input_text(parent = 'ADD_ROW',width = 400, label = GR_PROJ_label_list_ru[i], multiline= True, callback = add_row_text_input)
            elif i==2:
                result = connection.execute(text("SELECT MAX(g1) FROM gr_proj" ))
                add_mas = []
                for row in result:
                    add_mas.append([str(x) for x in row])
                for c in range(len(add_mas)):
                    add_mas[c] = add_mas[c][0]
                add_row_id_1 = dpg.add_input_text(parent = 'ADD_ROW',width = 400, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input, default_value = str(int(add_mas[0])+1), decimal=True, on_enter=True)
                add_mas.clear()
            elif i == 1:
                result = connection.execute(text("SELECT DISTINCT codkon FROM gr_proj" ))
                add_mas = []
                for row in result:
                    add_mas.append([str(x) for x in row])
                for c in range(len(add_mas)):
                    add_mas[c] = add_mas[c][0]
                add_mas.sort()
                add_row_id_1 = dpg.add_combo(parent = 'ADD_ROW',width = 400, items = add_mas, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input)
                add_mas.clear()
            elif i == 5:
                result = connection.execute(text("SELECT DISTINCT z2 FROM vuz" ))
                add_mas = []
                for row in result:
                    add_mas.append([str(x) for x in row])
                for c in range(len(add_mas)):
                    add_mas[c] = add_mas[c][0]
                add_mas.sort()
                add_row_id_1 = dpg.add_combo(parent = 'ADD_ROW',width = 400, items = add_mas, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input)
                add_mas.clear()
            elif i == 4 or i == 6 :
                add_row_id_1 = dpg.add_input_text(parent = 'ADD_ROW',width = 400, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input, decimal=True)
            else: 
                add_row_id_1 = dpg.add_input_text(parent = 'ADD_ROW',width = 400, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input )
        add_row_id.append(add_row_id_1)

def delete_no_callback(sender):
    _window = dpg.get_item_parent(sender)
    dpg.hide_item(_window)

def table_creation(info):
    if info[0] == 'gr_proj':
        result = connection.execute(text("SELECT codkon, g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11 FROM " + info[0]))
    else:
        result = connection.execute(text("SELECT * FROM " + info[0]))
    for row in result:
        with dpg.table_row():
            for j in range(-1,info[1]):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = info[1]+2)
                else:
                    dpg.add_text(f"{row[j]}")
    planned_and_actual_financing()
    codkon_row_counter()

def highlight_rows(sender, specs, user_data):
    _row = dpg.get_item_parent(sender)
    _table = dpg.get_item_parent(_row)
    first_row = dpg.get_item_children(_table, 1)[0]
    _row_ = int((_row-first_row)/user_data)
    cols = []
    for a in range(2,user_data):
        cols.append(dpg.get_value(_row+a))
    if(specs):
        if(len(high_list)==0):
            dpg.highlight_table_row(table = _table, row = _row_, color = (0,0,100))
            high_list.append([sender,_row_,_table])
            high_list.append(cols)
            print(high_list)
        else:
            dpg.unhighlight_table_row(table = high_list[0][2], row = high_list[0][1])
            dpg.set_value(high_list[0][0],False)
            high_list.clear()
            dpg.highlight_table_row(table = _table, row = _row_, color = (0,0,100))
            high_list.append([sender,_row_,_table])
            high_list.append(cols)
            print(high_list)
    else:
        dpg.unhighlight_table_row(table = _table, row = _row_)
        high_list.clear()
        print(high_list)
    edit_btn()

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

    if(dpg.get_item_label(sender) == 'gr_proj'):
        result = connection.execute(text("SELECT codkon,g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11 FROM " + dpg.get_item_label(sender) + " ORDER BY " + sorting_string))
    else:
        result = connection.execute(text("SELECT * FROM " + dpg.get_item_label(sender) + " ORDER BY " + sorting_string))
    dpg.delete_item(sender, children_only=True)
    exec("for _label in " + dpg.get_item_label(sender).upper() + "_label_list_ru: dpg.add_table_column(parent = sender,label=_label)")
    for _row in result:
        with dpg.table_row(parent = sender):
            for j in range(-1,ran):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = info[1]+2)
                else:
                    dpg.add_text(f"{_row[j]}")
    high_list.clear()

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
                exec("for _label in " + dpg.get_item_label(sender).upper() + "_label_list_ru: dpg.add_table_column(parent = i[0],label=_label)")
                if dpg.get_item_label(sender) == 'gr_proj':
                    result = connection.execute(text( "SELECT codkon, g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11 FROM " + info[0]))
                else:
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

def vuz_viz(sender):
    dpg.show_item('VUZ')

def hide_filter_callback():
    dpg.hide_item('FILTER')

def reset_filter(sender, specs,user_data):
    for i in combo_id_mas:
        dpg.delete_item(i[1], children_only=False)

    specs_filter_list.clear()
    combo_id_mas.clear()

    if len(high_list)==1:
        dpg.unhighlight_table_row(table = high_list[0][2], row = high_list[0][1])
        dpg.set_value(high_list[0][0],False)
        high_list.clear()

    for i,j in {'region':'Фед. округ','Oblname':'Субъект фед.','City': 'Город','z1':'ВУЗ'}.items():
        result = connection.execute(text("SELECT DISTINCT " + i + " FROM vuz"))
        for row in result:
            filter_mas_1.append([str(x) for x in row])
        for c in range(len(filter_mas_1)):
            filter_mas_1[c] = filter_mas_1[c][0]
        filter_mas_1.sort()
        combo = dpg.add_combo(parent = 'FILTER', label = j, callback = filtering, items = filter_mas_1, user_data = [i,filter_string])
        combo_id_mas.append([i,combo])
        filter_mas_1.clear()
    
    dpg.delete_item(table_name_id[1][0], children_only=True)
    exec("for _label in " + "GR_PROJ" + "_label_list_ru: dpg.add_table_column(parent = table_name_id[1][0],label=_label)")
    result = connection.execute(text("SELECT codkon,g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11 FROM gr_proj"))
    for _row in result:
        with dpg.table_row(parent = table_name_id[1][0]):
            for j in range(-1,len(_row)):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = 18)
                else:
                    dpg.add_text(f"{_row[j]}")

def set_filter_callback():
    if len(new_formed_filter_string)==0:
        return
    dpg.delete_item(table_name_id[1][0], children_only=True)
    exec("for _label in " + "GR_PROJ" + "_label_list_ru: dpg.add_table_column(parent = table_name_id[1][0],label=_label)")
    result = connection.execute(text("SELECT codkon,g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11 FROM gr_proj WHERE " + new_formed_filter_string))
    for _row in result:
        with dpg.table_row(parent = table_name_id[1][0]):
            for j in range(-1,len(_row)):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = 18)
                else:
                    dpg.add_text(f"{_row[j]}")

def filtering(sender,specs, user_data):
    print(specs, dpg.get_item_label(sender))

    if len(high_list)==1:
        dpg.unhighlight_table_row(table = high_list[0][2], row = high_list[0][1])
        dpg.set_value(high_list[0][0],False)
        high_list.clear()

    cheker = False
    specs = to_cyr(specs)
    if [user_data[0],specs] not in specs_filter_list:
            if(len(specs_filter_list)==0):
                specs_filter_list.append([user_data[0], specs])
            else:
                for i in range(len(specs_filter_list)):
                    if(user_data[0] == specs_filter_list[i][0] and specs != specs_filter_list[i][1]):
                        specs_filter_list[i][1] = specs
                        cheker = True
                        break
                if(not cheker):
                    specs_filter_list.append([user_data[0], specs])
    print(specs_filter_list)
    
    if(user_data[1].find(user_data[0]) == -1):
        counter = 1
        for i in specs_filter_list:
            user_data[1]  += i[0] + '=' + "'"+ i[1] + "' "
            if len(specs_filter_list) - counter != 0:
                user_data[1] += ' AND '
                counter+=1
    else:
        result = re.search(r'' + user_data[0] + '.*\s' , user_data[1])
        result = result.group(0)
        user_data[1] = user_data[1].replace(result,'')
        counter = 1
        for i in specs_filter_list:
            user_data[1]  += i[0] + '=' + "'"+ i[1] + "' "
            if len(specs_filter_list) - counter != 0:
                    user_data[1] += ' AND '
                    counter+=1

    to_remove = []
    a=0
    for i in range(len(combo_id_mas)):
        for j in range(len(specs_filter_list)):
            if specs_filter_list[j][0] != combo_id_mas[i][0]:
                a+=1
            if a == len(specs_filter_list):
                dpg.delete_item(combo_id_mas[i][1])
                to_remove.append(combo_id_mas[i])
        a=0
    for i in to_remove:
        combo_id_mas.remove(i)
    to_remove.clear()

    check_mas = ['region','Oblname','City','z1']

    for i in specs_filter_list:
        if i[0] in check_mas:
            check_mas.remove(i[0])

    for i in check_mas:
        result = connection.execute(text("SELECT DISTINCT " + i + " FROM vuz WHERE " + user_data[1]))
        for row in result:
            filter_mas_1.append([str(x) for x in row])
        for c in range(len(filter_mas_1)):
            filter_mas_1[c] = filter_mas_1[c][0]
        for c,j in {'region': 'Фед. округ' ,'Oblname': "Субъект фед.",'City': "Город" ,'z1': "ВУЗ" }.items():
            if c == i:
                combo = dpg.add_combo(parent = 'FILTER', label = j , callback = filtering, user_data = [i,filter_string], items = filter_mas_1)
                combo_id_mas.append([i,combo])
        filter_mas_1.clear()

    global new_formed_filter_string
    new_formed_filter_string = 'z2='
    z1_name = re.search(r'' + 'z1.*\s' , user_data[1])
    if z1_name == None:
        return
    else:
        z1_name = z1_name.group(0)
        result = connection.execute(text("SELECT z2 FROM vuz WHERE " + z1_name))
        for row in result:
            filter_mas_1.append([str(x) for x in row])
        for c in range(len(filter_mas_1)):
            filter_mas_1[c] = filter_mas_1[c][0]
        new_formed_filter_string+="'" + filter_mas_1[0] + "'"
        filter_mas_1.clear()


def filter_btn(sender):
    specs_filter_list.clear()
    combo_id_mas.clear()
    if(not dpg.does_item_exist('FILTER')):
        with dpg.window(tag = 'FILTER', label = "Фильтр", width = 520, height = 500):
            for i,j in {'region':'Фед. округ','Oblname':'Субъект фед.','City': 'Город','z1':'ВУЗ'}.items():
                result = connection.execute(text("SELECT DISTINCT " + i + " FROM vuz"))
                for row in result:
                    filter_mas_1.append([str(x) for x in row])
                for c in range(len(filter_mas_1)):
                    filter_mas_1[c] = filter_mas_1[c][0]
                filter_mas_1.sort()
                combo = dpg.add_combo(label = j, callback = filtering, items = filter_mas_1, user_data = [i,filter_string])
                combo_id_mas.append([i,combo])
                filter_mas_1.clear()
            with dpg.child_window(pos = (8,400),autosize_x=True, autosize_y=False):
                dpg.add_button(label = 'Установить фильтр', pos = (10,30), callback = set_filter_callback)
                dpg.add_button(label = 'Сбросить фильтр', pos = (200,30), callback = reset_filter)
                dpg.add_button(label = 'Выход/Отмена', pos = (370,30), callback = hide_filter_callback)
    else:                   
        dpg.delete_item('FILTER', children_only = True)
        combo_id_mas.clear()
        for i,j in {'region':'Фед. округ','Oblname':'Субъект фед.','City': 'Город','z1':'ВУЗ'}.items():
            result = connection.execute(text("SELECT DISTINCT " + i + " FROM vuz"))
            for row in result:
                filter_mas_1.append([str(x) for x in row])
            for c in range(len(filter_mas_1)):
                filter_mas_1[c] = filter_mas_1[c][0]
            filter_mas_1.sort()
            combo = dpg.add_combo(parent = 'FILTER', label = j, callback = filtering, items = filter_mas_1, user_data = [i,filter_string])
            combo_id_mas.append([i,combo])
            filter_mas_1.clear()
            with dpg.child_window(parent = 'FILTER',pos = (8,400),autosize_x=True, autosize_y=False):
                dpg.add_button(label = 'Установить фильтр', pos = (10,30), callback = set_filter_callback)
                dpg.add_button(label = 'Сбросить фильтр', pos = (200,30), callback = reset_filter)
                dpg.add_button(label = 'Выход/Отмена', pos = (370,30), callback = hide_filter_callback)
    dpg.show_item('FILTER')

def delete_btn(sender):
    if len(high_list)==0 or dpg.get_item_label(high_list[0][2])!='gr_proj':
        return
    if(not dpg.does_item_exist('DELETE')):
        with dpg.window(tag = 'DELETE', label = "Удаление", width = 300, height = 200, modal = True, pos = (35,50)):
            if len(high_list)!=0:
                dpg.add_text("Удалить выделенную строку?")
                dpg.add_button(label = "Да", callback = delete_callback)
                dpg.add_button(label = "Нет", callback = delete_no_callback)
                dpg.add_button(label = "Отмена", callback = delete_no_callback)
            else:
                dpg.add_text("Выберите строку для удаления")
    else:
        dpg.delete_item('DELETE')
        with dpg.window(tag = 'DELETE', label = "Удаление", width = 300, height = 200, modal = True, pos = (35,50)):
            if len(high_list)!=0:
                dpg.add_text("Удалить выделенную строку?")
                dpg.add_button(label = "Да", callback = delete_callback)
                dpg.add_button(label = "Нет", callback = delete_no_callback)
                dpg.add_button(label = "Отмена", callback = delete_no_callback)
            else:
                dpg.add_text("Выберите строку для удаления")
    dpg.show_item('DELETE')

def edit_btn():
    if(not dpg.does_item_exist('EDIT')):
        if len(high_list)==0 or dpg.get_item_label(high_list[0][2])!='gr_proj':
            return
        else:
            with dpg.window(tag = 'EDIT', label = "Редактирование", width = 1000, height = 600, pos = (30,250)):
                dpg.delete_item('choose_row')
                dpg.add_text('Редактировать строку')
                for i in range(16):
                    if i == 0:
                        result = connection.execute(text("SELECT DISTINCT codkon FROM gr_konk" ))
                        add_mas = []
                        for row in result:
                            add_mas.append([str(x) for x in row])
                        for c in range(len(add_mas)):
                            add_mas[c] = add_mas[c][0]
                        add_mas.sort()
                        dpg.add_combo(label = GR_PROJ_label_list_ru[i+1], default_value = high_list[1][i],items = add_mas,callback = edit_callback)
                        add_mas.clear()
                    elif i == 4:
                        result = connection.execute(text("SELECT DISTINCT z2 FROM vuz" ))
                        add_mas = []
                        for row in result:
                            add_mas.append([str(x) for x in row])
                        for c in range(len(add_mas)):
                            add_mas[c] = add_mas[c][0]
                        add_mas.sort()
                        dpg.add_combo(label = GR_PROJ_label_list_ru[i+1], default_value = high_list[1][i],items = add_mas,callback = edit_callback)
                        add_mas.clear()
                    elif i == 11:
                        continue
                    else:
                        dpg.add_input_text(label = GR_PROJ_label_list_ru[i+1], default_value = high_list[1][i], on_enter = True, callback = edit_callback)
                    edit_input.append(dpg.last_item())
    else:
        if len(high_list)==0 or dpg.get_item_label(high_list[0][2])!='gr_proj':
            return
        else:
            for x in edit_input:
                dpg.delete_item(x)
            edit_input.clear()
            if(len(high_list)):
                for i in range(16):
                        if i == 0:
                            result = connection.execute(text("SELECT DISTINCT codkon FROM gr_konk" ))
                            add_mas = []
                            for row in result:
                                add_mas.append([str(x) for x in row])
                            for c in range(len(add_mas)):
                                add_mas[c] = add_mas[c][0]
                            add_mas.sort()
                            dpg.add_combo(parent = 'EDIT', label = GR_PROJ_label_list_ru[i+1], default_value = high_list[1][i],items = add_mas,callback = edit_callback)
                            add_mas.clear()
                        elif i == 4:
                            result = connection.execute(text("SELECT DISTINCT z2 FROM vuz" ))
                            add_mas = []
                            for row in result:
                                add_mas.append([str(x) for x in row])
                            for c in range(len(add_mas)):
                                add_mas[c] = add_mas[c][0]
                            add_mas.sort()
                            dpg.add_combo(parent = 'EDIT',label = GR_PROJ_label_list_ru[i+1], default_value = high_list[1][i],items = add_mas,callback = edit_callback)
                            add_mas.clear()
                        elif i == 11:
                            continue
                        else:
                            dpg.add_input_text(parent = 'EDIT', label = GR_PROJ_label_list_ru[i+1], default_value = high_list[1][i], on_enter = True, callback = edit_callback)
                        edit_input.append(dpg.last_item())
            else:
                dpg.add_text('Выберите строку для редактирования', tag = 'choose_row', parent = 'EDIT')
        dpg.show_item('EDIT')

def add_row_text_input(sender, specs):
    if len(specs) % 39 == 0 and len(specs)!=0:
        keyboard.send('enter')
    sender_label = dpg.get_item_label(sender)
    specs = to_cyr(specs)
    if sender_label in ['Код НИР','Код конкурса','ГРНТИ','Плановый объем гранта']:
        specs = str(specs)
        result = re.search(r'' + "[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\/#$%&'\"()*+\\\:;<=>?@[\]\^_`{|}~абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ ]*",specs )
        result = result.group(0)
        if len(result) != len(specs):
            print('Введены недопустимые символы для данного поля')
            return
    for i in range(len(GR_PROJ_label_list_ru)):
        if i == 0:
            continue
        if sender_label == GR_PROJ_label_list_ru[i]:
            for j in range(len(add_row_input)):
                if i == add_row_input[j][0]:
                    add_row_input[j][1] = specs
            if [i,specs] not in add_row_input:
                if sender_label == 'ВУЗ':
                    add_row_input.append([i,specs])
                    add_row_input.append([12,str(VUZ_z2_codvuz_dict[specs])])
                else:
                    add_row_input.append([i,specs])
                

def add_row_btn(sender):
    if(not dpg.does_item_exist('ADD_ROW')):
        with dpg.window(tag = 'ADD_ROW', label = "Добавить строку", width = 800, height = 600, pos = (35,50)):
            dpg.add_button(parent ='ADD_ROW',callback = add_row_callback, label = "Добавить строку")
            dpg.add_button(parent ='ADD_ROW', label = "Сброс ввода", callback = clear_add_row)
            for i in range(17):
                if i in [0,7,8,9,10,11,12]:
                    continue
                else:
                    if i == 13:
                        add_row_id_1 = dpg.add_input_text(width = 400, label = GR_PROJ_label_list_ru[i], multiline= True, callback = add_row_text_input)
                    elif i==2:
                        result = connection.execute(text("SELECT MAX(g1) FROM gr_proj" ))
                        add_mas = []
                        for row in result:
                            add_mas.append([str(x) for x in row])
                        for c in range(len(add_mas)):
                            add_mas[c] = add_mas[c][0]
                        add_row_id_1 = dpg.add_input_text(width = 400, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input, default_value = str(int(add_mas[0])+1), decimal=True, on_enter=True)
                        add_mas.clear()
                    elif i == 1:
                        result = connection.execute(text("SELECT DISTINCT codkon FROM gr_konk" ))
                        add_mas = []
                        for row in result:
                            add_mas.append([str(x) for x in row])
                        for c in range(len(add_mas)):
                            add_mas[c] = add_mas[c][0]
                        add_mas.sort()
                        add_row_id_1 = dpg.add_combo(width = 400, items = add_mas, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input)
                        add_mas.clear()
                    elif i == 5:
                        result = connection.execute(text("SELECT DISTINCT z2 FROM vuz" ))
                        add_mas = []
                        for row in result:
                            add_mas.append([str(x) for x in row])
                        for c in range(len(add_mas)):
                            add_mas[c] = add_mas[c][0]
                        add_mas.sort()
                        add_row_id_1 = dpg.add_combo(width = 400, items = add_mas, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input)
                        add_mas.clear()
                    elif i == 4 or i == 6 :
                        add_row_id_1 = dpg.add_input_text(width = 400, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input, decimal=True)
                    else: 
                        add_row_id_1 = dpg.add_input_text(width = 400, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input )
                add_row_id.append(add_row_id_1)
            
    dpg.show_item('ADD_ROW')

with dpg.window(tag = 'Main Window', height = 720, width = 1280):
    dpg.set_primary_window("Main Window", True)
    with dpg.viewport_menu_bar():
        with dpg.menu(label="Таблицы"):
            dpg.add_menu_item(label='Конкурсы' , callback = gr_konk_viz)
            dpg.add_menu_item(label='Проекты', callback = gr_proj_viz)
            dpg.add_menu_item(label='ВУЗы', callback = vuz_viz)
        for i in window_specs:
            with dpg.window(tag = i[0], label  = i[0], width = 1200, height = 950, show = False, no_resize = True):
                dpg.set_item_pos(i[0],(400,50))
                with dpg.table(height = 800, label = i[0].lower(), header_row=True,
                            borders_innerH=True, borders_outerH=True, borders_innerV=True,
                            borders_outerV=True, resizable = False, scrollX=True, scrollY=True, no_keep_columns_visible=True, 
                            policy = dpg.mvTable_SizingFixedFit, sortable = True, callback=sort_callback, sort_multi=True):
                    table_name_id.append([dpg.last_item(), i[0].lower()])
                    for _label in eval( i[0] + '_label_list_ru'):
                        dpg.add_table_column(label=_label)
                    table_creation(table_list_name_size[i[1]])
                if i[0] == 'GR_PROJ':
                    with dpg.child_window(height = 100, autosize_x = True, autosize_y = False):
                            dpg.add_button(label = 'Добавить', pos = (100, 20), width = 200, height = 60, callback = add_row_btn)
                            dpg.add_button(label = 'Удалить', pos = (350,20), width = 200, height = 60, callback = delete_btn)
                            dpg.add_button(label = 'Редактировать', pos = (600,20), width = 200, height = 60, callback = edit_btn)
                            dpg.add_button(label = 'Фильтр', pos = (850,20), width = 200, height = 60, callback = filter_btn)         

dpg.create_viewport(title='Support of competitions for grants')
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.maximize_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
    
"""
def add_copy_btn(sender):
    if(not dpg.does_item_exist('COPY')):
        with dpg.window(tag = 'COPY', label = "Скопировать выделенное", width = 200, height = 200, modal = True):
            dpg.add_input_text()
    dpg.show_item('COPY')

def inst_window(sender):
    with dpg.window(tag = 'INS', label = "Инструменты", width = 250, height = 250, on_close = closing_inst_window):
        dpg.set_item_pos("INS",(30,45))
        dpg.add_text(default_value = 'Для всех таблиц')
        #dpg.add_button(label = 'Фильтр', callback = filter_btn)
        dpg.add_text(default_value = 'Для таблицы проектов')
        #dpg.add_button(label = 'Удалить', callback =  delete_btn)
        #dpg.add_button(label = 'Редактировать', callback = edit_btn)
        #dpg.add_button(label = 'Копировать', callback = add_copy_btn)
        #dpg.add_button(label = 'Добавить в конец', callback = add_row_btn)

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (235, 235, 235))
        dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (235, 235, 235))
        dpg.add_theme_color(dpg.mvThemeCol_Button, (128, 128, 128))
        dpg.add_theme_color(dpg.mvThemeCol_TableRowBg, (128, 128, 128))
        dpg.add_theme_color(dpg.mvThemeCol_TableRowBgAlt, (235, 235, 235))
        dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, (235, 235, 235))
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (235, 235, 235))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (235, 235, 235))
        dpg.add_theme_color(dpg.mvThemeCol_Header, (128, 128, 128))
        dpg.add_theme_color(dpg.mvThemeCol_Tab, (128, 128, 128))
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (128, 128, 128))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (128, 128, 128))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg , (60, 60, 60))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (128, 128, 128))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (233,118,246))

dpg.bind_theme(global_theme)
"""
