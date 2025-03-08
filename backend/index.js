const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const port = 5000;

// 使用中间件
app.use(cors());
app.use(bodyParser.json());

// 创建 MySQL 连接池
const pool = mysql.createPool({
  host: 'localhost', // 数据库地址
  user: 'root',      // 数据库用户名
  password: 'root', // 数据库密码
  database: 'arno_db',  // 数据库名称
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// 测试数据库连接
pool.getConnection((err, connection) => {
  if (err) {
    console.error('Error connecting to MySQL:', err);
  } else {
    console.log('Connected to MySQL database!');
    connection.release();
  }
});

// 创建一个 API 路由
app.get('/api/data', (req, res) => {
  pool.query('SELECT * FROM messages', (err, results) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to fetch data' });
    }
    res.json(results);
  });
});

// 插入数据到数据库
app.post('/api/data', (req, res) => {
  const { sender, text } = req.body;
  if (!sender || !text) {
    return res.status(400).json({ error: 'Sender and text are required' });
  }

  pool.query(
    'INSERT INTO messages (sender, text) VALUES (?, ?)',
    [sender, text],
    (err, results) => {
      if (err) {
        return res.status(500).json({ error: 'Failed to insert data' });
      }
      res.json({ id: results.insertId, sender, text });
    }
  );
});

// 启动服务器
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});