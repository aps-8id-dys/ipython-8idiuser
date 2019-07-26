logger.info(__file__)

"""overrides of code from imports"""

try:
    assert APS_utils.show_ophyd_symbols is not None

    def show_ophyd_symbols(
        show_pv=True, printing=True, verbose=False, symbols=None
      ):
        symbols = symbols or globals()
        return APS_utils.show_ophyd_symbols(
          show_pv=show_pv, printing=printing, verbose=verbose, symbols=symbols
        )

    logger.warning("in 09-overrides.py")
    logger.warning("APS_utils.show_ophyd_symbols() is available")
    logger.warning("Can remove local definition show_ophyd_symbols()")
except AssertionError:
    # could not find, must define it here
    logger.warning("in 09-overrides.py")
    logger.warning("APS_utils.show_ophyd_symbols() not available")
    logger.warning("Defining show_ophyd_symbols()")
    
    def show_ophyd_symbols(show_pv=True, printing=True, verbose=False, symbols=None):
        """
        copy of APS_utils.show_ophyd_symbols
        """
        table = pyRestTable.Table()
        table.labels = ["name", "ophyd structure"]
        if show_pv:
            table.addLabel("EPICS PV")
        if verbose:
            table.addLabel("object representation")
        g = symbols or globals()
        for k, v in sorted(g.items()):
            if isinstance(v, (ophyd.Signal, ophyd.Device)):
                row = [k, v.__class__.__name__]
                if show_pv:
                    if hasattr(v, "pvname"):
                        row.append(v.pvname)
                    elif hasattr(v, "prefix"):
                        row.append(v.prefix)
                    else:
                        row.append("")
                if verbose:
                    row.append(str(v))
                table.addRow(row)
        if printing:
            print(table)
        return table
