###PandasTables

A package for displaying dataframes in a GUI.

####Packages needed
Pandas
PyQt4

#####Usage Example

```python
df1 = pandas.DataFrame(np.random.randn(10, 5), columns=["A", "B", "C", "D", "E"])

app = QtGui.QApplication(sys.argv)
datatable = PandasTable(df1, editable=True, window_title="test")
app.exec_()
```

#####Usage Example - 2
```python
df1 = pandas.DataFrame(np.random.randn(10, 5), columns=["A", "B", "C", "D", "E"])
df2 = pandas.DataFrame(np.random.randn(50, 3), columns=["F", "G", "H"])

app = QtGui.QApplication(sys.argv)
datatable = PandasTable([df1, df2], editable=True, window_title="test")
app.exec_()
```