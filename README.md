# Django-Dynamic-Table



### Overview

"Django-Dynamic-Table" is a Django app that provides a flexible and dynamic approach to managing tables in a Django project. This app allows you to create tables with dynamic columns and rows, giving you fine-grained control over the structure and manipulation of tabular data.



### Table of Contents

- Overview
- Features
- Installation
- Usage
  - Creating a Dynamic Table
  - Adding Columns
  - Adding Rows
  - Querying and Manipulating Data
- Testing
- Contributing
- License
- Acknowledgments

### Features

- **Dynamic Tables:** Create tables with a flexible structure, allowing for dynamic addition and removal of columns and rows.
- **Column Types:** Support for various data types, including Char, Int, Float, Bool, TextField, and Date.
- **Table Management:** Easily manage tables, including adding, deleting, and querying columns and rows.
- **Bulk Operations:** Perform bulk operations such as adding multiple columns or rows in a single operation.
- **Data Validation:** Validate and enforce data types for table cells to maintain data integrity.
- **Cell Values:** Each cell in the table can hold values of different data types as specified in the column they belong to,
- **Error Handling:** Comprehensive error handling for common scenarios, such as unsupported data types or duplicate columns.



### Installation

1. Install the package using pip:

   ```bash
   pip install django-dynamic-table
   ```

2. Add "dynamic_table" to your `INSTALLED_APPS` in your Django project settings:

   ```python
   INSTALLED_APPS = [
       # ...
       'django_dynamic_table',
       # ...
   ]
   ```

3. Run migrations to create the necessary database tables:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```



### Usage

#### Creating a Dynamic Table

To create a new dynamic table, you can use the Django admin interface or programmatically in your Django application code:

```python
from django_dynamic_table.models import DynamicTable

# Create a new dynamic table
my_table = DynamicTable.objects.create(
    table_name='MyDynamicTable',
    table_description='Description of the dynamic table.'
)
```



#### Adding Columns

You can dynamically add columns to the table using the provided methods:

```python
# Add a single column
column = my_table.add_column(column_name='Column1', data_type='char')

# Add multiple columns in bulk
columns = my_table.bulk_add_columns(
    column_names=['Column2', 'Column3'],
    data_types=['int', 'float']
)
```

### Adding Rows

You can add rows to the table with values for each column:

```python
# Add a single row
single_row = {'Column1': 'Value1', 'Column2': 42, 'Column3': 3.14}
my_table.add_row(value=row_values)

# Add multiple rows in bulk
rows_data = [
    {'Column1': 'ValueA', 'Column2': 10, 'Column3': 2.71},
    {'Column1': 'ValueB', 'Column2': 20, 'Column3': 1.618},
]
multiple_rows = my_table.bulk_add_rows(values=rows_data)
```

### Querying and Manipulating Data

You can query and manipulate data in the dynamic table using various methods provided by the app. Refer to the app's documentation for more details on available methods.

```python
# Retrieve all tables
all_tables = DynamicTable.objects.all()

# Retrieve a specific table by name:
specific_table = DynamicTable.objects.get(table_name='YourTableName')


# Retrieve all columns of a table
table_columns = specific_table.table_columns.all()

# Retrieve all the cells that belongs to a specific column of a table
specific_table_column = specific_table.get_column_cells(column_name)


# Retrieve all rows of a table
table_rows: list = specific_table.table_rows.all()

# Retrieve all the cells that belongs to a specific row
specific_table_row: list = specific_table.get_row_cells(1) 


# Retrieving a specific cell in both row and column
cell = specific_table.get_cell(column_name, 1) # column name, row index


# Retrieving formatted value from cell
# DO NOT accesss the value directly from the attribute
# using the function will format the value to the column data type
formatted_value = cell.get_value()


```

#### **Deleting  from table**

```python
# Delete specific column from the table
deleted_column = specific_table.delete_column(column_name)

# Delete specific row from the table
deleted_row = specific_table.delete_row(1)

# last row from the table
deleted_last_row = specific_table.delete_row()
```



#### Additional Features

```python
# Get table info: no of rows and columns
table_info: dict = specific_table.table_info()

# check if a column is in the table
specific_table.is_column(column_name)

# check if the table is empty, that is, no column and rows 
# has been added yet
specific_table.is_empty()

# check for list of supported data type
specific_table.get_supported_data_types()

# check if a data type is supported
specific_table.data_type_is_supported('file')
specific_table.data_type_is_supported(['file', 'char', 'image', 'textField'])
```



## Contributing

We welcome contributions to this app! If you have any suggestions, bug reports, or pull requests, please feel free to create an issue or submit a pull request on the GitHub repository

## License

This project is licensed under the MIT License 

## Acknowledgments

- The motivation behind developing this app stemmed from my necessity to establish and handle dynamic tables in Django projects. This was prompted by the absence of a native Django solution, and existing alternatives often required resorting to various workarounds and hacks.



**Contact:**

For any questions or feedback, please feel free to contact the developer at:

senai.nkop@gmail.com
