"""
Creating a Dynamic Table using conventional Django standard

This Table gives you more control over it manipulation than Django models

Developed by: Samuel Effiong Nkopuruk
Email: senai.nkop@gmail.com

"""

from typing import Sequence
from datetime import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .errors import (
    TableHaveNoRow, TableHaveNoColumn, ColumnNotInTable,
    RowNotInTable, DuplicateColumnInTable, DynamicTableError,

    UnSupportedDataType, CantParseValueToDataType, CellDoesNotExist
)


__SUPPORTED_DATA_TYPE_CHOICES__ = (
    ('char', 'Char'),
    ('int', 'Int'),
    ('float', 'Float'),
    ('bool', 'Bool'),
    ('textfield', 'TextField'),
    ('date', 'Date'),
)


# Create your models here.
class DynamicTable(models.Model):

    table_name = models.CharField(_('Table Name'), max_length=255, unique=True)
    table_description = models.TextField(_('Table Description'), blank=True)
    date_created = models.DateTimeField(_('Date Created'), default=timezone.now)

    table_columns = models.ManyToManyField('TableColumn', blank=True)
    table_rows = models.ManyToManyField('TableRow', blank=True)

    class Meta:
        ordering = ('-date_created', )

    def __str__(self) -> str:
        return f"{self.table_name}"

    def __total_table_rows(self) -> int:
        field = self.table_columns.first()

        if field and isinstance(field, TableColumn):
            return self.table_columns.all().count()
        else:
            # the table is empty
            return 0

    def __total_table_columns(self) -> int:
        return self.table_columns.all().count()

    def table_info(self) -> dict[str, int]:
        description = {
            'rows': self.__total_table_rows(),
            'columns': self.__total_table_columns()
        }
        return description

    def is_empty(self) -> bool:
        table_info = self.table_info()

        rows = table_info['rows']
        columns = table_info['columns']

        return True if columns == 0 or rows == 0 else False

    def is_column(self, column_name: str) -> bool:
        if not isinstance(column_name, str):
            raise ValueError("column name must be a str")

        try:
            column = self.table_columns.get(column_name=column_name)
            return True
        except TableColumn.DoesNotExist:
            return False

    def get_supported_data_types(self) -> list[str]:
        return [data_type[0] for data_type in __SUPPORTED_DATA_TYPE_CHOICES__]

    def data_type_is_supported(self, data_type: str | list) -> bool | list[bool]:
        supported_data_types = self.get_supported_data_types()

        if isinstance(data_type, str):
            return data_type.lower().strip() in supported_data_types
        elif isinstance(data_type, (list, tuple, set)):
            return [_type.lower().strip() in supported_data_types for _type in data_type]
        else:
            raise ValueError('arg must be either a str or a sequence')

    def add_column(self, column_name: str, data_type: str):
        if isinstance(column_name, str) and isinstance(data_type, str):
            if not self.data_type_is_supported(data_type):
                raise UnSupportedDataType()
            if self.is_column(column_name):
                raise DuplicateColumnInTable()

            table_column = TableColumn(
                table=self,
                column_name=column_name,
                column_data_type=data_type
            )
            table_column.save()

            self.table_columns.add(table_column)

            return table_column
        else:
            raise DynamicTableError("argument must be str, use self.bulk_add_columns to add multiple columns")

    def bulk_add_columns(self, column_names: Sequence[str], data_types: Sequence[str]):
        allowed_argument_type = (list, tuple, set)
        if isinstance(column_names, allowed_argument_type) and isinstance(data_types, allowed_argument_type):
            if len(column_names) != len(data_types):
                raise DynamicTableError(f"len({column_names}) = {len(column_names)} != len({data_types}) = {len(data_types)}")
            else:
                # check if list of data_types contains any unsupported data type
                supported_data_type = self.data_type_is_supported(data_types)
                if False in supported_data_type:
                    raise UnSupportedDataType(f"{data_types} data type that are supported are: {supported_data_type}")
                else:
                    # check if the provided column names contain duplicates, raise an error if it does
                    unique_column_names = set(column_names)
                    if len(column_names) != len(unique_column_names):
                        raise DuplicateColumnInTable()

                    is_column = [self.is_column(column) for column in column_names]

                    if True in is_column:
                        raise DuplicateColumnInTable()

                    columns = [
                        TableColumn.objects.create(
                            table=self,
                            column_name=column_name,
                            column_data_type=data_type
                        )

                        for column_name, data_type in zip(column_names, data_types, strict=True)
                        # the above further exception should not be activated, but adding it there,
                        # if just in case, for some unknown reason it escape the other safeguard.
                    ]
                    self.table_columns.add(*columns)
                    return columns
        else:
            raise DynamicTableError("argument must be a sequence. use self.add_column to add a single column")

    def add_row(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError(f"{value} is not a list or a dict")

        if self.__total_table_columns() == 0:
            raise TableHaveNoColumn()

        row = []
        table_row = TableRow.objects.create(table=self)

        for table_column in self.table_columns.all():
            cell_value = value.get(table_column.column_name, "")

            cell = CellValue.objects.create(
                value=cell_value, table=self,
                table_column=table_column,
                table_row=table_row
            )
            row.append(cell)

            # add cell to column
            table_column.column_cells.add(cell)

        # add cell to row
        table_row.row_cells.add(*row)

        # add row to table
        self.table_rows.add(table_row)
        return table_row

    def bulk_add_rows(self, values: Sequence[dict]) -> list:
        if not isinstance(values, (list, tuple, set)):
            raise ValueError('values must be a sequence of dict')

        rows = []
        for row in values:
            if not isinstance(row, dict):
                raise ValueError('values must be a sequence of dict')
            if self.__total_table_columns() == 0:
                raise TableHaveNoColumn()

            rows.append(self.add_row(row))
        return rows

    def delete_column(self, column_name):
        # using get instead of filter if for some reason the unique parameter
        # was disabled in the table column definition, this will doubly ensure
        # that the field are unique else it will always raise an error if it
        # encounter duplicates column names

        if not isinstance(column_name, str):
            raise ValueError('column_name must be a str')
        try:
            column = self.table_columns.get(column_name=column_name)
        except TableColumn.MultipleObjectsReturned:
            raise DuplicateColumnInTable()
        except TableColumn.DoesNotExist:
            raise ColumnNotInTable()
        else:
            # remove column from the table
            self.table_columns.remove(column)

            # delete the removed column and all the cells associated with it
            column.delete()
            return column

    def delete_row(self, row_index=None):
        """if row_index is None remove the last row"""

        if not isinstance(row_index, (int, type(None))):
            raise TypeError("Row index value must be an integer")

        try:
            if row_index is None:
                row = self.table_rows.last()
            else:
                row = self.table_rows.get(pk=row_index)
        except TableRow.DoesNotExist:
            raise RowNotInTable()
        else:
            # remove row from the table
            self.table_rows.remove(row)

            # delete the removed row and all the cells associated with it
            row.delete()
            return row

    def get_cell(self, column_name, row_index):
        if isinstance(row_index, str):
            row_index = int(row_index)
        if not self.is_column(column_name):
            raise ColumnNotInTable()
        try:
            cell = CellValue.objects.get(
                table=self,
                table_column__column_name=column_name,
                table_row_id=row_index
            )
            return cell
        except CellValue.DoesNotExist:
            raise CellDoesNotExist

    def get_column_cells(self, column_name):
        if not self.is_column(column_name):
            raise ColumnNotInTable()

        column = TableColumn.objects.get(table=self, column_name=column_name)
        column_cells = column.column_cells.all()

        return list(column_cells)

    def get_row_cells(self, row_index):
        if isinstance(row_index, str):
            row_index = int(row_index)

        try:
            row = TableRow.objects.get(table=self, id=row_index)
            row_cells = row.row_cells.all()
        except TableRow.DoesNotExist:
            raise RowNotInTable()

        return list(row_cells)


class TableColumn(models.Model):
    table = models.ForeignKey(DynamicTable, on_delete=models.CASCADE)

    column_name = models.CharField(max_length=255, unique=True)
    column_data_type = models.CharField(max_length=15, choices=__SUPPORTED_DATA_TYPE_CHOICES__)

    column_cells = models.ManyToManyField('CellValue', blank=True)

    def __str__(self):
        return f"{self.column_name}: {self.column_data_type} -- {self.table}"

    def _get_column_values(self):
        return self.column_cells.all()


class TableRow(models.Model):
    table = models.ForeignKey(DynamicTable, on_delete=models.CASCADE)
    row_cells = models.ManyToManyField('CellValue', blank=True)

    def __str__(self):
        return f"{self.table} Table: Row no. {self.id}"

    def to_dict(self):
        values = {
            item.column.column_name: item.value
            for item in self.row_cells.all()
        }
        return values


class CellValue(models.Model):
    """Synonymous with the cell in a spreadsheet, it contains the value of the
    table along with relevant information about it position in the table"""
    value = models.TextField(blank=True)

    table = models.ForeignKey(DynamicTable, on_delete=models.CASCADE)
    table_column = models.ForeignKey(TableColumn, on_delete=models.CASCADE)
    table_row = models.ForeignKey(TableRow, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.value
    
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        super(CellValue, self).save()

    def clean(self):
        super(CellValue, self).clean()
        self.__validate_data_type__(self.value, self.table_column.column_data_type)

    def __validate_data_type__(self, value, data_type):
        """
        Ensures that the values is saved in the database in the format that
        can be easily be converted to the desired data type
        """
        if data_type == 'char' or data_type == 'textfield':
            self.value = str(value)
        elif data_type == 'int':
            if not isinstance(value, int):
                try:
                    if value:
                        self.value = int(float(value))
                    else:
                        self.value = ""
                except ValueError:
                    raise CantParseValueToDataType(f"{value} to {data_type}")
        elif data_type == 'float':
            if not isinstance(value, float):
                try:
                    if value:
                        self.value = float(value)
                    else:
                        self.value = ""
                except ValueError:
                    raise CantParseValueToDataType(f"{value} to {data_type}")
        elif data_type == 'datetime':
            if value:
                # is it a str or a datetime object
                if isinstance(value, str):
                    try:
                        value = self.value.strip().lower()
                        value = datetime.fromisoformat(value)
                        self.value = value.isoformat()
                    except ValueError:
                        self.value = ""
                else:
                    try:
                        self.value = value.isoformat()
                    except Exception:
                        self.value = ''
            else:
                self.value = ""
        elif data_type == 'bool':
            if value:
                if not isinstance(value, bool):
                    value = str(value).strip().title()
                    if value == 'True' or value == 'False':
                        self.value = eval(value)
                    else:
                        raise CantParseValueToDataType(f"{value} to {data_type}")
            else:
                self.value = ""

    def get_value(self):
        """Get the value base on the data type

        If the data type is of file, it will retrieve the file from where
        it was uploaded, else format the value to the data type.

        The value should not be accessed directly.
        """

        data_type = self.table_column.column_data_type

        if data_type == 'char' or data_type == 'textfield':
            return self.value
        elif data_type == 'int':
            try:
                return int(float(self.value))
            except ValueError:
                return self.value
        elif data_type == 'float':
            try:
                return float(self.value)
            except ValueError:
                return self.value
        elif data_type == 'bool':
            try:
            # FIXME: Put more restrictions on this
                return eval(self.value)
            except Exception:
                return self.value
        elif data_type == 'datetime':
            try:
                return datetime.fromisoformat(self.value)
            except ValueError:
                return self.value
