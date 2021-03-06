"""

=====================
`match_wrapper.match`
=====================

Wrappers for MATCH utilities.

Refer to the MATCH 2.5 README and the utility help strings (printed to the
terminal when a utility is executed without any arguments) for full
documentation on each utility. The wrapper functions are designed according
to the MATCH documentation (in terms of the command syntax and the options
avaiable), and a utility's help string is given precendence over the README
when there is confliciting information. Like their command line
counterparts, the functions in this module read and write data in files,
rather than being interactive tools that process data in memory.


Classes
-------

=============== ========================================================
`FlagFormatter` Formatter to assist in writing flags to command strings.
=============== ========================================================


Functions
---------

========== ===================
`calcsfh`  calcsfh wrapper.
`hybridMC` hybridMC wrapper.
`zcmerge`  zcmerge wrapper.
`zcombine` zcombine wrapper.
========== ===================


Notes
-----
The following MATCH utilities are not currently supported:

- asciibin2mod
- calcbinmod
- fake
- foreground
- getxform
- sspcombine
- combine1
- noisyCMD
- procMC
- sspcombine
- stats
- makefake

"""
import subprocess


class FlagFormatter(object):

    """Formatter to assist in writing flags to command strings.

    Each MATCH utility wrapper formats a flag for the command string using
    a formatter function that takes a key and value and returns a string.
    `FlagFormatter` has a call method that looks up a format string based
    on the key, and uses it to format the value. Each key corresponds to an
    argument in a wrapper function. The format strings may be adjusted from
    their default values, shown in the Parameters section below.

    A key can be assigned a list or tuple of format strings to specify
    individual formats for each value in a multivalued flag (e.g.,
    `diskAv`); otherwise the same format is used for all values.

    Parameters
    ----------
    dAv : '{:.2f}', optional
    diskAv : '{:.2f}', optional
    dAvy : '{:.2f}', optional
    zerobin : '{:s}', optional
    incmult : '{:.2f}', optional
    incmultsig : '{:.2f}', optional
    errmult : '{:.2f}', optional
    errmultsig : '{:.2f}', optional
    logterr : '{:.2f}', optional
    logterrsig : '{:.2f}', optional
    mbolerr : '{:.2f}', optional
    mbolerrsig : '{:.2f}', optional
    alpha : '{:.2f}', optional
    dt : '{:.2f}', optional
    nburn : '{:d}', optional
    nmc : '{:d}', optional
    nt : '{:d}', optional
    nsfr : '{:d}', optional
    pscape : '{:.2f}', optional
    tint : '{:.2f}', optional

    Attributes
    ----------
    fmt_dict : dict
        Dictionary of format strings for flags used by MATCH utilities.

    Methods
    -------
    __call__

    """

    def __init__(self, **kwargs):
        self.fmt_dict = {
            # calcsfh
            'dAv': '{:.2f}',
            'diskAv': '{:.2f}',
            'dAvy': '{:.2f}',
            'zerobin': '{:d}',
            'incmult': '{:.2f}',
            'incmultsig': '{:.2f}',
            'errmult': '{:.2f}',
            'errmultsig': '{:.2f}',
            'logterr': '{:.2f}',
            'logterrsig': '{:.2f}',
            'mbolerr': '{:.2f}',
            'mbolerrsig': '{:.2f}',
            'mcseed': '{:.2f}',
            'alpha': '{:.2f}',

            # hybridMC
            'dt': '{:.2f}',
            'nburn': '{:d}',
            'nmc': '{:d}',
            'nt': '{:d}',
            'nsfr': '{:d}',
            'pscape': '{:.2f}',
            'tint': '{:.2f}',
            }
        for key, val in kwargs.items():
            if key in self.fmt_dict:
                self.fmt_dict[key] = val

    def __call__(self, key, val, delim=','):
        """Return a string for the given key and value.

        Parameters
        ----------
        key : str
            The name of the value, and also the key corresponding to a
            format string in `fmt_dict`.
        val :
            The value to be formatted. No formatting is actually applied if
            `val` is True, False, None, or an empty sequence.
        delim : str, optional
            Delimiter for multivalued flags. Default is ','.

        Returns
        -------
        str or None
            None is returned if `val` is False, None, or an empty sequence.
            If `val` is True, then it is ignored and the returned string is
            of the form '-key'. Otherwise, `val` is formatted based on
            `key` and the returned string is of the form '-key=val'. If
            `val` is multivalued, the subvalues are separatd by `delim`.

        """
        if val is True:  # True is a special case
            result = '-{:s}'.format(key)
        elif val or val is 0:  # 0 is meaningful
            fmt = self.fmt_dict[key]
            if isinstance(val, basestring):
                # val is a string; catch here so it's not mistaken for a
                # list or tuple of values
                valstr_list = [fmt.format(val)]
            else:  # val is not a string
                try:  # val and fmt are sequences
                    valstr_list = [f.format(v) for v, f in zip(val, fmt)]
                except (TypeError, ValueError):  # val or fmt is not a sequence
                    try:  # val is a sequence, fmt is a string
                        valstr_list = [fmt.format(v) for v in val]
                    except TypeError:  # val is a single value, fmt is a string
                        valstr_list = [fmt.format(val)]
            valstr = delim.join(valstr_list)
            result = '-{0:s}={1:s}'.format(key, valstr)
        else:  # val is None, False, or an empty sequence (but not 0)
            result = None

        return result


def calcsfh(paramfile, photfile, fakefile, sfhfile, **kwargs):
    """calcsfh wrapper.

    Most command line flags have a corresponding keyword argument in the
    call signature. Mutually exclusive options, such as certain mode flags
    and flags for model and transformation selections, are instead
    available as values for the `mode`, `model`, and `transformation`
    keywords.

    All keyword arguments are None by default unless stated otherwise.
    Flag-related arguments set to None are not included in the command
    string.

    Parameters
    ----------
    paramfile : str
        Path to the calcsfh parameter file.
    photfile : str
        Path to the photometry file.
    fakefile : str
        Path to the fake photometry file.
    sfhfile : str
        Path to the SFH output file. The best-fit model CMD data is
        automatically written to the same path with a ".cmd" suffix.
    outfile : str, optional
        Path to a file to capture stdout.
    mode : {None, 'setz', 'ssp', 'zinc'}, optional
        Set the mode in which calcsfh is run (there are other modes that
        can also be specified, but only one of this particular set can be
        used at a time).
    ddist : bool, optional
    full : bool, optional
    verb : bool, optional
    allstars : bool, optional
    mcdata : bool, optional
    allmcdata : bool, optional
    dAv : float, 3-tuple, optional
    diskAv : 4-tuple, 7-tuple, optional
    dAvy : float, optional
    appDmod : str, optional
    zerobin : int, optional
    incmult : float, optional
    incmultsig : float, optional
    errmult : float, optional
    errmultsig : float, optional
    logterr : float, optional
    logterrsig : float, optional
    mbolerr : float, optional
    mbolerrsig : float, optional
    mcseed : float, optional
    model : str, optional
        Override the default stellar evolution models with one of
        'BASTInov', 'BASTI', 'BASTI02nov', 'BASTI02', 'DART', 'PADUA00',
        'PADUA06', 'VICTORIA', 'VICTORIASS'.
    alpha : {-0.2, 0, 0.2, 0.2}, optional
    transformation : str, optional
        Override the default transformation for the selected model with one
        of 'BASTInov', 'BASTI', 'BASTI02nov', 'BASTI02', 'DART', 'PADUA00',
        'PADUA06', 'VICTORIA', 'VICTORIASS'.
    formatter : FlagFormatter or function, optional
        Any function that takes a flag name (`key`) and a value (`val`) as
        the first and second arguments, and returns a string representation
        of the value. Formatting for multivalued flags (e.g., `diskAv`)
        need to be handled as well. `FlagFormatter` is used by default.
    norun : bool, optional
        If True, calcsfh is not actually run and the command string is
        returned instead. This is useful for checking the command before
        running it.

    Returns
    -------
    str or None
        The calcsh command string is returned if `norun` is True, otherwise
        the return value is None.

    """
    cmd = ('calcsfh {0:s} {1:s} {2:s} {3:s}'
           .format(paramfile, photfile, fakefile, sfhfile))

    flag_list = []

    # Mode flag
    modeflag = kwargs.get('mode')
    if modeflag:
        kwargs[modeflag] = True
        flag_list.append(modeflag)

    # Other mode flags
    flag_list += ['ddist', 'full', 'verb', 'allstars', 'mcdata', 'allmcdata']

    # Model generation flags
    flag_list += ['dAv', 'diskAv', 'dAvy', 'appDmod', 'zerobin', 'incmult',
                  'incmultsig', 'errmult', 'errmultsig', 'logterr',
                  'logterrsig', 'mbolerr', 'mbolerrsig', 'mcseed']

    # Model selection
    modelflag = kwargs.get('model')
    if modelflag:
        kwargs[modelflag] = True
        flag_list.append(modelflag)
        if modelflag in ['DART']:  # `alpha` for Dartmouth models only
            flag_list.append('alpha')

    # Transformation selection
    transflag = kwargs.get('transformation')
    if transflag:
        kwargs[transflag] = True
        flag_list.append(transflag)

    # Flag strings
    formatter = kwargs.get('formatter', FlagFormatter())
    flagstr_gen = (formatter(flag, kwargs.get(flag)) for flag in flag_list)
    flagstr_list = [flagstr for flagstr in flagstr_gen if flagstr]  # filter out None
    if flagstr_list:
        cmd = '{0:s} {1:s}'.format(cmd, ' '.join(flagstr_list))

    # stdout file
    outfile = kwargs.get('outfile')
    if outfile:
        cmd = '{0:s} > {1:s}'.format(cmd, outfile)

    norun = kwargs.get('norun')
    if norun:
        result = cmd
    else:
        # Run calcsfh
        subprocess.call(cmd, shell=True)
        result = None
    return result


def hybridMC(hmcdatfile, hmcsfhfile, **kwargs):
    """hybridMC wrapper.

    All command line flags have a corresponding keyword argument in the
    call signature.

    All keyword arguments are None by default unless stated otherwise.
    Flag-related arguments set to None are not included in the command
    string.

    Parameters
    ----------
    hmcdatfile : str
        Path to the binary ".dat" file output by calcsfh in 'mcdata' mode.
    hmcsfhfile : str
        Path to the SFH output file.
    outfile : str, optional
        Path to a file to capture stdout.
    countall : bool, optional
    dt : float, optional
    keepall : bool, optional
    nburn : int, optional
    nmc : int, optional
    nt : int, optional
    nsfr : int, optional
    pscape : float, optional
    tint : float, optional
    formatter : FlagFormatter or function, optional
        Any function that takes a flag name (`key`) and a value (`val`) as
        the first and second arguments, and returns a string representation
        of the value. `FlagFormatter` is used by default.
    norun : bool, optional
        If True, hybridMC is not actually run and the command string is
        returned instead. This is useful for checking the command before
        running it.

    Returns
    -------
    str or None
        The hybridMC command string is returned if `norun` is True,
        otherwise the return value is None.

    """
    cmd = 'hybridMC {0:s} {1:s}'.format(hmcsfhfile, hmcdatfile)

    flag_list = ['countall', 'dt', 'keepall', 'nburn', 'nmc', 'nt', 'nsfr',
                 'pscape', 'tint']

    # Flag strings
    formatter = kwargs.get('formatter', FlagFormatter())
    flagstr_gen = (formatter(flag, kwargs.get(flag)) for flag in flag_list)
    flagstr_list = [flagstr for flagstr in flagstr_gen if flagstr]  # filter out None
    if flagstr_list:
        cmd = '{0:s} {1:s}'.format(cmd, ' '.join(flagstr_list))

    # stdout file
    outfile = kwargs.get('outfile')
    if outfile:
        cmd = '{0:s} > {1:s}'.format(cmd, outfile)

    norun = kwargs.get('norun')
    if norun:
        result = cmd
    else:
        # Run hybridMC
        subprocess.call(cmd, shell=True)
        result = None
    return result


def zcmerge(zcbfile_list, merged_zcbfile, **kwargs):
    """zcmerge wrapper.

    Parameters
    ----------
    zcbfile_list : list
        List of paths to zcombine output files. Note that the zcombine file
        for the real data should be listed first.
    merged_zcbfile : str
        Path to the zcmerge output file (captured stdout).
    absolute : bool, optional
        Corresponds to the 'absolute' command line flag. Default is None,
        in which case it is not included in the command string.
    norun : bool, optional
        If True, zcmerge is not actually run and the command string is
        returned instead. This is useful for checking the command before
        running it. Default is False.

    Returns
    -------
    str or None
        The zcmerge command string is returned if `norun` is True,
        otherwise the return value is None.

    """
    cmd = 'zcmerge'

    # Flag string
    formatter = FlagFormatter()
    flagstr = formatter('absolute', kwargs.get('absolute'))
    if flagstr:
        cmd = '{0:s} {1:s}'.format(cmd, flagstr)

    # Files
    if not isinstance(zcbfile_list, basestring):
        zcbfile_list = ' '.join(zcbfile_list)
    cmd = '{0:s} {1:s} > {2:s}'.format(cmd, zcbfile_list, merged_zcbfile)

    norun = kwargs.get('norun')
    if norun:
        result = cmd
    else:
        # Run zcmerge
        subprocess.call(cmd, shell=True)
        result = None
    return result


def zcombine(sfhfile, zcbfile, **kwargs):
    """zcombine wrapper.

    All command line flags have a corresponding keyword argument in the
    call signature.

    All keyword arguments are None by default unless stated otherwise.
    Flag-related arguments set to None are not included in the command
    string.

    Parameters
    ----------
    sfhfile : str or list
        Path to the input SFH file, or a list of paths for multiple input
        files.
    zcbfile : str
        Path to the zcombine output file (captured stdout).
    param : str, optional
    out : str, optional
    bestonly : bool, optional
    unweighted : bool, optional
    jeffreys : bool, optional
    best : str, optional
    sigma : bool, optional
    pct16_84 : bool, optional
    fullwidth : bool, optional
    meanbest : bool, optional
    medbest : bool, optional
    norun : bool, optional
        If True, zcombine is not actually run and the command string is
        returned instead. This is useful for checking the command before
        running it.

    Returns
    -------
    str or None
        The zcombine command string is returned if `norun` is True,
        otherwise the return value is None.

    """
    cmd = 'zcombine'

    flag_list = ['param', 'out', 'bestonly', 'unweighted', 'jeffreys',
                 'best', 'sigma', 'pct16_84', 'fullwidth', 'meanbest',
                 'medbest']

    # Flag strings
    formatter = FlagFormatter()
    flagstr_gen = (formatter(flag, kwargs.get(flag)) for flag in flag_list)
    flagstr_list = [flagstr for flagstr in flagstr_gen if flagstr]  # filter out None
    if flagstr_list:
        cmd = '{0:s} {1:s}'.format(cmd, ' '.join(flagstr_list))

    # Files
    if not isinstance(sfhfile, basestring):
        sfhfile = ' '.join(sfhfile)
    cmd = '{0:s} {1:s} > {2:s}'.format(cmd, sfhfile, zcbfile)

    norun = kwargs.get('norun')
    if norun:
        result = cmd
    else:
        # Run zcombine
        subprocess.call(cmd, shell=True)
        result = None
    return result
