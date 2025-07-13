document.getElementById('fetchData').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/v1/data'); // Assuming a backend endpoint
        const data = await response.json();
        document.getElementById('output').innerText = JSON.stringify(data, null, 2);
    } catch (error) {
        document.getElementById('output').innerText = 'Error fetching data: ' + error;
    }
});