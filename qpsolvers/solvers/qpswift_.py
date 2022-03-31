#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2022 Stéphane Caron and the qpsolvers contributors.
#
# This file is part of qpsolvers.
#
# qpsolvers is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# qpsolvers is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with qpsolvers. If not, see <http://www.gnu.org/licenses/>.

"""
Solver interface for `qpSWIFT <https://github.com/qpSWIFT/qpSWIFT>`__.

qpSWIFT is a light-weight sparse Quadratic Programming solver targeted for
embedded and robotic applications. It employs Primal-Dual Interior Point method
with Mehrotra Predictor corrector step and Nesterov Todd scaling. For solving
the linear system of equations, sparse LDL' factorization is used along with
approximate minimum degree heuristic to minimize fill-in of the factorizations.

If you use qpSWIFT in your research, consider citing the corresponding paper:
`qpSWIFT: A Real-Time Sparse Quadratic Program Solver for Robotic Applications
<https://doi.org/10.1109/LRA.2019.2926664>`_.
"""

from typing import Optional

import numpy as np
import qpSWIFT


def qpswift_solve_qp(
    P: np.ndarray,
    q: np.ndarray,
    G: Optional[np.ndarray] = None,
    h: Optional[np.ndarray] = None,
    A: Optional[np.ndarray] = None,
    b: Optional[np.ndarray] = None,
    initvals: Optional[np.ndarray] = None,
    verbose: bool = False,
    opts: Optional[dict] = None,
) -> Optional[np.ndarray]:
    """
    Solve a Quadratic Program defined as:

    .. math::

        \\begin{split}\\begin{array}{ll}
        \\mbox{minimize} &
            \\frac{1}{2} x^T P x + q^T x \\\\
        \\mbox{subject to}
            & G x \\leq h                \\\\
            & A x = b
        \\end{array}\\end{split}

    using `qpSWIFT <https://github.com/qpSWIFT/qpSWIFT>`__.

    Note
    ----
    This solver does not handle problems without inequality constraints yet.

    Note
    ----
    qpSWIFT requires the equality constraint matrix to be full row rank. For
    performance reasons it will not perform a rank check on this matrix.

    Parameters
    ----------
    P :
        Symmetric quadratic-cost matrix.
    q :
        Quadratic-cost vector.
    G :
        Linear inequality constraint matrix.
    h :
        Linear inequality constraint vector.
    A :
        Linear equality constraint matrix. It needs to be full row rank.
    b :
        Linear equality constraint vector.
    initvals :
        Warm-start guess vector.
    verbose :
        Set to `True` to print out extra information.
    opts :
        Option dictionary for qpSWIFT.

    Returns
    -------
    :
        Solution to the QP, if found, otherwise ``None``.

    Notes
    -----
    The option dictionary accepts the following settings:

    .. list-table::
       :widths: 30 70
       :header-rows: 1

       * - Name
         - Effect
       * - MAXITER
         - maximum number of iterations needed
       * - ABSTOL
         - absolute tolerance
       * - RELTOL
         - relative tolerance
       * - SIGMA
         - maximum centering allowed

    If a verbose output shows that the maximum number of iterations is reached,
    check e.g. (1) the rank of your equality constraint matrix and (2) that
    your inequality constraint matrix does not have zero rows.
    """
    if initvals is not None:
        print("qpSWIFT: note that warm-start values ignored by wrapper")
    result: dict = {}
    if opts is None:
        opts = {}
    opts["OUTPUT"] = 1  # include "sol" and "basicInfo"
    opts["VERBOSE"] = 1 if verbose else 0
    if G is not None and h is not None:
        if A is not None and b is not None:
            result = qpSWIFT.run(q, h, P, G, A, b, opts)
        else:  # no equality constraint
            result = qpSWIFT.run(q, h, P, G, opts=opts)
    else:  # no inequality constraint
        # See https://qpswift.github.io/index.html#updates
        raise NotImplementedError(
            "QP without inequality constraints is still WIP for qpSWIFT"
        )
    exit_flag = result["basicInfo"]["ExitFlag"]
    if exit_flag != 0:
        return None
    return result["sol"]
