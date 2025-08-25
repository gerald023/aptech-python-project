// fetch('https://jsonplaceholder.typicode.com/comments/1')
// .then(res => res.json)
// .then(data => console.log(data))
// // .catch(error => console.log(error))


//Challenge - Async & Await

//Print on the console a random joke from the Chuck Norris API using Fetch and Async and Await

const apiUrl = "https://api.chucknorris.io/jokes/random";

const getData = ()=>{
fetch(apiUrl)
.then(res => res.json())
.then(data => console.log(data));
}

getData()

const getJoke = async ()=>{
    const response = fetch(apiUrl);
    const data = response.json();
    console.log(data.value);
}