from typing import Any

import numpy as np
import matplotlib.pyplot as plt

def test_function() -> Any:
    x = np.linspace(0, 10, 1000)
    y = np.sin(x)
    
    plt.plot(x, y)
    plt.show()


def add(a: int, b: int) -> int:
    return a + b


def empty() -> None:
    pass


''':
    pass
'''

test_function()
