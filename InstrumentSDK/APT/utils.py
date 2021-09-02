import os, sys, ctypes, ctypes.util

from . import _APTAPI



def list_available_devices():
    """
    Lists all devices connected to the computer.

    Returns
    -------
    out : list
        list of available devices. Each device is described by a tuple
        (hardware type, serial number)
    """
    # we have to check for all possible hardware types.
    # Unfortunately I couldn't find a list of all existing hardware types,
    # the list in the C header file is incomplete. Therefore we just check
    # the first 100 type values
    devices = []
    count = ctypes.c_long()
    for hwtype in range(100):
        if (_lib.GetNumHWUnitsEx(hwtype, ctypes.byref(count)) == 0):
            # found an existing hardware type
            if (count.value > 0):
                # devices are available!!
                # get their serial number
                serial_number = ctypes.c_long()
                for ii in range(count.value):
                    if (_lib.GetHWSerialNumEx(hwtype, ii,
                        ctypes.byref(serial_number)) == 0):
                        devices.append((hwtype, serial_number.value))
    return devices


def GetHardwareInfo(serial_number):
    """
    Retrieves hardware information about the devices identified by its
    serial number.

    Parameters
    ----------
    serial_number : int
        Serial number identifying the device

    Returns
    -------
    out : tuple
        hardware information: (model, software version, hardware notes)
    """
    model = ctypes.c_buffer(255)
    swver = ctypes.c_buffer(255)
    hwnotes = ctypes.c_buffer(255)
    err_code = _lib.GetHWInfo(serial_number, model, len(model),
        swver, len(swver), hwnotes, len(hwnotes))
    if (err_code != 0):
        raise Exception("Getting hardware info failed: %s" %
                _get_error_text(err_code))
    return (model.value, swver.value, hwnotes.value)



def _load_library():
    """
    Loads the APT.dll shared library. Calls APTInit.
    """
    # load library
    if (os.name != 'nt'):
        raise Exception("Your operating system is not supported. " \
                "Thorlabs' APT API only works on Windows.")
    lib = None
    filename = ctypes.util.find_library("APT")
    if (filename is not None):
        lib = ctypes.windll.LoadLibrary(filename)
    else:
        filename = "%s/APT.dll" % os.path.dirname(__file__)
        lib = ctypes.windll.LoadLibrary(filename)
        if (lib is None):
            filename = "%s/APT.dll" % os.path.dirname(sys.argv[0])
            lib = ctypes.windll.LoadLibrary(lib)
            if (lib is None):
                raise Exception("Could not find shared library APT.dll.")
    _APTAPI.set_ctypes_argtypes(lib)
    err_code = lib.APTInit()
    if (err_code != 0):
        raise Exception("Thorlabs APT Initialization failed: " \
                        "%s" % _get_error_text(err_code))
    if (lib.EnableEventDlg(False) != 0):
        raise Exception("Couldn't disable event dialog.")
    return lib


_lib = None
_lib = _load_library()
