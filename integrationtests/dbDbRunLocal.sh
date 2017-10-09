cp inittemplate.txt init.gradle
sed -i 's/_GRETL_VERSION_/1.0.2-SNAPSHOT/g' init.gradle
sed -i 's/_GRETL_JAR_URL_/https:\/\/artifactory.verw.rootso.org\/artifactory\/repo-agi-local-snapshot/g' init.gradle
python t_db2dbtask.py -v