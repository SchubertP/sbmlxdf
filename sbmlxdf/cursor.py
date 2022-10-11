"""ImportCursor tracks elements during Model.from_df()

So we can report errors during import of table data

Implemented according to Singleton pattern

Peter Schubert, 2022-07-25
"""


class Cursor:
    _instance = None
    component_type = None
    component_id = None
    parameter = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cursor, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_component_type(cls, component_type):
        cls.component_type = component_type
        cls.component_id = None
        cls.parameter = None

    @classmethod
    def set_component_id(cls, component_id):
        if cls.component_type is None:
            print('Cursor component type not defined')
            raise RuntimeError
        cls.component_id = component_id
        cls.parameter = None

    @classmethod
    def set_parameter(cls, parameter):
        if cls.component_type is None:
            print('Cursor component type not defined')
            raise RuntimeError
        if cls.component_id is None:
            print('Cursor component id not defined')
            raise RuntimeError
        cls.parameter = parameter

    @classmethod
    def get_component_info(cls):
        return {'type': cls.component_type, 'id': cls.component_id,
                'value': cls.parameter}
