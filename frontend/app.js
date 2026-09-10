navigator.geolocation.getCurrentPosition(
  async (position) => {
    const catchData = {
      species: document.querySelector("#species").value,
      length_cm: Number(document.querySelector("#length").value),
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
    };

    const response = await fetch(
      "http://127.0.0.1:8000/api/catches",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(catchData),
      }
    );

    const result = await response.json();
    console.log(result);
  },
  (error) => {
    console.error("Could not retrieve position", error);
  }
);