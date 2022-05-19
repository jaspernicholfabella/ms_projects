''' Test Ccass fetch robot'''
from projects.hk_ccass import ccass

def test_ccass():
    '''Test object initial'''
    argv = "ccass.py -o ../out/".split()
    web = ccass.Ccass(argv)
    assert web
