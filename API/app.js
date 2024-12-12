



//expressjs lib
const express = require('express');
const path = require('path');
const favicon = require('serve-favicon');


//uploading 
const multer = require('multer');

//require('dotenv').config();
//expressjs app
const app = express();
app.use(favicon(path.join(__dirname, 'static', 'favicon.ico')));
//app.use(express.static('static'));


//middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true}));
app.use(express.static(path.join(__dirname, 'static')));

//const
const port = 3000;

//authentication
const cookieParser = require("cookie-parser");
const { json } = require('body-parser');
app.use(cookieParser());
const jwtUtils = require("./authentication/jwtUtils");
const csrfMiddleware = require("./middleware/csrfMiddleware.js");

//session management
const sessionMiddleware= require('./middleware/sessionMiddleware.js');
app.use(sessionMiddleware);





const USERS = {
  username:'test', password:'test',
}
// const USERS = [
//   {username:'test', password:'test'},
//   {username:'oolnie', password:'iamtcte4*'}
// ]
  

const cors = require('cors');
const { verifyCSRFToken } = require('./middleware/csrfMiddleware.js');

// Enable CORS for the frontend
// app.use(
//   cors({
//     origin: 'http://localhost:4000', 
//     credentials: true, 
//   })
// );





//Routes
const mainRoutes = require('./routes/main.routes.js');
app.use('/main', mainRoutes);

const adminRoutes = require('./routes/admin.routes.js');
app.use('/', adminRoutes);

//const authRoutes = require('./routes/auth.routes.js');
//app.use('/', authRoutes);



const storage = multer.diskStorage({
  destination: (req, file, cb) =>{
    cb(null, 'uploads/');
  },
  filename: (req, file, cb)=>{
    cb(null, `${Date.now()}-${file.originalname}`);
  }
});

const upload = multer({storage});

app.post('/upload',  (req,res)=>{
  upload.array('dicomFiles[]', 10)(req,res, function(err){
      if(err){
        if(err.code === 'LIMIT_UNEXPECTED_FILE'){
          return res.status(400).json({message: 'Cannot upload more than 10 files at once.'});
        }
        return res.status(500).json({message:'An error occurred while uploading'});
      }

      res.json({
        message: '10 first files uploaded successfully',
        files: req.files.map(file=>({
          filename:file.filename,
          path:file.path
        }))
      });
  });
    
});
  


app.post('/login',async(req,res) => {
  try{
    
    if (!req.body.username || !req.body.password){
      return res.status(401).json({message:'Empty username or password!'})
    }

   
    if(req.body.username === "oolnie" && req.body.password === "iamtcte4*"){
      res.sendFile(path.join(__dirname, './static', 'underDevelopment.html'));
    }

    if(req.body.username === USERS.username && req.body.password === USERS.password){
      req.session.user ={username: req.body.username};
      console.log('User ','"',req.body.username,'"',' logged in. Session ID:', req.sessionID); // Log the session ID

      const accessToken = jwtUtils.generateAccessToken({username: req.body.username});
      const  refreshToken = jwtUtils.generateRefreshToken({username: req.body.username});
      //const csrfToken = csrfMiddleware.generateCSRFToken();
      
      //for local testing secure should be put to false
      res.cookie("accessToken", accessToken, {httpOnly:true, secure:false, sameSite:"Strict"});
      res.cookie("refreshToken", refreshToken, {httpOnly:true, secure:false, sameSite:"Strict"});
     // res.cookie("csrfToken", csrfToken, {httpOnly: false, secure: true, sameSite:"Strict"});
      console.log("cookie", res.cookie);
      //onsole.log("CSRF token:::", csrfToken);
      
      return res.status(200).json({message: 'Login successful!'});

    }else{
      //it has been "invalid credentials before"
      return res.status(401).json({message: 'Invalid username or password!'});
    }
  }catch(error){
    res.status(500).json({ message: error.message });
  }
});

app.post('/logout', (req,res)=>{
  req.session.destroy(err => {
    //console.log("before clearing", connect.sid);
    //res.clearCookie('connect.sid');
    //console.log("after clearing", connect.sid);
    //console.log("session destroyed");
    if (err) {
      return res.status(500).send('Error logging out');
    }
  })
  res.clearCookie('accessToken');
  //console.log("aaaaaaaa",res.clearCookie('accessToken'))
  res.clearCookie('refreshToken');
 // console.log("bbbbbbbbbbbbb", res.clearCookie('refreshToken'));
  res.status(200).json({message:"Logged out successfully"});
  //res.redirect('/');
});

app.get('/refresh', (req,res)=>{
  const refreshToken = req.cookies.refreshToken;

  if(!refreshToken){
    return res.status(401).json({message:"No refresh token"});
  }

  try{
    const decoded = jwtUtils.verifyRefreshToken(refreshToken);
    console.log("here",decoded);

    //Update the tokens
    const newAccessToken = jwtUtils.generateAccessToken({username:decoded.username});
    const newRefreshToken = jwtUtils.generateRefreshToken({username:decoded.username});

    res.cookie("accessToken", newAccessToken, {httpOnly:true, secure:false, sameSite:"Strict"});
    res.cookie("refreshToken", newRefreshToken, {httpOnly:true, secure:false, sameSite:"Strict"});

    res.redirect(req.query.redirectFrom);

  }catch(error){
    res.status(403).json({message:"Invalid or expired refresh token"});
  }

});

app.get('/', async(req, res) => {
  res.sendFile((path.join(__dirname, 'static', 'login.html')));
});

//check-admin-token is called loginAdmin to avoid fingerprinting
app.get('/loginAdmin', (req, res) => {
  const adminToken = req.cookies['adminAccessToken'];
  if (adminToken) {
      res.json({ isAdmin: true });
  } else {
      res.json({ isAdmin: false });
  }
});


// See all instances table has the option to download a single instance
app.get('/downloadInstance', (req,res)=>{
  const file = path.join(__dirname, './static/hf/image-000008sssssss.dcm.url');
  res.download(file, 'image-000008.dcm.url', (err) =>{
    if(err){
      console.error("File not available: ", err);
    }
  });
});

// See all studies table has the option to download a zip folder
app.get('/downloadStudyFiles', (req,res)=>{
  const file = path.join(__dirname, './static/hf/StudyFiles.zip');
  res.download(file, 'StudyFiles.zip', (err) =>{
    if(err){
      console.error("File not available: ", err);
    }
  });
});


//run the app
try{
  app.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
  });
}catch(error){
  console.error("Error. Server did not start", error);
}




/*
1. login
2. authentication (session,jwt,bcrypt)
3. redirect main
4. search for all studies (button-->backend-->dicomclient-->(got data)-->fill in the studyresults.html)
5. search for all patients
6. when patient name and/or is filled in, take it into account
7. redirect to studyresults.html
*/