(() => {
  const vDelBtn = document.querySelector(".venue_delete");
  vDelBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    const venueId = vDelBtn.getAttribute("id");
    fetch(`/venues/${venueId}/delete`, {
      method: "DELETE",
    })
      .then((res) => res.json())
      .then((data) => {
        window.location = data.homeUrl;
      })
      .catch(() => (window.location = "/500"));
  });

  const aDelBtn = document.querySelector(".artist_delete");
  aDelBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    const artistId = aDelBtn.getAttribute("id");
    fetch(`/artists/${artistId}/delete`, {
      method: "DELETE",
    })
      .then((res) => res.json())
      .then((data) => {
        window.location = data.homeUrl;
      })
      .catch(() => (window.location = "/500"));
  });
})();
