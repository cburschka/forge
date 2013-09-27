import os, sys

def try_import(module, msg):
    try:
        __import__(module)
    except ImportError:
        print(msg)
        sys.exit(1)

def setup():
    cnfpath = os.environ['HOME'] + '/.forge'
    if sys.version_info[0] != 3:
        print("Python 3 is required to run this program.")
    try_import('pygame', 'This software requires the pygame library to be installed.')
    sys.stdout.write("This installer will create and write into {0}/. Okay? [yn] ".format(cnfpath))
    if input() in ('Y', 'y'):
        if os.path.isdir(cnfpath):
            sys.stdout.write("Directory {0}/ already exists. Still write in there? [yn] ".format(cnfpath))
            if input() not in ('Y', 'y'):
                print("Cancelled")
                sys.exit(1)
        else:
            try:
                os.mkdir(cnfpath)
            except OSError:
                print("Could not create directory {0}/.".format(cnfpath))
                sys.exit(1)
        try:
            cnffile = open(cnfpath + '/forge.ini', 'w')
            print("Please enter the absolute path to your Blades of Avernum installation:")
            sys.stdout.write("> ")
            path = input()
            if os.path.exists(path + '/Blades of Avernum.exe'):
                cnffile.write('boa = {0}'.format(path))
            else:
                print("Path {0} not valid, does not contain 'Blades of Avernum.exe'".format(path))
                sys.exit(1)
        except OSError:
            print("Error while writing conf file.")
            sys.exit(1)
    else:
        print("Cancelled.")
        sys.exit(1)
    
setup()
