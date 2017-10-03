import sqlite3
import os.path
import tempfile

def assertGradleBuildReturnValue(expectSuccessfulBuild, buildReturnValue, owningTestCase):
    if expectSuccessfulBuild:
        owningTestCase.assertEqual(buildReturnValue, 0, "Gradle build must be succesful and return 0")
    else:
        owningTestCase.assertNotEqual(buildReturnValue, 0, "Gradle build must fail and return value <> 0")


        #todo sqlexecutor Tests auf diese Methode refactoren

def uniqueDbPath():
    dbDir = tempfile.mkdtemp()
    return os.path.join(dbDir, 'testdb.db')

def absDir(relDirPath):
    pySkriptPath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(pySkriptPath, relDirPath)


def connectToNewSqliteDb(dbsDir, dbName):

    if not os.path.exists(dbsDir):
        os.makedirs(dbsDir)

    pathToDb = os.path.join(dbsDir, dbName)

    if os.path.exists(pathToDb):
        os.remove(pathToDb)

    dbconnection = sqlite3.connect(pathToDb)
    return dbconnection

def connectToExistingSqliteDb(dbsDir, dbName):
    pathToDb = os.path.join(dbsDir, dbName)

    if not os.path.exists(pathToDb):
        raise 'Database does not exist: ' + pathToDb

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

def runGradle(relPathToBuildFile, buildCommand, dbsDir):
    pySkriptPath = os.path.dirname(os.path.abspath(__file__))
    buildFilePath = os.path.join(pySkriptPath, relPathToBuildFile)
    initFilePath = os.path.join(pySkriptPath, "init.gradle")
    gradleCall = "gradle -I " + initFilePath + " -b " + buildFilePath + " -P dbsDir=" + dbsDir + " " + buildCommand

    return os.system(gradleCall)