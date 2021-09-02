#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import pandas as pd

# https://thorlabs-apt-device.readthedocs.io/en/latest/
# Module multi plate-forme
import thorlabs_apt_device as apt


class Goniomètre:

    def __init__(self, id: int):
        self. id = id
        self.motor = None # Obtenier la classe appropriée d'apt

    def angle(self, a=None):
        if a is None:
            return self.motor.position #  TODO: changer pour le bon attribut
        else:
            self.motor.go(a) # TODO: utiliser la bonne méthode
