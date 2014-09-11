import os

class UObj(object):

    _serial_fmt = '#sim_{utype}_{num}'

    def _create_serial(self):
        self.serial = self._serial_fmt.format(utype = self.utype,
                                              num   = os.getpid())

    def __init__(self, utype, serial = None, id = None):
        self.utype = utype
        if serial is None:
            self.serial = serial
        else:
            self._create_serial()
        self.name = self.serial
        self.id = id

    def __str__(self):
        return 'utype: {utype}\nname: {name}\nserial: {serial}'.format(
            utype  = self.utype,
            name   = self.name,
            serial = self.serial
        )
