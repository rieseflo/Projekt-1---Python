<script>
    import { dev } from "$app/environment";
    let url = location.protocol + "//" + location.host;
    if (dev) {
        url = "http://localhost:5000";
    }

    let zip = 0;
    let km = 0;
    let first_registration = 0;
    let aufbau = 0;
    let marke = 0;
    let modell = 0;
    let türen = 0;
    let farbe = 0;
    let treibstoff = 0;
    let getriebeart = 0;
    let leistung = 0;

    let prediction = "n.a.";

    async function predict() {
        let result = await fetch(
            url +
                "/api/predict?" +
                new URLSearchParams({
                    zip_code: zip,
                    km: km,
                    first_registration: first_registration,
                    aufbau: aufbau,
                    marke: marke,
                    modell: modell,
                    türen: türen,
                    farbe: farbe,
                    treibstoff: treibstoff,
                    getriebeart: getriebeart,
                    leistung: leistung
                }),
            {
                method: "GET",
            },
        );
        let data = await result.json();
        console.log(data);
        prediction = data.Price;
    }
</script>

<h1>Car Price Prediction</h1>

<p>
    <strong>Zip:</strong>
    <input type="number" bind:value={zip} />
</p>

<p>
    <strong>Kilometers:</strong>
    <input type="number" bind:value={km} />
</p>

<p>
    <strong>First Registration Year:</strong>
    <input type="number" bind:value={first_registration} />
</p>

<p>
    <strong>Aufbau:</strong>
    <input type="number" bind:value={aufbau} />
</p>

<p>
    <strong>Marke:</strong>
    <input type="number" bind:value={marke} />
</p>

<p>
    <strong>Modell:</strong>
    <input type="number" bind:value={modell} />
</p>

<p>
    <strong>Türen:</strong>
    <input type="number" bind:value={türen} />
</p>

<p>
    <strong>Farbe:</strong>
    <input type="number" bind:value={farbe} />
</p>

<p>
    <strong>Treibstoff:</strong>
    <input type="number" bind:value={treibstoff} />
</p>

<p>
    <strong>Getriebeart:</strong>
    <input type="number" bind:value={getriebeart} />
</p>

<p>
    <strong>Leistung:</strong>
    <input type="number" bind:value={leistung} />
</p>

<button on:click={predict}>Predict</button>

<p>Predicted Price: {prediction}</p>

<button on:click={() => {
    // Clear input fields
    zip = 0;
    km = 0;
    first_registration = 0;
    aufbau = 0;
    marke = 0;
    modell = 0;
    türen = 0;
    farbe = 0;
    treibstoff = 0;
    getriebeart = 0;
    leistung = 0;
    // Clear prediction
    prediction = "n.a.";
}}>Clear</button>
