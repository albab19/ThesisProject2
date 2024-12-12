// const dcmjsDimse = require('dcmjs-dimse');
// const{Client} = dcmjsDimse;
// const{CEchoRequest} = dcmjsDimse.requests;
// const{Status}=dcmjsDimse.constants;
// const { CFindRequest } = dcmjsDimse.requests;




// function cEchoScu(ip, dicom_port){
//     const client = new Client();
//     ip ='52.6.96.126';
//     dicom_port = 104;
//     req = new CEchoRequest();

//     req.on('reponse', (res)=>{
//         if(res.getStatus() === Status.Success){
//             console.log('Received ECHO response')
//         }
//     });

//     client.addRequest(req);
//     client.on('networkError', (error)=>{
//         console.log('Network error: ', error);
//     });

//     return client.send(ip,  dicom_port, 'SCU', 'ANY-SCP')
// }
// //cEchoScu('52.6.96.126', 104 )

// function CFindStudy(ip, PatientID){
//     const client = new Client();
//     //PatientID = 'NOID';
//     //ip ='52.6.96.126';
//     ip = '127.0.0.1';

//     const req = CFindRequest.createStudyFindRequest({ PatientID: "NOID", PatientName: "NAME^NONE" });
    
//     req.on('response', (res)=>{
//         if(res.getStatus()===Status.Pending && res.hasDataset()){
//             console.log(res.getDataset());
//         }
//     });
//     client.addRequest(req);
//     client.on('networkError',(error)=>{
//         console.log('Network error: ', error);
//     });
//     client.send(ip, PatientID, 'SCU', 'ANY-SCP');
// }

// CFindStudy('127.0.0.1', '11112', 'SCU', 'ANY-SCP')