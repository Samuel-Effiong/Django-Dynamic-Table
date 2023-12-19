import datetime
from typing import List

from django.test import TestCase
from django.utils import timezone

from .models import DynamicTable, TableColumn, TableRow, CellValue
from .errors import (
    TableHaveNoRow, TableHaveNoColumn, ColumnNotInTable,
    RowNotInTable, DuplicateColumnInTable, DynamicTableError,

    UnSupportedDataType, CantParseValueToDataType, CellDoesNotExist
)


# Create your tests here.
class DynamicTableTest(TestCase):
    def setUp(self) -> None:
        self.name = 'Employee Records'
        self.description = "Contains company employee personal information"
        self.date_created = timezone.now().date()

        self.column_name = 'First Name'
        self.data_type = 'char'

        self.supported_data_type = ['int', 'char', 'textfield', 'float', 'bool', 'date']

        self.table = DynamicTable(
            table_name=self.name,
            table_description=self.description
        )
        self.table.save()

    def test_table_creation_with_no_columns_and_rows(self):

        self.assertEqual(self.name, str(self.table))
        self.assertEqual(self.description, self.table.table_description)
        self.assertEqual(self.date_created, self.table.date_created.date())

        default_value = {
            'rows': 0,
            'columns': 0
        }
        self.assertDictEqual(default_value, self.table.table_info())

        # Delete columns test
        self.assertRaises(ColumnNotInTable, self.table.delete_column, column_name='Name')

        # Delete rows test
        self.assertRaises(RowNotInTable, self.table.delete_row, row_index=1)
        self.assertRaises(TypeError, self.table.delete_row, row_index='1')
        self.assertTrue(self.table.is_empty())

        # ensures that rows can't be added to an empty table
        self.assertRaises(TableHaveNoColumn, self.table.add_row, value={})
        self.assertRaises(ValueError, self.table.add_row, value='love')
        self.assertRaises(ValueError, self.table.add_row, value=[1, 2, 3])
        self.assertRaises(ValueError, self.table.add_row, value=(1, 2, 3))

        self.assertRaises(TableHaveNoColumn, self.table.bulk_add_rows, values=[{}, {}])
        self.assertRaises(ValueError, self.table.bulk_add_rows, values={})
        self.assertRaises(ValueError, self.table.bulk_add_rows, values='love')
        self.assertRaises(ValueError, self.table.bulk_add_rows, values=(1, 2))
        self.assertRaises(ValueError, self.table.bulk_add_rows, values=[1, '2'])

    def test_supported_data_types(self):
        self.assertListEqual(sorted(self.supported_data_type), sorted(self.table.get_supported_data_types()))

        self.assertTrue(self.table.data_type_is_supported(' CHAR'))
        self.assertTrue(self.table.data_type_is_supported('DaTe '))
        self.assertTrue(self.table.data_type_is_supported('  bool  '))

        self.assertFalse(self.table.data_type_is_supported('File'))
        self.assertFalse(self.table.data_type_is_supported('timE'))

        self.assertIsInstance(self.table.data_type_is_supported(['file', 'char']), list)
        self.assertListEqual([True, False, True, False], self.table.data_type_is_supported(['cHar', 'file', 'DATE', 'time']))
        self.assertListEqual([True, True], self.table.data_type_is_supported(['cHar', 'DATE',]))
        self.assertListEqual([False, False], self.table.data_type_is_supported(['File', 'time']))

    def test_adding_column_with_incorrect_parameters(self):
        self.assertRaises(DynamicTableError, self.table.add_column, ['first name'], ['char'])
        self.assertRaises(DynamicTableError, self.table.bulk_add_columns, 'first name', 'char')

    def test_bulk_adding_columns_with_unequal_sequence_length(self):
        # test unequal sequence length
        self.assertRaises(DynamicTableError, self.table.bulk_add_columns, ['first name', 'bio'], ['char', 'textfield', 'int'])
        self.assertRaises(
            DynamicTableError, self.table.bulk_add_columns,
            ['first name', 'last name', 'bio'], ['char', 'textfield']
        )

    def test_adding_columns_with_unsupported_data_type(self):
        # test unsupported data type
        self.assertRaises(UnSupportedDataType, self.table.add_column, self.column_name, 'file')
        self.assertRaises(UnSupportedDataType, self.table.bulk_add_columns, [self.column_name], ['file'])
        self.assertRaises(UnSupportedDataType, self.table.bulk_add_columns, [self.column_name, 'last name'], ['char', ' filE '])

    def test_adding_columns_with_duplicate_columns(self):
        # test duplicate columns
        self.assertRaises(DuplicateColumnInTable, self.table.bulk_add_columns, [self.column_name, self.column_name], ['char', 'char'])
        self.assertRaises(
            DuplicateColumnInTable, self.table.bulk_add_columns,
            [self.column_name, 'Bio', self.column_name],
            ['char', 'char', 'char']
        )

    def test_adding_columns_with_correct_parameter(self):
        # ensures that the TableColumn is return on successful addition
        column = self.table.add_column(self.column_name, self.data_type)
        self.assertIsInstance(column, TableColumn)

        # confirm it is added to the table
        self.assertTrue(self.table.table_columns.contains(column))

        column = self.table.add_column('Last Name', self.data_type)
        self.assertIsInstance(column, TableColumn)

        self.assertTrue(self.table.is_column(self.column_name))
        self.assertTrue(self.table.is_column('Last Name'))

        self.assertFalse(self.table.is_column('Bio'))
        self.assertFalse(self.table.is_column('Sex'))
        self.assertRaises(ValueError, self.table.is_column, ['Bio', 'Sex'])

        columns = self.table.bulk_add_columns(['Sex', 'Bio'], ['char', 'textfield'])
        self.assertIsInstance(columns, list)
        self.assertEqual(len(columns), 2)

        # test further addition of duplicate column
        self.assertRaises(DuplicateColumnInTable, self.table.add_column, self.column_name, self.data_type)
        self.assertRaises(DuplicateColumnInTable, self.table.bulk_add_columns, ['Nationality', self.column_name], ['char', 'char'])

    def __add_columns_to_table(self):
        column_names = ['First Name', 'Last Name', 'Gender', 'Bio', 'Age', 'Is Married', 'Income']
        column_data_types = ['char', 'char', 'char', 'textfield', 'int', 'bool', 'float']
        columns = self.table.bulk_add_columns(column_names, column_data_types)
        return columns

    def __add_row_to_table(self):
        rows = [
            {
                'First Name': 'Samuel', 'Last Name': 'Nkopuruk',
                'Bio': 'A Backend Developer', 'Is Married': False
            },
            {
                'First Name': 'Ebuka', 'Last Name': 'Edward',
                'Bio': 'A Doctor', 'Is Married': 'true'
            },
            {
                'First Name': 'Sunday', 'Last Name': 'Akpan',
                'Bio': 'A Video Editor', 'Is Married': False
            }
        ]

        table_rows = self.table.bulk_add_rows(values=rows)
        return table_rows

    def test_adding_row(self):
        columns = self.__add_columns_to_table()

        row = {
            'First Name': 'Samuel', 'Last Name': 'Nkopuruk',
            'Bio': 'A Backend Developer', 'Is Married': 'True'
        }

        table_row = self.table.add_row(row)
        self.assertIsInstance(table_row, TableRow)

        self.assertTrue(self.table.table_rows.contains(table_row))
        self.assertEqual(row.get('Age', ''), table_row.row_cells.get(table_column__column_name='Age').value)
        self.assertEqual(row.get('First Name', ''), table_row.row_cells.get(table_column__column_name='First Name').value)

    def test_adding_row_with_wrong_columns(self):
        columns = self.__add_columns_to_table()

        row = {
            'One': 1, 'Two': 2, 'Three': 3, 'Four': 4
        }

        table_row = self.table.add_row(row)
        self.assertIsInstance(table_row, TableRow)
        self.assertFalse(table_row.row_cells.get(table_column__column_name='First Name').value)
        self.assertFalse(table_row.row_cells.get(table_column__column_name='Last Name').value)

    def test_adding_row_in_bulk(self):
        columns = self.__add_columns_to_table()

        rows = [
            {
                'First Name': 'Samuel', 'Last Name': 'Nkopuruk',
                'Bio': 'A Backend Developer', 'Is Married': False
            },
            {
                'First Name': 'Ebuka', 'Last Name': 'Edward',
                'Bio': 'A Doctor', 'Is Married': 'true'
            },
            {
                'First Name': 'Sunday', 'Last Name': 'Akpan',
                'Bio': 'A Video Editor', 'Is Married': False
            }
        ]

        table_rows = self.table.bulk_add_rows(values=rows)

        self.assertIsInstance(table_rows, list)
        self.assertEqual(len(table_rows), 3)

        for row in table_rows:
            self.assertTrue(self.table.table_rows.contains(row))

    def test_validate_data_type(self):
        self.__add_columns_to_table()
        self.__add_row_to_table()

        row = {
            'First Name': 'Samuel', 'Last Name': 'Nkopuruk',
            'Bio': 'A Backend Developer', 'Is Married': False, 'Income': 27000.00
        }

        table_row = self.table.add_row(row)
        self.assertIsInstance(table_row, TableRow)

        row = {
            'First Name': 'Samuel', 'Last Name': 'Nkopuruk',
            'Bio': 'A Backend Developer', 'Age': '3o'
        }
        self.assertRaises(CantParseValueToDataType, self.table.add_row, value=row)

        row = {
            'First Name': 'Samuel', 'Last Name': 'Nkopuruk',
            'Bio': 'A Backend Developer', 'Income': '30.0d'
        }
        self.assertRaises(CantParseValueToDataType, self.table.add_row, value=row)

    def test_delete_column(self):
        self.__add_columns_to_table()
        self.__add_row_to_table()

        column = self.table.delete_column('Income')
        self.assertIsInstance(column, TableColumn)

        # ValueError of QuerySet.contains() cannot be used on unsaved objects
        # should be raise
        self.assertRaises(ValueError, self.table.table_columns.contains, column)
        self.assertRaises(ValueError, TableColumn.objects.contains, column)
        self.assertRaises(CellValue.DoesNotExist, CellValue.objects.get, table_column__column_name=column.column_name)

        column = self.table.delete_column('Age')
        self.assertIsInstance(column, TableColumn)
        self.assertRaises(ValueError, self.table.table_columns.contains, column)
        self.assertRaises(ValueError, TableColumn.objects.contains, column)
        self.assertRaises(CellValue.DoesNotExist, CellValue.objects.get, table_column__column_name=column.column_name)

        self.assertRaises(ColumnNotInTable, self.table.delete_column, column_name='Not A Column')

        # test with multiple columns
        self.assertRaises(ValueError, self.table.delete_column, column_name=['Is Married', 'Age'])

    def test_delete_row(self):
        self.__add_columns_to_table()
        self.__add_row_to_table()
        self.__add_row_to_table()

        row = self.table.delete_row(1)
        self.assertIsInstance(row, TableRow)

        # ValueError of QuerySet.contains() cannot be used on unsaved objects
        # should be raise
        self.assertRaises(ValueError, self.table.table_rows.contains, row)
        self.assertRaises(ValueError, TableRow.objects.contains, row)

        row = self.table.delete_row()
        self.assertIsInstance(row, TableRow)

        self.assertRaises(ValueError, self.table.table_rows.contains, row)
        self.assertRaises(ValueError, TableRow.objects.contains, row)

    def test_get_cell(self):
        self.__add_columns_to_table()
        self.__add_row_to_table()

        cell = self.table.get_cell('Age', 1)
        self.assertIsInstance(cell, CellValue)
        self.assertEqual(cell.table_column.column_name, 'Age')
        self.assertEqual(cell.table_row.id, 1)

        self.assertRaises(ColumnNotInTable, self.table.get_cell, column_name='Not a Column', row_index=1)
        self.assertRaises(CellDoesNotExist, self.table.get_cell, column_name='First Name', row_index=10000)
        self.assertRaises(ColumnNotInTable, self.table.get_cell, column_name='Not a Column', row_index=10000)

        self.assertRaises(ValueError, self.table.get_cell, column_name='First Name', row_index='22a')
        self.assertRaises(ValueError, self.table.get_cell, column_name='Not A Column', row_index='22a')

    def test_get_column_cells(self):
        self.__add_columns_to_table()
        self.__add_row_to_table()

        self.assertRaises(ColumnNotInTable, self.table.get_column_cells, column_name='Not a Field')

        column = self.table.get_column_cells('First Name')
        self.assertIsInstance(column, list)
        self.assertEqual(len(CellValue.objects.filter(table_column__column_name='First Name')), len(column))

        self.assertIsInstance(column[0], CellValue)

        for cell in column:
            self.assertEqual(cell.table_column.column_name, 'First Name')

    def test_get_row_cells(self):
        self.__add_columns_to_table()
        self.__add_row_to_table()

        self.assertRaises(RowNotInTable, self.table.get_row_cells, row_index=1000)

        # row must be in integer
        self.assertRaises(ValueError, self.table.get_row_cells, row_index='ld')

        row = self.table.get_row_cells(1)

        self.assertIsInstance(row, list)
        self.assertEqual(len(CellValue.objects.filter(table_row__id=1)), len(row))

    def test_get_cell_value(self):
        self.__add_columns_to_table()
        self.__add_row_to_table()

        row_cells = self.table.get_row_cells(1)
        self.assertIsInstance(row_cells, list)

        for cell in row_cells:
            data_type = cell.table_column.column_data_type
            if data_type == 'char' or data_type == 'textfield':
                value = cell.get_value()
                self.assertIsInstance(value, str)
            elif data_type == 'int':
                value = cell.get_value()
                if value:
                    self.assertIsInstance(value, int)
            elif data_type == 'float':
                value = cell.get_value()
                if value:
                    self.assertIsInstance(value, float)
            elif data_type == 'bool':
                value = cell.get_value()
                if value:
                    self.assertIsInstance(value, bool)
            elif data_type == 'datetime':
                value = cell.get_value()
                if value:
                    self.assertIsInstance(value, datetime.datetime)



