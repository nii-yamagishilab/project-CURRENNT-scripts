#!/usr/bin/python
import sys
import os

currennt_cmd = 'currennt'
autosave = ".autosave"
jsnname = ".jsn"

def is_epoch(file_name):
    return file_name.endswith(autosave) and not file_name.startswith('._')

def is_jsn(file_name):
    return file_name.endswith(jsnname) and not file_name.startswith('._')

def delete_epoch(file_dir, file_name):
    print("delete %s/%s" % (file_dir, file_name))
    os.system("rm %s" % (file_dir + '/' + file_name))

def convert_epoch(file_dir, file_name):
    new_name = file_name.rstrip(autosave) + jsnname
    print("convert %s/%s" % (file_dir, file_name))
    os.system("%s --print_weight_opt 2 --print_weight_to %s --cuda off --network %s > /dev/null 2>&1" % (currennt_cmd, file_dir + '/' + new_name, file_dir + '/' + file_name))
    if is_jsn(new_name):
        delete_epoch(file_dir, file_name)
    return


def clean_epoch(file_dir, save_to_jsn=False):
    file_list = os.listdir(file_dir)
    if any([is_epoch(x) for x in file_list]):
        if any([is_jsn(x) for x in file_list]):
            for x in file_list:
                if is_jsn(x):
                    print("find: %s/%s" % (file_dir, x))
            for x in file_list:
                if is_epoch(x):
                    delete_epoch(file_dir, x)
        else:
            tmp = [x for x in file_list if is_epoch(x)]
            tmp.sort()
            for x in tmp[:-1]:
                delete_epoch(file_dir, x)
            convert_epoch(file_dir, tmp[-1])
    return
            
def clean_dir(file_dir):
    dir_list = os.listdir(file_dir)
    clean_epoch(file_dir)
    for x in dir_list:
        sub_dir_name = file_dir + '/' + x
        if os.path.isdir(sub_dir_name):
            clean_dir(sub_dir_name)
    return

if __name__ == "__main__":
    clean_dir(sys.argv[1])
