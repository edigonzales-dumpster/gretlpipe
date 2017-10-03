cp inittemplate.txt init.gradle
sed -i 's/_GRETL_VERSION_/1.0.1/g' init.gradle
sed -i 's/_GRETL_JAR_URL_/https:\/\/artifactory.verw.rootso.org\/artifactory\/repo-agi-local/g' init.gradle
python t_sqlexecutortask.py -v



