// JavaScript function to generate 6 random unique values in order and populate form
function luckyDip() {

    // create list of 6 random numbers
    const randomBuffer = new Uint32Array(6);
    window.crypto.getRandomValues(randomBuffer);

    // create empty set
    const draw = new Set();

    // generate 6 random numbers to fill the set
    for (let i = 0; i < 6; i++) {
        const min = Math.ceil(1);
        const max = Math.floor(60);
        let value = Math.floor((randomBuffer[draw.size] / 0xFFFFFFFF) * (max - min + 1) + min);
        console.log(draw.size, value, draw.has(value), randomBuffer[draw.size] / 0xFFFFFFFF);

        // whilst the number already exists in the set, generate a new one
        while (draw.has(value)) {
            window.crypto.getRandomValues(randomBuffer);
            value = Math.floor((randomBuffer[draw.size] / 0xFFFFFFFF) * (max - min + 1) + min);
            console.log("Number not unique, regenerating...");
            console.log(draw.size, value, draw.has(value), randomBuffer[draw.size] / 0xFFFFFFFF);
        }

        draw.add(value);
    }

    // turn set into an array
    const a = Array.from(draw);

    // sort array into size order
    a.sort(function (a, b) {
        return a - b;
    });

    // add values to fields in create draw form
    for (let i = 0; i < 6; i++) {
        document.getElementById("no" + (i + 1)).value = a[i];
    }
}