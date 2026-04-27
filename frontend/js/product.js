const products = [
  { id:1, name:"Dolo 650", brand:"Micro Labs", price:30, mrp:35, category:"essentials", condition:"pain", img:"💊", badge:"Bestseller" },
  { id:2, name:"Crocin Advance", brand:"GSK", price:45, mrp:50, category:"essentials", condition:"pain", img:"💊", badge:"Popular" },
  { id:3, name:"Azithromycin 500mg", brand:"Cipla", price:120, mrp:150, category:"essentials", condition:"immunity", img:"💉", badge:"Rx", badgeType:"rx" },
  { id:4, name:"Glycomet 500", brand:"USV", price:38, mrp:45, category:"essentials", condition:"diabetes", img:"💊", badge:"Rx", badgeType:"rx" },
  { id:5, name:"Omeprazole 20mg", brand:"Sun Pharma", price:55, mrp:70, category:"essentials", condition:"stomach", img:"💊" },
  { id:6, name:"Cetirizine 10mg", brand:"Cipla", price:25, mrp:30, category:"essentials", condition:"immunity", img:"💊", badge:"OTC" },
  { id:7, name:"Volini Gel 30g", brand:"Sanofi", price:115, mrp:135, category:"personal", condition:"pain", img:"🧴", badge:"Bestseller" },
  { id:8, name:"Burnol Cream", brand:"Boots", price:85, mrp:95, category:"personal", condition:"pain", img:"🧴" },
  { id:9, name:"Himalaya Septilin", brand:"Himalaya", price:130, mrp:155, category:"ayurveda", condition:"immunity", img:"🌿", badge:"Herbal" },
  { id:10, name:"Dabur Chyawanprash", brand:"Dabur", price:260, mrp:295, category:"ayurveda", condition:"immunity", img:"🫙", badge:"Popular" },
  { id:11, name:"Ensure Nutrition", brand:"Abbott", price:740, mrp:830, category:"nutrition", img:"🥛", badge:"Bestseller" },
  { id:12, name:"Protinex Original", brand:"Danone", price:490, mrp:550, category:"nutrition", img:"🥛" },
  { id:13, name:"Pampers Diapers M", brand:"P&G", price:550, mrp:620, category:"baby", img:"👶", badge:"Popular" },
  { id:14, name:"Johnson Baby Oil", brand:"J&J", price:180, mrp:200, category:"baby", img:"🍼" },
  { id:15, name:"Stayfree Secure", brand:"J&J", price:65, mrp:75, category:"women", img:"🌸", badge:"Trusted" },
  { id:16, name:"Glucometer FreeStyle", brand:"Abbott", price:1299, mrp:1599, category:"devices", condition:"diabetes", img:"📱", badge:"Top Rated" },
  { id:17, name:"BP Monitor Digital", brand:"Omron", price:2199, mrp:2799, category:"devices", condition:"cardiac", img:"🩺", badge:"Doctor's Choice" },
  { id:18, name:"Liv 52 DS", brand:"Himalaya", price:150, mrp:175, category:"ayurveda", condition:"liver", img:"🌿", badge:"Herbal" },
  { id:19, name:"Vicks VapoRub 25g", brand:"P&G", price:75, mrp:88, category:"essentials", condition:"respiratory", img:"💊", badge:"OTC" },
  { id:20, name:"Sensodyne Toothpaste", brand:"GSK", price:160, mrp:190, category:"personal", condition:"oral", img:"🦷", badge:"Dentist Rec." },
];

let cart = JSON.parse(localStorage.getItem("medi_cart")) || [];
let activeCategory = "all";
let activeCondition = null;
let searchQuery = "";

function renderProducts() {
  const grid = document.getElementById("productGrid");
  let filtered = products;

  if (activeCategory !== "all") filtered = filtered.filter(p => p.category === activeCategory);
  if (activeCondition) filtered = filtered.filter(p => p.condition === activeCondition);
  if (searchQuery) filtered = filtered.filter(p =>
    p.name.toLowerCase().includes(searchQuery) ||
    p.brand.toLowerCase().includes(searchQuery)
  );

  document.getElementById("prodCount").textContent = `${filtered.length} products found`;

  if (!filtered.length) {
    grid.innerHTML = `<div class="no-results"><i class="fa-solid fa-box-open"></i><p>No products found. Try a different search.</p></div>`;
    return;
  }

  grid.innerHTML = filtered.map(p => {
    const disc = Math.round((1 - p.price / p.mrp) * 100);
    const item = cart.find(c => c.id === p.id);
    const qty = item ? item.qty : 0;

    const badgeHtml = p.badge
      ? `<span class="product-badge ${p.badgeType||''}">${p.badge}</span>`
      : '';

    const ctaHtml = qty === 0
      ? `<button class="btn-add" onclick="addToCart(${p.id})">Add to Cart</button>`
      : `<div class="qty-control">
            <button class="qty-btn" onclick="changeQty(${p.id},-1)">−</button>
            <span class="qty-val">${qty}</span>
            <button class="qty-btn" onclick="changeQty(${p.id},1)">+</button>
            <button class="btn-remove" onclick="removeFromCart(${p.id})" title="Remove"><i class="fa-solid fa-trash"></i></button>
          </div>`;

    return `<div class="product-card">
      ${badgeHtml}
      <div style="font-size:32px;margin-bottom:4px;">${p.img}</div>
      <div class="product-name">${p.name}</div>
      <div class="product-brand">${p.brand}</div>
      <div style="display:flex;align-items:baseline;gap:8px;margin-top:4px;">
        <span class="product-price">₹${p.price}</span>
        <span class="product-mrp">₹${p.mrp}</span>
        <span class="product-discount">${disc}% off</span>
      </div>
      ${ctaHtml}
    </div>`;
  }).join('');
}