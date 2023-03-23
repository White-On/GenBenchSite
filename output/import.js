const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const cors = require('cors');
const server = require('http').createServer(app);
const io = require('socket.io')(server, {
    cors: {
        origin: '*',
        methods: ['GET', 'POST'],
    }
})
const port = 8080;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cors());

app.get('/', (req, res) => {
    res.send('Server is running');
});

require('./routes')(app);
require('./socket')(app);

server.listen(port, () => { console.log(`Server is running on port ${port}`) });

// import {my_func} from './my-func.js';

// my_func(1, 2);
// console.log(my_func(1, 2));