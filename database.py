# SQLite3 interface
# Project: CISP71 Fall/2020
#  Author: TuttiPazzo

import sqlite3

class database:
    def __init__(self, tName, createStmt, dbFileName):
        """
        Initialize SQLlite3 DB and create the table if it does not exist.
        """
        if( tName != "" ):
            self.tableName = tName
        else:
            raise ValueError("Table Name must be provided.")

        if( createStmt != "" ):
            self.createStmt = createStmt
        else:
            raise ValueError("Table create statement must be provided.")

        if( dbFileName != "" ):
            self.dbfile = dbFileName
        else:
            raise ValueError("SQLite DB file must be provided.")

        try:
            conn = sqlite3.connect(self.dbfile)
        except sqlite3.Error as e:
            print("ERROR: connecting to \"{0}\": {1}".format(self.dbfile,e))
        finally:
            if (conn):
                conn.close()

        self.columns = []

        self.__createTable()
        self.__populateColumnInfo()

    def __createTable(self):
        """
        Use SQL to create the table if it does not exist.
        """
        try:
            conn = sqlite3.connect(self.dbfile)
            cursor = conn.cursor()
#            createStmt = """CREATE TABLE IF NOT EXISTS {0} (
#                            fName   TEXT,
#                            lName   TEXT,
#                            address TEXT,
#                            city    TEXT,
#                            state   TEXT,
#                            zipCode integer);""".format(self.tableName)
            cursor.execute(self.createStmt)
            conn.commit()
            cursor.close()
        except sqlite3.Error as e:
            print("ERROR: connecting to \"{0}\": {1}".format(self.dbfile,e))
        finally:
            if (conn):
                conn.close()

    def __populateColumnInfo(self):
        """
        Create a dictionary of columns names and respective types.
        """
        try:
            conn = sqlite3.connect(self.dbfile)
            cursor = conn.cursor()

            cursor.execute("PRAGMA TABLE_INFO({0})".format(self.tableName))
            data = cursor.fetchall()
#            print("Type: {0}\nData: {1}".format(type(data),data))
            # The column information is returned as a list of list.
            # The column indexes matches with the table so all we want
            # save os the column type
            for row in data:
                self.columns.insert(row[0],row[2].upper())
            cursor.close()
        except sqlite3.Error as e:
            print("ERROR: connecting to \"{0}\": {1}".format(self.dbfile,e))
        finally:
            if (conn):
                conn.close()

    def __getColumnNames(self):
        """
        Get the column Names for building sql where clauses
        """
        colNames=""
        try:
            conn = sqlite3.connect(self.dbfile)
            cursor = conn.cursor()
            cursor = cursor.execute("SELECT * from {0}".format(self.tableName))
            conn.commit()
            cursor.close()
        except sqlite3.Error as e:
            print("ERROR: connecting/retrieving column Names \"{0}\": {1}".format(self.dbfile,e))
        except ValueError as e:
            print("ERROR: retrieving column names:", e)
        else:
            colNames = cursor.description
        finally:
            if (conn):
                conn.close()

        return colNames

    def __normalizeColData(self,colData):
        newColData = []
        try:
            for i in range(len(colData)):
                if self.columns[i] ==  "TEXT":
                    newColData.insert(i,str("\"{0}\"".format(colData[i])))
                else:
                    newColData.insert(i,colData[i])
        except ValueError as e:
            print("ERROR:", e)
        except IndexError as e:
            print("ERROR:", e)

        return newColData

    def add(self, rowData):
        """
        Insert row data into table.
        """
        newData = []
        try:
            conn = sqlite3.connect(self.dbfile)
            cursor = conn.cursor()

            # Let's build up the row data statement values to be inserted
            addStm="INSERT INTO {0} values (".format(self.tableName)
            aSize = len(rowData)
            newData = self.__normalizeColData(rowData)
            for i in range(aSize):
                if( i == (aSize - 1) ):
                    addStm = addStm + "{0})".format(newData[i])
                else:
                    addStm = addStm + "{0},".format(newData[i])

            cursor = cursor.execute(addStm)
            conn.commit()
            cursor.close()
        except sqlite3.Error as e:
            print("ERROR: connecting/adding RowData \"{0}\": {1}".format(self.dbfile,e))
        except ValueError as e:
            print("ERROR: row data: (\"", rowData, "\"):", e)
        except IndexError as e:
            print("ERROR: indexing row data: (\"", rowData, "\"):", e)
        finally:
            if (conn):
                conn.close()

    def delete(self, rowData):
        """
        Delete the row corresponding to the given rowdata.  This method
        will compare every value in the row in the select statement.
        """
        colNames=""
        try:
            colNames = self.__getColumnNames()
        except ValueError as e:
            print("ERROR: retrieving column name data:", e)
            return

        try:
            conn = sqlite3.connect(self.dbfile)
            cursor = conn.cursor()

            # Let's build up the row data statement values to be inserted
            deleteStm="DELETE FROM {0} WHERE (".format(self.tableName)
            aSize = len(rowData)
            for i in range(aSize):
                if( i == (aSize - 1) ):
                    deleteStm = deleteStm + "{0} = \"{1}\")".format(colNames[i][0],rowData[i])
                else:
                    deleteStm = deleteStm + "{0} = \"{1}\" AND ".format(colNames[i][0],rowData[i])

            cursor = cursor.execute(deleteStm)
            conn.commit()
            cursor.close()
        except sqlite3.Error as e:
             print("ERROR: connecting/deleting row data \"{0}\": {1}".format(self.dbfile,e))
        except ValueError as e:
            print("ERROR: deleting row data: (\"", rowData, "\"):", e)
        except IndexError as e:
            print("ERROR: indexing row data: (\"", rowData, "\"):", e)
        finally:
            if (conn):
                conn.close()

    def update(self, curRowData, newRowData):
        """
        Delete the row corresponding to the given rowdata.  This method
        will compare every value in the row in the select statement.
        """
        colNames=""
        try:
            colNames = self.__getColumnNames()
        except ValueError as e:
            print("ERROR: retrieving column name data:", e)
            return

        try:
            conn = sqlite3.connect(self.dbfile)
            cursor = conn.cursor()

            # Let's build up the SET part of the Update st
            updateStm="UPDATE {0} SET ".format(self.tableName)
            aSize = len(curRowData)
            for i in range(aSize):            
                if( i == (aSize - 1) ):
                    updateStm = updateStm + "{0} = \"{1}\" WHERE (".format(colNames[i][0],newRowData[i])
                else:
                    updateStm = updateStm + "{0} = \"{1}\", ".format(colNames[i][0],newRowData[i])

            # Let's build up the WHERE part of the Update statement
            aSize=len(curRowData)
            for i in range(aSize):
                if( i == (aSize - 1) ):
                    updateStm = updateStm + "{0} = \"{1}\")".format(colNames[i][0],curRowData[i])
                else:
                    updateStm = updateStm + "{0} = \"{1}\" AND ".format(colNames[i][0],curRowData[i])

            cursor = cursor.execute(updateStm)
            conn.commit()
            cursor.close()
        except sqlite3.Error as e:
            print("ERROR: connecting/updating row data \"{0}\": {1}".format(self.dbfile,e))
        except ValueError as e:
            print("ERROR: updating row data:", e)
        except IndexError as e:
            print("ERROR: indexing row data:", e)
        finally:
            if (conn):
                conn.close()

    def getAllRows(self):
        """
        Fetch all rows from the table
        """
        records = ""
        try:
            conn = sqlite3.connect(self.dbfile)
            cursor = conn.cursor()
            cursor = cursor.execute("SELECT * FROM {0}".format(self.tableName))
            records = cursor.fetchall()
            cursor.close()
        except sqlite3.Error as e:
            print("ERROR: connecting/fecthing row data:".format(e))
        finally:
            if (conn):
                conn.close()

        return records
