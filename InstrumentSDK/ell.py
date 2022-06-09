# -*- coding: utf-8 -*-

# Bibliothèques publiques
import serial

from serial.tools.list_ports import comports
from elliptecstage.elliptecstage import ElloStage, ElloException


# Trouver un port série connecté à un dispositif Elliptec
def port_elliptec():
    motif_elliptec = 'FT230X Basic UART'
    return next(filter(lambda x: motif_elliptec in str(x), comports()))

# Tests de la présence de différents moteurs ELL0 sur un port série
def tester_appareil(com, n: int = 0) -> bool:
    cmd = f'{format(n, "01x")}in\n'
    com.write(bytes(cmd, encoding='utf-8'))
    res = str(com.readline(), encoding='utf-8').strip()
    return bool(res)

def lister_appareils(com, début: int = 0, fin: int = 15) -> list:
    return [n for n in range(début, fin+1) if tester_appareil(com, n)]


if __name__ == '__main__':
    with serial.Serial(port_elliptec().device, timeout=5) as com:
        for i in lister_appareils(com, 1, 3):
            # Exemple tiré de https://github.com/augvislab/elliptecstage
            print(f'# Étage {i}')

            try:
                stage = ElloStage(com, i)
                
                print('1. Positionnement: ', end='')
                stage.move_home()
                cmd, dat, add = stage.read_message_blocking_position_response()
                print(f'{cmd=!r}, {dat=!r}, {add=!r}')

                print('2. Déplacement: ', end='')
                stage.move_absolute(2.0)
                cmd, z, add = stage.read_message_blocking_position_response()
                print(f'{z=!r}')
            except ElloException as e:
                print()
                print('**', e, '**')
                print()
