import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.Connection;
import java.sql.ResultSet;


// RDF_LOAD_SQL = "DB.DBA.RDF_LOAD_RDFXML_MT (file_to_string_output (?), '', ?);"
LOAD_SQL = 'ld_dir (?, ?, ?)';
SQL_DELETE_LOAD_LIST = "delete from DB.DBA.load_list where ll_file like ?";
SQL_QUERY_FINISHED = "select count(*) from DB.DBA.load_list where ll_file like ? and ll_state = 2";
SQL_LOAD = "rdf_loader_run()";
CLEAR_GRAPH = "DELETE FROM rdf_quad WHERE g = iri_to_id (?)"
SQL_CHECKPOINT = "checkpoint";

Connection getSqlConnection(String url, String username, String password) {
    try {
        return DriverManager.getConnection(url, username, password);
    } catch (SQLException ex) {
        throw new RuntimeException("Can't create sql connection.", ex);
    }
}

PreparedStatement prepareStatement(
        Connection connection, String statement)
        throws SQLException {
    return connection.prepareStatement(statement);
}

PreparedStatement createRdfLdStatement(Connection connection, String filePath, String graph)
            throws SQLException {
    print(RDF_LOAD_SQL)
    final PreparedStatement statement =
            connection.prepareStatement(RDF_LOAD_SQL);
    statement.setString(1, filePath);
    statement.setString(2, graph);
    return statement;
}

PreparedStatement createLdStatement(Connection connection, String directory, String file, String graph)
            throws SQLException {
    println(LOAD_SQL)
    final PreparedStatement statement =
            connection.prepareStatement(LOAD_SQL);
    statement.setString(1, directory);
    statement.setString(2, file);
    statement.setString(3, graph);
    return statement;
}

void loadData(Connection connection) {
    PreparedStatement statement = null;
    try {
        statement = prepareStatement(connection, SQL_LOAD)
        statement.executeQuery();
    } catch (SQLException ex) {
        throw new RuntimeException("Can't load data.", ex);
    }
}

void clearLoadList(Connection connection, String directory) {
    PreparedStatement statement = null;
    try {
        statement = prepareClearStatement(connection, directory)
        statement.executeUpdate();
    } catch (SQLException ex) {
        throw new RuntimeException("Can't clear loading table.", ex);
    }
}
 
PreparedStatement prepareClearStatement(Connection connection, String directory) throws SQLException {
    final PreparedStatement statement = connection.prepareStatement(
            SQL_DELETE_LOAD_LIST);
    statement.setString(1, directory + "%");
    return statement;
}

void checkpoint(Connection connection) {
        PreparedStatement statement = null;
    try {
        statement = prepareStatement(connection, SQL_CHECKPOINT)
        statement.executeQuery();
    } catch (SQLException ex) {
        throw new RuntimeException("Can't create sql connection.", ex);
    }
}

int getFilesLoaded(Connection connection, String directory){
    PreparedStatement statement = null;
    try {
        statement = prepareLoadedFilesStatement(connection, directory)
        return executeStatementForSingleInt(statement);
    } catch (SQLException ex) {
        throw new RuntimeException("Can't get number of loaded files.", ex);
    }
}

PreparedStatement prepareLoadedFilesStatement(Connection connection, String directory) throws SQLException {
    final PreparedStatement statement = connection.prepareStatement(SQL_QUERY_FINISHED);
    statement.setString(1, directory + "%");
    return statement;
}

int executeStatementForSingleInt(PreparedStatement statement) throws SQLException {
    ResultSet resultSetProcessing = null
    try {
        resultSetProcessing = statement.executeQuery()
        resultSetProcessing.next();
        return resultSetProcessing.getInt(1);
    } finally {
        if (resultSetProcessing != null) {
            resultSetProcessing.close();
        }
    }
}

void deleteGraph(Connection connection, String graph) {
        PreparedStatement statement = null;
    try {
        statement = createDeleteStatement(connection, graph, CLEAR_GRAPH)
        statement.executeQuery();
    } catch (SQLException ex) {
        throw new RuntimeException("Can't create sql connection.", ex);
    }
}

PreparedStatement createDeleteStatement(Connection connection, String graph, String query)
            throws SQLException {
    final PreparedStatement statement = connection.prepareStatement(query);
    statement.setString(1, graph);
    return statement;
}

try {
    scriptDir = new File(getClass().getResource('config.properties').toURI()).parent
    input = new FileInputStream(scriptDir + "/config.properties")
    Properties prop = new Properties();
    prop.load(input);

    virtuosoUrl = prop.get("virtuoso.url")
    virtuosoUser = prop.get("virtuoso.user")
    virtuosoPwd = prop.get("virtuoso.pwd")
    graph = prop.get("graph")
    sourceDirectory = prop.get("source.directory")
    path = System.getProperty("user.home");

    Connection connection = getSqlConnection('jdbc:virtuoso://'+ virtuosoUrl +'/charset=UTF-8/', virtuosoUser, virtuosoPwd);
    println("Deleting existing graph: " + graph)
    deleteGraph(connection, graph)
    println("Creating load statements")
    PreparedStatement statement = createLdStatement(connection, sourceDirectory, 'predictive_gene2phenotype-10.rdf', graph)
    statement.executeQuery().close();


    println("Loading data")
    loadData(connection)
    println("number of files loaded: " + getFilesLoaded(connection, sourceDirectory));
    clearLoadList(connection, sourceDirectory)

    checkpoint(connection)

    System.out.println("Data Loaded");
} catch (SQLException ex) { 
    throw new RuntimeException("Can't execute RDF_LOAD_RDFXML_MT statement .", ex);
} catch (Exception e) {
    e.printStackTrace()
}

