#!/bin/bash
python3 -c "import pysat; print('pysat', pysat.__version__)" 2>&1 | tail -1
python3 -c "import z3; print('z3py', z3.get_version_string())" 2>&1 | tail -1
python3 -c "import ortools; print('ortools', ortools.__version__)" 2>&1 | tail -1
python3 -c "import numpy; print('numpy', numpy.__version__)" 2>&1 | tail -1
which cbc glpsol scip highs minisat glucose open-wbo rc2 2>/dev/null
python3 --version
