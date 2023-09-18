import re
import pprint
from typing import List, Dict, Optional
import pandas as pd

import yaml_io

class SpreadsheetFormat:
    """Attributes of Register Block"""
    def __init__(self):
        self.block_name = {
            'cell_location': {
                'row': 0,
                'col': 1
            }
        }

        self.byte_size = {
            'cell_location': {
                'row': 1,
                'col': 1
            }
        }

        self.attributes = [
            {
                'name': 'register_name',
                'cell_location': {
                    'row': 3,
                    'col': 1
                }
            },
            {
                'name': 'offset_address',
                'cell_location': {
                    'row': 3,
                    'col': 2
                }
            },
            {
                'name': 'bit_field_name',
                'cell_location': {
                    'row': 3,
                    'col': 3
                }
            },
            {
                'name': 'bit_assignment',
                'cell_location': {
                    'row': 3,
                    'col': 4
                }
            },
            {
                'name': 'lsb',
                'cell_location': {
                    'row': 3,
                    'col': 5
                }
            },
            {
                'name': 'width',
                'cell_location': {
                    'row': 3,
                    'col': 6
                }
            },
            {
                'name': 'bit_field_type',
                'cell_location': {
                    'row': 3,
                    'col': 7
                }
            },
            {
                'name': 'initial_value',
                'cell_location': {
                    'row': 3,
                    'col': 8
                }
            },
            {
                'name': 'reference',
                'cell_location': {
                    'row': 3,
                    'col': 9
                }
            },
            {
                'name': 'comment',
                'cell_location': {
                    'row': 3,
                    'col': 10
                }
            },
        ]

    def get_names(self) -> List:
        return [attr['name'] for attr in self.attributes]

    def get_usecols(self) -> List:
        return [attr['cell_location']['col'] for attr in self.attributes]

    def get_skiprows(self) -> List:
        attr_row = self.attributes[0]['cell_location']['row']
        for attr in self.attributes:
            assert attr_row == attr['cell_location']['row'], 'Rows set in attributes do not match'
        return list(range(attr_row))

class RegisterMap:
    """
    Register Map Specifications
    Reference: https://github.com/rggen/rggen/wiki/Register-Map-Specifications
    """
    register_block = {
        'name': '',
        'byte_size': 0
    }

class Register:
    """
    Describe attributes of a register here
    E.G. register name, offset_address
    """
    def __init__(self, name: str, offset_address: str):
        self.name = name
        self.set_offset_address(offset_address)
        self.bit_field = []

    def set_offset_address(self, offset_address):
        pattern = r"(0x|[0-9]+'h)([a-fA-F0-9_]+)"
        match = re.match(pattern, offset_address)
        if match:
            self.offset_address = match.group(2).replace('_', '')
        else:
            raise ValueError(f'offse_address of {self.name} is None or {offset_address} is invalid description')

    def dict(self) -> Dict[str, int|str]:
        "Return register in Dict format"
        return {
            'name': self.name,
            'offset_address': self.offset_address,
            'bit_field': [bf.dict() for bf in self.bit_field]
        }

    def append_bit_field(
        self, name: str,
        bit_assignment: Optional[str],
        lsb: int,
        width: int,
        bit_field_type: str,
        initial_value: int,
        comment: str
    ):
        "Append list of bit_field in Register class"
        self.bit_field.append(
            BitField(name, bit_assignment, lsb, width, bit_field_type, initial_value, comment)
        )

class BitField:
    """
    Describe attributes of a bit field here
    E.G. bit field name, bit bit_assignment
    """
    def __init__(
        self,
        name: str,
        bit_assignment: str,
        lsb: int,
        width: int,
        bit_field_type: str,
        initial_value: int,
        comment: str
    ):
        self.name = name
        # self.bit_assignment = {
        #     'lsb': lsb,
        #     'width': width
        # }
        self.set_bit_assignment(bit_assignment)
        self.bit_field_type = bit_field_type
        self.initial_value = initial_value
        self.comment = comment

    def set_bit_assignment(self, bit_assignment):
        single_bit_pattern = r"\[?([0-9+])\]?"
        multi_bits_pattern = r"\[?([0-9]+):([0-9]+)\]?"
        single_match = re.match(single_bit_pattern, bit_assignment)
        multi_match = re.match(multi_bits_pattern, bit_assignment)
        if multi_match:
            assert multi_match.group(1) >= multi_match.group(2), f'{bit_assignment} is not "downto" description'
            self.bit_assignment = {
                'lsb': multi_match.group(2),
                'width': int(multi_match.group(1)) - int(multi_match.group(2)) + 1
            }
        elif single_match:
            self.bit_assignment = {
                'lsb': single_match.group(1),
                'width': 1
            }
        else:
            raise ValueError(f'bit_assignment of {self.name} is None or {bit_assignment} is invalid description')

    def dict(self) -> Dict[str, int|str]:
        "Return bit_field in Dict format"
        return {
            'name': self.name,
            'bit_assignment': self.bit_assignment,
            'bit_field_type': self.bit_field_type,
            'initial_value': self.initial_value,
            'comment': self.comment
        }

def main():
    """
    Describe attributes of a register block here
    E.G. block name, size
    """
    sheet_format = SpreadsheetFormat()

    df = pd.read_excel(
        'sample.xlsx',
        sheet_name='block_0',
        usecols=sheet_format.get_usecols(),
        names=sheet_format.get_names(),
        # header=None,
        skiprows=sheet_format.get_skiprows()
    )
    print(df)

    registers = []

    register = None
    for label in range(len(df)):
        item = df.loc[label, :]
        if isinstance(item['register_name'], str):
            register = Register(item['register_name'], item['offset_address'])
            registers.append(register)

        register.append_bit_field(
            item['bit_field_name'],
            item['bit_assignment'],
            item['lsb'],
            item['width'],
            item['bit_field_type'],
            item['initial_value'],
            item['comment']
        )

    for reg in registers:
        print(f'register_name={reg.name}')
        pprint.pprint(reg.dict())

    print(yaml_io.load())
