from unittest import TestCase
from portality import schema
from copy import deepcopy

# set this to true if you want the tests to fail, so you can see the actual errors
fail = False

_complete = {
    "bools" : ["mybool1", "mybool2"],
    "fields" : ["field1", "field2"],
    "lists" : ["list1", "list2"],
    "objects" : ["obj1", "obj2"],
    
    "list_entries" : {
        "list1" : {
            "bools" : ["listbool"],
            "fields" : ["listfield"],
            "lists" : ["listlist"],
            "objects" : ["listobj"],
            
            "object_entries" : {
                "listobj" : {
                    "fields" : ["objfield1", "objfield2"]
                }
            }
        }
    },
    
    "object_entries" : {
        "obj1" : {
            "bools" : ["objbool"],
            "fields" : ["objfield"],
            "lists" : ["objlist"],
            "objects" : ["objobj"],
            
            "object_entries" : {
                "objobj" : {
                    "fields" : ["objfield3", "objfield4"]
                }
            }
        },
        "obj2" : {
            "fields" : ["objfield5", "objfield6"]
        }
    }
}

class TestSchema(TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_01_complete_correct(self):
        correct = {
            "mybool1" : True,
            "mybool2" : False,
            "field1" : "stuff",
            "field2" : "other stuff",
            "list1" : [{
                "listbool" : True,
                "listfield" : "more stuff",
                "listlist" : ["plain string", "another string"],
                "listobj" : {
                    "objfield1" : "object property 1",
                    "objfield2" : "object property 2"
                }
            }],
            "list2" : ["string", u"unicode"],
            "obj1" : {
                "objbool" : False,
                "objfield" : "a field",
                "objlist" : [],
                "objobj" : {
                    "objfield3" : "3",
                    "objfield4" : "4"
                }
            },
            "obj2" : {
                "objfield5" : 5,
                "objfield6" : 6
            }
        }
        schema.validate(correct, _complete)
    
    def test_02_complete_bool_error(self):
        wrong = {
            "mybool1" : "wibble",
            "mybool2" : False,
            "field1" : "stuff",
            "field2" : "other stuff",
            "list1" : [{
                "listbool" : True,
                "listfield" : "more stuff",
                "listlist" : ["plain string", "another string"],
                "listobj" : {
                    "objfield1" : "object property 1",
                    "objfield2" : "object property 2"
                }
            }],
            "list2" : ["string", u"unicode"],
            "obj1" : {
                "objbool" : False,
                "objfield" : "a field",
                "objlist" : [],
                "objobj" : {
                    "objfield3" : "3",
                    "objfield4" : "4"
                }
            },
            "obj2" : {
                "objfield5" : 5,
                "objfield6" : 6
            }
        }
        with self.assertRaises(schema.ObjectSchemaValidationError):
            schema.validate(wrong, _complete)
        if fail:
            schema.validate(wrong, _complete)
    
    def test_03_complete_field_error(self):
        wrong = {
            "mybool1" : True,
            "mybool2" : False,
            "field1" : [],
            "field2" : "other stuff",
            "list1" : [{
                "listbool" : True,
                "listfield" : "more stuff",
                "listlist" : ["plain string", "another string"],
                "listobj" : {
                    "objfield1" : "object property 1",
                    "objfield2" : "object property 2"
                }
            }],
            "list2" : ["string", u"unicode"],
            "obj1" : {
                "objbool" : False,
                "objfield" : "a field",
                "objlist" : [],
                "objobj" : {
                    "objfield3" : "3",
                    "objfield4" : "4"
                }
            },
            "obj2" : {
                "objfield5" : 5,
                "objfield6" : 6
            }
        }
        with self.assertRaises(schema.ObjectSchemaValidationError):
            schema.validate(wrong, _complete)
        if fail:
            schema.validate(wrong, _complete)
    
    def test_04_complete_list_error(self):
        wrong = {
            "mybool1" : True,
            "mybool2" : False,
            "field1" : "stuff",
            "field2" : "other stuff",
            "list1" : "not a list",
            "list2" : ["string", u"unicode"],
            "obj1" : {
                "objbool" : False,
                "objfield" : "a field",
                "objlist" : [],
                "objobj" : {
                    "objfield3" : "3",
                    "objfield4" : "4"
                }
            },
            "obj2" : {
                "objfield5" : 5,
                "objfield6" : 6
            }
        }
        with self.assertRaises(schema.ObjectSchemaValidationError):
            schema.validate(wrong, _complete)
        if fail:
            schema.validate(wrong, _complete)
    
    def test_05_complete_obj_error(self):
        wrong = {
            "mybool1" : True,
            "mybool2" : False,
            "field1" : "stuff",
            "field2" : "other stuff",
            "list1" : [{
                "listbool" : True,
                "listfield" : "more stuff",
                "listlist" : ["plain string", "another string"],
                "listobj" : {
                    "objfield1" : "object property 1",
                    "objfield2" : "object property 2"
                }
            }],
            "list2" : ["string", u"unicode"],
            "obj1" : [],
            "obj2" : {
                "objfield5" : 5,
                "objfield6" : 6
            }
        }
        with self.assertRaises(schema.ObjectSchemaValidationError):
            schema.validate(wrong, _complete)
        if fail:
            schema.validate(wrong, _complete)
    
    def test_06_complete_inside_list_error(self):
        wrong = {
            "mybool1" : True,
            "mybool2" : False,
            "field1" : "stuff",
            "field2" : "other stuff",
            "list1" : [{
                "listbool" : True,
                "listfield" : "more stuff",
                "listlist" : "not a list",
                "listobj" : {
                    "objfield1" : "object property 1",
                    "objfield2" : "object property 2"
                }
            }],
            "list2" : ["string", u"unicode"],
            "obj1" : {
                "objbool" : False,
                "objfield" : "a field",
                "objlist" : [],
                "objobj" : {
                    "objfield3" : "3",
                    "objfield4" : "4"
                }
            },
            "obj2" : {
                "objfield5" : 5,
                "objfield6" : 6
            }
        }
        with self.assertRaises(schema.ObjectSchemaValidationError):
            schema.validate(wrong, _complete)
        if fail:
            schema.validate(wrong, _complete)
    
    def test_07_complete_inside_obj_error(self):
        wrong = {
            "mybool1" : True,
            "mybool2" : False,
            "field1" : "stuff",
            "field2" : "other stuff",
            "list1" : [{
                "listbool" : True,
                "listfield" : "more stuff",
                "listlist" : ["plain string", "another string"],
                "listobj" : {
                    "objfield1" : "object property 1",
                    "objfield2" : "object property 2"
                }
            }],
            "list2" : ["string", u"unicode"],
            "obj1" : {
                "objbool" : "not a bool",
                "objfield" : "a field",
                "objlist" : [],
                "objobj" : {
                    "objfield3" : "3",
                    "objfield4" : "4"
                }
            },
            "obj2" : {
                "objfield5" : 5,
                "objfield6" : 6
            }
        }
        with self.assertRaises(schema.ObjectSchemaValidationError):
            schema.validate(wrong, _complete)
        if fail:
            schema.validate(wrong, _complete)
    
    def test_08_complete_extra_field(self):
        wrong = {
            "not_allowed" : "I shouldn't be here",
            "mybool1" : True,
            "mybool2" : False,
            "field1" : "stuff",
            "field2" : "other stuff",
            "list1" : [{
                "listbool" : True,
                "listfield" : "more stuff",
                "listlist" : ["plain string", "another string"],
                "listobj" : {
                    "objfield1" : "object property 1",
                    "objfield2" : "object property 2"
                }
            }],
            "list2" : ["string", u"unicode"],
            "obj1" : {
                "objbool" : False,
                "objfield" : "a field",
                "objlist" : [],
                "objobj" : {
                    "objfield3" : "3",
                    "objfield4" : "4"
                }
            },
            "obj2" : {
                "objfield5" : 5,
                "objfield6" : 6
            }
        }
        with self.assertRaises(schema.ObjectSchemaValidationError):
            schema.validate(wrong, _complete)
        if fail:
            schema.validate(wrong, _complete)
    
    def test_09_complete_default_list_error(self):
        wrong = {
            "mybool1" : True,
            "mybool2" : False,
            "field1" : "stuff",
            "field2" : "other stuff",
            "list1" : [{
                "listbool" : True,
                "listfield" : "more stuff",
                "listlist" : [{}, []],
                "listobj" : {
                    "objfield1" : "object property 1",
                    "objfield2" : "object property 2"
                }
            }],
            "list2" : ["string", u"unicode"],
            "obj1" : {
                "objbool" : False,
                "objfield" : "a field",
                "objlist" : [],
                "objobj" : {
                    "objfield3" : "3",
                    "objfield4" : "4"
                }
            },
            "obj2" : {
                "objfield5" : 5,
                "objfield6" : 6
            }
        }
        with self.assertRaises(schema.ObjectSchemaValidationError):
            schema.validate(wrong, _complete)
        if fail:
            schema.validate(wrong, _complete)
    
    def test_10_incomplete_error(self):
        correct = {
            "mybool1" : True,
            "mybool2" : False,
            "field1" : "stuff",
            "field2" : "other stuff",
            "list1" : [{
                "listbool" : True,
                "listfield" : "more stuff",
                "listlist" : ["plain string", "another string"],
                "listobj" : {
                    "objfield1" : "object property 1",
                    "objfield2" : "object property 2"
                }
            }],
            "list2" : ["string", u"unicode"],
            "obj1" : {
                "objbool" : False,
                "objfield" : "a field",
                "objlist" : [],
                "objobj" : {
                    "objfield3" : "3",
                    "objfield4" : "4"
                }
            },
            "obj2" : {
                "objfield5" : 5,
                "objfield6" : 6
            }
        }
        
        incomplete = deepcopy(_complete)
        del incomplete["object_entries"]["obj1"]
        
        with self.assertRaises(schema.ObjectSchemaValidationError):
            schema.validate(correct, incomplete)
        if fail:
            schema.validate(correct, incomplete)
    
    
    
    
