//db
const sqlite3 = require('sqlite3').verbose();
var databasePath= "./../../db.db"
var env  = process.env.Docker_ENV;
console.log("Hellooo",env)
if (env =="True"){
    databasePath = '/app/db.db'

}
// Connect to the SQLite database
function connectToDB() {
    const db = new sqlite3.Database(databasePath, sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE, (err) => {
    if (err) {
        console.error('Error opening database:', err.message);
    } else {
        console.log('Connected to the SQLite database.');
    }
});

return db;
}


module.exports={
    connectToDB
  };
  