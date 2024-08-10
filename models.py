from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Date

Base = declarative_base()

class OrderDetail(Base):
    __tablename__ = 'OrderDetail'

    ID = Column(Integer, primary_key=True)
    OrderID = Column(Text)
    EmployeeID = Column(Text)
    ProductID = Column(Text)
    Quantity = Column(Integer)
    DateAdded = Column(Text)

class ProductUnit(Base):
    __tablename__ = 'ProductUnit'

    ID = Column(Integer, primary_key=True)
    ProductUnitCode = Column(Integer)
    ProductUnit = Column(Text)
    ProductUnitShort = Column(Text)

class StateNames(Base):
    __tablename__ = 'StateNames'

    ID = Column(Integer, primary_key=True)
    StateName = Column(Text)
    Abbreviation = Column(Text)

class Suppliers(Base):
    __tablename__ = 'Suppliers'

    ID = Column(Integer, primary_key=True)
    SupplierID = Column(Integer)
    SupplierName = Column(Text)
    SupplierAddress = Column(Text)
    SupplierCity = Column(Integer)
    SupplierState = Column(Integer)
    SupplierZipCode = Column(Text)
    ContactName1 = Column(Text)
    ContactPhone1 = Column(Text)
    ContactEmail1 = Column(Text)
    ContactName2 = Column(Text)
    ContactPhone2 = Column(Text)
    ContactEmail2 = Column(Text)
    Website = Column(Text)
    AccountNumber = Column(Integer)
    TaxID = Column(Integer)

class Orders(Base):
    __tablename__ = 'Orders'

    ID = Column(Integer, primary_key=True)
    MondayOrderID = Column(Integer)
    OrderDate = Column(Text)
    WorkDescription = Column(Text)
    WorkAddress = Column(Text)
    WorkState = Column(Text)
    WorkZipCode = Column(Integer)

class Inventory(Base):
    __tablename__ = 'Inventory'

    ID = Column(Integer, primary_key=True)
    ProductName = Column(Text)
    ProductDescription = Column(Text)
    productID = Column(Text)
    QuantityOnHand = Column(Integer)
    ProductUnit = Column(Text)
    ProductUnitCost = Column(Integer)
    SupplierID = Column(Integer)

class Employee(Base):
    __tablename__ = 'Employees'

    ID = Column(Integer, primary_key=True)
    EmployeeID = Column(Text)
    EmployeeName = Column(Text)
    EmployeeAddress = Column(Text)
    EmployeeCity = Column(Text)
    EmployeeState = Column(Text)
    EmployeeZipcode = Column(Text)
    EmployeePhone = Column(Text)
    EmployeeEmail = Column(Text)
    EmployeeActive = Column(Integer)
    DateOfHire = Column(Date)