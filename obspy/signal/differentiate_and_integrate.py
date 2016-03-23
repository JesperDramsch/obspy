#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integration and differentiation routines.

:copyright:
    The ObsPy Development Team (devs@obspy.org)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from future.builtins import *  # NOQA

import numpy as np
import scipy.integrate
import scipy.interpolate


def integrate_cumtrapz(data, dx, **kwargs):
    """
    Performs first order integration of data using the trapezoidal rule.

    :param data: Data array to integrate.
    :param dx: Sample spacing usually in seconds.
    """
    # Integrate. Set first value to zero to avoid changing the total
    # length of the array.
    # (manually adding the zero and not using `cumtrapz(..., initial=0)` is a
    # backwards compatibility fix for scipy versions < 0.11.
    ret = scipy.integrate.cumtrapz(data, dx=dx)
    return np.concatenate([np.array([0], dtype=ret.dtype), ret])


def integrate_spline(data, dx, k=3, **kwargs):
    """
    Integrate by generating an interpolating spline and integrating that.

    :param data: The data to integrate.
    :param dx: Sample spacing usually in seconds.
    :param k: Spline order. 1 is linear, 2 quadratic, 3 cubic, Must be
        between 1 and 5.
    """
    time_array = np.linspace(0, (len(data) - 1) * dx, len(data))
    spline = scipy.interpolate.InterpolatedUnivariateSpline(time_array, data,
                                                            k=k)

    # Backport of the antiderivative() method to old scipy versions.
    if not hasattr(spline, "antiderivative"):
        from scipy.interpolate import fitpack  # NOQA
        tck = fitpack.splantider(spline._eval_args, 1)

        tmp = scipy.interpolate.InterpolatedUnivariateSpline.__new__(
            scipy.interpolate.InterpolatedUnivariateSpline)
        t, c, k = tck
        tmp._eval_args = tck
        tmp._data = (None, None, None, None, None, k, None, len(t), t, c,
                     None, None, None, None)
        tmp.ext = 0
        return tmp(time_array)

    return spline.antiderivative(n=1)(time_array)
