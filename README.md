###DataTables

A package for displaying dataframes in a GUI.

####Packages needed
Pandas
PyQt4

#####Usage Example

```python
from PyQt4 import QtGui
from DataTables import DataTable
import pandas
import numpy as np
import sys

df1 = pandas.DataFrame(np.random.randn(1000, 10), columns=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])#columns=[str(x) for x in range(0, 10)])

app = QtGui.QApplication(sys.argv)
datatable = DataTable(df1, editable=True, window_title="test")
app.exec_()
```

#####Usage Example - 2
```python
from PyQt4 import QtGui
from DataTables import DataTable
import pandas
import numpy as np
import sys

df1 = pandas.DataFrame(np.random.randn(1000, 10), columns=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])#columns=[str(x) for x in range(0, 10)])
df2 = pandas.DataFrame(np.random.randn(50, 3), columns=["F", "G", "H"])

app = QtGui.QApplication(sys.argv)
datatable = DataTable([df1, df2], editable=True, window_title="DataTables")
app.exec_()
```