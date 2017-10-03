import unittest
import sqlite3
import os.path
import sqlsteps_common


class TestSqlExecutorTask(unittest.TestCase):
    """
    Executes the integration tests for the SqlExecutor Gradle Task
    """

    def test_positiveInsertFromSelect_Sqlite(self):
        """
        Test's that a correct "insert into select from" inserts the proper number of rows
        """
        dbPath = "tmp/sqlexecutor/insertFromSelect.sqlite"
        conn = None
        try:
            conn = sqlsteps_common.connectToNewSqliteDb(dbPath)

            expectedCount = sqlsteps_common.prepareSrcAndDestTables(conn)
            conn.close()

            res = sqlsteps_common.runGradle("sqlexecutor/sqlite/insertFromSelect.gradle", "sqlExecutor")

            conn = sqlite3.connect(dbPath)
            cursor = conn.cursor()

            cursor.execute("""select count(*) from albums_dest""")
            transferredCount = cursor.fetchone()[0]

            self.assertEqual(expectedCount, transferredCount, 'Rowcount in destination table must be equal to rowcount in source table')
            sqlsteps_common.assertGradleBuildReturnValue(True, res, self)

        finally:
            if conn is not None:
                conn.close()

    def test_relativePathConfiguration_Sqlite(self):
        """
        Test's that the *.grade configuration of the sql files
        can be relative to the location of the gradle project (aka the *.gradle file)
        """
        dbPath = "tmp/sqlexecutor/relativePathConfiguration.sqlite"

        conn = None
        try:
            conn = sqlsteps_common.connectToNewSqliteDb(dbPath)
            sqlsteps_common.prepareSrcAndDestTables(conn)
            conn.close()

            res = sqlsteps_common.runGradle("sqlexecutor/sqlite/relativePathConfiguration.gradle", "relativePathConfiguration")

            sqlsteps_common.assertGradleBuildReturnValue(True, res, self)

        finally:
            if conn is not None:
                conn.close()


    def test_positiveStatementChain_Sqlite(self):
        """
        Test's that a chain of statements executes properly and results in the correct
        number of inserts (corresponding to the last statement)
        1. statement: create the schema for the tables
        2. statement: fill the source table with rows
        3. statement: execute the "insert into select from" statement
        """
        dbPath = "tmp/sqlexecutor/postitiveStatementChain.sqlite"

        conn = None
        try:
            conn = sqlsteps_common.connectToNewSqliteDb(dbPath)
            conn.close()

            res = sqlsteps_common.runGradle("sqlexecutor/sqlite/statementChain.gradle", "insertInto")

            conn = sqlite3.connect(dbPath)

            srcCurs = conn.cursor()
            srcCurs.execute("""select count(*) from albums_src""")
            srcCount = srcCurs.fetchone()[0]

            destCurs = conn.cursor()
            destCurs.execute("""select count(*) from albums_dest""")
            destCount = destCurs.fetchone()[0]

            self.assertEqual(srcCount, destCount, "Rowcount in destination table must be equal to rowcount in source table")
            self.assertTrue(destCount > 0, "Rowcount in destination table must be greater than zero")
            sqlsteps_common.assertGradleBuildReturnValue(True, res, self)

        finally:
            if conn is not None:
                conn.close()


    def test_buildFailsOnInvalidConnection_Sqlite(self):
        """
        Test's if the return value from the gradle build is <> 0 when trying to
        connect to a non existant database file
        """
        res = sqlsteps_common.runGradle("sqlexecutor/sqlite/invalidConnection.gradle", "invalidConnection")

        sqlsteps_common.assertGradleBuildReturnValue(False, res, self)


    def test_failsOnInvalidSql_Sqlite(self):
        """
        Test's that a invalid sql statement on a valid database fails the gradle build
        """
        dbPath = "tmp/sqlexecutor/invalidSql.sqlite"

        conn = None
        try:
            conn = sqlsteps_common.connectToNewSqliteDb(dbPath)
            conn.close()

            res = sqlsteps_common.runGradle("sqlexecutor/sqlite/invalidSql.gradle", "invalidSql")

            sqlsteps_common.assertGradleBuildReturnValue(False, res, self)

        finally:
            if conn is not None:
                conn.close()


if __name__ == '__main__':
    unittest.main()