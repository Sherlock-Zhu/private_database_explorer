from executor import MilvusExecutor

import yaml
from easydict import EasyDict
import argparse

def read_yaml_config(file_path):
    with open(file_path, "r") as file:
        config_data = yaml.safe_load(file)
    return EasyDict(config_data)

class CommandLine():
    def __init__(self, config_path):
        self._mode = None
        self._executor = None
        self.config_path = config_path

    def show_start_info(self):
        with open('./start_info.txt') as fw:
            print(fw.read())

    def run(self):
        self.show_start_info()
        conf = read_yaml_config(self.config_path)
        self._executor = MilvusExecutor(conf) 
        print('  1.use command `build data/history_24/baihuasanguozhi.txt` to build the knowledge database')
        print('  2.use command `ask` to start ask question, use `-d` for debug mode')
        print('  3.to delete knowledge, please use `remove baihuasanguozhi.txt`。')
        self._mode = 'milvus'
        while True:
            command_text = input("(llm mode select)  ")
            self.parse_input(command_text)

    def parse_input(self, text):
        commands = text.split(' ')
        if commands[0] == 'build':
            if len(commands) == 3:
                if commands[1] == '-overwrite':  
                    print(commands)
                    self.build_index(path=commands[2], overwrite=True)
                else:
                    print('(llm mode select)  build only supports parameter `-overwrite`')
            elif len(commands) == 2:
                self.build_index(path=commands[1], overwrite=False)
        elif commands[0] == 'ask':
            if len(commands) == 2:
                if commands[1] == '-d':
                    self._executor.set_debug(True)
                else: 
                    print('(llm mode select)  ask only supports parameter `-d`')
            else:
                self._executor.set_debug(False)
            self.question_answer()
        elif commands[0] == 'remove':
            if len(commands) != 2:
                print('(llm mode select) remove only accept one parameter')
            self._executor.delete_file(commands[1])
            
        elif 'quit' in commands[0]:
            self._exit()
        else: 
            print('(llm mode select) currently only support command [build|ask|remove|quit], please try again')
            
    def query(self, question):
        ans = self._executor.query(question)
        print(ans)
        print('+---------------------------------------------------------------------------------------------------------------------+')
        print('\n')

    def build_index(self, path, overwrite):
        self._executor.build_index(path, overwrite)
        print('(llm mode select) index build completed')

    def remove(self, filename):
        self._executor.delete_file(filename)
        
    def question_answer(self):
        self._executor.build_query_engine()
        while True: 
            question = input("(llm) question: ")
            if question == 'quit':
                print('(llm) quit from aks mode')
                break
            elif question == "":
                continue
            else:
                pass
            self.query(question)

    def _exit(self):
        exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str, help='Path to the configuration file', default='cfgs/config.yaml')
    args = parser.parse_args()

    cli = CommandLine(args.config)
    cli.run()

