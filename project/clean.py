
import csv


ATTRIBUTES = [
    ('Status', 'Status Text'),
    ('Category', 'Category Text'),
    ('Problem', 'Problem Text'),
    ('Department', 'Department Text'),
    ('Division', 'Division Text'),
    ('Main Task', 'Main Task Text'),
    ('Problem', 'Problem Text'),
    ('Assigned Crew', 'Assigned Crew Text'),
    ('Route (Geographic)', 'Route (Geographic) Text'),
    ('Task', 'Task Text'),
    ('Resource Type', 'Resource Type Text'),
    ('Resource', 'Resource Text'),
    ('Time Cost', 'Time Cost Text'),
    ('Unit of Measure', 'Unit of Measure Text'),
]

def clean_attribute(dict_reader, code_field, text_field):
    data_gen = zip(dict_reader.get())


def clean_attributes(filepath):
    with open(filepath, mode='r') as f:
        dict_reader = csv.DictReader(f)
        for attr_code, attr_text in ATTRIBUTES:
            data = clean_attribute(dict_reader, attr_code, attr_text)

