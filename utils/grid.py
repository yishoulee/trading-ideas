from __future__ import annotations
from typing import Dict, Iterable, List


def parameter_grid(param_dict: Dict[str, Iterable]) -> List[Dict[str, object]]:
    """Create a list of parameter dicts from param grid.

    Example: parameter_grid({'n':[2,3], 'lookback':[60,120]})
    """
    from itertools import product
    keys = list(param_dict.keys())
    grids: List[Dict[str, object]] = []
    for combo in product(*param_dict.values()):
        grids.append({k: v for k, v in zip(keys, combo)})
    return grids
