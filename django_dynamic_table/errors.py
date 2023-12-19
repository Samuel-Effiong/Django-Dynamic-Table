class DynamicTableError(Exception):
    pass


class TableColumnError(Exception):
    pass


class TableRowError(Exception):
    pass


class CellValueError(Exception):
    pass


# #################################3
# ##################################
class TableHaveNoColumn(DynamicTableError):
    pass


class TableHaveNoRow(DynamicTableError):
    pass


class ColumnNotInTable(DynamicTableError):
    pass


class RowNotInTable(DynamicTableError):
    pass


class DuplicateColumnInTable(DynamicTableError):
    pass


# ############### Errors Specific to the Table Columns ##############
class UnSupportedDataType(TableColumnError):
    pass


# ########### Errors Specific to Cell Value
class CantParseValueToDataType(CellValueError):
    pass


class CellDoesNotExist(CellValueError):
    pass