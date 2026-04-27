function filterProducts() {
  searchQuery = document.getElementById("navSearch").value.toLowerCase();
  document.getElementById("heroSearch").value = searchQuery;
  activeCondition = null;
  renderProducts();
  if (searchQuery) scrollToProducts();
}

function syncHeroSearch() {
  document.getElementById("navSearch").value = document.getElementById("heroSearch").value;
}

function doHeroSearch() {
  searchQuery = document.getElementById("heroSearch").value.toLowerCase();
  document.getElementById("navSearch").value = searchQuery;
  activeCondition = null;
  renderProducts();
  scrollToProducts();
}

function filterByCategory(cat, btn) {
  activeCategory = cat;
  activeCondition = null;
  document.querySelectorAll(".cat-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  renderProducts();
  scrollToProducts();
}

function filterByCondition(cond) {
  activeCondition = activeCondition === cond ? null : cond;
  activeCategory = "all";
  document.querySelectorAll(".cat-btn").forEach(b => b.classList.remove("active"));
  document.querySelector(".cat-btn").classList.add("active");
  searchQuery = "";
  document.getElementById("navSearch").value = "";
  renderProducts();
  scrollToProducts();
}

function scrollToProducts() {
  document.getElementById("products").scrollIntoView({ behavior: "smooth", block: "start" });
}
