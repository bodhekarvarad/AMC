const express = require('express');
const app = express();
const port=8500;
app.use(express.json());
app.use(express.urlencoded({extended:true}));
app.use(express.static('public'));
app.get('/',(req,res)=>{
    res.send('Dashboard is spaces');
});
app.get('/login',(req,res)=>{
res.render('login');
});
app.listen(port,()=>{
    console.log(`Server is running on port ${port}`);
});
