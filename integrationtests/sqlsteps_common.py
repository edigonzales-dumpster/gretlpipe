import sqlite3
import os.path

def assertGradleBuildReturnValue(expectSuccessfulBuild, buildReturnValue, owningTestCase):
    if expectSuccessfulBuild:
        owningTestCase.assertEqual(buildReturnValue, 0, "Gradle build must be succesful and return 0")
    else:
        owningTestCase.assertNotEqual(buildReturnValue, 0, "Gradle build must fail and return value <> 0")


        #todo sqlexecutor Tests auf diese Methode refactoren


def connectToNewSqliteDb(pathToDb):
    if os.path.exists(pathToDb):
        os.remove(pathToDb)

    dbconnection = sqlite3.connect(pathToDb)
    return dbconnection


def closeSqliteConnection(connection):
    if connection is not None:
        connection.close()


def prepareSrcAndDestTables(connection):

    cursor = connection.cursor()

    # create source table
    cursor.execute("""CREATE TABLE albums_src
                          (title text, artist text, release_date text,
                           publisher text, media_type text)
                       """)

    # insert multiple records using the more secure "?" method
    albums = [('Exodus', 'Andy Hunter', '7/9/2002',
               'Sparrow Records', 'CD'),
              ('Until We Have Faces', 'Red', '2/1/2011',
               'Essential Records', 'CD'),
              ('The End is Where We Begin', 'Thousand Foot Krutch',
               '4/17/2012', 'TFKmusic', 'CD'),
              ('The Good Life', 'Trip Lee', '4/10/2012',
               'Reach Records', 'CD')]

    cursor.executemany("INSERT INTO albums_src VALUES (?,?,?,?,?)",
                       albums)

    #create target table
    cursor.execute("""CREATE TABLE albums_dest
                          (title text, artist text, release_date text,
                           publisher text, media_type text)
                       """)

    connection.commit()

    return len(albums)