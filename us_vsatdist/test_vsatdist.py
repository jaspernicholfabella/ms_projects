''' Test Vsatdist fetch robot'''
from projects.us_vsatdist import vsatdist

def test_vsatdist():
    '''Test object initial'''
    argv = "vsatdist.py -o ../out/".split()
    web = vsatdist.Vsatdist(argv)
    assert web