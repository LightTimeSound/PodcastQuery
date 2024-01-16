import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

source_code_dir = os.getenv('SOURCE_DIR')
backup_dir = os.getenv('BACKUP_DIR') + '\PodcastQuery'

def create_directory(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)


def copy_files(src_dir, file_names, dest_dir):
    dest_dir = dest_dir + ' ' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    create_directory(dest_dir)

    for file in file_names:
        src_file = os.path.join(src_dir, file)
        if os.path.isfile(src_file):
            shutil.copy(src_file, dest_dir)
        else:
            print(f'File {file} does not exist in the source directory.')

file_names = []

for file in os.listdir(source_code_dir):
    #if file ends with .py, .sql, .env, .yaml, .txt, .md, .pickle, .csv, .index, add it to the list:
    if file.endswith('.py') or file.endswith('.sql') or file.endswith('.env') or file.endswith('.yaml') or file.endswith('.txt') or file.endswith('.md') or file.endswith('.pickle') or file.endswith('.csv') or file.endswith('.index'):
        file_names.append(file)

copy_files(source_code_dir, file_names, backup_dir)