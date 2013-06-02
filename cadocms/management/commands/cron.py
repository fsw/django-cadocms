from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

import os, sys, time

from multiprocessing import Process

class TaskProcess(Process):
    daemon = True
    def __init__(self, command, *args, **kwargs):
        self.command = command
        Process.__init__(self, *args, **kwargs)
    
    def run(self):
        call_command(command)

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        
        tasks = []
        for task in settings.CRON_TASKS:
            proc = TaskProcess(task[0])
            proc.start()
            tasks.append(proc)

        while tasks:
            for i in range(len(tasks)):
                if not tasks[i].is_alive():
                    tasks.pop(i)
                    break
            time.sleep(.1)