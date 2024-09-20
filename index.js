const express = require('express')
const app = express()
const bodyParser = require('body-parser')
const expressFileupload = require('express-fileupload')
const cors = require('cors') 
const knex = require('knex')({
  client: 'mysql',
  connection: {
    host: 'localhost',
    port: 3306,
    user: 'root',
    password: '',
    database: 'member'
  }
})
app.use(cors())
app.use(bodyParser.json())
const port = 7000

app.get('/', (req, res) => {
  res.send('Hello World!')
})
app.get('/user/picture/:id', async (req, res) => {
  const { id } = req.params;
  try {
    const [user] = await knex('users').where({ id }).select('picture');
    if (user && user.picture) {
      // ส่งข้อมูลภาพในรูปแบบ Base64
      res.send({ picture: `data:image/jpeg;base64,${user.picture.toString('base64')}` });
    } else {
      res.status(404).send({ error: 'Image not found' });
    }
  } catch (error) {
    res.status(500).send({ error: error.message });
  }
});
// http://localhost:7000/listStudent
app.get('/liststds',async (req, res) => {
   let rows = await knex('users')
      res.send({
        ok: 1,
        students: rows,
        })
})
app.get('/liststd',async (req, res) => {
  console.log(req.query)
  try{
    let rows = await knex('users').where({id: req.query.id})
    res.send({
      ok: 1,
      students: rows,
      })
  }catch(error){
    res.send({ ok: 0, error: error.message})
  }
  
})

app.post('/insert', async (req,res) => {
console.log(req.body)
let username = req.body.username
let password = req.body.password
let email = req.body.email
try {
  let ids = await knex('users')
.insert({username: username, password: password, email: email})
res.send({ ok: 1, id: ids})
} catch (e) {
  res.send({ok: 0, error: e.message})
}
})

app.post('/delete', async (req,res) => {
  console.log(req.body)
  try{
    let rows = await knex('users').where({id: req.body.id})
    .delete()
    res.send({
      ok: 1,
      students: rows,
      })
  }catch(error){
    res.send({ ok: 0, error: error.message})
  }
})

app.post('/update', async (req, res) => {
  console.log(req.body)
  let username = req.body.username
  let password = req.body.password
  let email = req.body.email
  try {
      let rows = await knex('users').where({ id: req.body.id })
          .update({ username: username, password: password, email: email })
      res.send({ ok: 1, id: rows })
  }
  catch (error) {
      res.send({ ok: 0, error: error.message })
  }
})

app.post('/search', async (req, res) => {
  console.log(req.body)
  let username = req.body.username
  let rows = await knex('users').where({ id: req.body.id })
  res.send({
      ok: 1,
      students: rows,
  })
})

app.post('/image_save', async (req, res) => {
  console.log(req.body);
  let { device, data_type, zone, sample, count, file_name, this_stamp } = req.body;
  try {
    let ids = await knek('image_save')
      .insert({ device, data_type, zone, sample, count, file_name, time_stamp})
      .returning('id');
    res.send({ ok: 1, id: ids});
  } catch (error) {
      res.send({ ok: 0, error: error.message});
  }
})


app.listen(port, () => {
  console.log('Example app listening on port 7000')
})