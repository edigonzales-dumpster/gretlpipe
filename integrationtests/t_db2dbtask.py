import unittest
import sqlite3
import os.path
import sqlsteps_common


class TestDb2DbTask(unittest.TestCase):
    """
    Executes the integration tests for the SqlExecutor Gradle Task
    """


    def test_positiveSqlite2Postgres(self):
        """
        Test's that transferring rows from an sqlexecutor databse to a postgres database
        results in the correct number of rows transferred.
        """
        raise NotImplementedError()

        # todo implementieren....

    def test_relativePathConfiguration_Sqlite(self):
        """
        Test's that the *.grade configuration of the sql files
        can be relative to the location of the gradle project (aka the *.gradle file)
        """
        dbPath = "tmp/db2db/relativePathConfiguration.sqlite"

        conn = None
        try:
            conn = sqlsteps_common.connectToNewSqliteDb(dbPath)
            sqlsteps_common.prepareSrcAndDestTables(conn)

            sqlsteps_common.closeSqliteConnection(conn)

            res = os.system(
                "gradle -b /home/bjsvwjek/IdeaProjects/gretlpipe/integrationtests/db2db/sqlite/relativePathConfiguration.gradle relativePathConfiguration")

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
        dbPathA = "tmp/db2db/postitiveStatementChainA.sqlite"
        dbPathB = "tmp/db2db/postitiveStatementChainB.sqlite"

        connA = None
        connB = None
        try:
            connA = sqlsteps_common.connectToNewSqliteDb(dbPathA)
            connB = sqlsteps_common.connectToNewSqliteDb(dbPathB)

            srcRowCount = sqlsteps_common.prepareSrcAndDestTables(connA)
            self._statementChain_prepareDbB(connB)

            res = os.system(
                "gradle -b /home/bjsvwjek/IdeaProjects/gretlpipe/integrationtests/db2db/sqlite/statementChain.gradle bToA")

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
        dbPath = "tmp/db2db/invalidSrcConnection_TargetDb.sqlexecutor"
        connection = None

        try:
            connection = sqlsteps_common.connectToNewSqliteDb(dbPath)
            sqlsteps_common.closeSqliteConnection(connection)

            res = os.system(
                "gradle -b /home/bjsvwjek/IdeaProjects/gretlpipe/integrationtests/db2db/sqlexecutor/invalidSrcConnection.gradle invalidSrcConnection")

            sqlsteps_common.assertGradleBuildReturnValue(False, res, self)

        finally:
            sqlsteps_common.closeSqliteConnection(connection)


    def test_failsOnInvalidTargetConnection_Sqlite(self):
        """
        Test's if the return value from the gradle build is <> 0 when trying to
        connect to a non existant database file
        """
        dbPath = "tmp/db2db/invalidTargetConnection_SourceDb.sqlexecutor"
        connection = None

        try:
            connection = sqlsteps_common.connectToNewSqliteDb(dbPath)
            sqlsteps_common.closeSqliteConnection(connection)

            res = os.system(
                "gradle -b /home/bjsvwjek/IdeaProjects/gretlpipe/integrationtests/db2db/sqlexecutor/invalidTargetConnection.gradle invalidTargetConnection")

            sqlsteps_common.assertGradleBuildReturnValue(False, res, self)

        finally:
            sqlsteps_common.closeSqliteConnection(connection)


    def test_failsOnInvalidSql_Sqlite(self):
        """
        Test's that a invalid sql statement on a valid database fails the gradle build
        """
        dbPathSrc = "tmp/db2db/invalidSql_Source.sqlexecutor"
        dbPathDest = "tmp/db2db/invalidSql_Target.sqlexecutor"

        conn = None
        try:
            srcConn = sqlsteps_common.connectToNewSqliteDb(dbPathSrc)
            targetConn = sqlsteps_common.connectToNewSqliteDb(dbPathSrc)
            sqlsteps_common.prepareSrcAndDestTables(targetConn)

            sqlsteps_common.closeSqliteConnection(srcConn)
            sqlsteps_common.closeSqliteConnection(targetConn)

            res = os.system(
                "gradle -b /home/bjsvwjek/IdeaProjects/gretlpipe/integrationtests/db2db/sqlexecutor/invalidSql.gradle invalidSql")

            sqlsteps_common.assertGradleBuildReturnValue(False, res, self)

        finally:
            sqlsteps_common.closeSqliteConnection(srcConn)
            sqlsteps_common.closeSqliteConnection(targetConn)


if __name__ == '__main__':
    unittest.main()


def suite():
    tests = ['test_positiveStatementChain_Sqlite']
    return unittest.TestSuite(map(TestDb2DbTask, tests))