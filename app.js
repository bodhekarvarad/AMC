const express = require('express');
const ejsMate = require('ejs-mate');
const path = require("path");

const app = express();
const port = 3000;

//middlewares
app.engine('ejs', ejsMate);
app.set('view engine', 'ejs');
app.set("views", path.join(__dirname, "views"));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname,'public')));

//dashboard
app.get('/', (req, res) => {
    res.send('Dashboard is spaces');
});

app.get('/navbar', (req, res) => {
    res.render('includes/navbar');
});

//server starting
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});