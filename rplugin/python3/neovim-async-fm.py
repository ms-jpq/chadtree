from pynvim import function


@function("TestFunction", sync=True)
def testfunction(self, args):
    return 3
