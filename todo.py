#!/usr/bin/env python3
from __future__ import annotations
import argparse
from subprocess import run
import shutil
import json
from pathlib import Path
from typing import Dict, Optional, List
from enum import Enum
import re

class TodoManager:
    def __init__(self, todo_path: Path) -> None:
        self.FilePath:Path = todo_path
        self.TodoLists: Dict[str,List[str]] = {}
        self.DoneLists: Dict[str,List[str]] = {}
        self.__parseFile()
    
    def __parseFile(self)->None:
        file_lines: List[str] = []
        with open(self.FilePath, 'r') as f:
            for line in f:
                file_lines.append(line.strip())
            
            current_section : Dict[str, List[str]] = {}
            for l in file_lines:
                if not l:
                    continue
                if l.startswith('# '):
                    section_name = l[2:].strip()
                    if section_name == 'Todo':
                        current_section = self.TodoLists
                    elif section_name == 'Done':
                        current_section = self.DoneLists
                    else:
                        print(f"Unknown section: {section_name}")
                        continue
                elif l.startswith('## '):
                    list_name = l[3:].strip()
                    current_section[list_name] = []
                else:
                    line_match = re.match(r'^\d+\.\s(.*)$', l.strip())
                    # plain text line will be treated as a task
                    task : str= line_match.group(1) if line_match else l.strip()
                    current_section[list_name].append(task)
        pass
    
    def __writeFile(self)->None:
        pass
    
    def __addTask(self, list_name: str, task: str)->None:
        self.TodoLists[list_name].append(task)

    def __addList(self,list_name: str)->None:
        if list_name in self.TodoLists:
            return
        else:
            self.TodoLists[list_name] = []

    def __checkListName(self,list_name: str )->str:
        if list_name in self.TodoLists:
            return list_name
        else:
            print(f"No such list named as {list_name}.")

            # Check matching results.
            matched_name: List[str] = []
            for exist_list in self.TodoLists:
                if list_name in exist_list:
                    matched_name.append(exist_list)
            print(f"Possible list you'd like to refer to:")
            for i in range(len(matched_name)):
                name:str = matched_name[i]
                print(f"{i+1}. {name}")
            
            # Handle user input
            print(f"Which one is what you are looking? Enter the number: (0 for abort)")
            try:
                selection: int = int(input())
                if  selection == 0:
                    return ''
                elif selection < len(matched_name)+1:
                    new_name = matched_name[int(selection-1)]
                    return new_name
                else:
                    print("Invalid input: out of range")
                    exit(1)
            except ValueError:
                print("Invalid input: not a integer")
                exit(2)

            return ''

    def addTask(self, list_name: str, task: str)-> None:
        processed_list_name =self.__checkListName(list_name)
        if processed_list_name:
            self.__addList(processed_list_name)
            self.__addTask(processed_list_name,task)
        else:
            print(f"Abort by user.")
        return

    def addList(self, list_name: str)-> None:
        processed_list_name =self.__checkListName(list_name)
        if processed_list_name:
            self.__addList(processed_list_name)
        else:
            print(f"Abort by user.")
        return

    def __orderList(self, list_name:str) -> None:
        pass
        
    def __orderTask(self, list_name:str, old_task_number: int, new_task_number: int)-> None:
        pass
        
    def doneList(self, list_name:str)->None:
        self.__orderList(list_name)
        pass
    
    def restoreList(self, list_name:str)->None:
        pass
    
    def doneTask(self, list_name:str, task_number: int)->None:
        pass
        
    def restoreTask(self, list_name:str, task_number: int) -> None:
        pass
        
    def clearDoneList(self)-> None:
        print("Are you sure to delete all the done tasks and done lists? (y/N)")
        opt = input()
        if opt.lower() == 'y':
            self.DoneLists={}
            print("Cleared.")
        else:
            print("Abort. Done list not modified.")
            return
            
    def viewTodo(self)->None:
        pass
    
    def viewTodoList(self, list_name: str)->None:
        pass
    
    def viewDone(self)->None:
        pass
    
    def viewDoneList(self, list_name: str)->None:
        pass
    
        
# ----------------------
DEBUG:bool = True
# DEBUG:bool = False

def main():
    if DEBUG is not None:
        HOME = Path.home()
        TODO_FILE = HOME / 'TODO.md'
        todo_manager:TodoManager = TodoManager(TODO_FILE)
    pass
    
if __name__=="__main__":
   main() 