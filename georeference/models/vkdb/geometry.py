# -*- coding: utf-8 -*-
'''
Copyright (c) 2014 Jacob Mendt

Created on Jul 2, 2015

@author: mendt
'''
from sqlalchemy import func
from sqlalchemy.types import UserDefinedType

class Geometry(UserDefinedType):

    def get_col_spec(self):
        return "GEOMETRY"
    
    def bind_expression(self, bindvalue, srid=-1):
        return func.ST_GeomFromText(bindvalue,  srid, type_=self)
    
    def column_expression(self, col):
        return func.ST_AsText(col, type_=self)