const express = require('express');
const ejsMate = require('ejs-mate');
const path = require("path");
const mongoose = require('mongoose');
const app = express();
const port = 3000;

//middlewares
app.engine('ejs', ejsMate);
app.set('view engine', 'ejs');
app.set("views", path.join(__dirname, "views"));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname,'public')));

//database connection
const dbUrl = 'mongodb://localhost:27017/water_leakage_project_db';
main().then(() => {
    console.log('Database connected');
}).catch(err => {
    console.log('Database connection error:', err);
});

async function main() {
    await mongoose.connect(dbUrl);
}

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