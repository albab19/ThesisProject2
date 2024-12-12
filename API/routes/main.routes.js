const express = require("express");
const router = express.Router();
router.use(express.json());
router.use(express.urlencoded({ extended: true }));
const path = require('path');
const cookieParser = require("cookie-parser");

//Midddleware
const authMiddleware = require("./../authentication/authMiddleware.js");



//DB Connection
const { connectToDB } = require('../controllers/dbController.js');
db = connectToDB();



const { json } = require('body-parser');


//main
router.get('/', authMiddleware.authenticate, async(req,res)=>{
    res.sendFile((path.join(__dirname, '../static', 'main.html')));
    
  });

//see all studies - retrieve html
router.get('/searchStudies', authMiddleware.authenticate, async(req,res)=>{
res.sendFile((path.join(__dirname, '../static', 'searchStudies.html')));
});

//see all studies - populate the table
router.get('/studies', authMiddleware.authenticate, (req,res)=>{
    db.all('SELECT * FROM study', (err, rows) => {
        if (rows.length === 0){
          return res.status(200).json({ message: "No data found" });
          }
        if (err) {
            return res.status(500).json({ message:"Internal server error" });
        }
        return res.json(rows); 
    });
});

//see all patients 
router.get('/searchPatients', authMiddleware.authenticate, async(req,res)=>{
res.sendFile((path.join(__dirname, '../static', 'searchPatients.html')));
});

//see all patients - populate the table
router.get('/patients',async(req,res)=>{
    db.all('SELECT * FROM patient', (err, rows) => {
        if (rows.length === 0){
          return res.status(200).json({ message: "No data found" });
          }
        if (err) {
            console.log("the prob with db")
            console.log(err);
            return res.status(500).json({ message:"Internal server error" });
            
        }
        return res.json(rows); 
    });
});


router.get('/searchImages', authMiddleware.authenticate, async(req,res)=>{
    res.sendFile((path.join(__dirname, '../static', 'searchImages.html')))
  });
  
router.get('/images', authMiddleware.authenticate, async(req,res)=>{

db.all('SELECT * FROM image', (err, rows) => {
    if (rows.length === 0){
      return res.status(200).json({ message: "No data found" });
      }
    if (err) {
        return res.status(500).json({ message:"Internal server error" });
    }
    return res.json(rows); 
    });
});
  
  
//Instances

//Load the search instances html
router.get('/searchInstances', authMiddleware.authenticate, async(req,res)=>{
res.sendFile((path.join(__dirname, '../static', 'searchInstances.html')))
})

//Query the db for instances and load the results into the table
router.get('/instances', authMiddleware.authenticate, async(req,res)=>{
db.all('SELECT * FROM instance', (err, rows) => {
    if (rows.length === 0){
      return res.status(200).json({ message: "No data found" });
      }
    if (err) {
        return res.status(500).json({ message:"Internal server error" });
    }
    return res.json(rows); 
    });
});
  
  router.get('/searchSeries', authMiddleware.authenticate, async(req,res)=>{
    res.sendFile((path.join(__dirname, '../static', 'searchSeries.html')))
  });
  
  router.get('/series', authMiddleware.authenticate, async(req,res)=>{
  
    db.all('SELECT * FROM series', (err, rows) => {
        if (rows.length === 0){
          return res.status(200).json({ message: "No data found" });
          }
      
        if (err) {
            return res.status(500).json({message:"Internal server error" });
        }
        return res.json(rows); 
    });
  });
  
  router.post('/searchBy', authMiddleware.authenticate, (req,res)=>{
      console.log("request",req.body["searchInput"]);
  
    if(req.body["searchType"] === "name"){
    db.all('SELECT patient_id, patient_name, study_instance_uid, study_date, study_time, accession_number, study_id, transfer_syntax_uid, sop_class_uid, series_instance_uid,modality,series_number, sop_instance_uid, instance_number FROM instance WHERE patient_name = ?', [req.body["searchInput"]], (err, rows) => {
        if (err) {
            return res.send(500).json({ message: "Internal server error" });
        }
        if (rows.length === 0){
        return res.status(200).json({ message: "No data found" });
        }
        return res.send(rows); 
      });
    }else{
  
  
    db.all(
      'SELECT patient_id, patient_name, study_instance_uid, study_date, study_time, accession_number, study_id, transfer_syntax_uid, sop_class_uid, series_instance_uid,modality,series_number, sop_instance_uid, instance_number FROM instance WHERE  patient_id = ?  COLLATE BINARY', [req.body["searchInput"]], (err, rows) => {
        if (err) {
        return res.sendStatus(500).json({ message: "Internal server error" });
        }
        if (rows.length === 0){
        return res.status(200).json({ message: "No data found" });
        }
        return res.send(rows);
      });
    }
  });

  router.get('/upload', authMiddleware.authenticate, async(req,res)=>{
    res.sendFile((path.join(__dirname, '../static', 'upload.html')));
  });
  


module.exports = router;