/*
Raw jenkins pipeline to deploy a tested gretl.jar to production.
The jar ist autotested with the "inline" unittests that are run
in the gradle build stage and with integration tests that are run
in the integration test stage.
Many of the environment variables are used as configuration in
the gradle build or in the integration test code.

todo:
- Migrate the integration tests to gradle/junit to use the same
db drivers for test staging and testing and to be based throughout
on the same tools
- Rethink the versioning as it is overly complex for it's limited benefit
- Refactor the pipeline to result in docker image for the gretl runtime
 and finally in the released runtime with job configuration

 questions:
 - Stages snapshot jar and integration test share the same environment variables.
 Can these be declared only once?
 - Stages integration test and release jar share the same code (dir block).
 How can the block be reused in declarative syntax?
 - The workflow to set version and jar url in init.gradle is a bit "hacky".
 Better alternatives?
 - How to add simple if statements in declarative pipe (for AVOID_PROD_PUBLICATION)?
*/
pipeline {
    agent any
    parameters {
        string(name: 'PUBLISH_USER_PASS', description: 'What is the publish user and password (Write access for the AIO Maven Repository)?')
        string(name: 'GRETL_VERSION_NUM', description: 'What Version number should be deployed? Example: 1.0.2')
        string(name: 'AVOID_PROD_PUBLICATION', defaultValue: 'yes', description: 'Any non empty string causes the pipeline to fail and stop before the production publication')
    }
    environment{
        GRADLE_HOME = '/opt/gradle/gradle-3.5.1/bin/'
        GRETL_JAR_USER = "${params.PUBLISH_USER_PASS}"
        GRETL_JAR_PASS = "${params.PUBLISH_USER_PASS}"
        GRETL_JAR_BASEURL = 'https://artifactory.verw.rootso.org/artifactory/repo-agi-local'
        GRETL_VERSION_NUMBER = "${params.GRETL_VERSION_NUM}"
    }
    stages {
        stage('Gradle Build') {
            steps {
                git 'https://github.com/uncoyote/gretlv1.git'

                // Run the gradle build
                sh GRADLE_HOME + "gradle build"
            }
        }
        stage('Snapshot Jar') {
            environment {
                GRETL_VERSION = "$GRETL_VERSION_NUMBER" + '-SNAPSHOT'
                GRETL_JAR_URL = "$GRETL_JAR_BASEURL" + '-snapshot'
            }
            steps { //publish to snapshot
                sh GRADLE_HOME + "gradle publish"
            }
        }
        stage('Integration Test'){
            environment {
                GRETL_VERSION = "$GRETL_VERSION_NUMBER" + '-SNAPSHOT'
                GRETL_JAR_URL = "$GRETL_JAR_BASEURL" + '-snapshot'
            }
            steps{
                dir('./itest'){
                    git 'https://github.com/sogis/gretlpipe.git'
                }

                dir('./itest/integrationtests'){
                    sh "cp inittemplate.txt init.gradle"
                    sh "sed -i 's/_GRETL_VERSION_/" + "$GRETL_VERSION" + "/g' init.gradle"
                    sh "sed -i 's/_GRETL_JAR_URL_/" + "$GRETL_JAR_URL".replace('/','\\/') + "/g' init.gradle"
                    sh "python t_db2dbtask.py"
                    sh "python t_sqlexecutortask.py"
                }
            }
        }
        stage('Release Jar') {
            environment {
                GRETL_VERSION = "$GRETL_VERSION_NUMBER"
                GRETL_JAR_URL = "$GRETL_JAR_BASEURL"
            }
            steps { //publish to release
                sh GRADLE_HOME + "${params.AVOID_PROD_PUBLICATION}" + "gradle publish"

                dir('./itest/integrationtests'){
                    sh "cp inittemplate.txt init.gradle"
                    sh "sed -i 's/_GRETL_VERSION_/" + "$GRETL_VERSION" + "/g' init.gradle"
                    sh "sed -i 's/_GRETL_JAR_URL_/" + "$GRETL_JAR_URL".replace('/','\\/') + "/g' init.gradle"
                    sh "python t_db2dbtask.py"
                    sh "python t_sqlexecutortask.py"
                }
            }
        }
    }
}

