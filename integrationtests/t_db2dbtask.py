import unittest
import sqlite3
import os.path
import sqlsteps_common


class TestDb2DbTask(unittest.TestCase):
    """
    Executes the integration tests for the SqlExecutor Gradle Task
    """

    def test_relativePathConfiguration_Sqlite(self):
        """
        Test's that the *.grade configuration of the sql files
        can be relative to the location of the gradle project (aka the *.gradle file)
        """
        dbsDir = sqlsteps_common.absDir('tmp/db2db/relativePathConfiguration')

        conn = None
        try:
            conn = sqlsteps_common.connectToNewSqliteDb(dbsDir, 'db.sqlite')
            sqlsteps_common.prepareSrcAndDestTables(conn)

            sqlsteps_common.closeSqliteConnection(conn)

            res = sqlsteps_common.runGradle("db2db/sqlite/relativePathConfiguration.gradle", "relativePathConfiguration", dbsDir)

            sqlsteps_common.assertGradleBuildReturnValue(True, res, self)

        finally:
            sqlsteps_common.closeSqliteConnection(conn)



    def test_statementChain_Sqlite(self):
        """
        Test's that a chain of statements executes properly and results in the correct
        number of inserts (corresponding to the last statement)
        1. Statement transfers rows from a to b
        2. Statement transfers rows from b to a
        """
        dbsDir = sqlsteps_common.absDir('tmp/db2db/postitiveStatementChain')

        connA = None
        connB = None
        try:
            connA = sqlsteps_common.connectToNewSqliteDb(dbsDir, 'a.sqlite')
            connB = sqlsteps_common.connectToNewSqliteDb(dbsDir, 'b.sqlite')

            srcRowCount = sqlsteps_common.prepareSrcAndDestTables(connA)
            self._statementChain_prepareDbB(connB)

            res = sqlsteps_common.runGradle("db2db/sqlite/statementChain.gradle",  "bToA", dbsDir)

            cursor = connA.cursor()
            cursor.execute("""select count(*) from albums_dest""")

            destRowCount = cursor.fetchone()[0]

            self.assertEqual(srcRowCount, destRowCount, "Row count in table albums_src must be equal to row count in table albums_dest")
            self.assertGreater(destRowCount, 0, "Destination row count must be greater than zero")
            sqlsteps_common.assertGradleBuildReturnValue(True, res, self)


        finally:
            sqlsteps_common.closeSqliteConnection(connA)
            sqlsteps_common.closeSqliteConnection(connB)


    def _statementChain_prepareDbB(self, connToDbB):

        cursor = connToDbB.cursor()

        # create intermediate table
        cursor.execute("""CREATE TABLE albums_intermediate
                              (title text, artist text, release_date text,
                               publisher text, media_type text)""")

        connToDbB.commit()


    def test_failsOnInvalidSrcConnection_Sqlite(self):
        """
        Test's if the return value from the gradle build is <> 0 when trying to
        connect to a non existant database file
        """
        dbsDir = sqlsteps_common.absDir('tmp/db2db/invalidSrcConnection')
        connection = None

        try:
            connection = sqlsteps_common.connectToNewSqliteDb(dbsDir, 'db.sqlite')
            sqlsteps_common.closeSqliteConnection(connection)

            res = sqlsteps_common.runGradle("db2db/sqlite/invalidSrcConnection.gradle", "invalidSrcConnection", dbsDir)

            sqlsteps_common.assertGradleBuildReturnValue(False, res, self)

        finally:
            sqlsteps_common.closeSqliteConnection(connection)


    def test_failsOnInvalidTargetConnection_Sqlite(self):
        """
        Test's if the return value from the gradle build is <> 0 when trying to
        connect to a non existant database file
        """
        dbsDir = sqlsteps_common.absDir('tmp/db2db/invalidTargetConnection')
        connection = None

        try:
            connection = sqlsteps_common.connectToNewSqliteDb(dbsDir, 'db.sqlite')
            sqlsteps_common.closeSqliteConnection(connection)

            res = sqlsteps_common.runGradle("db2db/sqlite/invalidTargetConnection.gradle", "invalidTargetConnection", dbsDir)

            sqlsteps_common.assertGradleBuildReturnValue(False, res, self)

        finally:
            sqlsteps_common.closeSqliteConnection(connection)


    def test_failsOnInvalidSql_Sqlite(self):
        """
        Test's that a invalid sql statement on a valid database fails the gradle build
        """
        dbsDir = sqlsteps_common.absDir('tmp/db2db/invalidSql')

        srcConn = None
        targetConn = None
        try:
            srcConn = sqlsteps_common.connectToNewSqliteDb(dbsDir, 'source.sqlite')
            targetConn = sqlsteps_common.connectToNewSqliteDb(dbsDir, 'target.sqlite')
            sqlsteps_common.prepareSrcAndDestTables(targetConn)

            sqlsteps_common.closeSqliteConnection(srcConn)
            sqlsteps_common.closeSqliteConnection(targetConn)

            res = sqlsteps_common.runGradle("db2db/sqlite/invalidSql.gradle", "invalidSql", dbsDir)

            sqlsteps_common.assertGradleBuildReturnValue(False, res, self)

        finally:
            sqlsteps_common.closeSqliteConnection(srcConn)
            sqlsteps_common.closeSqliteConnection(targetConn)


if __name__ == '__main__':
    unittest.main()


def suite():
    tests = ['test_positiveStatementChain_Sqlite']
    return unittest.TestSuite(map(TestDb2DbTask, tests))