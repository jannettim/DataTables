from PyQt4 import QtCore
from PyQt4 import QtGui
import warnings
import pyparsing as pp
from numpy import float64
import re
import pandas
import sys


class DataTable(QtGui.QMainWindow):

    def __init__(self, df, width=1000, height=500, editable=False, window_title="DataFrame Viewer"):

        super(DataTable, self).__init__()
        self.setWindowTitle(window_title)
        self.datatable = TableWidget(df, self, width, height, editable)
        self.main_layout = QtGui.QVBoxLayout()

        self.next_action = QtGui.QAction(QtGui.QIcon(""), 'Next', self)
        self.quit_action = QtGui.QAction(QtGui.QIcon(""), "Quit", self)
        self.filter_action = QtGui.QAction(QtGui.QIcon(""), "Live Filtering", self)
        self.revert_action = QtGui.QAction(QtGui.QIcon(""), "Revert", self)
        self.head_action = QtGui.QAction(QtGui.QIcon(""), "Head", self)
        self.tail_action = QtGui.QAction(QtGui.QIcon(""), "Tail", self)
        self.columns_action = QtGui.QAction(QtGui.QIcon(""), "Show Columns", self)
        self.row_action = QtGui.QAction(QtGui.QIcon(""), "Show Rows", self)
        self.export = QtGui.QAction(QtGui.QIcon(""), "Export", self)
        self.progressbar = QtGui.QProgressBar()
        self.statusbar = self.statusBar()

        self.set_triggers()

        self.get_tooltips()

        if isinstance(df, (tuple, list)):

            pass

        else:

            self.next_action.setEnabled(False)

        self.create_toolbar()
        self.get_shortcuts()
        self.get_menubar()

        self.centralWidget = self.datatable
        self.centralWidget.setLayout(self.main_layout)
        self.setCentralWidget(self.centralWidget)

        self.init_ui(width, height)

    def get_menubar(self):

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.export)
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.revert_action)
        edit_menu.addAction(self.filter_action)
        edit_menu.addAction(self.head_action)
        edit_menu.addAction(self.tail_action)
        edit_menu.addAction(self.columns_action)
        edit_menu.addAction(self.row_action)

        file_menu.addAction(self.quit_action)

    def get_shortcuts(self):

        self.next_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Tab))
        self.quit_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Q))
        self.filter_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_R))
        self.revert_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_R))
        self.head_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_H))
        self.tail_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_T))
        self.columns_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.SHIFT + QtCore.Qt.Key_C))
        self.row_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.ALT + QtCore.Qt.Key_R))
        self.export.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_S))

    def get_tooltips(self):

        self.next_action.setToolTip("Load next dataframe")
        self.filter_action.setToolTip("Reload dataframe with custom filter")
        self.revert_action.setToolTip("Return dataframe to original state")
        self.head_action.setToolTip("Open dialog box with top n rows")
        self.tail_action.setToolTip("Open dialog box with last n rows")
        self.columns_action.setToolTip("Open dialog box with selected columns")
        self.row_action.setToolTip("Open dialog box with selected rows")
        self.export.setToolTip("Export table as file")

    def set_triggers(self):

        self.next_action.triggered.connect(self.clicked_next_button)
        self.quit_action.triggered.connect(self.exit_action)
        self.filter_action.triggered.connect(self.open_filter_dialog)
        self.revert_action.triggered.connect(self.revert_df)
        self.head_action.triggered.connect(self.open_input_dialog)
        self.tail_action.triggered.connect(self.open_input_dialog)
        self.columns_action.triggered.connect(self.open_input_dialog)
        self.row_action.triggered.connect(self.open_input_dialog)
        self.export.triggered.connect(self.open_input_dialog)

    def create_toolbar(self):

        self.toolbar = self.addToolBar("Next")
        self.toolbar.addAction(self.next_action)
        self.toolbar.addAction(self.quit_action)
        self.toolbar.addAction(self.filter_action)
        self.toolbar.addAction(self.revert_action)

    def clicked_next_button(self):

        test = self.datatable.next_button_clicked()

        if test:
            self.next_action.setEnabled(False)

    def init_ui(self, width, height):

        self.resize(width, height)


        self.show()

    def open_input_dialog(self):

        sender = self.sender()

        if sender.text() == "Export":

            filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", "", self.tr('*.txt;;*.csv;;*.xlsx'))
            if re.search(r'.*\.txt', filename):
                self.datatable.df.to_csv(filename, sep="\t")
            elif re.search(r'.*\.csv', filename):
                self.datatable.df.to_csv(filename, sep=",")
            elif re.search(r'.*\.xlsx', filename):
                wb = pandas.ExcelWriter(filename)
                self.datatable.df.to_excel(wb, "Sheet1")

        else:

            i_dialog = InputDialog(sender.text(), self.datatable.df)

    def open_filter_dialog(self):

        fd = FilterDialog(self.datatable.df, self.datatable)

    def revert_df(self):

        self.datatable.update_data(self.datatable.df)

    def exit_action(self):
        self.close()

    def main(self):

        pass


class TableWidget(QtGui.QTableWidget):

    def __init__(self, df, parent, width=1000, height=500, editable=False, window_title="DataFrame Viewer"):

        super(TableWidget, self).__init__()

        # self.window_title = window_title

        if not editable:
            self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        if isinstance(df, (tuple, list)):

            self.table_iter = df
            self.df = df[0]
            self.iter_index = 0

        else:

            self.table_iter = None
            self.iter_index = None
            self.df = df

        self.setColumnCount(len(self.df.columns))
        self.setRowCount(len(self.df.index))
        self.update_thread = WorkerThread(self)

        self.init_ui(width, height)

    def init_ui(self, width, height):

        # self.resize(width, height)

        self.setHorizontalHeaderLabels(self.df.columns.tolist())
        self.set_data(self.df)

        self.itemChanged.connect(self.edit_dataframe)

    def edit_dataframe(self):

        try:

            row = self.currentRow()
            column = self.currentColumn()

            item = self.item(row, column)

            col_type = self.df.iloc[:, column].dtype

            try:
                self.df.set_value(row, self.df.columns.tolist()[column], item.text())
                self.df[self.df.columns.tolist()[column]] = self.df[self.df.columns.tolist()[column]].astype(col_type)
            except ValueError:
                warnings.warn("Value supplied does not match dtype of pandas column.  Type of column converted to object.")
                self.df[self.df.columns.tolist()[column]] = self.df[self.df.columns.tolist()[column]].astype(object)

        except AttributeError:

            pass

    def next_button_clicked(self):

        self.clear()
        self.iter_index += 1
        self.df = self.table_iter[self.iter_index]

        self.setHorizontalHeaderLabels(self.df.columns.tolist())
        self.setColumnCount(len(self.df.columns.tolist()))
        self.setRowCount(len(self.df.index))
        self.set_data(self.df)

        if self.iter_index == len(self.table_iter) - 1:

            return True
            # self.mw.next_button.deleteLater()
            # self.hbox.addWidget(self.finish_button)

    def set_data(self, df):

        if self.update_thread.isRunning():
            pass

        else:
            self.update_thread.start()

        self.update_thread.set_data(df)
        self.update_thread.exit()

        # for i in range(len(df.index)):
        #     for j in range(len(df.columns)):
        #         self.setItem(i, j, QtGui.QTableWidgetItem(str(df.iat[i, j])))

    def update_data(self, df):

        if self.update_thread.isRunning():
            pass

        else:
            self.update_thread.start()

        self.update_thread.update_data(df)

        # self.clearContents()
        #
        # self.setHorizontalHeaderLabels(df.columns.tolist())
        # self.setColumnCount(len(df.columns.tolist()))
        # self.setRowCount(len(df.index))
        # self.set_data(df)

        self.update_thread.exit()


class FilterDialog(QtGui.QDialog):

    def __init__(self, df, parent):

        super(FilterDialog, self).__init__()

        self.df = df
        self.parent = parent

        self.eval_string = ""

        self.grid = QtGui.QGridLayout()

        self.widgets_dict = {}

        self.conditionals = QtGui.QComboBox()
        self.or_button = QtGui.QPushButton("or")
        self.and_button = QtGui.QPushButton("and")
        self.advanced_filter = QtGui.QLineEdit()

        self.lit_labels = QtGui.QLabel("Literals")
        self.col_label = QtGui.QLabel("Columns")
        self.con_label = QtGui.QLabel("Conditionals")
        # self.open_label = QtGui.QLabel("Open Parentheses")
        # self.close_label = QtGui.QLabel("Close Parentheses")
        self.text_label = QtGui.QLabel("Pandas Code")
        self.code_prompt = QtGui.QLabel("self.df.")

        self.refresh_data = QtGui.QPushButton("Refresh Data")
        self.advanced_button = QtGui.QPushButton("Advanced Filter")
        self.basic_button = QtGui.QPushButton("Basic Filter")
        self.refresh_data_adv = QtGui.QPushButton("Refresh Data")

        self.cur_row = 0

        self.init_ui()

        self.exec_()

    def init_ui(self):

        self.setLayout(self.grid)

        self.setWindowTitle("Live Filtering")

        self.add_labels()

        self.set_triggers()

        self.add_row()

    def eval_filter(self):

        indexes = []
        prev_row = []

        for x in range(1, self.cur_row):
            try:
                literal_text = int(self.widgets_dict[x]["Literals"].text())

            except ValueError:

                try:

                    literal_text = float(self.widgets_dict[x]["Literals"].text())

                except ValueError:

                    literal_text = self.widgets_dict[x]["Literals"].text()

            if self.widgets_dict[x]["Conditionals"].currentText() == "isnull":
                indexes.append(set(self.df.loc[self.df[self.widgets_dict[x]["Columns"].currentText()].isnull()].index.values))
            elif self.widgets_dict[x]["Conditionals"].currentText() == "isnotnull":
                indexes.append(set(self.df.loc[~self.df[self.widgets_dict[x]["Columns"].currentText()].isnull()].index.values))
            elif self.widgets_dict[x]["Conditionals"].currentText() == ">":
                indexes.append(set(self.df.loc[self.df[self.widgets_dict[x]["Columns"].currentText()] > literal_text].index.values))
            elif self.widgets_dict[x]["Conditionals"].currentText() == "<":
                indexes.append(set(self.df.loc[self.df[self.widgets_dict[x]["Columns"].currentText()] < literal_text].index.values))
            elif self.widgets_dict[x]["Conditionals"].currentText() == ">=":
                indexes.append(set(self.df.loc[self.df[self.widgets_dict[x]["Columns"].currentText()] >= literal_text].index.values))
            elif self.widgets_dict[x]["Conditionals"].currentText() == "<=":
                indexes.append(set(self.df.loc[self.df[self.widgets_dict[x]["Columns"].currentText()] <= literal_text].index.values))
            elif self.widgets_dict[x]["Conditionals"].currentText() == "=":
                indexes.append(set(self.df.loc[self.df[self.widgets_dict[x]["Columns"].currentText()] == literal_text].index.values))
            elif self.widgets_dict[x]["Conditionals"].currentText() == "!=":
                indexes.append(set(self.df.loc[self.df[self.widgets_dict[x]["Columns"].currentText()] != literal_text].index.values))
            elif self.widgets_dict[x]["Conditionals"].currentText() == "isin":
                if self.df[self.widgets_dict[x]["Columns"].currentText()].dtype == float64:
                    indexes.append(set(self.df.loc[self.df[self.widgets_dict[x]["Columns"].currentText()].isin([float(l.strip()) for l in literal_text.split(",")])].index.values))
                elif self.df[self.widgets_dict[x]["Columns"].currentText()].dtype == int:
                    indexes.append(set(self.df.loc[self.df[self.widgets_dict[x]["Columns"].currentText()].isin([int(l.strip()) for l in literal_text.split(",")])].index.values))
                else:
                    indexes.append(set(self.df.loc[self.df[self.widgets_dict[x]["Columns"].currentText()].isin([l.strip() for l in literal_text.split(",")])].index.values))
            elif self.widgets_dict[x]["Conditionals"].currentText() == "isnotin":
                if self.df[self.widgets_dict[x]["Columns"].currentText()].dtype == float64:
                    indexes.append(set(self.df.loc[~self.df[self.widgets_dict[x]["Columns"].currentText()].isin([float(l.strip()) for l in literal_text.split(",")])].index.values))
                elif self.df[self.widgets_dict[x]["Columns"].currentText()].dtype == int:
                    indexes.append(set(self.df.loc[~self.df[self.widgets_dict[x]["Columns"].currentText()].isin([int(l.strip()) for l in literal_text.split(",")])].index.values))
                else:
                    indexes.append(set(self.df.loc[~self.df[self.widgets_dict[x]["Columns"].currentText()].isin([l.strip() for l in literal_text.split(",")])].index.values))

        for i in indexes:


            if self.widgets_dict[indexes.index(i) + 1]["CondCombo"].currentText() == "and":

                if not prev_row:

                    prev_row = [i, "and"]

                else:

                    if prev_row[1] == "and":

                        prev_row = [prev_row[0].intersection(i), "and"]

                    if prev_row[1] == "or":

                        prev_row = [prev_row[0].union(i), "and"]

            elif self.widgets_dict[indexes.index(i) + 1]["CondCombo"].currentText() == "or":

                if not prev_row:

                    prev_row = [i, "or"]

                else:

                    if prev_row[1] == "and":
                        prev_row = [prev_row[0].intersection(i), "or"]

                    if prev_row[1] == "or":
                        prev_row = [prev_row[0].union(i), "or"]
            else:

                if not prev_row:

                    prev_row = [i]

                else:

                    if prev_row[1] == "and":

                        prev_row = [prev_row[0].intersection(i), ""]

                    elif prev_row[1] == "or":

                        prev_row = [prev_row[0].union(i), ""]

                    else:

                        if prev_row[1] == "" and indexes.index(i) != len(indexes) - 1:

                            ErrorDialog("Missing and/or statement")

        if not prev_row:
            df = self.df

        else:
            df = self.df.iloc[list(prev_row[0])]

        self.parent.update_data(df)
        self.exit_action()

    def eval_advaced(self):

        pp.ParserElement.enablePackrat()

        print_func = pp.Word("print(", exact=6)
        df_str = pp.Word("self.df", exact=7)
        period_match = pp.Word(".")
        loc_match = pp.Word("loc[", exact=4)
        left_bracket = pp.Word("[")
        right_bracket = pp.Word("]")
        right_paren = pp.Word(")")
        gte = pp.Word(">=", exact=2)  # <===!=", exact=2)
        lte = pp.Word("<=", exact=2)
        quote = pp.Word("\"", exact=1)
        equal_cond = pp.Word("==", exact=2)
        nequal_cond = pp.Word("!=", exact=2)
        python_str_floats = pp.OneOrMore(pp.Word(pp.alphanums + "." + "," + ")"))
        columns_df = []

        for x in self.df.columns.values.tolist():
            columns_df.append(pp.Word(x, exact=len(x)))

        parse_eval = loc_match + pp.OneOrMore(pp.ZeroOrMore("(") + pp.Optional("~") + "self.df" + pp.Or([".", "[\"", "['"]) + pp.Or(columns_df) + pp.Optional(pp.Or(["\"]", "']"])) + \
                     pp.Or([gte, lte, equal_cond, nequal_cond, pp.Word(".isin([", exact=7), pp.Word(".isnull(", exact=8)]) + pp.Optional(pp.Or(["\"", "'"])) + pp.Or(python_str_floats) + pp.Optional(pp.Or("\"]", "']")) + pp.ZeroOrMore(")") + pp.Optional(pp.Or(["|", "&"]))) + "]"

        parse_eval.parseString(self.advanced_filter.text())
        exec("self.df = " + "self.df." + self.advanced_filter.text())

        self.parent.update_data(self.df)
        self.exit_action()

    def isnull_chosen(self):

        sender = self.sender()
        idx = self.grid.indexOf(sender)
        button_row = self.grid.getItemPosition(idx)[0]

        cur_text = self.widgets_dict[button_row]["Conditionals"].currentText()

        if cur_text == "isnull" or cur_text == "isnotnull":

            self.widgets_dict[button_row]["Literals"].setEnabled(False)

        else:

            self.widgets_dict[button_row]["Literals"].setEnabled(True)

    def revert_to_basic(self):

        self.text_label.hide()
        self.code_prompt.hide()
        self.advanced_filter.hide()
        self.refresh_data_adv.hide()
        self.basic_button.hide()

        self.code_prompt.setEnabled(False)

        for k, v in self.widgets_dict.items():

            for k2 in v.keys():
                self.widgets_dict[k][k2].show()
                self.lit_labels.show()
                self.col_label.show()
                self.con_label.show()

                self.advanced_button.show()
                self.refresh_data.show()

    def advanced_layout(self):

        self.refresh_data.hide()

        for k, v in self.widgets_dict.items():

            for k2 in v.keys():
                self.widgets_dict[k][k2].hide()
                self.lit_labels.hide()
                self.col_label.hide()
                self.con_label.hide()


                self.refresh_data.hide()
                self.advanced_button.hide()
                self.and_button.hide()
                self.or_button.hide()

        if self.code_prompt.isEnabled():
            self.grid.addWidget(self.text_label, 0, 1)
            self.grid.addWidget(self.code_prompt, 1, 0)
            self.grid.addWidget(self.advanced_filter, 1, 1)
            self.grid.addWidget(self.refresh_data_adv, 1, 2)
            self.grid.addWidget(self.basic_button, 2, 2)

        else:
            self.refresh_data_adv.show()
            self.code_prompt.setEnabled(True)
            self.text_label.show()
            self.code_prompt.show()
            self.advanced_filter.show()
            self.basic_button.show()

    def set_triggers(self):

        self.refresh_data.clicked.connect(self.eval_filter)
        self.advanced_button.clicked.connect(self.advanced_layout)
        self.basic_button.clicked.connect(self.revert_to_basic)
        self.refresh_data_adv.clicked.connect(self.eval_advaced)

    def add_labels(self):
        self.grid.addWidget(self.col_label, 0, 1)
        self.grid.addWidget(self.con_label, 0, 2)
        self.grid.addWidget(self.lit_labels, 0, 3)

        self.cur_row = 1

    def and_conditionals(self):

        sender = self.sender()

        if sender.currentText() == "and" or sender.currentText() == "or":

            if self.cur_row < 5:

                self.add_row()

            else:
                self.add_row(False)

    def add_row(self, add_conditional_combo=True):

        self.widgets_dict.update({self.cur_row: {"Columns": QtGui.QComboBox(),
                                                 "Conditionals": QtGui.QComboBox(), "Literals": QtGui.QLineEdit(),
                                                 "CondCombo": QtGui.QComboBox()}})

        self.widgets_dict[self.cur_row]["Columns"].addItems(self.df.columns.tolist())
        self.widgets_dict[self.cur_row]["Conditionals"].addItems(["", ">", "<", "=", ">=", "<=", "!=", "isnull",
                                                                        "isnotnull", "isin", "isnotin"])
        self.widgets_dict[self.cur_row]["CondCombo"].addItems(["", "and", "or"])

        self.add_buttons(add_conditional_combo)

        self.widgets_dict[self.cur_row]["CondCombo"].currentIndexChanged.connect(self.and_conditionals)
        self.widgets_dict[self.cur_row]["Conditionals"].currentIndexChanged.connect(self.isnull_chosen)

        self.cur_row += 1

    def add_buttons(self, add_conditional_combo):
        self.grid.addWidget(self.widgets_dict[self.cur_row]["Columns"], self.cur_row, 1)
        self.grid.addWidget(self.widgets_dict[self.cur_row]["Conditionals"], self.cur_row, 2)
        self.grid.addWidget(self.widgets_dict[self.cur_row]["Literals"], self.cur_row, 3)
        self.grid.addWidget(self.refresh_data, self.cur_row + 1, 6)
        self.grid.addWidget(self.advanced_button, self.cur_row + 1, 5)

        if add_conditional_combo:
            self.grid.addWidget(self.widgets_dict[self.cur_row]["CondCombo"], self.cur_row, 5)

    def exit_action(self):
        self.close()

class InputDialog(QtGui.QDialog):

    def __init__(self, box_type, df):

        super(InputDialog, self).__init__()

        self.df = df
        self.box_type = box_type

        self.grid = QtGui.QGridLayout()

        self.filter_input = QtGui.QLineEdit()
        self.filter_input2 = QtGui.QLineEdit()
        self.label = QtGui.QLabel(box_type)
        self.rows_label1 = QtGui.QLabel("Start Value")
        self.rows_label2 = QtGui.QLabel("End Value")
        self.ok_button = QtGui.QPushButton("OK")

        self.ok_action = QtGui.QAction(QtGui.QIcon(""), "OK", self)

        self.set_triggers()

        self.init_ui(box_type)

        self.exec_()

    def init_ui(self, box_type):

        self.setLayout(self.grid)
        self.setWindowTitle(box_type)

        self.add_widgets()

    def add_widgets(self):

        if self.box_type == "Show Rows":

            self.grid.addWidget(self.filter_input, 0, 1)
            self.grid.addWidget(self.rows_label1, 0, 0)
            self.grid.addWidget(self.rows_label2, 1, 0)
            self.grid.addWidget(self.filter_input2, 1, 1)
            self.grid.addWidget(self.ok_button, 2, 1)

        else:

            self.grid.addWidget(self.filter_input, 0, 1)
            self.grid.addWidget(self.label, 0, 0)
            self.grid.addWidget(self.ok_button, 0, 2)

    def set_triggers(self):

        self.ok_button.clicked.connect(self.perform_actions)

    def perform_actions(self):

        if self.box_type == "Head":
            self.resize(500, 500)

            self.filter_input.deleteLater()
            self.label.deleteLater()
            self.ok_button.deleteLater()

            vd = TableWidget(self.df.head(int(self.filter_input.text())), self)
            self.grid.addWidget(vd, 0, 0)

        elif self.box_type == "Tail":

            self.resize(500, 500)

            self.filter_input.deleteLater()
            self.label.deleteLater()
            self.ok_button.deleteLater()

            vd = TableWidget(self.df.tail(int(self.filter_input.text())), self)
            self.grid.addWidget(vd, 0, 0)

        elif self.box_type == "Show Columns":

            self.filter_input.deleteLater()
            self.label.deleteLater()
            self.ok_button.deleteLater()

            try:
                self.resize(500, 500)
                new_df = self.df[[c.strip() for c in self.filter_input.text().split(",")]]
                vd = TableWidget(new_df, self)
                self.grid.addWidget(vd, 0, 0)
            except KeyError:

                ErrorDialog("One or more column names provided not recognized.  Please enter column names separated by commas.")
                self.close()

        elif self.box_type == "Show Rows":

            self.filter_input.deleteLater()
            self.rows_label1.deleteLater()
            self.rows_label2.deleteLater()
            self.filter_input2.deleteLater()
            self.ok_button.deleteLater()

            text1 = self.filter_input.text()
            text2 = self.filter_input2.text()
            self.resize(500, 500)

            if text1 and text2:

                new_df = self.df[int(text1):int(text2)]
                vd = TableWidget(new_df, self)
                self.grid.addWidget(vd, 0, 0)

            elif text1 and not text2:

                new_df = self.df.iloc[[int(text1)]]
                vd = TableWidget(new_df, self)
                self.grid.addWidget(vd, 0, 0)

            elif not text1 and text2:

                new_df = self.df[:int(text2)]
                vd = TableWidget(new_df, self)
                self.grid.addWidget(vd, 0, 0)


class ErrorDialog(QtGui.QDialog):

    def __init__(self, msg):
        super(ErrorDialog, self).__init__()

        self.grid = QtGui.QGridLayout()

        self.ok_button = QtGui.QPushButton("OK")
        self.err_msg = QtGui.QLabel(msg)

        self.ok_button.clicked.connect(self.close)

        self.init_ui()

        self.exec_()

    def init_ui(self):

        self.setLayout(self.grid)

        self.err_msg.setAlignment(QtCore.Qt.AlignCenter)
        self.err_msg.setMaximumWidth(700)
        self.err_msg.setWordWrap(True)
        self.ok_button.setMaximumWidth(100)

        self.grid.addWidget(self.err_msg, 0, 0)
        self.grid.addWidget(self.ok_button)


class WorkerThread(QtCore.QThread):

    tick = QtCore.pyqtSignal(int, name="changed")

    def __init__(self, table):

        QtCore.QThread.__init__(self)
        self.table = table


    def set_data(self, df):

        for i in range(len(df.index)):
            for j in range(len(df.columns)):
                self.table.setItem(i, j, QtGui.QTableWidgetItem(str(df.iat[i, j])))

    def update_data(self, df):

        self.table.clearContents()

        self.table.setHorizontalHeaderLabels(df.columns.tolist())
        self.table.setColumnCount(len(df.columns.tolist()))
        self.table.setRowCount(len(df.index))
        self.set_data(df)