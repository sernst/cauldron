import cauldron as cd
import _testlib

value = cd.shared.value
cd.shared.result = _testlib.patching_test(value)
