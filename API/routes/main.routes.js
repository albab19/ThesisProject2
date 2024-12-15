const express = require("express");
const router = express.Router();
const axios = require('axios');
router.use(express.json());
router.use(express.urlencoded({ extended: true }));
const path = require('path');
const FormData = require('form-data');
const fs = require('fs');
const cookieParser = require("cookie-parser");

//Midddleware
const authMiddleware = require("./../authentication/authMiddleware.js");



//DB Connection
const { connectToDB } = require('../controllers/dbController.js');
db = connectToDB();



const { json } = require('body-parser');
//const redisLogger = require("../redisLogger.js");
const redisClient= require("../redisLogger");
const { report } = require("process");


//main
router.get('/', authMiddleware.authenticate, async(req,res)=>{
    res.sendFile((path.join(__dirname, '../static', 'main.html')));
    
  });

  router.get('/dev',authMiddleware.authenticate, async(req,res)=>{
    res.sendFile(path.join(__dirname, '../static', 'underDevelopment.html'));
    
  });

  

//see all studies - retrieve html
router.get('/searchStudies', authMiddleware.authenticate, async(req,res)=>{
res.sendFile((path.join(__dirname, '../static', 'searchStudies.html')));
});

//see all studies - populate the table
router.get('/studies', authMiddleware.authenticate, (req,res)=>{

  logEvent('Search all studies',req)
      db.all('SELECT * FROM study', (err, rows) => {
        if(rows){

      
        return res.json(rows); 
      }
      return res.status(200).json({ message: "No data found" });
          
    });

    
});

//see all patients 
router.get('/searchPatients', authMiddleware.authenticate, async(req,res)=>{
res.sendFile((path.join(__dirname, '../static', 'searchPatients.html')));
});

//see all patients - populate the table
router.get('/patients',async(req,res)=>{
  logEvent('Search all patients',req)

    db.all('SELECT * FROM patient', (err, rows) => {
      try{
        if (rows.length === 0){
          return res.status(200).json({ message: "No data found" });
          }
        if (err) {
            console.log("the prob with db")
            console.log(err);
            return res.status(500).json({ message:"Internal server error" });
            
        }
        return res.json(rows); 
      }catch(e){
          console.log(e)
      }
    });
});


router.get('/searchImages', authMiddleware.authenticate, async(req,res)=>{
    res.sendFile((path.join(__dirname, '../static', 'searchImages.html')))
  });
  
router.get('/images', authMiddleware.authenticate, async(req,res)=>{
  logEvent('Search all images',req)


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
  logEvent('Search all instances',req)

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
    
    logEvent('Search all series',req,req.body["searchInput"])

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
      logEvent('Search by name',req,req.body["searchInput"])

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
      
      logEvent('Search by id',req,req.body["searchInput"])

  
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

  router.post('/scan', async (req, res) => {
    const APIKey = "715bccfb503dc801d1fdc5f095bb3c0c2a4412a7b81cca1a2f5c15e14361f1fa";
    console.log("Received filename:", req.body.filename);
    var ip= req.socket.remoteAddress
    var port=req.connection.remotePort
    console.log("poo",port)
    const formData = new FormData();
    const fileToScan = `./uploads/${req.body.filename}`;
    formData.append('file', fs.createReadStream(fileToScan));
    
    try {
        const response = await axios({
            method: 'post',
            url: 'https://www.virustotal.com/api/v3/files',
            headers: {
                ...formData.getHeaders(),
                'X-Apikey': APIKey
            },
            data: formData
        });
        await checkAnalysis(response.data.data.id, APIKey,req,ip,port);
        res.send('');
    } catch (error) {
        console.error('Error uploading file to VirusTotal:', error);
        res.status(500).send('Failed to initiate file scan.');
    }
});

async function checkAnalysis(analysisId, APIKey,req,ip,port) {
    try {
        const result = await axios({
            method: 'get',
            url: `https://www.virustotal.com/api/v3/analyses/${analysisId}`,
            headers: {
                'x-apikey': APIKey
            }
        });

        if (result.data.data.attributes.status !== 'completed') {
            console.log('Analysis status:', result.data.data.attributes.status);
            setTimeout(() => checkAnalysis(analysisId, APIKey), 10000); 
        } else {
            logEvent(`FileUploaded`,req,JSON.stringify(result.data.data.attributes.stats),ip,port)

            console.log('Analysis completed. Results:', result.data.data.attributes.stats);
        }
    } catch (error) {
        console.error('Error checking analysis status:', error);
    }
}


  router.get('/upload', authMiddleware.authenticate, async(req,res)=>{
    

    res.sendFile((path.join(__dirname, '../static', 'upload.html')));
  });
  
  function logEvent(e,req,parameter="",ip="",port=0){
    console.log("poo",port)

   

    if(parameter==="" || e==="Search by id" || e==="Search by name"){     
    try {
      const ip= req.socket.remoteAddress
      if (ip.substr(0, 7) === "::ffff:") {
        ip = ip.split(':').pop();
        }        
        let r_port= req.connection.remotePort
        const jsonObject = {
            id: new Date().toISOString().slice(0, 19),
            ip: ip,
            timestamp: new Date().toISOString().slice(0, 19) ,
            sessionId: process.env.SESSION_SECRET,
            event:e,
            port: r_port,
            report:"N/A"
          };
    
          const jsonString = JSON.stringify(jsonObject);
  
          redisClient.rPush('mylist',jsonString);
      } catch (error) {
        console.error('Error:', error);
      } 
    }
    else if (parameter!="" && e=="FileUploaded") {

    try {
  
        const jsonObject = {
            ip: ip,
            timestamp: new Date().toISOString().slice(0, 19) ,
            event:e,
            port: port,
            sessionId: process.env.SESSION_SECRET,
            report: parameter
          };
    
          const jsonString = JSON.stringify(jsonObject);
  
          redisClient.rPush('mylist',jsonString);
      } catch (error) {
        console.error('Error:', error);
      } 
      console.log("")


    }
  
  
  }
  


module.exports = router;