import json
import subprocess

json_file = open("developer_log.json")
data = json.load(json_file)
length_data = len(data['issues'])
paths = []
working_directory = input("Set working directory: ")
working_directory = working_directory.strip()

for i in range(length_data):
    paths.append(data['issues'][i]['path'])

paths = [*set(paths)]
paths = [s.replace('/ALFREDRevival.zip', '') for s in paths]
paths = [s.replace('.zip', '') for s in paths]
paths = [s.replace('ALFREDRevival', f'{working_directory}/') for s in paths]

print(paths)

for path in paths:
    bash_command = 'codesign -s "Developer ID Application: Aale Agans (RC7HB96RSJ)" -v --timestamp --force "{0}"'.format(path)
    subprocess.run(bash_command, shell=True, cwd=working_directory)


