document.getElementById("payButton").addEventListener("click", function () {
  fetch("/create-session", {
    method: "POST",
  })
    .then((response) => {
      if (response.redirected) {
        window.location.href = response.url;
      } else {
        return response.json().then((data) => {
          alert(data.error);
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
});
