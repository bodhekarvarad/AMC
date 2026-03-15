const mongoose = require("mongoose");


// database connection
const MONGO_URI = "mongodb://127.0.0.1:27017/water_leakage_project_db";

async function main() {
  await mongoose.connect(MONGO_URI);
  console.log("Connected to MongoDB");
}

main().catch(err => {
  console.error("Error connecting to MongoDB:", err);
});