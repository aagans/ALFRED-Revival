# region Imports of dependencies
import csv
import json
import pickle

import PySimpleGUI as sg
import mysql.connector
import pyperclip
from mysql.connector import Error


# endregion

# region Custom functions
def extract_first(lst):
    return [item[0] for item in lst]


def open_about(layout_of_window):
    window_w3 = sg.Window('About Page', layout_of_window, icon=png)
    while True:
        event_w3, values_w3 = window_w3.read()
        if event_w3 == sg.WIN_CLOSED:
            break


def open_window(table_data, table_headings, samp_table_data, samp_table_headings):
    layout_w2 = [[sg.Text('Generated Frequency Table')],
                 [sg.Table(table_data, table_headings, expand_x=True, expand_y=True, alternating_row_color='white',
                           auto_size_columns=True, enable_events=True, right_click_selects=True, k='-TableSelect-')],
                 [sg.Text('Sample Info')],
                 [sg.Table(samp_table_data, samp_table_headings, expand_x=True, expand_y=True,
                           alternating_row_color='white', auto_size_columns=True, enable_events=True,
                           right_click_selects=True, k='-SampleTableSelect-')],
                 [sg.Button('Exit', key='-TableExit-')]]
    window_w2 = sg.Window("Frequency Table", layout_w2, resizable=True, icon=png)
    while True:
        event_w2, values_w2 = window_w2.read()
        if event_w2 == '-TableSelect-':
            row_values = window_w2['-TableSelect-'].get()
            row_values = row_values[0]
            row_values = [str(x) for x in row_values]
            row_string = ", ".join(row_values)
            pyperclip.copy(row_string)

        if event_w2 == '-TableExit-' or event_w2 == sg.WIN_CLOSED:
            break

    window_w2.close()


def fetch_results(which_pop):
    selected_pop_1 = values[which_pop]

    if isinstance(selected_pop_1, str):
        selected_pop_1 = (selected_pop_1,)
    pop_uid_selected_1 = 'SELECT pop_uid FROM populationtable WHERE population = %s'
    my_cursor.execute(pop_uid_selected_1, selected_pop_1)
    selected_pop_uid_1 = my_cursor.fetchall()

    find_sample_1 = 'SELECT sample_uid FROM samplegrouptable WHERE pop_uid = %s'
    my_cursor.execute(find_sample_1, selected_pop_uid_1[0])
    list_sample_uid_1 = my_cursor.fetchall()
    listed_sample_uid_1 = [item for t in list_sample_uid_1 for item in t]
    dup_sample_uid_1 = [*set(listed_sample_uid_1)]

    find_snp_uid_1 = 'SELECT snp_uid FROM samplecoveragetable WHERE sample_uid IN ({0})'.format(
        ', '.join('%s' for _ in dup_sample_uid_1))

    my_cursor.execute(find_snp_uid_1, dup_sample_uid_1)
    list_snp_uid_1 = my_cursor.fetchall()
    listed_snp_uid_1 = [item for t in list_snp_uid_1 for item in t]
    dup_snp_uid_1 = [*set(listed_snp_uid_1)]
    return dup_snp_uid_1


def region_comparison(region_submit, update_box):
    try:
        selected_region_c = values[f'{region_submit}']
        if isinstance(selected_region_c, str):
            selected_region_c = (selected_region_c,)
        pop_sql_c = 'SELECT population FROM populationtable WHERE geo_region = %s'
        my_cursor.execute(pop_sql_c, selected_region_c)
        list_pop_c = my_cursor.fetchall()
        dup_list_pop_c = [*set(list_pop_c)]
        dup_list_pop_c.sort()
        sort_pop_c = dup_list_pop_c
        sort_pop_c = extract_first(sort_pop_c)
        window[f'{update_box}'].update(values=sort_pop_c)
    except Error as err:
        sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                       "aagans@bowdoin.edu".format(err), keep_on_top=True)
    except NameError as err:
        sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                       "aagans@bowdoin.edu".format(err), keep_on_top=True)
# endregion


# region Settings and meta info
png = pickle.load(open("png.pickle", "rb"))
with open("default_settings.json", "r") as file_def:
    default_dict = json.load(file_def)
with open("user_settings.json", "r") as file_def:
    user_dict = json.load(file_def)
connect_var = {"host": None, "user": None, "pass": None}
for index in ["host", "user", "password"]:
    if user_dict[index] is None or user_dict[index] == "":
        connect_var[index] = default_dict[index]
    else:
        connect_var[index] = user_dict[index]

version_installed = 1.3
sg.theme('GreenTan')
# endregion

# region GUI frames/layout section
database_connection_frame = [
    [sg.Text('Connection Status:'), sg.Image('noconnect.png', subsample=40, key='-StatusImg-')],
    [sg.Button("Connect", key="-DataConnect-"), sg.Button('Disconnect', key='-DataDisconnect-')]
]

layout_w3 = [[sg.Push(), sg.Text('About the ALFRED Revival Interface', justification='center',
                                 expand_x=True, expand_y=True, font=['Helvetica', 14, 'bold']), sg.Push()],
             [sg.Push(), sg.Text('Designed and Created by A. J. Agans for the Bowdoin College Biology Department',
                                 justification='center'), sg.Push()],
             [sg.Push(), sg.Text(f'Version {version_installed} Release:', justification='center'),
              sg.Text('Fratercula arctica', font=['Helvetica', 11, 'italic'], justification='left'), sg.Push()],
             [sg.Push(), sg.Text('The phoenix logo has been designed using images from Flaticon.com'), sg.Push()],
             [sg.Push(), sg.Text('Copyright 2023 Aale Juno Agans, Hawkwood Research Group'), sg.Push()],
             [sg.Push(), sg.Text('This software is offered under the MIT License'), sg.Push()]]

choice_selection_frame = [[sg.Text('Geographic Region:'),
                           sg.Combo(['Select From List', 'Please Connect to Database for Options!'],
                                    default_value='Select From List', key='-RegionSelect-', enable_events=True)],
                          [sg.Text('Ethnic Population:'),
                           sg.Combo(['Select From List', 'Please Select Region for Options!'], 'Select From List',
                                    key='-PopSelect-', enable_events=True)],
                          [sg.Text('SNP Site:'),
                           sg.Combo(['Select From List', 'Please Select Ethnic Population for Options!'],
                                    'Select From List', key='-SNPSelect-', enable_events=True)],
                          [sg.Text('SNP Locus'),
                           sg.Combo(['Select From List', 'Please Select SNP Site for Options!'],
                                    'Select From List', key='-LocusSelect-', enable_events=True)],
                          [sg.Button('Retrieve Frequency Data', key='-RequestTable-')]
                          ]
search_pop_from_snp_frame = [[sg.Text('Type the name of a locus or SNPs to see what populations have been sampled for it!')],
                             [sg.Input(key='-SNPTypeField-'), sg.Button(button_text='Find Populations',
                                                                        key='-PopSearchButton-'),
                              sg.Checkbox("Use SNP instead of locus", key = '-UseSNP-', enable_events = True)],
                             [sg.Listbox(["Populations will be found here!"], select_mode='LISTBOX_SELECT_MODE_EXTENDED',
                                         key='-PopSNPOutput-', visible=False, expand_y=True, expand_x=True,
                                         enable_events=True)]]

comparison_frame = [[sg.Slider(range = (2,15), default_value = 1, resolution = 1,
                               orientation = 'h', key = '-CompSlider-'),
                     sg.Button("Select Number of Populations to Compare", key='-UpdateNumberComparison-')],
                    [sg.Text('Choose Multiple Regions')],
                    [sg.Combo(['Connect to Database for Options!'], key='-Reg1Choice-', enable_events=True),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg2Choice-', enable_events=True),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg3Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg4Choice-', enable_events=True, visible=False)],
                     [sg.Combo(['Connect to Database for Options!'], key='-Reg5Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg6Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg7Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg8Choice-', enable_events=True, visible=False)],
                     [sg.Combo(['Connect to Database for Options!'], key='-Reg9Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg10Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg11Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg12Choice-', enable_events=True, visible=False)],
                     [sg.Combo(['Connect to Database for Options!'], key='-Reg13Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg14Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Reg15Choice-', enable_events=True, visible=False)],
                    [sg.Text('Choose Two Populations')],
                    [sg.Combo(['Connect to Database for Options!'], key='-Pop1Choice-', enable_events=True),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop2Choice-', enable_events=True),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop3Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop4Choice-', enable_events=True, visible=False)],
                     [sg.Combo(['Connect to Database for Options!'], key='-Pop5Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop6Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop7Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop8Choice-', enable_events=True, visible=False)],
                     [sg.Combo(['Connect to Database for Options!'], key='-Pop9Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop10Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop11Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop12Choice-', enable_events=True, visible=False)],
                     [sg.Combo(['Connect to Database for Options!'], key='-Pop13Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop14Choice-', enable_events=True, visible=False),
                     sg.Combo(['Connect to Database for Options!'], key='-Pop15Choice-', enable_events=True, visible=False)],
                    [sg.Table(values=[['SNP', 'Locus']], headings=['SNP Name', 'Locus Name'], expand_y=True,
                              expand_x=True, key='-SNPCommonOutput-', alternating_row_color='white',
                              auto_size_columns=True, enable_click_events=True)],
                    [sg.Button('Fetch Results', key='-FetchResults-')]]

settings_frame = [[sg.Text('Database IP:'), sg.Input(default_text=None, key='-IPInput-')],
                  [sg.Text('Database User:'), sg.Input(default_text=None, key='-UserInput-')],
                  [sg.Text('Database Password:'), sg.Input(default_text=None, key='-PassInput-')],
                  [sg.Button('Save Settings', key='-SettingsUpdate-')]
                  ]

sample_info_frame = [[sg.Text("Type a Sample ID")],
                      [sg.Input(key='-SampleIDField-'), sg.Button(button_text='Find Sample Info',
                                                                 key='-SampleIDButton-')],
                     [sg.Multiline("Sample Descriptions will be found here!",
                                 key='-SampleDescOutput-', visible=False, expand_y=True, expand_x=True,
                                 enable_events=True)]
                     ]

tab_1_layout = [[sg.Frame('Query Options', choice_selection_frame, expand_x=True)],
                [sg.Frame('Population Search from Locus Name', search_pop_from_snp_frame,
                          expand_x=True, expand_y=True)]]
tab_2_layout = [[sg.Frame('Population Comparison Options', comparison_frame, expand_x=True, expand_y=True)]]
tab_3_layout = [[sg.Frame('Settings Options', settings_frame, expand_x=True, expand_y=True)]]
tab_4_layout = [[sg.Frame('Sample Information', sample_info_frame, expand_x=True, expand_y=True )]]

left_column_layout = [[sg.Frame('Database Connection', database_connection_frame, expand_x=True)],
                      [sg.TabGroup([[sg.Tab('Query Selection', tab_1_layout),
                                     sg.Tab('Comparison Selection', tab_2_layout),
                                     sg.Tab('Settings', tab_3_layout, visible=False, key='-SettingsTab-'),
                                     sg.Tab('Sample Info', tab_4_layout)]
                                    ], expand_x=True, expand_y=True)]
                      ]

layout = [[sg.Push(), sg.Text('Welcome to the ALFRED Revival Interface. Please make a selection!',
                              font=['Helvetica', 14, 'bold']), sg.Push()],
          [sg.Column(left_column_layout, expand_x=True, expand_y=True)],
          [sg.Button('Exit'), sg.Button('Settings'), sg.Button('About')]]

window = sg.Window('ALFRED Revival Interface', layout, resizable=True, icon=png)
# endregion

# region GUI block
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == 'Settings':
        try:
            submitted_pass = sg.PopupGetText('Please enter the password to enter the settings menu',
                                             title='Settings Password', password_char='*')
            if submitted_pass == 'Semibalanus.balanoides':
                window['-SettingsTab-'].update(visible=True)
            else:
                sg.PopupError('Woops! Wrong Password! Please try again.', keep_on_top=True)
        except Error as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)
        except NameError as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)

    if event == 'About':
        open_about(layout_w3)

    if event == '-SettingsUpdate-':
        try:
            user_dict["host"] = values['-IPInput-']
            user_dict["user"] = values['-UserInput-']
            user_dict["password"] = values['-PassInput-']
            for index in ["host", "user", "password"]:
                if user_dict[index] is None or user_dict[index] == "":
                    connect_var[index] = default_dict[index]
                else:
                    connect_var[index] = user_dict[index]
            with open('user_settings.json', 'w') as json_file:
                json.dump(user_dict, json_file)
        except Error as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)
        except NameError as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)

    if event == '-DataConnect-':
        try:
            alfred_db = mysql.connector.connect(
                host=connect_var["host"],
                user=connect_var["user"],
                password=connect_var["password"],
                database='alfred',
                connection_timeout=3
            )
            my_cursor = alfred_db.cursor()
            my_cursor.execute('SELECT geo_region FROM populationtable')
            list_region = my_cursor.fetchall()
            dup_list_region = [*set(list_region)]
            dup_list_region.sort()
            sort_region = dup_list_region
            window['-RegionSelect-'].update(values=sort_region)
            window['-Reg1Choice-'].update(values=sort_region)
            window['-Reg2Choice-'].update(values=sort_region)
            window['-Reg3Choice-'].update(values=sort_region)
            window['-Reg4Choice-'].update(values=sort_region)
            window['-Reg5Choice-'].update(values=sort_region)
            window['-Reg6Choice-'].update(values=sort_region)
            window['-Reg7Choice-'].update(values=sort_region)
            window['-Reg8Choice-'].update(values=sort_region)
            window['-Reg9Choice-'].update(values=sort_region)
            window['-Reg10Choice-'].update(values=sort_region)
            window['-Reg11Choice-'].update(values=sort_region)
            window['-Reg12Choice-'].update(values=sort_region)
            window['-Reg13Choice-'].update(values=sort_region)
            window['-Reg14Choice-'].update(values=sort_region)
            window['-Reg15Choice-'].update(values=sort_region)

            window['-IPInput-'].update(visible=False)
            window['-UserInput-'].update(visible=False)
            window['-PassInput-'].update(visible=False)
            version_check = 'SELECT version FROM gui_management'
            my_cursor.execute(version_check)
            newest_version = my_cursor.fetchall()
            newest_version = float(newest_version[0][0])
            if newest_version > version_installed:
                sg.popup_ok("A newer version of this interface is available. Please update as soon as possible!")

            if alfred_db.is_connected():
                window['-StatusImg-'].update("connected.png", subsample=40)
        except Error as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)
        except NameError as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)

    if event == '-DataDisconnect-':
        try:
            alfred_db.close()
            window['-StatusImg-'].update("noconnect.png", subsample=40)
            window['-IPInput-'].update(visible=True)
            window['-UserInput-'].update(visible=True)
            window['-PassInput-'].update(visible=True)
        except NameError:
            sg.popup_error("Oops! Please Connect to the Database Before Disconnecting", keep_on_top=True)
        except Error as err:
            sg.popup_error("Something went wrong: {} Please contact the system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)

    if event == '-RegionSelect-':
        try:
            selected_region = values['-RegionSelect-']
            if isinstance(selected_region, str):
                selected_region = (selected_region,)
            pop_sql = 'SELECT population FROM populationtable WHERE geo_region = %s'
            my_cursor.execute(pop_sql, selected_region)
            list_pop = my_cursor.fetchall()
            dup_list_pop = [*set(list_pop)]
            dup_list_pop.sort()
            sort_pop = dup_list_pop
            sort_pop = extract_first(sort_pop)
            window['-PopSelect-'].update(values=sort_pop)
        except Error as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)
        except NameError as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)

    if event == '-PopSelect-':
        try:
            selected_pop = values['-PopSelect-']
            if isinstance(selected_pop, str):
                selected_pop = (selected_pop,)
            pop_uid_selected = 'SELECT pop_uid FROM populationtable WHERE population = %s'
            my_cursor.execute(pop_uid_selected, selected_pop)
            selected_pop_uid = my_cursor.fetchall()

            find_sample = 'SELECT sample_uid FROM samplegrouptable WHERE pop_uid = %s'
            my_cursor.execute(find_sample, selected_pop_uid[0])
            list_sample_uid = my_cursor.fetchall()
            listed_sample_uid = [item for t in list_sample_uid for item in t]
            dup_sample_uid = [*set(listed_sample_uid)]

            find_snp_uid = 'SELECT snp_uid FROM samplecoveragetable WHERE sample_uid IN ({0})'.format(
                ', '.join('%s' for _ in dup_sample_uid))
            my_cursor.execute(find_snp_uid, dup_sample_uid)
            list_snp_uid = my_cursor.fetchall()
            listed_snp_uid = [item for t in list_snp_uid for item in t]
            dup_snp_uid = [*set(listed_snp_uid)]

            find_snp_name = 'SELECT site_name FROM snptable WHERE SNP_id IN ({0})'.format(
                ', '.join('%s' for _ in dup_snp_uid))
            my_cursor.execute(find_snp_name, dup_snp_uid)
            list_snp_name = my_cursor.fetchall()

            listed_snp_name = [item for t in list_snp_name for item in t]
            dup_snp_name = [*set(listed_snp_name)]
            dup_snp_name.sort()
            sort_snp = dup_snp_name
            window['-SNPSelect-'].update(values=sort_snp)
        except Error as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)
        except NameError as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)

    if event == '-SNPSelect-':
        try:
            locus_sql = 'SELECT locus_name FROM snptable WHERE site_name = %s'
            snp_selected_tup = values["-SNPSelect-"]
            if not isinstance(snp_selected_tup, tuple):
                snp_selected_tup = (snp_selected_tup,)
            my_cursor.execute(locus_sql, snp_selected_tup)
            locus_names = my_cursor.fetchall()
            locus_names.sort()
            sorted_locus = locus_names
            sorted_locus = extract_first(sorted_locus)
            window['-LocusSelect-'].update(values=sorted_locus)
            if len(sorted_locus) == 1:
                window['-LocusSelect-'].update(value=sorted_locus[0])
        except Error as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)
        except NameError as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)

    if event == '-RequestTable-':
        try:
            snp_uid_from_locus = 'SELECT SNP_id FROM snptable WHERE site_name = %s AND locus_name = %s'
            locus_selected_tup = values['-LocusSelect-']
            if not isinstance(locus_selected_tup, tuple):
                locus_selected_tup = (locus_selected_tup,)
            snp_selected_tup = values["-SNPSelect-"]
            if not isinstance(snp_selected_tup, tuple):
                snp_selected_tup = (snp_selected_tup,)
            my_cursor.execute(snp_uid_from_locus, (snp_selected_tup[0], locus_selected_tup[0]))
            locus_uid_requested = my_cursor.fetchall()
            if isinstance(locus_uid_requested, list):
                locus_uid_requested = locus_uid_requested[0]

            table_number_sql = 'SELECT tabletype_uid FROM samplecoveragetable WHERE snp_uid = %s LIMIT 1'
            my_cursor.execute(table_number_sql, locus_uid_requested)
            table_number_uid = my_cursor.fetchall()

            table_name_sql = 'SELECT type_num FROM tabletypetable WHERE type_uuid = %s'
            my_cursor.execute(table_name_sql, table_number_uid[0])
            table_name = my_cursor.fetchall()
            table_name = table_name[0][0].lower()

            create_table_sql = f'SELECT * FROM {table_name} WHERE SNPCol = %s AND SampCol ' \
                               f'IN ({", ".join("%s" for val in dup_sample_uid)})'

            args_table_list = [locus_uid_requested[0]]
            args_table_list.extend(dup_sample_uid)

            my_cursor.execute(create_table_sql, args_table_list)
            table_column_names = my_cursor.column_names
            table_column_names = list(table_column_names)
            table_column_names.remove("SNPCol")
            table_column_names = tuple(table_column_names)
            table_row_list = my_cursor.fetchall()
            table_row_list = list(table_row_list)
            for vals in range(len(table_row_list)):
                row_list = table_row_list[vals]
                row_list = list(row_list)
                row_list.remove(row_list[1])
                table_row_list[vals] = row_list
            samp_list = extract_first(table_row_list)
            samp_list = list(samp_list)

            sample_table_row_list = samp_list.copy()
            sample_table_column_names = ["Sample ID", "Sample Size", "Sample Description", "Number of Chromosomes",
                                         "Relationships to Other Samples"]

            if samp_list != []:
                samp_size_sql = 'SELECT sample_size FROM samplegrouptable WHERE ' \
                                f'sample_uid IN ({", ".join("%s" for _ in samp_list)})'
                my_cursor.execute(samp_size_sql, samp_list)
                sample_sizes = my_cursor.fetchall()
                sample_sizes = extract_first(sample_sizes)
                for sample_size in range(len(sample_sizes)):
                    mod_row = [sample_table_row_list[sample_size], sample_sizes[sample_size]]
                    sample_table_row_list[sample_size] = mod_row
                samp_desc_sql = 'SELECT sample_desc FROM samplegrouptable WHERE ' \
                                f'sample_uid IN ({", ".join("%s" for _ in samp_list)})'
                my_cursor.execute(samp_desc_sql, samp_list)
                sample_descs = my_cursor.fetchall()
                sample_descs = extract_first(sample_descs)
                for sample_desc in range(len(sample_descs)):
                    mod_row = sample_table_row_list[sample_desc]
                    mod_row.append(sample_descs[sample_desc])
                    sample_table_row_list[sample_desc] = mod_row

                samp_num_sql = 'SELECT chromosome_amount FROM samplegrouptable WHERE ' \
                               f'sample_uid IN ({", ".join("%s" for _ in samp_list)})'
                my_cursor.execute(samp_num_sql, samp_list)
                sample_nums = my_cursor.fetchall()
                sample_nums = extract_first(sample_nums)
                for sample_num in range(len(sample_nums)):
                    mod_row = sample_table_row_list[sample_num]
                    mod_row.append(sample_nums[sample_num])
                    sample_table_row_list[sample_num] = mod_row

                samp_relation_sql = 'SELECT sample_relationship FROM samplegrouptable WHERE ' \
                                    f'sample_uid IN ({", ".join("%s" for _ in samp_list)})'
                my_cursor.execute(samp_relation_sql, samp_list)
                sample_relation = my_cursor.fetchall()
                sample_relation = extract_first(sample_relation)
                for sample_rel in range(len(sample_relation)):
                    mod_row = sample_table_row_list[sample_rel]
                    mod_row.append(sample_relation[sample_rel])
                    sample_table_row_list[sample_rel] = mod_row

            try:
                if bool(table_row_list) is False:
                    insert_pop = selected_pop_uid[0][0]
                    insert_snp = locus_uid_requested[0]
                    insert_table = table_name
                    auto_fix_data = 'SELECT sample_uid FROM samplecoveragetable WHERE snp_uid = %s ' \
                                    'AND sample_uid IN ({0})'.format(', '.join('%s' for _ in dup_sample_uid))
                    auto_fix_list = [insert_snp]
                    auto_fix_list.extend(dup_sample_uid)
                    my_cursor.execute(auto_fix_data, auto_fix_list)
                    sample_uid_auto_fix = my_cursor.fetchall()
                    insert_sample = sample_uid_auto_fix[0][0]
                    insert_list = [insert_pop, insert_snp, insert_table, insert_sample]
                    insertion_check_sql = 'SELECT * FROM missingdata ' \
                                          'WHERE pop = %s AND snp_uid = %s AND `table` = %s AND sample = %s'
                    my_cursor.execute(insertion_check_sql, insert_list)
                    data_check = my_cursor.fetchall()
                    if bool(data_check) is False:
                        insertion_sql = 'INSERT INTO missingdata VALUES (%s, %s, %s, %s)'
                        my_cursor.execute(insertion_sql, insert_list)
                        alfred_db.commit()
                        sg.popup_error("Whoops! That data is missing at the moment. "
                                       "However, the database manager has been notified and the data will be added "
                                       "soon!")
                    else:
                        sg.popup_error("Whoops! That data is missing at the moment. "
                                       "However, the database manager has been notified and the data will be added "
                                       "soon!")

            except IndexError as err:
                print("Whoops")
            open_window(table_row_list, table_column_names, sample_table_row_list, sample_table_column_names)

        except Error as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)
        except NameError as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)
        except IndexError as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)
    if event == '-PopSNPOutput-':
        selected_pop_str = window['-PopSNPOutput-'].get()
        selected_pop_str = str(selected_pop_str[0])
        pyperclip.copy(selected_pop_str)
    if event == '-SampleIDButton-':
        sample_id_value = values['-SampleIDField-']
        snp_desc_search = f"SELECT sample_desc FROM samplegrouptable WHERE sample_uid = '{sample_id_value}'"
        my_cursor.execute(snp_desc_search)
        sample_desc_str = my_cursor.fetchall()
        sample_descs_str = extract_first(sample_desc_str)
        sample_descs_str = sample_descs_str[0]
        space_indexes = [i for i in range(len(sample_descs_str)) if sample_descs_str.startswith(" ", i)]
        space_indexes = [space_indexes[i] for i in range(0,len(space_indexes),14)]
        space_indexes.pop(0)
        for i in space_indexes:
            sample_descs_str = sample_descs_str[:i] + "\n" + sample_descs_str[(i+1):]
        print(sample_descs_str)
        window['-SampleDescOutput-'].update(value=sample_descs_str, visible=True)
        
    if event == '-PopSearchButton-':
        use_locus = window['-UseSNP-'].get()
        pop_snp_selected = values['-SNPTypeField-']
        pop_snp_selected = (pop_snp_selected,)
        if use_locus is False:
            pop_snp_search_sql = 'SELECT SNP_id FROM snptable WHERE locus_name = %s'
        else:
            pop_snp_search_sql = 'SELECT SNP_id FROM snptable WHERE site_name = %s'
        my_cursor.execute(pop_snp_search_sql, pop_snp_selected)
        snp_ids = my_cursor.fetchall()
        snp_ids = extract_first(snp_ids)
        if bool(snp_ids) is False:
            sg.popup_error("Whoops! That is not a known locus name. Try again!", keep_on_top=True)
        else:
            samp_snp = f'SELECT sample_uid FROM samplecoveragetable WHERE snp_uid IN ({", ".join("%s" for _ in snp_ids)})'
            my_cursor.execute(samp_snp, snp_ids)
            samples_retrieved = my_cursor.fetchall()
            samples_retrieved = extract_first(samples_retrieved)
            samp_pop = 'SELECT pop_uid FROM samplegrouptable WHERE sample_uid IN ({0})'. \
                format(', '.join('%s' for _ in samples_retrieved))
            my_cursor.execute(samp_pop, samples_retrieved)
            pops_retrieved = my_cursor.fetchall()
            pops_retrieved = extract_first(pops_retrieved)
            pops_retrieved = [*set(pops_retrieved)]
            pop_names = 'SELECT Population from populationtable WHERE pop_uid IN ({0})'. \
                format(', '.join('%s' for _ in pops_retrieved))
            my_cursor.execute(pop_names, pops_retrieved)
            pops_list = my_cursor.fetchall()
            pops_list = extract_first(pops_list)
            pops_list.sort()
            window['-PopSNPOutput-'].update(values=pops_list, visible=True)

    if event == '-Reg1Choice-':
        region_comparison('-Reg1Choice-', '-Pop1Choice-')
    if event == '-Reg2Choice-':
        region_comparison('-Reg2Choice-', '-Pop2Choice-')
    if event == '-Reg3Choice-':
        region_comparison('-Reg3Choice-', '-Pop3Choice-')
    if event == '-Reg4Choice-':
        region_comparison('-Reg4Choice-', '-Pop4Choice-')
    if event == '-Reg5Choice-':
        region_comparison('-Reg5Choice-', '-Pop5Choice-')
    if event == '-Reg6Choice-':
        region_comparison('-Reg6Choice-', '-Pop6Choice-')
    if event == '-Reg7Choice-':
        region_comparison('-Reg7Choice-', '-Pop7Choice-')
    if event == '-Reg8Choice-':
        region_comparison('-Reg8Choice-', '-Pop8Choice-')
    if event == '-Reg9Choice-':
        region_comparison('-Reg9Choice-', '-Pop9Choice-')
    if event == '-Reg10Choice-':
        region_comparison('-Reg10Choice-', '-Pop10Choice-')
    if event == '-Reg11Choice-':
        region_comparison('-Reg11Choice-', '-Pop11Choice-')
    if event == '-Reg12Choice-':
        region_comparison('-Reg12Choice-', '-Pop12Choice-')
    if event == '-Reg13Choice-':
        region_comparison('-Reg13Choice-', '-Pop13Choice-')
    if event == '-Reg14Choice-':
        region_comparison('-Reg14Choice-', '-Pop14Choice-')
    if event == '-Reg15Choice-':
        region_comparison('-Reg15Choice-', '-Pop15Choice-')

    if event == '-FetchResults-':
        number_of_comparisons = values['-CompSlider-']
        number_of_comparisons = int(number_of_comparisons)
        results_snps = []
        for i in range(2, number_of_comparisons+1):
            result_for_single = fetch_results(f'-Pop{i}Choice-')
            results_snps.append(result_for_single)
        snps_pop1 = fetch_results('-Pop1Choice-')
        list_common_snps = set(snps_pop1).intersection(*[set(x) for x in results_snps])
        try:
            list_common_snps = [(x,) for x in list_common_snps]
            list_common_snps = extract_first(list_common_snps)

            sql_for_common = 'SELECT site_name, locus_name FROM snptable WHERE ' \
                             f'SNP_id IN ({", ".join("%s" for _ in list_common_snps)})'
            my_cursor.execute(sql_for_common, list_common_snps)
            locuses_and_sites = my_cursor.fetchall()
            locuses_and_sites.sort()
            window['-SNPCommonOutput-'].update(values=locuses_and_sites)
        except mysql.connector.errors.ProgrammingError:
            sg.popup_ok("There are no common SNPs! Try a different selection of populations.", keep_on_top=True)
        except NameError as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err), keep_on_top=True)
    if event == '-UpdateNumberComparison-':
        number_of_comparisons = values['-CompSlider-']
        number_of_comparisons = int(number_of_comparisons)
        for i in range(2,number_of_comparisons+1):
            window[f'-Reg{i}Choice-'].update(visible = True)
            window[f'-Pop{i}Choice-'].update(visible = True)
        for i in range(number_of_comparisons+1, 16):
            window[f'-Reg{i}Choice-'].update(visible=False)
            window[f'-Pop{i}Choice-'].update(visible=False)
    if '+CLICKED+' in event:
        try:
            selected_value = locuses_and_sites[event[2][0]][event[2][1]]
            pyperclip.copy(selected_value)
        except NameError:
            error = 1

window.close()
# endregion
