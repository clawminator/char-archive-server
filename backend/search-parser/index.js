const express = require('express');
const bodyParser = require('body-parser');
const {parseSearchQuery} = require('./search-parser');

const app = express();
app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());

app.post('/search', (req, res) => {
    const {query} = req.body;

    // Allow empty queries
    // if (!query) {
    //     return res.status(400).json({error: 'Search query is missing'});
    // }

    try {
        const parsedQuery = parseSearchQuery(query);
        // console.log(JSON.stringify(parsedQuery));
        console.log(`GET - ${req.socket.remoteAddress} - ${query.length}`)
        res.json(parsedQuery);
    } catch (error) {
        console.error(`Error parsing search query: "${query}"`, error);
        res.status(500).json({error: 'Internal server error'});
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '127.0.0.1', () => {
    console.log(`Server is running on port ${PORT}`);
});