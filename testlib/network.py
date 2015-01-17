import subprocess


def isolate(*names):
    subprocess.check_call(
        ('vagga_network', 'isolate') + names)


def restore():
    subprocess.check_call(('vagga_network', 'fullmesh'))
