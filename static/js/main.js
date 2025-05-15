if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const { latitude, longitude } = position.coords;

                        // Отправка данных на сервер
                        fetch("/save_location", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ lat: latitude, lon: longitude }),
                        })
                        .then(response => response.json())
                        .then(data => console.log(data))
                        .catch(error => console.error("Ошибка:", error));
                    },
                    (error) => {
                        alert(`Ошибка: ${error.message}`);
                    },
        {
          timeout: 10000, // Макс. время ожидания (10 сек)
        }
      );
    } else {
      console.log("Геолокация не поддерживается в вашем браузере");
    }