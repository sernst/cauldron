import cauldron as cd
import _testlib

value = cd.shared.value
result_value = _testlib.patching_test(value)
cd.shared.result = result_value
