import dearpygui.dearpygui as dpg
from sqlalchemy import String, Column,Text, Integer,MetaData,engine, text
import sqlalchemy as sql
import re
import psycopg2 
import dearpygui.demo as demo

engine = sql.create_engine('postgresql://postgres:1111@localhost:5432/postgres',echo=True)
connection = engine.connect()
metadata = MetaData()
metadata.create_all(engine)

connection.execute(text(
"""
CREATE OR REPLACE FUNCTION insert_into_gr_proj(
    in_codkon TEXT,
    in_g1 INTEGER,
    in_g8 TEXT DEFAULT NULL,
    in_g7 TEXT DEFAULT '00.00',
    in_z2 TEXT DEFAULT NULL,
    in_g5 INTEGER DEFAULT 0,
    in_codvuz INTEGER DEFAULT NULL,
    in_g6 TEXT DEFAULT NULL,
    in_g9 TEXT DEFAULT NULL,
    in_g10 TEXT DEFAULT NULL,
    in_g11 TEXT DEFAULT NULL)
RETURNS VOID AS $$
BEGIN
    INSERT INTO gr_proj (codkon,g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11) VALUES (in_codkon,in_g1,in_g8,in_g7,in_z2,in_g5,0,0,0,0,0,in_codvuz,in_g6,in_g9,in_g10,in_g11);
END;
$$ LANGUAGE plpgsql;
"""
))

connection.execute(text(
"""
CREATE OR REPLACE FUNCTION edit_row_gr_proj(
    in_codkon TEXT,
    in_g1 INTEGER,
    in_g8 TEXT DEFAULT NULL,
    in_g7 TEXT DEFAULT NULL,
    in_z2 TEXT DEFAULT NULL,
    in_g5 INTEGER DEFAULT NULL,
    in_codvuz INTEGER DEFAULT NULL,
    in_g6 TEXT DEFAULT NULL,
    in_g9 TEXT DEFAULT NULL,
    in_g10 TEXT DEFAULT NULL,
    in_g11 TEXT DEFAULT NULL,
    out_codkon TEXT DEFAULT NULL,
    out_g1 INTEGER DEFAULT NULL,
    out_g8 TEXT DEFAULT NULL,
    out_g7 TEXT DEFAULT NULL,
    out_z2 TEXT DEFAULT NULL,
    out_g5 INTEGER DEFAULT NULL,
    out_codvuz INTEGER DEFAULT NULL,
    out_g6 TEXT DEFAULT NULL,
    out_g9 TEXT DEFAULT NULL,
    out_g10 TEXT DEFAULT NULL,
    out_g11 TEXT DEFAULT NULL
    )
RETURNS VOID AS $$
BEGIN
    UPDATE gr_proj SET codkon = COALESCE(out_codkon, in_codkon), g1 = COALESCE(out_g1,in_g1), g8 = COALESCE(out_g8, in_g8),
    g7 = COALESCE(out_g7, in_g7), z2 = COALESCE(out_z2, in_z2),g5 = COALESCE(out_g5, in_g5), codvuz = COALESCE(out_codvuz, in_codvuz),
    g6 = COALESCE(out_g6, in_g6), g9 = COALESCE(out_g9, in_g9), g10 = COALESCE(out_g10, in_g10),g11 = COALESCE(out_g11, in_g11) 
    WHERE codkon = in_codkon AND g1 = in_g1;
END;
$$ LANGUAGE plpgsql;
"""
))

connection.execute(text(
"""
CREATE OR REPLACE FUNCTION delete_row_gr_proj(
    in_codkon TEXT,
    in_g1 INTEGER
)
RETURNS VOID AS $$
BEGIN
    DELETE FROM gr_proj WHERE codkon=in_codkon AND g1 = in_g1;
END;
$$ LANGUAGE plpgsql;
"""
))

connection.execute(text(
"""
CREATE OR REPLACE FUNCTION planed_financing()
RETURNS TRIGGER AS $$
DECLARE 
array_str text [] := ARRAY['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17'];
i text;
BEGIN
    FOREACH i IN ARRAY array_str
        LOOP
        UPDATE gr_konk SET k12 = COALESCE((SELECT SUM(COALESCE(g5, 0)) FROM gr_proj WHERE codkon=i),0) WHERE codkon=i;
        END LOOP;
        RETURN NEW; 
END;
$$ LANGUAGE plpgsql;
"""
))

connection.execute(text(
"""
CREATE OR REPLACE TRIGGER gr_konk_financing
AFTER INSERT OR DELETE OR UPDATE ON gr_proj
FOR EACH ROW
EXECUTE PROCEDURE planed_financing();
"""
))

connection.execute(text(
"""
CREATE OR REPLACE FUNCTION konk_participants()
RETURNS TRIGGER AS $$
DECLARE 
array_str text [] := ARRAY['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17'];
i text;
BEGIN
    FOREACH i IN ARRAY array_str
        LOOP
        UPDATE gr_konk SET npr = COALESCE((SELECT COALESCE(COUNT(*),0) FROM gr_proj WHERE codkon=i),0) WHERE codkon=i;
        END LOOP;
        RETURN NEW; 
END;
$$ LANGUAGE plpgsql;
"""
))

connection.execute(text(
"""
CREATE OR REPLACE TRIGGER gr_konk_npr
AFTER INSERT OR DELETE OR UPDATE ON gr_proj
FOR EACH ROW
EXECUTE PROCEDURE konk_participants();
"""
))

dpg.create_context()

big_let_start = 0x00C0  # Capital "A" in cyrillic alphabet
big_let_end = 0x00DF  # Capital "Я" in cyrillic alphabet
small_let_end = 0x00FF  # small "я" in cyrillic alphabet
remap_big_let = 0x0410  # Starting number for remapped cyrillic alphabet
alph_len = big_let_end - big_let_start + 1  # adds the shift from big letters to small
alph_shift = remap_big_let - big_let_start  # adds the shift from remapped to non-remapped

#demo.show_demo()

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
high_list_copy = []
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
gr_proj_for_vuz_dict = {'g5':'k12','g2':'k4','g21':'k41','g22':'k42','g23':'k43','g24':'k44'}
edit_id_input = []
add_row_input = []
add_row_id = []
add_grnti = []
edit_grnti = []
first_grnti_input = 0
first_grnti_edit = 0
add_row_max_g1 = 0
grnti_edit_defaults = []

def court_to_string(mas, result):
    for row in result:
        mas.append([str(x) for x in row])
    for c in range(len(mas)):
        mas[c] = mas[c][0]

def add_row_window_input_creation():
    for i in range(17):
        if i in [0,7,8,9,10,11,12]:
            continue
        else:
            if i == 1:
                result = connection.execute(text("SELECT DISTINCT codkon FROM gr_konk" ))
                add_mas = []
                court_to_string(add_mas,result)
                add_mas.sort()
                add_row_id_1 = dpg.add_combo(parent ='ADD_ROW',width = 400, items = add_mas, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input)
                add_mas.clear()
            elif i == 2:
                add_row_id_1 = dpg.add_input_text(parent ='ADD_ROW',width = 400, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input, decimal=True, on_enter=True , enabled  = False)
            elif i == 4:
                add_row_id_1 = dpg.add_input_int(parent ='ADD_ROW',width = 60, callback = add_row_grnti_input,
                                                 enabled  = False, min_value = 0, max_value = 99, min_clamped = True, max_clamped = True, step = 0, on_enter = False)
                dpg.add_text(parent ='ADD_ROW', pos = (66,130), default_value = '.')
                global first_grnti_input
                first_grnti_input = add_row_id_1
                add_row_id.append(add_row_id_1)

                add_row_id_1 = dpg.add_input_int(parent ='ADD_ROW',width = 60, pos = (74,124), callback = add_row_grnti_input, enabled  = False,
                                                 min_value = 0, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
                dpg.add_text(parent ='ADD_ROW', pos = (132,130), default_value = '.')
                add_row_id.append(add_row_id_1)

                add_row_id_1 = dpg.add_input_int(parent ='ADD_ROW',width = 60, pos = (140,124), callback = add_row_grnti_input, enabled  = False, default_value = -1,
                                                 min_value = 0, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
                dpg.add_text(parent ='ADD_ROW', pos = (198,130), default_value = ',')
                add_row_id.append(add_row_id_1)

                add_row_id_1 = dpg.add_input_int(parent ='ADD_ROW',width = 60, pos = (206,124), callback = add_row_grnti_input, enabled  = False, default_value = -1,
                                                 min_value = 0, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
                dpg.add_text(parent ='ADD_ROW', pos = (264,130), default_value = '.')
                add_row_id.append(add_row_id_1)

                add_row_id_1 = dpg.add_input_int(parent ='ADD_ROW',width = 60, pos = (272,124), callback = add_row_grnti_input, enabled  = False, default_value = -1,
                                                 min_value = 0, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
                dpg.add_text(parent ='ADD_ROW', pos = (330,130), default_value = '.')
                add_row_id.append(add_row_id_1)

                add_row_id_1 = dpg.add_input_int(parent ='ADD_ROW',width = 70, pos = (338,124), label = GR_PROJ_label_list_ru[i], callback = add_row_grnti_input, enabled  = False, 
                                                 default_value = -1,min_value = 0, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
            elif i == 5:
                result = connection.execute(text("SELECT DISTINCT z2 FROM vuz" ))
                add_mas = []
                court_to_string(add_mas,result)
                add_mas.sort()
                add_row_id_1 = dpg.add_combo(parent ='ADD_ROW',width = 400, items = add_mas, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input, enabled  = False)
                add_mas.clear()
            elif i == 6:
                add_row_id_1 = dpg.add_input_int(parent ='ADD_ROW',width = 400, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input, min_value=0, min_clamped = True, enabled  = False)
            elif i == 13:
                add_row_id_1 = dpg.add_input_text(parent ='ADD_ROW',width = 400, label = GR_PROJ_label_list_ru[i], multiline= True, callback = add_row_text_input, enabled  = False)
            else: 
                add_row_id_1 = dpg.add_input_text(parent ='ADD_ROW',width = 400, label = GR_PROJ_label_list_ru[i], callback = add_row_text_input, enabled  = False)
        add_row_id.append(add_row_id_1)

def edit_text_input(sender,specs):
    sender_label = dpg.get_item_label(sender)
    if sender_label == 'Код конкурса':
        result = connection.execute(text("SELECT COALESCE(MAX(g1)+1,1) FROM gr_proj WHERE codkon='" + str(specs) + "'"))
        add_mas = []
        court_to_string(add_mas,result)
        dpg.set_value(edit_id_input[1], int(add_mas[0]))
        high_list[1][0] = str(specs)
        high_list[1][1] = add_mas[0]
        add_mas.clear()
        print(high_list)
        return
    elif sender_label == 'Код НИР':
        high_list[1][1] = str(specs)
        print(high_list)
        return
    elif sender_label == 'Руководитель НИР':
        high_list[1][2] = specs
        print(high_list)
        return
    elif sender_label == 'ВУЗ':
        high_list[1][4] = specs
        high_list[1][11] = str(VUZ_z2_codvuz_dict[specs])
        print(high_list)
        return
    elif sender_label == 'Плановый объем гранта':
        high_list[1][5] = str(specs)
        print(high_list)
        return
    elif sender_label == 'НИР':
        high_list[1][12] = specs
        print(high_list)
        return
    elif sender_label == 'Должность':
        high_list[1][13] = specs
        print(high_list)
        return
    elif sender_label == 'Ученое звание':
        high_list[1][14] = specs
        print(high_list)
        return
    else:
        high_list[1][15] = specs
        print(high_list)
        return

def edit_row_window_input_creation():
    for i in range(17):
        if i in [0,7,8,9,10,11,12]:
            continue
        else:
            if i == 1:
                result = connection.execute(text("SELECT DISTINCT codkon FROM gr_konk" ))
                add_mas = []
                court_to_string(add_mas,result)
                add_mas.sort()
                dpg.add_combo(width = 400, parent ='EDIT',label = GR_PROJ_label_list_ru[i], default_value = high_list[1][i-1],items = add_mas,callback = edit_text_input)
                add_mas.clear()
            elif i == 2:
                dpg.add_input_int(parent ='EDIT',width = 400, label = GR_PROJ_label_list_ru[i], callback = edit_text_input, default_value = int(high_list[1][i-1]), 
                                    min_value = int(high_list[1][i-1]), min_clamped = True)
            elif i == 4:
                edit_grnti_default_values()
                global first_grnti_edit
                first_grnti_edit = dpg.add_input_int(parent ='EDIT',width = 60, callback = edit_grnti_input, default_value = int(grnti_edit_defaults[0][1]),
                                                    min_value = 0, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
                edit_id_input.append(dpg.last_item())
                dpg.add_text(parent ='EDIT', pos = (66,130), default_value = '.')

                dpg.add_input_int(parent ='EDIT',width = 60, pos = (74,124), callback = edit_grnti_input, default_value = int(grnti_edit_defaults[1][1]),
                                                    min_value = 0, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
                edit_id_input.append(dpg.last_item())
                dpg.add_text(parent ='EDIT', pos = (132,130), default_value = '.')

                dpg.add_input_int(parent ='EDIT',width = 60, pos = (140,124), callback = edit_grnti_input, default_value = int(grnti_edit_defaults[2][1]),
                                                    min_value = -1, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
                edit_id_input.append(dpg.last_item())
                dpg.add_text(parent ='EDIT', pos = (198,130), default_value = ',')

                dpg.add_input_int(parent ='EDIT',width = 60, pos = (206,124), callback = edit_grnti_input, default_value = int(grnti_edit_defaults[3][1]),
                                                    min_value = 0, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
                edit_id_input.append(dpg.last_item())
                dpg.add_text(parent ='EDIT', pos = (264,130), default_value = '.')

                dpg.add_input_int(parent ='EDIT',width = 60, pos = (272,124), callback = edit_grnti_input, default_value = int(grnti_edit_defaults[4][1]),
                                                    min_value = 0, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
                edit_id_input.append(dpg.last_item())
                dpg.add_text(parent ='EDIT', pos = (330,130), default_value = '.')

                dpg.add_input_int(parent ='EDIT',width = 70, pos = (338,124), label = GR_PROJ_label_list_ru[i], callback = edit_grnti_input, default_value = int(grnti_edit_defaults[5][1]),
                                                    min_value = -1, max_value = 99, min_clamped = True, max_clamped = True, step = 0)
            elif i == 5:
                result = connection.execute(text("SELECT DISTINCT z2 FROM vuz" ))
                add_mas = []
                court_to_string(add_mas,result)
                add_mas.sort()
                dpg.add_combo(width = 400, parent ='EDIT',label = GR_PROJ_label_list_ru[i], default_value = high_list[1][i-1],items = add_mas,callback = edit_text_input)
                add_mas.clear()
            elif i == 6:
                add_row_id_1 = dpg.add_input_text(parent ='EDIT',width = 400, label = GR_PROJ_label_list_ru[i], default_value =high_list[1][i-1] ,callback = edit_text_input, decimal=True)
            elif i == 13:
                dpg.add_input_text(width = 400, parent ='EDIT',label = GR_PROJ_label_list_ru[i], default_value = high_list[1][i-1], callback = edit_text_input, multiline=True)
            else:
                dpg.add_input_text(width = 400, parent ='EDIT',label = GR_PROJ_label_list_ru[i], default_value = high_list[1][i-1], callback = edit_text_input)
            edit_id_input.append(dpg.last_item())

def gr_proj_table_recreation():
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

def gr_konk_table_recreation():
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

def info_selection(sender):
    if(dpg.get_item_label(sender) == 'gr_konk'):
        info = table_list_name_size[0]
    elif(dpg.get_item_label(sender) == 'gr_proj'):
        info = table_list_name_size[1]
    else:
        info = table_list_name_size[2]
    return info

def edit_callback():
    complete_grnti_edit_input()
    edit_string = ''
    counter = 0
    for i in range(16):
        if high_list_copy[i] != high_list[1][i]:
            counter += 1

    if counter == 0:
        print('Нет изменений')
        return
    
    for i in range(17):
        if i == 0:
            continue
        else:
            if high_list_copy[i-1] != 'None' and i not in [7,8,9,10,11]:
                    edit_string += 'in_' + GR_PROJ_label_list[i] + ":='" + high_list_copy[i-1] + "',"
            else: 
                continue

    for i in range(16):
        if high_list_copy[i] != high_list[1][i] and counter != 1:    
            edit_string += 'out_' + GR_PROJ_label_list[i+1] + ":='" + high_list[1][i] + "',"
            counter -= 1
        elif high_list_copy[i] != high_list[1][i] and counter == 1:
            edit_string += 'out_' + GR_PROJ_label_list[i+1] + ":='" + high_list[1][i] + "'"
            

    try:
        connection.execute(text("SELECT edit_row_gr_proj("+ edit_string +")"))
        dpg.unhighlight_table_row(table = high_list[0][2], row = high_list[0][1])
        dpg.set_value(high_list[0][0],False)
        high_list.clear()
    except:
        print("Нельзя выполнить SQL запрос")
        for i in range(16):
            high_list[1][i] = high_list_copy[i]
        edit_btn()
        return
    connection.execute(text("COMMIT"))
    dpg.hide_item('EDIT')
    high_list_copy.clear()
    gr_proj_table_recreation()
    gr_konk_table_recreation()


def delete_callback():
    delete_string = ''
    delete_string += "in_codkon:='" + high_list[1][0] + "',"
    delete_string += "in_g1:='" + high_list[1][1] + "'"
    print(delete_string)
    try:
        connection.execute(text("SELECT delete_row_gr_proj(" + delete_string + ")"))
        dpg.hide_item('EDIT')
        high_list.clear()
    except:
        print("Неверный SQL запрос")
        return
    connection.execute(text("COMMIT"))
    gr_proj_table_recreation()
    gr_konk_table_recreation()
    dpg.hide_item("DELETE")

def add_row_callback():
    if len(add_row_input)<2:
        return
    complete_grnti_input()
    add_row_string = ''
    for i in range(len(add_row_input)):
        if i!=len(add_row_input)-1:
            add_row_string += 'in_' + add_row_input[i][1] +":='" + add_row_input[i][2] + "'" + ', '
        else:
            add_row_string += 'in_' + add_row_input[i][1] + ":='" + add_row_input[i][2] + "'"
    print(add_row_string)
    try:
        connection.execute(text("SELECT insert_into_gr_proj(" + add_row_string + ");"))
    except:
        print('Неверный SQL запрос')
        return

    add_row_input.clear()
    connection.execute(text('COMMIT'))
    hide_add_row_input()
    gr_proj_table_recreation()
    gr_konk_table_recreation()

def clear_add_row():
    for i in range(len(add_row_id)):
        dpg.delete_item(add_row_id[i])
    add_row_id.clear()
    add_grnti.clear()
    add_row_window_input_creation()

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
    for i in high_list[1]:
        high_list_copy.append(i)
    print(high_list_copy)
    edit_btn()

def sort_algo(col_id, s_dir, row, sender):
    info = info_selection(sender)
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
            for j in range(-1,len(_row)):
                if (j==-1):
                    dpg.add_selectable(height = 27, width = 27, callback = highlight_rows, user_data = info[1]+2)
                else:
                    dpg.add_text(f"{_row[j]}")
    high_list.clear()

def sort_callback(sender, sort_specs):
    print(sort_specs)
    info = info_selection(sender)
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
    elif(dpg.get_item_label(sender) == 'vuz'):
        row-=12
    elif(dpg.get_item_label(sender) =='gr_konk'):
        row-=10

    sort_algo(column_id, direction, row, sender)
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

def hide_add_row_input():
    for i in add_row_id:
        dpg.delete_item(i)
    add_row_id.clear()
    add_row_window_input_creation()
    dpg.hide_item('ADD_ROW')

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
        court_to_string(filter_mas_1,result)
        filter_mas_1.sort()
        combo = dpg.add_combo(parent = 'FILTER', label = j, callback = filtering, items = filter_mas_1, user_data = [i,filter_string])
        combo_id_mas.append([i,combo])
        filter_mas_1.clear()
    gr_proj_table_recreation()

def set_filter_callback():
    if len(new_formed_filter_string)==0:
        return
    dpg.delete_item(table_name_id[1][0], children_only=True)
    exec("for _label in " + "GR_PROJ" + "_label_list_ru: dpg.add_table_column(parent = table_name_id[1][0],label=_label)")
    result = connection.execute(text("SELECT codkon,g1,g8,g7,z2,g5,g2,g21,g22,g23,g24,codvuz,g6,g9,g10,g11 FROM gr_proj WHERE z2 IN (SELECT z2 FROM vuz WHERE " + new_formed_filter_string+ " )"))
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
        court_to_string(filter_mas_1,result)
        for c,j in {'region': 'Фед. округ' ,'Oblname': "Субъект фед.",'City': "Город" ,'z1': "ВУЗ" }.items():
            if c == i:
                combo = dpg.add_combo(parent = 'FILTER', label = j , callback = filtering, user_data = [i,filter_string], items = filter_mas_1)
                combo_id_mas.append([i,combo])
        filter_mas_1.clear()

    global new_formed_filter_string
    new_formed_filter_string = user_data[1]

def filter_btn(sender):
    specs_filter_list.clear()
    if(not dpg.does_item_exist('FILTER')):
        with dpg.window(tag = 'FILTER', label = "Фильтр", width = 520, height = 500):
            for i,j in {'region':'Фед. округ','Oblname':'Субъект фед.','City': 'Город','z1':'ВУЗ'}.items():
                result = connection.execute(text("SELECT DISTINCT " + i + " FROM vuz"))
                court_to_string(filter_mas_1,result)
                filter_mas_1.sort()
                combo = dpg.add_combo(label = j, callback = filtering, items = filter_mas_1, user_data = [i,filter_string])
                combo_id_mas.append([i,combo])
                filter_mas_1.clear()
            with dpg.child_window(pos = (8,400),autosize_x=True, autosize_y=False):
                dpg.add_button(label = 'Установить фильтр', pos = (10,30), callback = set_filter_callback)
                dpg.add_button(label = 'Сбросить фильтр', pos = (200,30), callback = reset_filter)
                dpg.add_button(label = 'Выход/Отмена', pos = (370,30), callback = hide_filter_callback)
    else:                   
        if dpg.is_item_shown('FILTER'):
            return
        else:
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
        if dpg.is_item_shown('DELETE'):
            return
        else:
            dpg.show_item('DELETE')

def edit_btn():
    if(not dpg.does_item_exist('EDIT')):
        if len(high_list)==0 or dpg.get_item_label(high_list[0][2])!='gr_proj':
            return
        else:
            with dpg.window(tag = 'EDIT', label = "Редактирование", width = 800, height = 600, pos = (30,250)):
                edit_row_window_input_creation()
                with dpg.child_window(pos = (8,500),autosize_x=True, autosize_y=False):
                    dpg.add_button(label = "Редактировать строку", callback = edit_callback, pos =(78,20), height = 50)
                    dpg.add_button(label = "Сброс изменений", callback = clear_edit_row, pos = (368,20),  height = 50)
                    dpg.add_button(label = "Выход", callback = hide_edit, pos = (608,20), height = 50 )
    else:
        if len(high_list)==0 or dpg.get_item_label(high_list[0][2])!='gr_proj':
            return
        else:
            for x in edit_id_input:
                dpg.delete_item(x)
            edit_id_input.clear()
            if(len(high_list)):
                edit_row_window_input_creation()
        dpg.show_item('EDIT')

def add_row_text_input(sender, specs):
    sender_label = dpg.get_item_label(sender)
    if sender_label == 'Плановый объем гранта':
        specs = str(specs)

    specs = to_cyr(specs)
    global add_row_max_g1
    if sender_label == 'Код НИР':
        if int(specs) < int(add_row_max_g1):
            dpg.set_value(sender,add_row_max_g1)
            return

    for i in range(len(GR_PROJ_label_list_ru)):
        if i == 0:
            continue
        if sender_label == GR_PROJ_label_list_ru[i]:
            for j in range(len(add_row_input)):
                if i == add_row_input[j][0]:
                    add_row_input[j][2] = specs
            if [i,GR_PROJ_label_list[i],specs] not in add_row_input:
                if sender_label == 'ВУЗ':
                    add_row_input.append([i,GR_PROJ_label_list[i],specs])
                    add_row_input.append([12,GR_PROJ_label_list[12],str(VUZ_z2_codvuz_dict[specs])])
                else:
                    add_row_input.append([i,GR_PROJ_label_list[i],specs])
    
    if add_row_input[0][1] == 'codkon' and sender_label == 'Код конкурса':
        add_row_choose_codkon = add_row_input[0][2]
        result = connection.execute(text("SELECT COALESCE(MAX(g1)+1,1) FROM gr_proj WHERE codkon='" + str(add_row_choose_codkon) + "'"))
        add_mas = []
        court_to_string(add_mas,result)
        add_row_max_g1 = add_mas[0]
        dpg.set_value(add_row_id[1], add_mas[0])
        if not dpg.is_item_enabled(add_row_id[1]):
            for i in range(1,len(add_row_id)):
                if i in [5,8]:
                    continue
                dpg.enable_item(add_row_id[i])
        add_mas.clear()

def clear_edit_row():
    for i in edit_id_input:
        dpg.delete_item(i)
    edit_id_input.clear()
    for i in range(len(high_list_copy)):
        high_list[1][i] = high_list_copy[i]
    edit_row_window_input_creation()

def hide_edit():
    dpg.unhighlight_table_row(table = high_list[0][2], row = high_list[0][1])
    dpg.set_value(high_list[0][0],False)
    high_list.clear()
    dpg.hide_item('EDIT')

def sorter_1(a):
    return a[0]

def edit_grnti_default_values():
    grnti_edit_defaults.clear()
    value = high_list[1][3]
    if len(value) == 5:
        grnti_edit_defaults.append([0,value[0:2]])
        grnti_edit_defaults.append([2,value[3:5]])
        grnti_edit_defaults.append([4,'-1'])
        grnti_edit_defaults.append([6,'-1'])
        grnti_edit_defaults.append([8,'-1'])
        grnti_edit_defaults.append([10,'-1'])
    elif len(value) == 8:
        grnti_edit_defaults.append([0,value[0:2]])
        grnti_edit_defaults.append([2,value[3:5]])
        grnti_edit_defaults.append([4,value[6:]])
        grnti_edit_defaults.append([6,'-1'])
        grnti_edit_defaults.append([8,'-1'])
        grnti_edit_defaults.append([10,'-1'])
    elif len(value) == 11:
        grnti_edit_defaults.append([0,value[0:2]])
        grnti_edit_defaults.append([2,value[3:5]])
        grnti_edit_defaults.append([4,'-1'])
        grnti_edit_defaults.append([6,value[6:8]])
        grnti_edit_defaults.append([8,value[9:]])
        grnti_edit_defaults.append([10,'-1'])
    elif len(value) == 14:
        if value.find(",") == 8:
            grnti_edit_defaults.append([0,value[0:2]])
            grnti_edit_defaults.append([2,value[3:5]])
            grnti_edit_defaults.append([4,value[6:8]])
            grnti_edit_defaults.append([6,value[9:11]])
            grnti_edit_defaults.append([8,value[12:]])
            grnti_edit_defaults.append([10,'-1'])
        else:
            grnti_edit_defaults.append([0,value[0:2]])
            grnti_edit_defaults.append([2,value[3:5]])
            grnti_edit_defaults.append([4,'-1'])
            grnti_edit_defaults.append([6,value[6:8]])
            grnti_edit_defaults.append([8,value[9:11]])
            grnti_edit_defaults.append([10,value[12:]])
    else:
        grnti_edit_defaults.append([0,value[0:2]])
        grnti_edit_defaults.append([2,value[3:5]])
        grnti_edit_defaults.append([4,value[6:8]])
        grnti_edit_defaults.append([6,value[9:11]])
        grnti_edit_defaults.append([8,value[12:14]])
        grnti_edit_defaults.append([10,value[15:]])
    print(grnti_edit_defaults)

def edit_grnti_input(sender, specs):
    
    global first_grnti_edit
    if specs < 10 and specs >= 0:
        specs = '0' + str(specs)
    else:
        specs = str(specs)
    print(specs)
    if sender != first_grnti_edit:
        grnti_input_index = sender - first_grnti_edit
        checker = False
        for i in grnti_edit_defaults:
            if i[0] == grnti_input_index:
                i[1] = specs
                checker = True
                break
        if not checker:
            grnti_edit_defaults.append([grnti_input_index,specs])
    else:
        checker = False
        for i in grnti_edit_defaults:
            if i[0] == 0:
                i[1] = specs
                checker = True
                break
        if not checker:
            grnti_edit_defaults.append([0,specs])
    print(grnti_edit_defaults)
    print(high_list)

def complete_grnti_edit_input():
    grnti_edit_defaults.sort(key = sorter_1)
    grnti_first_half = []
    grnti_second_half = []
    to_remove = []

    for i in grnti_edit_defaults:
        if i[1] == '-1':
            to_remove.append(i)
    if len(to_remove):
        for i in to_remove:
            grnti_edit_defaults.remove(i)

    for i in grnti_edit_defaults:
        if i[0]<5:
            grnti_first_half.append(i[1])
        else:
            grnti_second_half.append(i[1])

    if len(grnti_first_half) < 2 and len(grnti_second_half) < 2:
        print("Введите все значения в полях ГРНТИ")
        return
    else:
        if len(grnti_first_half) > 1:
            grnti_first_half_str = ''
            for i in range(len(grnti_first_half)):
                if i != len(grnti_first_half)-1:
                    grnti_first_half_str += grnti_first_half[i] + '.'
                else:
                    grnti_first_half_str += grnti_first_half[i]

        if len(grnti_second_half) > 1:
            grnti_second_half_str = ''
            for i in range(len(grnti_second_half)):
                if i != len(grnti_second_half)-1:
                    grnti_second_half_str += grnti_second_half[i] + '.'
                else:
                    grnti_second_half_str += grnti_second_half[i]

        if len(grnti_first_half) > 1 and len(grnti_second_half) > 1:
            complete_grnti_str = grnti_first_half_str + ',' + grnti_second_half_str
        elif len(grnti_first_half) > 1:
            complete_grnti_str = grnti_first_half_str
        else:
            complete_grnti_str = grnti_second_half_str
    high_list[1][3] = complete_grnti_str

def add_row_grnti_input(sender,specs):
    if specs < 10:
        specs = '0' + str(specs)
    else:
        specs = str(specs)
    print(specs)
    global first_grnti_input
    if sender != first_grnti_input:
        grnti_input_index = sender - first_grnti_input
        checker = False
        for i in add_grnti:
            if i[0] == grnti_input_index:
                i[1] = specs
                checker = True
                break
        if not checker:
            add_grnti.append([grnti_input_index,specs])
        if grnti_input_index == 2:
            dpg.enable_item(add_row_id[5])
        elif grnti_input_index == 8:
            dpg.enable_item(add_row_id[8])
    else:
        checker = False
        for i in add_grnti:
            if i[0] == 0:
                i[1] = specs
                checker = True
                break
        if not checker:
            add_grnti.append([0,specs])

    print(add_grnti)

def sorter(a):
    return a[0]

def complete_grnti_input():
    add_grnti.sort(key = sorter)
    grnti_first_half = []
    grnti_second_half = []
    for i in add_grnti:
        if i[0]<5:
            grnti_first_half.append(i[1])
        else:
            grnti_second_half.append(i[1])

    if len(grnti_first_half) < 2 and len(grnti_second_half) < 2:
        print("Введите все значения в полях ГРНТИ")
        return
    else:
        if len(grnti_first_half) > 1:
            grnti_first_half_str = ''
            for i in range(len(grnti_first_half)):
                if i != len(grnti_first_half)-1:
                    grnti_first_half_str += grnti_first_half[i] + '.'
                else:
                    grnti_first_half_str += grnti_first_half[i]

        if len(grnti_second_half) > 1:
            grnti_second_half_str = ''
            for i in range(len(grnti_second_half)):
                if i != len(grnti_second_half)-1:
                    grnti_second_half_str += grnti_second_half[i] + '.'
                else:
                    grnti_second_half_str += grnti_second_half[i]

        if len(grnti_first_half) > 1 and len(grnti_second_half) > 1:
            complete_grnti_str = grnti_first_half_str + ',' + grnti_second_half_str
        elif len(grnti_first_half) > 1:
            complete_grnti_str = grnti_first_half_str
        else:
            complete_grnti_str = grnti_second_half_str
    if [4,GR_PROJ_label_list[4],complete_grnti_str] not in add_row_input:
        add_row_input.append([4,GR_PROJ_label_list[4],complete_grnti_str])
        
def add_row_btn(sender):
    if(not dpg.does_item_exist('ADD_ROW')):
        with dpg.window(tag = 'ADD_ROW', label = "Добавить строку", width = 800, height = 600, pos = (35,50)):
            add_row_window_input_creation()
            with dpg.child_window(pos = (8,500),autosize_x=True, autosize_y=False):
                dpg.add_button(label = "Добавить строку", callback = add_row_callback, pos =(128,20), height = 50)
                dpg.add_button(label = "Сброс ввода", callback = clear_add_row, pos = (368,20),  height = 50)
                dpg.add_button(label = "Выход", callback = hide_add_row_input, pos = (608,20), height = 50 )
            
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

dpg.create_viewport(title='Support of competitions for grants', width = 2200, height = 1200)
dpg.setup_dearpygui()
dpg.show_viewport()
#dpg.maximize_viewport()
dpg.start_dearpygui()
dpg.destroy_context()