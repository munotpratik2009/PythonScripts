#coutner
#varibale paramter

import logging
import sys, os
import datetime
import argparse
from shutil import copyfile, move

# Command Line = <Filepath> --move --debug --new_ext=py,Python;ex,Executables

logging.basicConfig(level = None)
logger = logging.getLogger(__name__)

target_folder = 'C:\\Users\\pratik.munot\\Documents\\cleaned'

file_extensions_to_copy = [
    'dat', 'xls', 'xlsx', 'doc','docx','ppt', 'pptx','log','exe','msi','xml',
    'sql', 'png','jpg','ico','html','file','zip','ica', 'catalog','pdf', 'csv','txt',
    'htm', 'xlsm','rtf','ipynb','py'
]

file_extensions_to_move = [
    'dat', 'xls', 'xlsx', 'doc','docx', 'ppt', 'pptx','log','exe','msi','xml',
    'sql', 'png','jpg','ico','html','file','zip','ica','catalog','pdf', 'csv', 'txt',
    'htm','xlsm','rtf','ipynb','py'
]

ext_folder_map = {
    'dat' : 'HDL files',
    'xls' : 'Excel',
    'xlsx': 'Excel',
    'doc' : 'Documents',
    'docx': 'Documents',
    'pptx': 'PowerPoint',
    'ppt' : 'PowerPoint',
    'log' : 'Log Files',
    'exe' : 'Executables',
    'msi' : 'Executables',
    'xml' : 'XMLs',
    'sql' : 'SQLs',
    'png' : 'Images',
    'jpg' : 'Images',
    'ico' : 'Images',
    'html': 'HTMLs',
    'htm': 'HTMLs',
    'file': 'Files',
    'zip' : 'Zips',
    'ica' : 'Citrix',
    'catalog' : 'Report Catlog',
    'pdf' : 'PDFs',
    'txt' : 'Texts',
    'csv' : 'CSVs',
    'xlsm': 'Macros',
    'rtf' : 'RTF Templates',
    'ipynb': 'Python Notebooks',
    'py': 'Python Files'
}


class CopyMoveFiles():

    def __init__(self):
        #logging.basicConfig(level = None)
        #self.logger = logging.getLogger(__name__)
        self.root_file_path = ""
        self.move_files = False
        self.debug_flag = False
        self.new_ext_folder = {}
        self.error = False
        self.copied_counter = 0
        self.error_counter = 0
        self.root_only = False
        self.arg_parser = argparse.ArgumentParser(description='A command line utlitity to clean your folder')
        self.init_arg_parser()
        if self.debug_flag:
            self.print_args()
        #self.validate_execute_args()

    def add_new_ext_folder_to_map(self, args):
        try:
            new_ef = args.split(';')
            for ef in new_ef:
                ef1 = ef.split(',')
                if ef1[0].isalpha() and ef1[1].isalpha():
                    ext_folder_map[ef1[0]] = ef1[1]
                else:
                    self.error = True
                    logger.error('Key value pair should only contain characters')
                    return
        except:
            pass

    def init_arg_parser(self):
        self.arg_parser.add_argument('file_path', help = "Filepath to be cleaned")
        self.arg_parser.add_argument('--debug', action = "store_true", help = "Turn debug on")
        self.arg_parser.add_argument('--move', action = "store_true", help = "Move the files instead of copy")
        self.arg_parser.add_argument('--new_ext', help = "set new extensions")
        self.arg_parser.add_argument('--root', action = "store_true", help = "Clean root folder only")
        args = self.arg_parser.parse_args()
        self.root_file_path = args.file_path
        self.move_files = args.move
        self.debug_flag = args.debug
        self.root_only = args.root
        self.add_new_ext_folder_to_map(args.new_ext)

    def print_args(self):
        print('Root File Path: ', self.root_file_path)
        print('Move Files?: ', self.move_files)
        print('Debug Flag: ', self.debug_flag)
        print('New Extension: ', self.new_ext_folder)
        print('Root Only', self.root_only)

    def validate_execute_args(self):
        if not len(sys.argv) > 1:
            logger.error('No Parameters Passed. Program will exit.')
            self.error = True
            return

        if len(sys.argv) > 5:
            logger.error('Invalid number of parameters passed. Exiting..')
            self.error = True
            return

        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            logger.error('File path does not exists. Please pass a proper path.')
            self.error = True
            return
        else:
            self.root_file_path = file_path

        #move arg
        if len(sys.argv) > 2:
            if not sys.argv[2] == "--move":
                logger.error('Argument 2 is invalid')
                self.error = True
                return
            else:
                self.move_files = True

        #debug
        if len(sys.argv) > 3:
            if not sys.argv[3] == "--debug":
                logger.error('Argument 3 is invalid')
                self.error = True
                return
            else:
                self.debug_flag = True

        if len(sys.argv) > 4:
            kp = sys.argv[4].split("=")
            if kp[0] == "--new_ext":
                try:
                    new_ef = kp[1].split(';')
                    for ef in new_ef:
                        ef1 = ef.split(',')
                        if ef1[0].isalpha() and ef[1].isalpha():
                            ext_folder_map[ef1[0]] = ef1[1]
                        else:
                            self.error = True
                            logger.error('Key value pair should only contain characters')
                            return
                        print(ext_folder_map)
                except:
                    self.error = True
                    logger.error('Argument 4 not in proper format')
                    return
            else:
                self.error = True
                logger.error('Argument 4 is invalid')
                return

    def ext_to_folder_map(self, ext, return_all_folder = False):
        if return_all_folder:
            return set(x for x in ext_folder_map.values())
        else:
            return ext_folder_map.get(ext,'NA')

    def check_if_folder_exists(self):
        folder_list = self.ext_to_folder_map("",True)
        for folder in folder_list:
            dir_name = os.path.join(target_folder, folder)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

    def copy_files_to_target(self, src, file_to_copy, ext):
        folder = self.ext_to_folder_map(ext)
        if folder == 'NA':
            print('NO FOLDER FOR THIS TYPE OF EXTENSION')
        else:
            file_copied = False

            try:
                if ext in file_extensions_to_move and self.move_files:
                    move(src, os.path.join(target_folder,folder,file_to_copy))
                    #os.remove(os.path.join(target_folder,folder,file_to_copy))
                else:
                    copyfile(src, os.path.join(target_folder,folder,file_to_copy))
                    file_copied = True
            except Exception as e:
                print('[ERROR]   ', src)
                self.error_counter += 1
            self.copied_counter += 1

            print('[SUCCESS] ', '[COPIED] ' if file_copied else '[MOVED]  ' ,file_to_copy)


    def recursive_folder_traverse(self, root_fp ):

        #get the abosulte path
        ab_path = os.path.abspath(root_fp)
        #print('current path ', ab_path)

        cur_folder_files = os.listdir(root_fp)

        for f in cur_folder_files:
            f_path_name = os.path.join(ab_path, f)
            #print(f_path_name)
            if os.path.isfile(f_path_name):
                ext = f_path_name.lower().split(".")[-1]
                if ext in file_extensions_to_copy:
                    try:
                        self.copy_files_to_target(f_path_name, f, ext )
                    except Exception as e:
                        print(str(e))
            elif os.path.isdir(f_path_name) and not self.root_only:
                self.recursive_folder_traverse(f_path_name)
            else:
                print("----------UNKNOWS--------- ",f_path_name)


    def initiate_movecopy_files(self):
        self.check_if_folder_exists()
        self.recursive_folder_traverse(self.root_file_path)


# Command Line = <Filepath> --move --debug --new_ext=py,Python;ex,Executables
def main():

    logger.debug(sys.argv)
    logger.debug(len(sys.argv))


    start = datetime.datetime.now()
    logger.info('Executions Starts: ', str(start))

    print('Target Folder: ', target_folder)

    current_program = sys.argv[0]
    cm_obj = CopyMoveFiles()
    cm_obj.initiate_movecopy_files()

    print('Total Files:', cm_obj.error_counter + cm_obj.copied_counter)
    print('Total Success: ', cm_obj.copied_counter)
    print('Total Error: ', cm_obj.error_counter)

    end  = datetime.datetime.now()
    logger.info('Execution Ends: ', str(end))
    print("Total Time: ", end - start)


if __name__ == '__main__':
    main()
