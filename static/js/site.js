/* G&T OrthoCare storefront JS */
(function () {
  // ---- toast ----
  let toastTimer;
  window.gtToast = function (msg) {
    const el = document.getElementById("toast");
    if (!el) return;
    el.querySelector("#toastmsg").textContent = msg;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("show"), 2400);
  };

  // Django messages -> toast
  document.querySelectorAll(".dj-message").forEach((m, i) => {
    setTimeout(() => gtToast(m.dataset.msg), 300 + i * 2600);
  });

  // ---- mobile menu ----
  document.querySelector(".burger")?.addEventListener("click", () => {
    document.getElementById("mainnav")?.classList.toggle("open");
  });

  // ---- product page: gallery thumbnails ----
  document.querySelectorAll(".pdthumbs img").forEach((th) => {
    th.addEventListener("click", () => {
      document.querySelectorAll(".pdthumbs img").forEach((i) => i.classList.remove("on"));
      th.classList.add("on");
      const main = document.getElementById("pdmain");
      if (main) main.src = th.dataset.full || th.src;
    });
  });

  // ---- banner carousel ----
  const track = document.querySelector(".banners .track");
  if (track) {
    const slides = track.children.length;
    let idx = 0;
    const dots = document.querySelectorAll(".banners .dots button");
    const show = (i) => {
      idx = (i + slides) % slides;
      track.style.transform = `translateX(-${idx * 100}%)`;
      dots.forEach((d, j) => d.classList.toggle("on", j === idx));
    };
    dots.forEach((d, j) => d.addEventListener("click", () => show(j)));
    if (slides > 1) setInterval(() => show(idx + 1), 5000);
  }
})();
