"""
EC codebase Python library (AKA the "frontend")

Module mapping details:

TODO: remove module mapping code when backwards-compatibility is no longer required.

The below module mapping is required for backwards-compatibility with old pickle files
generated from before the EC codebase refactor. New files added to the codebase do not
need to be added to the mapping, but if the existing modules are moved, then this the
mapping needs to be updated to reflect the move or rename.

The mapping uses the following pattern:

    sys.modules[<old module path>] = <new module reference>

This is because the previous structure of the codebase was completely flat, and when refactoring
to a hierarchical files, loading previous pickle files no longer works properly. It is important
to retain the ability to read old pickle files generated from official experiments. As a workaround,
the old module paths are included below. A preferable alternative would be to export program state
into JSON files instead of pickle files to avoid issues where the underlying classes change, so that
could be a future improvement to this project. Until then, we use the module mapping workaround.

For more info, see this StackOverflow answer: https://stackoverflow.com/a/2121918/2573242
"""
import sys

from dreamcoder import dreamcoder
from dreamcoder import enumeration
from dreamcoder import frontier
from dreamcoder import grammar
from dreamcoder import likelihoodModel
from dreamcoder import program
from dreamcoder import primitiveGraph
try:
    from dreamcoder import recognition
except:
    print("Failure loading recognition - only acceptable if using pypy ",file=sys.stderr)
from dreamcoder import task
from dreamcoder import taskBatcher
from dreamcoder import type
from dreamcoder import utilities
from dreamcoder.domains.list import listPrimitives
from dreamcoder.domains.list import makeListTasks
from dreamcoder.domains.list import main as list_main
from dreamcoder.domains.arithmetic import arithmeticPrimitives

sys.modules['ec'] = dreamcoder
sys.modules['enumeration'] = enumeration
sys.modules['frontier'] = frontier
sys.modules['grammar'] = grammar
sys.modules['likelihoodModel'] = likelihoodModel
sys.modules['program'] = program
try: sys.modules['recognition'] = recognition
except: pass
sys.modules['task'] = task
sys.modules['taskBatcher'] = taskBatcher
sys.modules['type'] = type
sys.modules['utilities'] = utilities
sys.modules['listPrimitives'] = listPrimitives
sys.modules['makeListTasks'] = makeListTasks
#sys.modules['list'] = list_main
sys.modules['arithmeticPrimitives'] = arithmeticPrimitives
sys.modules['primitiveGraph'] = primitiveGraph
