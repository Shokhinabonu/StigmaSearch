import { search } from 'google-play-scraper';

search({
    term: process.argv[2],
    num: 1
})
.then((data) => console.log(JSON.stringify(data)))
.catch(console.error);