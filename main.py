import PySimpleGUI as sg
import mysql.connector
from mysql.connector import Error
import csv

sg.theme('Dark Blue 3')  # please make your windows colorful

database_connection_frame = [
    [sg.Text('Connection Status:'), sg.Image('noconnect.png', subsample=40, key='-StatusImg-')],
    [sg.Button("Connect", key="-DataConnect-"), sg.Button('Disconnect', key='-DataDisconnect-')]
]


def open_window(table_data, table_headings):
    layout_w2 = [[sg.Text('Generated Frequency Table')],
              [sg.Table(table_data, table_headings, expand_x=True, expand_y=True)],
              [sg.Button('Export Table', key='-ExportTable-'),
               sg.Button('Exit', key='-TableExit-')]]
    window_w2 = sg.Window("Frequency Table", layout_w2, resizable=True)
    while True:
        event, values = window_w2.read()
        if event == '-TableExit-' or event == sg.WIN_CLOSED:
            break
        if event == '-ExportTable-':
            file_path = sg.popup_get_file('Please save your table!', 'Saving Frequency Table as CSV', save_as=True,
                              file_types=(('.csv',),))
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(table_headings)
                writer.writerows(table_data)

        window_w2.close()


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
table_frame = [[sg.Table([['Allele Frequency Here!', 'Allele Frequency Here!', 'Allele Frequency Here!'],
                          ['Allele Frequency Here!', 'Allele Frequency Here!', 'Allele Frequency Here!']],
                         ['Sample ID', 'Freq1', 'Freq2'], expand_x=True, expand_y=True, key='-FreqTable-')],
               [sg.Button('Export Results', key='-Export-')]]
right_column_layout = [[sg.Frame('Database Results Table', table_frame, expand_x=True, expand_y=True)]]
left_column_layout = [[sg.Frame('Database Connection', database_connection_frame, expand_x=True)],
                      [sg.Frame('Query Options', choice_selection_frame, expand_x=True)]
                      ]
layout = [[sg.Text('Welcome to the ALFRED Revival Interface. Please make a selection!')],
          [sg.Column(left_column_layout, expand_x=True, expand_y=True)],
          [sg.Button('Exit')]]

window = sg.Window('ALFRED Revival Interface', layout, resizable=True)

while True:  # Event Loop
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == '-DataConnect-':
        try:
            alfred_db = mysql.connector.connect(
                host="139.140.208.19",
                user="clientInterface",
                password='password',
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

            if alfred_db.is_connected():
                window['-StatusImg-'].update("connected.png", subsample=40)
        except Error as err:
            sg.popup_error("Something went wrong: {} Please contact your system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err))
    if event == '-DataDisconnect-':
        try:
            alfred_db.close()
            window['-StatusImg-'].update("noconnect.png", subsample=40)
        except NameError:
            sg.popup_error("Oops! Please Connect to the Database Before Disconnecting")
        except Error as err:
            sg.popup_error("Something went wrong: {} Please contact the system administrator for assistance at "
                           "aagans@bowdoin.edu".format(err))

    if event == '-RegionSelect-':
        selected_region = values['-RegionSelect-']
        pop_sql = 'SELECT population FROM populationtable WHERE geo_region = %s'
        my_cursor.execute(pop_sql, selected_region)
        list_pop = my_cursor.fetchall()
        dup_list_pop = [*set(list_pop)]
        dup_list_pop.sort()
        sort_pop = dup_list_pop
        window['-PopSelect-'].update(values=sort_pop)

    if event == '-PopSelect-':
        selected_pop = values['-PopSelect-']
        pop_uuid = 'SELECT pop_uid FROM populationtable WHERE geo_region = %s'
        my_cursor.execute(pop_uuid, selected_region)
        list_pop_uuid = my_cursor.fetchall()
        dup_list_pop_uid = [*set(list_pop_uuid)]
        pop_uid_selected = 'SELECT pop_uid FROM populationtable WHERE population = %s'
        my_cursor.execute(pop_uid_selected, selected_pop)
        selected_pop_uid = my_cursor.fetchall()

        find_sample = 'SELECT sample_uid FROM samplegrouptable WHERE pop_uid = %s'
        my_cursor.execute(find_sample, selected_pop_uid[0])
        list_sample_uid = my_cursor.fetchall()
        listed_sample_uid = [item for t in list_sample_uid for item in t]
        dup_sample_uid = [*set(listed_sample_uid)]

        find_snp_uid = 'SELECT snp_uid FROM samplecoveragetable WHERE sample_uid = %s'
        list_snp_uid = []
        for sampled_uids in dup_sample_uid:
            sampled_uids = (sampled_uids,)
            my_cursor.execute(find_snp_uid, sampled_uids)
            loop_snp_uid = my_cursor.fetchall()
            list_snp_uid.append(loop_snp_uid)
        listed_snp_uid = [item for t in list_snp_uid for item in t]
        dup_snp_uid = [*set(listed_snp_uid)]

        list_snp_name = []
        find_snp_name = 'SELECT site_name FROM snptable WHERE SNP_id = %s'
        for snp_uids in dup_snp_uid:
            my_cursor.execute(find_snp_name, snp_uids)
            loop_snp_name = my_cursor.fetchall()
            list_snp_name.append(loop_snp_name)
        listed_snp_name = [item for t in list_snp_name for item in t]
        dup_snp_name = [*set(listed_snp_name)]
        dup_snp_name.sort()
        sort_snp = dup_snp_name
        window['-SNPSelect-'].update(values=sort_snp)

    if event == '-SNPSelect-':
        locus_sql = 'SELECT locus_name FROM snptable WHERE site_name = %s'
        snp_selected_tup = values["-SNPSelect-"]
        my_cursor.execute(locus_sql, snp_selected_tup)
        locus_names = my_cursor.fetchall()
        locus_names.sort()
        sorted_locus = locus_names
        window['-LocusSelect-'].update(values=sorted_locus)

    if event == '-RequestTable-':
        snp_uid_from_locus = 'SELECT SNP_id FROM snptable WHERE site_name = %s AND locus_name = %s'
        locus_selected_tup = values['-LocusSelect-']
        snp_selected_tup = values["-SNPSelect-"]
        my_cursor.execute(snp_uid_from_locus, (snp_selected_tup[0], locus_selected_tup[0]))
        locus_uid_requested = my_cursor.fetchall()
        locus_uid_requested = locus_uid_requested[0]
        locus_uid_requested = (locus_uid_requested,)

        table_number_sql = 'SELECT tabletype_uid FROM samplecoveragetable WHERE snp_uid = %s'
        my_cursor.execute(table_number_sql, locus_uid_requested[0])
        table_number_uid = my_cursor.fetchall()

        table_name_sql = 'SELECT type_num FROM tabletypetable WHERE type_uuid = %s'
        my_cursor.execute(table_name_sql, table_number_uid[0])
        table_name = my_cursor.fetchall()
        table_name = table_name[0][0].lower()

        select_snp = 'SELECT snp_uid FROM samplecoveragetable WHERE snp_uid = %s AND sample_uid = %s'
        snp_samples_list = []
        for samples_snps in dup_sample_uid:
            samples_snps = (samples_snps,)
            my_cursor.execute(select_snp, (locus_uid_requested[0][0], samples_snps[0]))
            snpsamples_loop = my_cursor.fetchall()
            snp_samples_list.append(snpsamples_loop)

        snp_samples_list = [i for i in snp_samples_list if i]

        create_table_sql = 'SELECT * FROM {tablename} WHERE SNPCol = %s'
        my_cursor.execute(create_table_sql.format(tablename=table_name), snp_samples_list[0][0])
        table_column_names = my_cursor.column_names
        table_row_list = my_cursor.fetchall()
        open_window(table_row_list, table_column_names)
window.close()
