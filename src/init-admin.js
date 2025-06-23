const mongoose = require('mongoose');
const dotenv = require('dotenv');
dotenv.config();
const User = require('./model/user');

const uri = process.env.DATABASE_URL;

async function createAdmin() {
  await mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true });
  const admin = await User.findOne({ username: 'admin' });
  if (!admin) {
    const newAdmin = new User({
      username: 'admin',
      password: 'admin123',
      role: 'admin',
      createdAt: new Date(),
    });
    await newAdmin.save();
    console.log('Admin user created.');
  } else {
    console.log('Admin user already exists.');
  }
  await mongoose.disconnect();
}

createAdmin();
