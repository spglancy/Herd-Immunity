#!/usr/bin/env python
import pytest

class Virus(object):
    '''Properties and attributes of the virus used in Simulation.'''

    def __init__(self, name, repro_rate, mortality_rate):
        self.name = name
        self.repro_rate = repro_rate
        self.mortality_rate = mortality_rate


def test_virus_instantiation():
    #TODO: Create your own test that models the virus you are working with
    '''Check to make sure that the virus instantiator is working.'''
    virus = Virus("Cholera", .0213, 0.163)
    assert virus.name == "Cholera"
    assert virus.repro_rate == 2.13
    assert virus.mortality_rate == 0.163
