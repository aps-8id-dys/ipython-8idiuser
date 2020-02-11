
"""
diagnostic functions
"""


__all__ = [
    'full_dotted_name',
    'object_explorer',
]


from ..session_logs import logger
logger.info(__file__)

from ophyd import Device
from ophyd.signal import EpicsSignalBase
import pyRestTable


def full_dotted_name(obj):
    """
    Return the full dotted name

    The ``.dotted_name`` property does not include the 
    name of the root object.  This routine adds that.

    see: https://github.com/bluesky/ophyd/pull/797
    """
    names = []
    while obj.parent is not None:
        names.append(obj.attr_name)
        obj = obj.parent
    names.append(obj.name)
    return '.'.join(names[::-1])


def get_child(obj, nm):
    try:
        child = getattr(obj, nm)
        return child
    except TimeoutError:
        print(f"timeout: {obj.name}_{nm}")
        return "TIMEOUT"
    print(f"None: {obj.name}_{nm}")


def miner(obj):
    # import pdb; pdb.set_trace()
    if isinstance(obj, EpicsSignalBase):
        return [obj]
    elif isinstance(obj, Device):
        items = []
        for nm in obj.component_names:
            child = get_child(obj, nm)
            if child in (None, "TIMEOUT"):
                continue
            result = miner(child)
            if result is not None:
                items.extend(result)
        return items


def object_explorer(obj):
    """
    print the contents of obj
    """
    t = pyRestTable.Table()
    t.addLabel("name")
    t.addLabel("PV reference")
    t.addLabel("value")
    items = miner(obj)
    # print(len(items))

    def sorter(obj):
        return obj.dotted_name

    for item in sorted(items, key=sorter):
        # t.addRow((full_dotted_name(item), pv_ref(item), item.get()))
        t.addRow((item.dotted_name, pv_ref(item), item.get()))
    print(t)
    return t


def pv_ref(obj):
    if isinstance(obj, EpicsSignalBase):
        return obj.pvname
    elif isinstance(obj, Device):
        return obj.prefix
