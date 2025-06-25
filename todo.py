#!/usr/bin/env python3
from __future__ import annotations
import argparse
from subprocess import run
import shutil
import json
from pathlib import Path
from typing import Dict, Optional, List
from enum import Enum

# class CheckListResult(Enum):
#     EXIST = 1
#     CREATE = 2
#     EMPTY = 3

class TodoManager:
    def __init__(self) -> None:
        self.TodoLists: Dict[str,List[str]] = {'Main':[]}
        self.DoneLists: Dict[str,List[str]] = {'Main':[]}
    
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

    def doneTask(self, list_name:str, task_number: int)->None:
        pass
        