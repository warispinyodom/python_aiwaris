const express = require('express');
const { exec } = require('child_process');
const app = express();
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');
const knex = require('knex')({
  client: 'mysql',
  connection: {
    host: 'localhost',
    port: 3306,
    user: 'root',
    password: '',
    database: 'python_ai_waris'
  }
});

app.use(cors());
app.use(bodyParser.json());
const port = 7000;

// Basic route
app.get('/', (req, res) => {
  res.send('Hello World!');
});

// Endpoint to run the first Python script
app.get('/run-python', (req, res) => {
  console.log('Run Python route hit!');
  exec('python "project/learndata.py"', (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      return res.status(500).send('Error occurred while running Python script');
    }
    res.send(`Python script output: ${stdout}`);
  });
});

// Endpoint to run the second Python script
app.get('/run-python2', (req, res) => {
  console.log('Run Python2 route hit!');
  exec('python "project/learnregis.py"', (error, stdout, stderr) => {
    if (error) {
      console.error(`exec error: ${error}`);
      return res.status(500).send('Error occurred while running Python2 script');
    }
    res.send(`Python2 script output: ${stdout}`);
  });
});

// Endpoint to fetch all users from the database
app.get('/api/users', async (req, res) => {
  try {
    const users = await knex('users').select('*');
    res.json(users);
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).send('Error occurred while fetching users');
  }
});

// API for editing (PUT) user
app.put('/api/users/:id', async (req, res) => {
  const { id } = req.params;
  const { student_id, username, group, level, picture, status } = req.body;

  try {
    // Update user information
    const result = await knex('users')
      .where({ id })
      .update({ 
        student_id,
        username,
        group,
        level,
        picture,
        status
      });

    if (result === 0) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json({ message: 'User updated successfully' });
  } catch (error) {
    console.error('Error updating user:', error);
    res.status(500).send('Error occurred while updating user');
  }
});

// API for deleting (DELETE) user
app.delete('/api/users/:id', async (req, res) => {
  const { id } = req.params;

  try {
    // Delete user
    const result = await knex('users')
      .where({ id })
      .del();

    if (result === 0) {
      return res.status(404).json({ message: 'User not found' });
    }

    res.json({ message: 'User deleted successfully' });
  } catch (error) {
    console.error('Error deleting user:', error);
    res.status(500).send('Error occurred while deleting user');
  }
});

// Endpoint to fetch all passes from the database
app.get('/api/passes', async (req, res) => {
  try {
    const passes = await knex('passes').select('id', 'time_id', 'name', 'timestamp', 'direction', 'image_path');
    res.json(passes);
  } catch (error) {
    console.error('Error fetching passes:', error);
    res.status(500).send('Error occurred while fetching passes');
  }
});

// API for deleting (DELETE) pass
app.delete('/api/passes/:id', async (req, res) => {
  const { id } = req.params;

  try {
    // Delete pass
    const result = await knex('passes')
      .where({ id })
      .del();

    if (result === 0) {
      return res.status(404).json({ message: 'Pass not found' });
    }

    res.json({ message: 'Pass deleted successfully' });
  } catch (error) {
    console.error('Error deleting pass:', error);
    res.status(500).send('Error occurred while deleting pass');
  }
});

// Serve static files (images)
app.use('/images', express.static(path.join('C:/NodeAPI/app/public/')));

// Login endpoint
app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;

  try {
    const admin = await knex('admin')
      .select('admin_id', 'username', 'password', 'status')
      .where({ username })
      .first();

    if (admin) {
      if (admin.password === password) {
        res.json({ message: 'Login successful', admin });
      } else {
        res.status(401).json({ message: 'Invalid password' });
      }
    } else {
      res.status(401).json({ message: 'Invalid username' });
    }
  } catch (error) {
    console.error('Error logging in:', error);
    res.status(500).send('Error occurred while logging in');
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
