#!/usr/bin/env python3

import argparse
import re
import time
import signal
import subprocess
import random
import sys

def parse_time_argument(time_arg):
    match = re.match(r"(\d+)([smh])", time_arg)
    if not match:
        raise argparse.ArgumentTypeError("El formato del tiempo debe ser numérico seguido de 's', 'm' o 'h'")

    value = int(match.group(1))
    unit = match.group(2)

    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600

def timer(seconds):
    start_time = time.time()
    end_time = start_time + seconds

    try:
        while time.time() < end_time:
            remaining_time = int(end_time - time.time())
            print(f"Tiempo restante: {remaining_time} segundos", end="\r")
            time.sleep(1)

        print("¡Tiempo completado!")
        print_ascii_image()
        play_sound()
    except KeyboardInterrupt:
        print("\nTemporizador interrumpido. Saliendo...")
        sys.exit()

def print_ascii_image():
    ascii_images = [
            '''
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠠⢄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⢉⣶⣦⣄⣀⣀⠀⠀⠀⣠⣤⣶⣶⣶⠤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⡿⠋⠉⠉⠀⠈⣩⣿⣾⣿⢋⣉⠻⡟⣻⣿⣶⣿⣦⣀⣠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣆⠁⠀⠀⠀⣠⣴⣿⣿⡏⢰⢴⣯⢿⣽⣿⡿⠏⣉⣿⣿⣯⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⠀⠀⣰⣿⣏⣾⡟⣷⣿⡶⢿⣧⡹⣿⣿⣀⠸⣿⣿⣿⠿⣿⣷⣄⠀⠀⠀⠀⠀⠀⣠⠴⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠀⠀⠀⠀⠻⡀⠈⢷⠀⣿⣉⣻⣼⣷⢿⣿⣷⣾⡹⣿⡽⣿⣿⣄⣸⣿⡝⣷⡙⢻⣿⡳⣄⣀⣠⡴⠚⠁⠀⠀⠀⠀⠀⢠⠴⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠳⣄⠀⠀⠀⠳⡀⠈⣷⣿⣼⣿⣿⣿⣄⡉⣿⣿⣇⣿⣿⣿⡆⠛⠻⣿⣿⢸⣷⣿⣿⣷⣬⡿⠁⠀⠀⠀⠀⠀⠀⣠⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⣤⡀⠀⢷⠀⢹⣿⣿⣿⣿⠋⠀⠀⠉⢻⣿⣿⣿⣿⠁⠀⣶⣿⣿⣿⣿⣻⣿⣿⣿⡄⠀⠀⠀⠀⠀⣠⡾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣟⣄⠈⣧⣿⣿⣿⣇⠀⢀⣀⡤⠀⠀⣿⣿⣿⣿⠀⡀⣿⣿⣿⣿⣟⣿⣿⣿⢿⢻⡄⠀⣀⡴⣾⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠒⠶⠦⣄⣀⣹⣯⣶⣿⣿⣿⣿⠿⠀⠉⠉⠀⠀⠀⣿⣿⢿⣿⣦⣿⣿⣿⣿⣿⡆⣿⣿⣿⣸⠀⣏⠉⢁⣼⡟⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢻⡇⢿⠀⣿⣿⣧⠀⠀⠀⠀⠀⠀⠰⠿⠉⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⢻⣠⡞⡜⠀⣠⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠈⠁⠀⢷⢿⣷⣶⠆⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣻⣧⢴⢾⠿⢮⣁⣴⣟⣥⣶⣶⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡄⠀⠀⠀⠀⠻⠿⣄⣀⣀⣀⠤⣾⣻⣿⡿⣿⠟⠸⣿⣿⡿⣿⣿⢋⣽⠃⡞⠘⠀⠀⡟⣿⡛⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⠀⢠⠎⠀⠀⠀⠀⠀⠀⠀⠀⠉⠟⠉⠴⠋⠀⠀⢿⡛⠘⠋⠉⠉⠛⠚⠀⠀⠀⠀⢁⡿⠗⠲⠦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠐⠶⠦⠤⣄⣀⣀⣀⣀⣀⣀⣨⡷⣹⠀⠀⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠒⠒⠒⠒⠶⠶⣛⠛⣧⡇⠀⠀⢻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣤⣤⣤⠤⠤⡤⠤⠄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣄⠀⠀⠈⠳⣿⢷⠀⠀⣸⠃⠀⠀⠀⠀⠀⣠⠞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡶⠀⣾⡇⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠀⠀⠀⠈⠓⢦⣀⣠⡟⣸⠀⢀⠏⠀⠀⠀⠀⠀⠸⠋⠀⠀⠀⠀⢠⠆⠀⠸⣄⠀⠀⠀⠀⢀⣾⠁⢰⣿⣁⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠓⠶⣤⣀⣀⠙⣿⣧⠇⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⠀⠀⠀⠉⢳⠀⠀⠀⢸⠇⠀⣿⠏⠁⠀⠉⠉⠉⠐⠒⠄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡠⠀⠀⠀⠀⠀⠀⠀⠉⠛⠷⣾⡿⠀⠀⣼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⠁⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⢼⡟⠲⠦⢄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣽⠃⠀⠀⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⠁⠀⠀⠀⠀⠀⠀⠀⠀⢠⡏⣸⣾⠇⠀⠀⠀⠉⠑⠦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠉⡿⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⣼⠃⠀⠀⠀⠀⠀⡴⠀⠀⢀⡾⢀⠟⣿⠆⠀⢀⡀⠀⠀⠀⠀⠙⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⠤⠤⠶⠶⠶⠖⠾⣇⠀⠀⠀⢸⣷⠀⠀⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⠀⠀⠸⠁⠀⢠⡟⠁⡞⢠⠃⠀⠀⢀⠿⢶⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢠⣀⡀⠀⠀⣴⠶⠋⠉⠁⠀⠀⠀⠀⠀⠀⠀⢀⡿⡄⠀⠀⣼⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡟⢀⡞⠁⣼⠒⠶⠦⠤⠀⠀⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠉⢧⣱⣄⣘⡶⠖⠀⠀⠀⠀⠀⠀⢀⣠⠴⠛⣡⢙⣤⠴⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢦⣟⡄⠚⢀⣼⠯⢄⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡠⠴⠖⠊⠉⠀⢀⣴⡧⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣴⠿⠦⢄⡀⠀⠀⠉⠙⠲⠦⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠐⠒⢉⣉⣉⠠⠤⠴⠶⠶⠶⢶⡿⠋⣀⡤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠮⣟⠳⢦⣀⠙⠢⡄⠀⠀⠀⠀⠀⠉⠲⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⣠⡴⠶⠋⠉⠁⠀⠀⠀⠀⢀⣀⣴⣯⠶⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢧⡀⠈⠙⠦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢾⡍⠳⠦⡄⠀⠀⠀⠀⢀⡴⢋⣽⠏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠲⢴⡶⢦⣳⣦⣄⡀⠈⠑⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⠻⣦⡀⢹⡀⠀⢀⡴⠋⣠⡟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⡉⢿⣶⣏⣲⣦⡀⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⠳⣌⣱⠞⠉⠀⣼⡻⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣦⡀⠉⠉⠙⢷⡀⠀⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⣴⠞⠉⣁⡀⠀⣼⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⡄⠀⠀⠀⢻⡄⠀⠀⠹⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⡾⠁⢀⣾⠏⢀⣼⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣷⡀⠀⠀⠀⠹⣆⠀⠀⠘⢦⠀⠀⠀⠀⣀⣴
⠀⢠⡞⠁⢀⣾⠇⢀⣾⣿⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⢸⣿⣧⡀⠀⠀⠀⠘⢦⡀⠀⠘⢇⣠⣶⣾⣿⣿
⣰⠏⠀⠀⠿⠁⢠⣾⡇⢸⢸⢠⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⠋⡄⢸⣿⠻⢿⣦⢦⡀⠀⠀⠹⣦⣶⣿⣿⣿⣿⣿⣿
⠁⠀⠀⠀⠀⢠⡏⠈⣇⢸⡜⣏⢿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡞⠁⠼⠃⢰⣾⡆⠀⠈⢿⣹⣦⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⢰⣿⣤⣶⡿⠿⠿⣿⣆⠳⣄⠀⠀⠀⠀⠀⠠⣄⡀⠀⠀⢀⡞⠉⠉⠙⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠋⠀⠀⠀⠆⣾⢹⣷⠀⠀⢘⣷⣏⢧⠀⠀⠈⢿⣿⣿⣿⣿⣿
⠀⠀⠀⠀⣿⠿⠃⠀⠀⠀⠀⠈⢻⣷⣌⡓⠀⠀⠀⠀⠀⠈⠉⠁⢰⣏⣴⣯⣷⡀⢻⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢪⣞⣹⣦⡽⠦⢤⣘⡟⣏⠊⠃⠀⠀⠈⢻⣿⣿⣿⣿
⠀⠀⠀⢰⠇⠀⠀⠀⠀⠀⠀⠰⣄⡻⣎⠙⠲⠤⣄⣀⣀⣀⣀⣀⣼⡿⡿⠉⢸⣷⣀⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣿⣿⠟⠁⠀⠀⠀⠘⢽⣿⡀⠀⠀⠀⠀⠀⠹⣿⣿⣿
⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢾⣿⣦⣀⠀⠉⠉⠉⣿⣿⣿⣡⡇⠀⠀⣿⣿⠉⠓⠶⣄⣀⡀⠀⠀⣀⣠⡴⠞⣋⡾⡛⠁⠀⠀⠀⠀⠀⠀⠈⢿⡇⠀⠀⠀⠀⠀⠀⠘⢿⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠳⣏⣳⣶⣄⣴⠿⡿⠟⠛⠛⠛⠛⠻⠿⢦⣄⣀⠀⠉⠉⣿⠉⠉⣁⣠⣞⡉⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡀⠀⠀⠀⠀⠀⠀⠈⢿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⠉⡉⣉⢉⣙⡛⠃⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠳⠶⢶⠿⠊⠉⠙⡒⡊⠉⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
        ''',
        '''
        ⣀⣀⢀⣀⣀⣤⡴⠞⠋⠁⠀⠀⣀⣠⡞⠁⠀⢸⡄⢠⡏⠀⣿⠀⠀⢀⣿⢹⠀⠀⠀⠀⠀⠀⠀⢰⢏⡏⢀⡼⢿⣧⠟⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣩⡽⠋⠉⠀⣸⠃⠀⠀⠀⠀⢠⣟⡿⠀⠀⠀⠀⣧⡞⠀⠀⢿⠀⠀⢸⣿⢸⠀⠀⠀⢾⡲⢤⣀⣟⣾⣠⡿⢣⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣈⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠉⠀⠀⠀⣸⡇⠀⠀⠀⠀⢀⣟⡿⠁⠀⠀⠀⠀⠘⠃⠀⠀⠘⣆⠀⣼⣿⣿⠀⠀⠀⠈⠙⣦⠙⢯⣵⡿⣡⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣿⡿⠋⠳⢿⣀⠀⠀⠀⠀⠀⠀⠀
⣠⡞⠀⢰⣿⠀⠀⠀⠏⠀⣼⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡄⡇⢸⣿⠀⠀⠀⠀⠸⣧⣤⡾⢟⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⣹⣿⠋⠀⠀⠀⠀⠉⠓⠲⠤⠤⠀⠀⢰
⠏⠀⠀⣿⡇⠀⠀⢸⠀⣸⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣧⠀⣿⠀⠀⠀⠀⠀⣿⣿⣡⣞⡞⠀⠀⠀⠀⠀⠀⠀⣀⡴⠋⢠⣼⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⢄⠴⠛
⠂⠀⣸⡟⡇⠀⠀⡏⢠⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣄⠸⡄⠀⠀⠀⠀⣽⡿⢋⡟⠀⠀⠀⠀⠀⣀⡴⠞⠁⢀⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣶⠗⠉⠀⡐
⠀⠀⣿⢁⣇⠀⢠⠀⣾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡄⠀⠀⣼⡟⢠⠞⠀⠀⢀⣤⠔⠋⠁⠀⢠⣴⠟⠁⠀⠀⠀⠀⠀⠀⠀⢀⣤⡤⠚⠋⠀⠀⠀⠀⡇
⠀⠀⣿⢸⢻⣀⣸⣠⡧⠶⠶⠶⠾⠿⠿⠿⠿⠿⣷⣶⣦⣤⣀⣀⣀⣀⠀⠀⠀⢳⡄⣰⠋⣠⣏⡤⠖⠋⠉⠀⠀⢀⡤⠞⠉⠀⠀⠀⠀⢀⣀⣠⠤⠶⠚⠉⠁⠀⠀⠀⠀⠀⠀⠀⡇
⠀⠀⡏⠈⢸⡇⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⡟⠉⠿⠛⠉⠀⠀⠀⠀⠹⠏⡴⠋⠁⠀⠀⠀⢠⣴⣾⠭⠤⠤⠴⠒⠒⠒⠋⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃
⠀⢘⡇⠀⢸⣿⡄⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣦⣾⣆⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠
⡆⠘⢿⣶⣾⣁⠳⣼⣀⠠⠤⠤⠄⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠿⠻⢷⣦⣤⢦⣄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
⡇⠀⠀⢹⣿⣿⣿⣿⣿⣿⣶⣶⣶⣶⣦⣉⠙⠲⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠙⢿⡿⠿⣿⣶⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
⡇⠀⠀⢸⡏⠻⣿⣿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣦⣀⢻⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣹⠟⠋⠁⠀⠈⠙⠻⠿⣶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
⢿⡀⠀⠨⡇⠀⢻⣧⠀⠀⢻⣿⣿⣿⣏⠉⣻⣿⣿⣦⠹⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⣷⣄⠀⠀⠀⠀⠀⠀⠀⢸
⣺⣧⠀⠀⢻⣻⠁⢻⡄⠀⠘⣿⣉⣿⣿⣷⣿⣿⣿⡿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣦⠀⠀⠀⠀⠀⠈
⣿⣿⣧⡀⢸⣟⠦⢀⠻⢦⡀⠈⠿⣷⣬⣭⣍⣉⣿⡇⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣶⠾⠷⠤⠤⣄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⢄⠀⠀⠀⢀
⣿⣿⣿⣿⢶⣿⡀⠀⠀⠈⠓⣒⣲⠤⠀⠈⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠉⠁⢰⣶⣶⣶⣶⣾⣭⣭⣒⡶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠃⠀⢠⣯
⣿⣿⣿⡟⠀⠭⢿⣾⣿⠿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢤⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣤⣀⣀⣀⡀⠀⠀⢀⣴⠟⠃
⠉⠻⣿⡇⠀⠀⠈⠁⠀⠤⠶⠒⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠀⢸⣿⣻⣿⣿⣍⣉⣿⡿⢿⣿⣿⣿⣿⣿⣿⣭⡉⠉⠐⠋⠁⠀⢀
⠀⠀⠈⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣧⣿⣍⣿⡀⢀⣾⣿⠛⠛⠻⢿⣿⣿⣷⣦⡤⡤⢠⡟
⠀⠀⠀⣼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠛⠻⢯⣉⣴⡾⠟⠁⠀⠀⣀⡾⠟⠋⠁⠀⠀⣴⠏⠀
⠀⠀⣠⡇⠀⠀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣀⠉⠁⣀⣠⠤⠶⡾⠋⠀⠀⠀⠀⢠⡿⠁⢀⢈
⠀⢸⣿⡷⠞⠋⠁⠀⠉⢻⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢭⡭⠿⠓⠀⠀⠀⠀⠀⠀⠀⠀⣴⠟⠀⠀⣠⣼
⣤⠟⠁⠀⢀⠀⠀⠀⠀⡸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠁⢀⣴⣾⣿⣿
⠀⠀⢰⣀⡇⠀⠀⠀⢠⣧⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⡶⠞⣻⣿⣿⣿⣿
⠀⠙⢺⡏⠀⠀⠀⣴⠋⠀⠀⠙⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠾⠛⡅⠀⣸⣿⣿⣿⣿⣯
⠀⠀⢸⡀⠀⠀⣰⢃⣠⠖⠋⠁⢹⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠁⢰⣿⣿⣿⣿⠋⣠
⠀⠀⠈⣷⠀⣰⣿⠟⠁⠀⠀⠀⠈⣏⠉⠙⠦⡄⢰⣶⣶⣶⣶⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠏⢀⣴⣿⣿⣿⣿⣿⣿⣿
⠀⠀⠀⠈⣹⠟⠁⠀⠀⠀⠀⠀⣰⠃⠀⠀⠀⣿⣿⢿⣿⣯⣭⠿⠻⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠴⢁⣴⠿⠛⠋⠁⠀⠀⠈⠙⠻
⠀⠀⣴⠟⠁⠀⠀⠀⠀⢀⣠⠴⠋⠀⠀⢀⡼⢹⣿⠶⢾⡿⠁⠀⠀⠰⠙⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⢉⡴⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢸⠃⠀⠀⢀⢀⡤⠖⠋⠀⠀⠀⠀⢠⡾⠛⠛⠛⠛⢿⣇⠀⠀⠀⢤⣰⢨⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣢⣶⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠸⡀⠀⢀⡰⠋⠀⠀⠀⠀⠀⣀⣴⢋⡴⠋⠀⠀⠀⢸⠋⠳⣦⡀⢸⡿⡜⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⠤⠶⠶⣶⣶⡿⠟⢡⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠒⠀⢳⡶⠋⠀⠀⠀⠀⣀⡴⠚⠉⢷⡞⠀⠀⠀⠀⢠⡿⣤⣤⠤⠿⡟⠻⣟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠞⠉⣀⣤⡴⠊⠉⠀⠘⢀⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢠⠏⠀⠀⠈⢸⣀⠞⠁⠀⠀⠀⢈⡇⠀⠀⠙⣶⢸⣇⠀⠀⠀⠀⠘⣆⠙⢦⠀⠀⠀⠀⠀⠀⢀⣀⣤⡞⢀⣴⣿⣿⠋⠀⠀⠀⠀⢀⣸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢸⡀⢠⠀⢀⡾⠉⠀⠀⠀⢀⣠⠞⢷⡄⠀⠀⠙⣾⡏⢳⣄⠀⠀⠀⣼⠀⢈⣧⣤⣤⣶⣶⣿⣿⣿⡟⠀⢠⡾⠋⠁⢀⣀⣤⣴⣶⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠳⣄⡴⠋⠈⠛⣲⡶⠚⠉⣽⠀⠈⠻⢦⣀⠀⠘⣇⠀⢻⡟⢻⠻⣿⣶⠋⢹⣿⣿⣿⣿⣿⣿⣿⠀⢀⣤⣴⣾⣿⣿⣿⣿⣿⣿⣽⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣀⠀⠀⡀⣀⣀⣴⢞⣥⡤⠖⠛⡟⠀⠀⠀⣰⠏⠉⠉⠁⠀⠀⠻⣾⠘⣟⠸⠟⠸⠼⠻⡍⠛⢿⣿⣿⣦⢸⣿⣿⣿⣿⣿⣿⣿⢿⣿⠟⢳⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ''',
        '''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡟⣯⡿⣝⣯⠿⣽⢯⣟⡿⣻⣟⣿⣿⣿⢿⣿⣿⣿⣿⣻⣿⣶⣾⣷⣬⡁⠈⢀⣀⣵⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡰⢌
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⢯⣽⢯⣟⢾⣵⣻⡽⣾⡽⣽⣳⢯⣟⣿⣿⣯⣿⢾⣿⣿⣟⡾⣯⢿⣿⣿⣿⣷⣤⣿⡇⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠠⠁⠊⠀⠁⠀⠀⠀⠀⠀⠂⠘⠂
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣏⣿⢯⣿⢾⣟⡾⣳⣟⣳⣟⡷⣯⣟⣾⣿⣿⣿⢾⣿⣟⡾⣿⣿⣽⣿⣿⣏⣿⣿⣿⣿⣷⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⡳⣞⣿⣿⡯⣿⢾⣽⣳⢯⡷⣯⣟⣷⣻⣽⣿⣿⣿⣿⡽⣯⣿⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⢀⣀⣄⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⢯⣗⣻⣿⣟⡾⣽⢿⣛⣾⡽⣯⢟⣷⣻⢾⣽⣿⣿⣞⣯⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⠀⠀⣀⣀⣠⣶⠿⣻⠿⠛⢹⣿⢿⠟⠛⠉⠐⣌⢻⡀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡿⣝⣾⣿⡟⣼⣻⣏⣿⣹⢺⣟⣵⣫⣶⡿⣾⣿⣿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡄⢀⣠⣴⡾⢋⣽⣿⣯⣿⠋⡔⠉⣼⣿⠇⠀⠀⠀⠣⢌⣻⠇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡿⣽⣿⣟⢾⣿⡵⣯⢾⣱⣯⣿⣷⢯⣷⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣷⣾⣿⣿⣿⣴⣿⣿⣿⣿⠃⢌⠀⢰⣿⡏⠀⠀⠀⠀⠱⢨⠼⡇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⣻⣿⣿⣯⢿⣿⣟⣯⣿⣯⣿⣿⣿⣯⣿⣟⣿⣿⣳⣿⣿⣿⣈⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢳⣿⢣⠘⣀⡞⢸⣿⠁⠀⠀⠀⠀⢀⠃⢾⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣻⣽⣿⣿⣯⢿⣿⣻⣾⢿⣿⣽⣿⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣭⣴⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⣧⣿⢋⢆⠃⣾⠀⣸⡟⠀⠀⠀⠀⠀⠀⠎⡽⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣾⡟⣽⣿⣿⣿⣯⣿⣿⣏⣿⣿⢿⣿⣧⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⡟⢯⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿⡿⢿⡿⢣⢍⣢⣭⡇⢀⣿⢃⠀⠀⠀⠀⠀⢈⢒⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣼⡟⢰⣿⢾⣿⣯⣷⣿⣿⣿⣞⣿⣿⣿⣿⣦⣛⢿⣿⣿⣿⣿⣿⣿⣽⠏⠉⠗⣚⣩⣾⠟⣭⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣗⣿⣿⣿⣿⣷⣿⡏⢠⠃⢸⡟⠰⠀⠀⠀⠀⠀⢌⣺⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢰⡿⠀⣾⡏⣿⣿⡷⣿⣿⣿⣿⣧⣧⣼⣿⣿⣿⣿⣶⡹⢿⣿⣿⣿⣿⡸⢄⠉⠉⡙⣉⠡⣚⣵⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⣿⣿⣇⡞⠀⣼⠁⠁⠀⠀⠀⠀⠈⡴⡇⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⠁⢸⡟⠀⣿⣯⣿⣿⣿⣿⣿⣿⣿⣿⣟⠻⢾⣫⣼⠗⠀⠙⢟⡻⣿⣷⡂⠀⠀⠐⠀⠂⢡⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣿⣿⣿⠃⣿⣿⠟⠀⢠⡇⠀⠀⠀⠀⠀⠀⣘⡾⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⡇⢀⣿⠁⠀⣿⣿⣳⣿⣿⣿⣿⣿⣿⣿⣬⠉⡒⠋⠁⠀⠀⠀⣤⠙⠌⠻⢆⡀⠀⠀⢀⣰⡿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢸⣿⠋⠀⠀⣸⠁⠀⠀⠀⠀⠀⠐⣼⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢸⢀⣾⠏⠀⢰⡿⣿⣳⣿⣿⣿⣿⣿⣿⣿⣿⣷⣌⢡⣁⡀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠤⠚⢱⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⣸⠇⠀⠀⢠⠇⠀⠀⠀⠀⠀⢀⣹⡏⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣾⠟⠀⢀⣾⣟⣿⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡻⢎⣀⣀⠄⠀⠀⣤⣠⣤⡀⠀⠀⠀⣠⡿⣿⣿⣿⣿⣿⡟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢟⠏⠀⠀⢠⠏⠀⠀⠀⠀⠀⠠⣜⡾⣷⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢠⣟⡞⠀⠀⣼⣿⣞⡿⣾⣿⣾⢿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣄⣀⠀⠀⠀⠀⠉⠉⠀⠀⢀⡼⢏⣵⣿⣿⣿⡟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠣⠋⠀⢀⣴⠏⠀⡄⠀⠀⠀⣀⢳⡞⠀⢿⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣴⣟⣷⣇⢀⣼⠏⢸⢾⡿⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⣿⡲⢤⣄⣀⣠⠖⣏⣱⣾⣿⣿⣿⣿⠇⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠉⠓⢶⣾⠟⠁⠀⡜⠀⠀⠀⡰⣬⠟⠀⠀⠘⣧⠀⠀⠀⠀⠀⠀
⠀⢠⣾⡳⠋⢸⢾⡾⡟⠀⣾⣿⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢷⣃⢎⠲⣁⠏⣴⣿⡿⢻⢽⣿⣿⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⢃⠈⣆⠀⠀⠀⣠⠞⠀⠀⢀⡰⣳⠋⠀⠀⠀⠀⠘⠆⠀⠀⠀⠀⠀
⣰⣻⠞⠀⢀⣼⣿⣿⠀⢰⣟⣾⣽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢋⡜⣻⣆⠣⠜⡒⢼⡿⣈⠗⣚⣏⠿⣼⣿⡿⣿⣿⣿⢿⣙⢮⡿⠃⠀⠈⠒⠶⠾⠋⠀⠀⢀⢦⡟⠁⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⠀
⡗⠁⠀⣠⡾⢃⣽⡾⣧⡾⣽⣯⣿⣿⣿⣿⣿⡿⠻⠿⠿⣿⣿⣿⣿⣿⣿⣯⣇⠎⡴⢡⢎⠳⡜⢺⣄⢛⣦⢙⡴⢪⠜⣆⣛⣷⣿⣿⣟⢣⠎⠻⠁⠀⠀⠀⠀⠀⠀⠀⠀⡄⣯⡞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣧⠀⠀⠀
⠀⢀⣾⢋⣴⠟⠁⠻⣽⡿⣿⣾⣿⣿⡟⠉⠉⢿⣄⠀⡸⠛⢉⠛⣿⣿⣿⣷⣮⣛⠍⠲⢌⠣⡜⡄⠛⡷⢏⠲⡌⣧⣻⠞⣋⢶⣿⣿⣏⠆⠁⠀⠀⠀⠀⠀⠀⠀⠀⡄⣳⣾⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡄⠀⠀
⣴⣿⣵⠟⠁⠀⢀⣼⣿⣿⢷⣿⣿⡟⠀⠀⠀⠀⠙⣏⠀⠁⢢⡀⠸⣿⣿⣿⣿⠿⣿⣷⡾⠶⢶⣌⢓⡰⢊⣕⡾⢛⠤⡙⡔⢺⣿⢿⣿⠀⠀⠀⠀⠀⠀⠀⠀⡄⣣⣼⡏⢽⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣧⠀⠀
⠟⢏⠀⠀⠀⢀⣾⣿⣟⣿⣿⣿⣿⡁⠀⠀⠀⠀⠀⠸⡄⠀⠀⠈⠂⣿⣿⣿⣿⣿⣷⣤⡙⣷⣬⡘⠳⠐⢃⠌⡰⢉⠆⡱⢈⣽⣿⡎⢿⡆⠰⣇⠀⡀⢄⠢⣍⣶⣿⣿⡅⢺⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡿⠀⠀
⠀⠀⠉⠒⢀⡾⠛⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⠀⠀⠀⢱⠀⠀⠀⢠⣿⣿⣿⣇⢻⣿⣿⢿⣾⣿⣷⠀⠁⠂⠌⢀⠁⠂⠁⢰⣿⣿⣷⡈⢻⡄⢹⡖⣈⠦⡿⣾⣿⣿⣿⣿⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣟⠀⠀
⡰⢪⡕⡴⠃⢠⣾⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠈⢿⣄⡀⣼⣿⠟⣹⠇⠀⢿⣿⠀⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠘⠆⣻⣿⣿⣦⣽⣾⣧⣝⣾⣷⢻⣿⣿⣿⣿⣷⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠇⠀⠀
⢡⣣⠞⠀⣰⣿⣿⢋⣿⣿⣿⣿⡷⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⡿⠟⠊⠁⠀⣠⣿⣏⣾⣿⣾⡿⢿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⣿⡞⣿⣿⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⣠⣾⡿⠀⠀⠀
⠚⠁⠀⢀⣿⣷⠏⣼⣿⣿⣿⣿⣟⠀⠀⠀⠀⠀⠀⢀⣠⣶⢿⡟⠀⠀⢀⠄⢊⣿⣿⣿⣿⠟⠛⠉⠁⠀⠀⠰⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⢿⣿⣿⣿⣿⢿⣿⣿⣷⡀⠀⠀⠀⠀⠒⠛⠛⠁⠀⠀⠀⠀
⠀⠀⢀⣼⣿⣟⣴⣿⣿⣿⣿⣿⡏⠀⠀⠀⣀⣤⣾⣿⠟⣉⢾⠇⠀⠐⣁⢶⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠙⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⣿⡆⠈⢻⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣠⣾⣟⣾⣿⣿⣿⣿⣿⣿⣿⠇⢀⣤⠾⠛⠋⠁⠀⠈⡔⣾⠖⢀⠜⣠⡾⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢙⢄⡀⠻⣿⠙⠳⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀
⡴⣟⡷⣯⣿⢿⣿⣿⡿⣿⣿⣿⡴⠋⠀⠀⠀⠀⠀⠀⠐⣸⡿⠀⠘⡶⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠲⢿⣷⡀⠀⠻⡷⣄⠀⠀⠀⠀⠀⠀
⡸⠋⠉⠙⢣⣿⣿⣿⣇⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⢰⡿⠁⠀⢰⣁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡝⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡖⣦⡘⣧⡀⠀⠉⢌⠳⡀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⣿⢾⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠁⠀⠀⠘⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠨⣿⠌⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠓⡛⠁⢣⠀⠀⠀⠡⡘⢆⠀⠀⠀
⣦⣀⣀⣤⢾⣿⣻⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⢸⠇⠀⠀⠀⠀⠀⠀⠀⠀⣠⢴⣲⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢽⡚⡌⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⠘⢸⠀⠀⠀⠀⠐⣌⡆⠀⠀
⢿⡟⠏⠻⢿⣷⣻⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠻⠟⠗⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢺⡝⡔⠁⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⣼⡇⠀⠀⠀⠀⢸⡷⠀⠀
⡏⠀⠀⠀⠀⠙⢿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠠⢁⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢾⡹⢬⡁⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⡇⠀⠀⠀⢀⣾⣿⠀⠀
⢇⡀⠂⠀⠀⠀⠈⠙⠿⣯⠀⠀⠀⠀⠀⠀⢀⠑⡂⣯⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⡘⣽⡝⢦⡃⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣺⣿⣿⣷⣄⠀⢀⣾⣿⡇⠀⠀
⡄⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⣄⠀⠀⠀⠀⠠⢃⡕⢺⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⡑⢼⡟⡼⣩⠿⣦⡡⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠰⣌⣷⣿⣿⣿⣿⣿⣶⣿⣿⣿⠁⠀⠀
⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⢐⡈⢳⡄⠀⢠⠡⢣⠜⣹⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢄⠣⣹⢾⡙⠶⡡⢞⡩⢷⣯⡰⠡⢄⠠⣀⠀⡄⢠⢂⡜⣬⣷⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀
⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⡘⢄⢻⡄⢣⠜⣡⢞⣿⣿⣷⡆⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠘⢤⡷⢏⢧⡙⣣⠕⡪⠜⡡⢞⡹⠿⣮⣵⣦⣹⣬⣷⣾⣾⡙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀
⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀⠐⡈⢦⡙⢦⡙⢦⣻⢡⣿⣿⣿⣦⣐⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠰⣈⣦⢽⢫⠜⡩⢆⡱⢢⠙⠄⠃⠁⠊⠔⢫⠔⢦⠣⣝⢲⣿⠿⣿⡅⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀
⣿⣿⣿⣇⢤⠀⠀⠀⠀⠀⠀⠀⢈⠒⡜⢦⣹⣳⣿⣿⣿⣿⣿⡿⢠⣷⠶⢤⣤⣀⣀⣀⣄⣠⣤⣬⠶⢓⢋⠆⢣⠊⠌⠑⡀⠂⠁⠈⠀⠀⠀⠀⠈⠐⣊⠦⡙⢦⣿⣿⣨⣿⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀
⣿⣿⣿⣿⣿⣶⢄⡀⠀⠀⠀⠀⠠⢩⢜⣣⢷⢃⣿⣿⣿⣿⣿⣇⣿⣿⣧⠀⠀⠈⠉⠉⠈⠁⠀⠀⠐⠈⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠠⢎⣹⣿⣿⢿⣿⣿⢿⣿⣿⣿⣿⣿⣿⠙⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣧⣿⣦⣿⣥⣤⣀⣀⠂⡇⣞⣼⣿⣿⣿⣿⣿⢿⣿⣿⣿⡿⠛⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⣨⡿⢻⣿⣿⠏⠀⣸⣿⣿⣿⣿⣿⡿⠀⣿⢿⣿⣿⣿⣿⣿⣿
⡇⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠙⣾⣾⣿⣯⣿⣿⣿⣏⣼⡿⠛⠙⠁⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠱⣿⣿⣿⡿⣏⠀⣰⣿⣿⣿⣿⣿⣿⡇⠀⡿⢸⣿⣿⣿⣿⣿⣟
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⢰⣿⡿⠟⠛⢫⡹⠖⠉⠁⠀⠀⠀⠀⠀⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢻⣿⡿⢻⡇⠉⣹⣿⣿⣿⡟⣿⣿⡿⢀⣼⣡⣿⣿⣿⣿⣿⣿⣯
⡿⢿⠟⣿⣿⣿⣿⣿⣿⣿⡿⠟⢋⣁⡤⠒⣠⠞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢲⣿⣿⡀⠘⢛⣿⣿⣿⣿⡟⢀⣿⣿⣅⣾⣿⣿⣿⣿⣿⣿⣿⣿⣧
⣿⣿⢰⣿⣿⣿⣿⣿⠛⢣⠐⢌⣖⠡⠔⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡰⠂⠀⠀⠀⠀⠀⠀⠀⠀⢨⡟⠙⢿⡿⠿⣻⣿⣿⣿⠟⣠⣿⡿⣻⣿⣿⢟⣋⣱⣿⣿⣿⣿⣿⣿
⣿⢿⢿⣿⣭⡿⠃⠄⠀⡠⠈⠸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠔⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠀⠀⠀⣹⣾⣿⣿⣿⣿⣾⠿⠋⠀⠹⡸⣏⡉⠉⣿⣿⣿⣿⣿⣿⠋
⡟⠁⢸⡾⠋⠀⢡⡤⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⢽⠂⢀⣼⣿⠟⠉⠉⠋⠉⠀⠀⠀⣆⣠⠇⠀⠀⣼⣿⣿⣿⣿⣿⣧⡀
⣇⠀⠋⠀⠀⠀⡺⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡃⢻⡇⢸⣿⢻⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⡿⠏⠉⠉
⣿⡀⠀⠀⠀⠠⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠌⡑⣇⠘⣿⠈⢆⡀⠀⠀⠀⣀⠀⠀⣀⠤⣊⡽⢟⠿⠛⠉⠁⠐⠠⠀⠀
        ''',
        '''
        ⠶⠶⣶⣿⣆⠀⠐⠙⠛⠛⠳⠂⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠀⠀⠈⠙⠦⢄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠉⠉⠑⠒⠲⠤⠤⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠞⠁⣠⠔⠉⠀⠀⠀⠀⠙⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠑⠒⠤⢄⡀⠀⠀⠀⠤⡀⠀⢶⡏⠀⡰⠁⠄⢀⣀⠀⣀⣀⡤⠤⠂⠀⠰⣄⠁⠀⠀⣀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠦⣠⣤⣼⣦⣀⣧⠀⡇⢀⣤⣾⣯⣽⣄⠀⢀⣀⡠⢶⡀⠈⣳⠖⠊⠁⠀⠀⠀⠀
⠓⢦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣤⣧⡀⠉⠹⠿⣿⡏⠠⣸⣿⠟⠉⠁⠀⠀⣀⡠⡿⠋⠁⠀⠀⠀⠀⠀⠀⠀
⣷⣶⣾⣿⣶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠴⠋⠀⠀⣿⣶⣟⣻⣀⠀⣀⡁⠀⠀⢠⡀⠀⣄⣀⣉⡹⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢥⣤⣤⣤⣤⣬⠹⠛⢶⣦⣤⠤⠤⠴⠖⠒⠉⠁⠀⠀⠀⢀⠟⠉⠉⠉⠙⢠⠋⣹⠆⠀⠘⠓⠾⡩⠟⠉⠀⢰⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣶⣦⣭⣽⣛⣛⣿⣿⡴⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡎⠀⠀⠀⠀⢀⡇⡴⠃⠀⠀⣀⠴⠊⠀⠀⠀⠀⠀⠙⠳⢤⣀⣀⣀⣀⣠⣤⣾
⠉⠻⣿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣧⠤⠖⠶⠟⠻⠛⠻⢶⠖⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠋⢹⣿⠟⠛⠉
⣦⣄⣈⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣎⠀⠀⠀⠀⠀⠀⣠⠖⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡿⠒⠲⠤
⣿⣿⣿⡟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡔⠋⢁⡬⠛⠉⠉⢑⠖⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⡀⠀⠀
⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡏⠀⢀⠎⠀⠀⠀⢠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣷⣄⡀
⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⣸⠀⠀⠀⢠⠏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣁
⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⢠⡏⠀⠀⣠⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠹⡿⣿
⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢧⡸⣿⣠⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠹⠌
⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠉⢻⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀
⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣷⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠀⠀⠀
⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡷⠀⠀⠀
⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠇⠀⠀⠀
⣿⣿⣿⢿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡏⠀⠀⠀⠀
⠿⠋⠁⢀⣹⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡞⠀⠀⠀⠀⠀
⢀⡤⠖⠉⠀⠀⠹⣷⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢸⣬⣿⠷⠶⠶⠤⢤⣤⣤⡤⣤⣹⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣿⣿⠟⠀⠀⠀⠀⠀⠀
⠀⠀⢀⡠⠤⠒⠋⠉⠀⠀⠀⠀⢀⡴⠞⠋⣀⡴⠞⠋⠻⢿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀
⠒⠁⠀⢀⡀⠀⠀⠀⠀⣠⡴⠞⣉⣠⠴⠚⠁⠀⠀⢀⣴⣿⣿⣿⣿⣶⣦⣤⣤⣀⣤⣤⣤⣤⣶⣿⣿⣿⣿⣿⣿⡗⠀⠀⠀⠀⠀⠀⠀⠀
        '''
    ]
    random_image = random.choice(ascii_images)
    print(random_image)

def play_sound():
    sound_file = '/home/cybersanguche/mis_tools/timerNSFW/sound.mp3'  # Ruta al archivo de sonido
    subprocess.run(['mpv', sound_file])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Temporizador desde la terminal')
    parser.add_argument('time', type=parse_time_argument, help='Tiempo en formato "Xs" (segundos), "Xm" (minutos) o "Xh" (horas)')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal.default_int_handler)  # Restaurar el manejador de señal predeterminado para Ctrl + C

    timer(args.time)

