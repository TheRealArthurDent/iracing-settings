from git import Repo
from pick import pick
import time
import os
import subprocess
import json
import os
from colorama import Fore
from colorama import just_fix_windows_console

os.system('chcp 1252')
just_fix_windows_console()

kill_on_exit = []

def print_colored(text: str, color: str = Fore.RESET):
    print(f'{color}{text}{Fore.RESET}')


def choose_branch():
    
    parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    repo = Repo(parent_dir)
    assert not repo.bare

    assert repo.remote().exists

    repo.remote().fetch()

    if len(repo.branches) > 1:
        option, index = pick(repo.branches, 'Pick a configuration')
        repo.branches[index].checkout()

    print_colored(f'Using configuration {Fore.BLUE}{repo.active_branch}', Fore.GREEN)

def suppress_software():
    to_suppress = get_software_config()['suppress']
    for software in to_suppress:
        task_name = software['taskName']
        print(f'Checking if {task_name} is running.')
        running_processes = get_processes(task_name)
        if (running_processes):
            print_colored(f'  {task_name} is running {len(running_processes)} times.', Fore.YELLOW)
            if software['kill']:
                for running_process in running_processes:
                    pid = running_process[1]
                    print_colored(f'  Killing PID: {pid}', Fore.RED)
                    os.system(f'taskkill /F /PID {pid}')
                    #os.kill(pid, signal.SIGKILL)
            else:
                for running_process in running_processes:
                    print(f'  Running: {running_process}')
                print_colored('  Stop the running processes and press ENTER to continue.', Fore.GREEN)
                input()
        else:
            print(f'{task_name} is not running.')      

def ensure_software_running(software, indentation: str = ''):
    name = software['name']
    task_name = software['taskName']
    print_colored(f'{indentation}Ensuring {Fore.BLUE}{name}', Fore.GREEN)
    if (get_processes(task_name)):
        print(f'{indentation}  {Fore.BLUE}{name}{Fore.RESET} is already running')
    else:
        if 'delaySeconds' in software:
            delay = software['delaySeconds']
            print_colored(f'{indentation}  Starting {Fore.BLUE}{name}{Fore.RESET} in {delay} seconds...')
            time.sleep(delay)
        else:
            print_colored(f'{indentation}  Starting {Fore.BLUE}{name}')
        exe = software['executable']
        #os.system(software['executable'])
        subprocess.Popen(exe, stdout=subprocess.DEVNULL)
    if 'killOnExit' in software:
        if(software['killOnExit']):
            print_colored(f'{indentation}  {Fore.BLUE}{name}{Fore.RESET} will be stopped if iRacing terminates.')
            kill_on_exit.append(software)
    if 'dependents' in software:
        for dependent in software['dependents']:
            ensure_software_running(dependent, f'{indentation}  ')

def check_and_start_supporting_software():
    print_colored('Starting supporting software', Fore.GREEN)
    supporting_software = get_software_config()['supporting']
    for software in supporting_software:
        ensure_software_running(software, '  ')

def start_iracing():
    print_colored(f'Starting {Fore.BLUE}iracing...', Fore.GREEN)
    iracing = get_software_config()['iracing']
    ensure_software_running(iracing, '  ')

def monitor_iracing_process():
    if(len(kill_on_exit) > 0):
        iracing = get_software_config()['iracing']
        name = iracing['name']
        task_name = iracing['taskName']
        print_colored(f'Monitoring {Fore.BLUE}{name}', Fore.GREEN)
        while len(get_processes(task_name)) > 0:
            time.sleep(3)
        print_colored(f'{Fore.BLUE}{name} has been terminated.')
        kill_processes(kill_on_exit)

def kill_processes(to_kill_list):
    for to_kill in to_kill_list:
        name = to_kill['name']
        task_name = to_kill['taskName']
        print_colored(f'  Stopping {Fore.BLUE}{name}', Fore.RED)
        # TODO really stop
        running_processes = get_processes(task_name)
        if (running_processes):
            #print_colored(f'  {task_name} is running {len(running_processes)} times.', Fore.YELLOW)
            for running_process in running_processes:
                pid = running_process[1]
                print_colored(f'    Killing PID: {pid}', Fore.RED)
                os.system(f'taskkill /F /PID {pid}')

def get_software_config():
    return json.load(open('software.json'))

def get_processes(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name, '/FO', 'CSV', '/NH'
    # use built-in check_output right away
    output = subprocess.check_output(call).decode('cp1252')
    #print(f'output: {output}')
    
    if (output.startswith('INFORMATION')):
        # process is not running
        return []
    # return an array of running processes
    result = []
    for raw_line in output.strip().split('\r\n'):
        line = []
        for token in raw_line.split(','):
            line.append(token.replace('"',''))
        result.append(line)
    return result

choose_branch()
suppress_software()
check_and_start_supporting_software()
start_iracing()
monitor_iracing_process()

