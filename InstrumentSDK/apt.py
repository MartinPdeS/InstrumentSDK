# -*- coding: utf-8 -*-

# Bibliothèques standards
import time

# bibliothèques publiques
import serial

from serial.tools.list_ports import comports
from thorlabs_apt_device.devices.bsc import BSC, BSC201 # https://thorlabs-apt-device.readthedocs.io/en/latest/

# Trouver un port série connecté à un dispositif APT
def port_apt():
    motif_apt = 'APT Stepper Motor Controller'
    return next(filter(lambda x: motif_apt in str(x), comports()))

# Basé sur https://thorlabs-apt-device.readthedocs.io/en/latest/api/thorlabs_apt_device.devices.bsc.html#thorlabs_apt_device.devices.bsc.BSC201
class BSC201_HDR50(BSC201):
    # Données tirées de Kinesis
    kinesis = {'travel [pas]': 27_033_577,
               'vel [pas/s]': 201_576_964,
               'acc [pas/s²]': 20_653,
               'jog_step [pas]': 37_547,
               'jog_vel [pas/s]': 40_315_393,
               'jog_acc [pas/s²]': 4_131,
               'travel [°]': 360,
               'vel [°/s]': 50,
               'acc [°/s²]': 25,
               'jog_step [°]': 0.5,
               'jog_vel [°/s]': 10,
               'jog_acc [°/s²]': 5}
    
    # Données tirées de https://www.thorlabs.com/drawings/8d6029bfe62e7acd-DF270E33-CE4C-A18B-8D52A70104946BCD/HDR50-Manual.pdf
    manuel = {'travel [°]': 360,
              'vel [°/s]': 50,
              'acc [°/s²]': 80,
              'macropas [°]': 1.8,
              'micropas [1/macropas]': 2048,
              'jog_step [pas]': kinesis['jog_step [pas]']}
    manuel['micropas [°]'] = manuel['macropas [°]'] / manuel['micropas [1/macropas]']
    manuel['travel [pas]'] = int( manuel['travel [°]'] / manuel['micropas [°]'] )
    manuel['vel [pas/s]'] = int( manuel['vel [°/s]'] / manuel['micropas [°]'] )
    manuel['acc [pas/s²]'] = int( manuel['acc [°/s²]'] / manuel['micropas [°]'] )
    
    def __init__(self,
                 serial_port=None,
                 vid=None,
                 pid=None,
                 manufacturer=None,
                 product=None,
                 serial_number='40',
                 location=None,
                 home=True,
                 invert_direction_logic=False,
                 swap_limit_switches=True,
                 réglages=kinesis):
        début = time.time()
        super().__init__(serial_port=serial_port,
                         vid=vid, pid=pid,
                         manufacturer=manufacturer,
                         product=product,
                         serial_number=serial_number,
                         location=location,
                         home=home,
                         invert_direction_logic=invert_direction_logic,
                         swap_limit_switches=swap_limit_switches)
    
        # Initial velocity parameters are effectively zero on startup, set something more sensible
        # Homing is initiated 1.0s after init, so hopefully these will take effect before then...
        # Tiré de la source pour BSC201_DRV250
        for bay_i, _ in enumerate(self.bays):
            for channel_i, _ in enumerate(self.channels):
                self.set_home_params(velocity=réglages['vel [pas/s]'],
                                     offset_distance=0,
                                     bay=bay_i,
                                     channel=channel_i)
                self.set_velocity_params(acceleration=réglages['acc [pas/s²]'],
                                         max_velocity=réglages['vel [pas/s]'],
                                         bay=bay_i,
                                         channel=channel_i)
                self.set_jog_params(size=réglages['jog_step [pas]'],
                                    acceleration=réglages['jog_acc [pas/s²]'],
                                    max_velocity=réglages['jog_vel [pas/s]'],
                                    bay=bay_i,
                                    channel=channel_i)
                # Use open-loop positioning (only using stepper counts)
                #self.set_loop_params(loop_mode=2, prop=50000, integral=5000, diff=100, pid_clip=16000000, pid_tol=80, encoder_const=4292282941, bay=bay_i, channel=channel_i)
                self.set_loop_params(loop_mode=1, prop=0, integral=0, diff=0, pid_clip=0, pid_tol=0, encoder_const=0, bay=bay_i, channel=channel_i)
        
        délai = time.time() - début
        if délai > 1:
            print(f"L'initialisation s'est faite trop lentement ({délai=}s).")

            
if __name__ == '__main__':
    print('Initialisation...', end='\r')
    stage = BSC201_HDR50()
    time.sleep(10)
    print('Initialisation.  ')
    
    try:
        print('Identification...', end='\r')
        stage.identify() # La lumière sur le contrôleur externe devrait clignoter.
        print('Identifié.       ')
    
        print('Déactivation...', end='\r')
        stage.set_enabled(False)
        time.sleep(10)
        print('Déactivé.      ', end='\r')
        print('Réactivation...', end='\r')
        stage.set_enabled(True)
        print('Réactivé.      ')
        
        print('Déplacement rapide...', end='\r')
        stage.move_velocity(direction='forward')
        time.sleep(10)
        stage.stop()
        print('Déplacement rapide.  ')
        
        print('Dans l\'autre sens...', end='\r')
        stage.move_velocity(direction='reverse')
        time.sleep(5)
        stage.stop()
        print('Dans l\'autre sens.  ')
        
        print('Retour...', end='\r')
        stage.home()
        time.sleep(10)
        print('Retour.  ')
    finally:   
        stage.close()
    
    print('Fin.')