const express = require("express");
const router = express.Router();
router.use(express.json());
router.use(express.urlencoded({ extended: true }));
const path = require('path');

const jwtUtils = require("./../authentication/jwtUtils");

const redisLogger= require("./../redisLogger")

const robotsTxtContent = `
User-agent: MJ12bot
Disallow: /

User-agent: SemrushBot
Disallow: /

User-agent: *
Disallow: /admin/
Disallow: /admin-config/
Disallow: /secure/
Disallow: /ensurance_data/


# Sitemap location (optional but recommended)
Sitemap: https://www.example.com/sitemap.xml
`;

router.get('/robots.txt',(req,res)=>{
  res.type('text/plain');
  res.send(robotsTxtContent);
});

const routes = ['/admin', '/admin-config','/secure'];

routes.forEach((route)=>{
    router.get(route, (req,res)=>{
        console.log(`New entry: ${req.ip} accessed ${route}`);
        if(route=="/admin"){

            
            try {

                const jsonObject = {
                    ip: req.ip,
                    timestamp: new Date().toISOString()  // Current time in ISO format
                  };
              
                  // Convert JSON object to a string
                  const jsonString = JSON.stringify(jsonObject);

                // Adding elements to the list "mylist"
                const result =  redisLogger.rPush('mylist',jsonString);
                console.log('Number of elements in the list:', result);
              } catch (error) {
                console.error('Error:', error);
              } finally {
                // Don't forget to close the connection
                redisLogger.quit();
              }
        }
        //sign the token
        const adminAccessToken = jwtUtils.generateAdminAccessToken({username: 'admin' });
        //console.log("here", adminAccessToken({username: admin}));
        
        const  adminRefreshToken = jwtUtils.generateAdminRefreshToken({username: 'admin'});
        
        //for local testing secure should be put to false
        //put it into the cookie
       res.cookie("adminAccessToken", adminAccessToken, {httpOnly:true, secure:false, sameSite:"Strict"});
       res.cookie("adminRefreshToken", adminRefreshToken, {httpOnly:true, secure:false, sameSite:"Strict"});
       //res.redirect("/");
       
        res.status(401).send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Unauthorized</title>
                <script>
                    let seconds = 3;
                    function updateCountdown() {
                        document.getElementById('countdown').innerText = seconds;
                        seconds--;
                        if (seconds < 0) {
                            window.location.href = '/';
                        }
                    }
                    setInterval(updateCountdown, 1000);
                </script>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; margin-top: 20%; }
                    h1 { color: red; }
                    p { font-size: 18px; }
                </style>
            </head>
            <body>
                <h1>401 - Unauthorized</h1>
                <p>You are not authorized to access this page.</p>
                <p>Redirecting to the <a href="/">login page</a> in <span id="countdown">3</span> seconds...</p>
            </body>
            </html>
        `);
    });
});

router.get('/admin-config',(req,res)=>{

})

module.exports = router; 