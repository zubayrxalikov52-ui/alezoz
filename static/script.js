/* ==========================================================================
   ALLON CAFE - MENU & INTERACTIVE PAGE SCRIPT (script.js)
   ========================================================================== */

function initMenuApp() {
    // Kategoriya va nom bo'yicha yuqori sifatli barqaror taom rasmlari
    const stableImages = {
        burger: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=500&q=80",
        double: "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?auto=format&fit=crop&w=500&q=80",
        cheese: "https://images.unsplash.com/photo-1550547660-d9450f859349?auto=format&fit=crop&w=500&q=80",
        chicken: "https://images.unsplash.com/photo-1625813506062-0aeb1d7a094b?auto=format&fit=crop&w=500&q=80",
        pizza: "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?auto=format&fit=crop&w=500&q=80",
        lavash: "/static/banner_lavash.jpg",
        combo: "/static/banner_combo.jpg",
        osh: "/static/dish_osh.jpg",
        shashlik: "/static/dish_shashlik.jpg",
        salad: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=500&q=80",
        snack: "https://images.unsplash.com/photo-1576107232684-1279f3908594?auto=format&fit=crop&w=500&q=80",
        drink: "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=500&q=80",
        dessert: "https://images.unsplash.com/photo-1551024601-bec78aea704b?auto=format&fit=crop&w=500&q=80"
    };

    function getFallbackForCard(img) {
        const alt = (img.alt || "").toLowerCase();
        const card = img.closest(".food-card");
        const cat = card ? (card.dataset.category || "").toLowerCase() : "";

        if (alt.includes("osh") || alt.includes("palov")) return stableImages.osh;
        if (alt.includes("shashlik") || alt.includes("kabob")) return stableImages.shashlik;
        if (alt.includes("lavash") || alt.includes("donar") || alt.includes("donarchi")) return stableImages.lavash;
        if (alt.includes("combo") || alt.includes("piramida") || alt.includes("qanot")) return stableImages.combo;
        if (alt.includes("double") || alt.includes("dabl")) return stableImages.double;
        if (alt.includes("cheese") || alt.includes("chiz")) return stableImages.cheese;
        if (alt.includes("chicken") || alt.includes("tovuq")) return stableImages.chicken;
        if (alt.includes("pizza") || alt.includes("pitsa")) return stableImages.pizza;
        if (cat === "salad" || alt.includes("salat")) return stableImages.salad;
        if (cat === "snack" || alt.includes("fri") || alt.includes("kartoshka")) return stableImages.snack;
        if (cat === "drink" || alt.includes("cola") || alt.includes("choy") || alt.includes("sharbat")) return stableImages.drink;
        if (cat === "dessert" || alt.includes("cake") || alt.includes("donut") || alt.includes("waffle")) return stableImages.dessert;
        return stableImages.burger;
    }

    // Rasmlarni avtomatik yuqori sifatli va barqaror manbalar bilan almashtiramiz
    document.querySelectorAll(".food-card img").forEach(img => {
        if (!img.src || img.src.includes("loremflickr.com")) {
            img.src = getFallbackForCard(img);
        }
        img.addEventListener("error", function() {
            if (!this.dataset.fallbackApplied) {
                this.dataset.fallbackApplied = "true";
                this.src = getFallbackForCard(this);
            }
        });
    });

    const menuBtn = document.querySelector("#menu-btn");
    const menuDropdown = document.querySelector("#menu-dropdown");
    const categories = document.querySelectorAll(".category, .cat-pill");
    const foodList = document.querySelector("#food-list");
    const foodCards = Array.from(document.querySelectorAll(".food-card"));
    const plusButtons = document.querySelectorAll(".plus");
    const minusButtons = document.querySelectorAll(".minus");

    /* BANNER SLIDER */
    const bannerTrack = document.querySelector("#banner-track");
    const bannerSlides = document.querySelectorAll(".banner-slide");
    const bannerDots = document.querySelectorAll(".banner-dot");
    let currentBannerIndex = 0;
    let bannerInterval = null;

    function goToBanner(index) {
        if (!bannerTrack || bannerSlides.length <= 1) return;
        currentBannerIndex = (index + bannerSlides.length) % bannerSlides.length;
        bannerTrack.style.transform = `translateX(-${currentBannerIndex * 100}%)`;
        bannerDots.forEach((dot, idx) => {
            dot.classList.toggle("active", idx === currentBannerIndex);
        });
    }

    if (bannerTrack && bannerSlides.length > 1) {
        bannerDots.forEach((dot, idx) => {
            dot.addEventListener("click", () => {
                goToBanner(idx);
                resetBannerTimer();
            });
        });

        function startBannerTimer() {
            bannerInterval = setInterval(() => {
                goToBanner(currentBannerIndex + 1);
            }, 3000);
        }

        function resetBannerTimer() {
            clearInterval(bannerInterval);
            startBannerTimer();
        }

        startBannerTimer();

        // Touch Swipe
        let startX = 0;
        let isSwiping = false;
        bannerTrack.addEventListener("touchstart", (e) => {
            startX = e.touches[0].clientX;
            isSwiping = true;
        }, { passive: true });

        bannerTrack.addEventListener("touchend", (e) => {
            if (!isSwiping) return;
            isSwiping = false;
            const diffX = e.changedTouches[0].clientX - startX;
            if (Math.abs(diffX) > 40) {
                if (diffX < 0) {
                    goToBanner(currentBannerIndex + 1);
                } else {
                    goToBanner(currentBannerIndex - 1);
                }
                resetBannerTimer();
            }
        });
    }

    if (foodList && foodCards.length > 0) {
        /* BO'LIMLAR - EMOJILARSIZ TOZA MATN VA SVG */
        const groups = [
            { key: "food",    title: "Taomlar",     svg: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#e52d27" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>` },
            { key: "salad",   title: "Salatlar",    svg: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#10b981" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"></path><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"></path></svg>` },
            { key: "snack",   title: "Snacklar",    svg: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#f59e0b" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>` },
            { key: "drink",   title: "Ichimliklar", svg: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#3b82f6" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 8h1a4 4 0 1 1 0 8h-1"></path><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"></path><line x1="6" y1="2" x2="6" y2="4"></line><line x1="10" y1="2" x2="10" y2="4"></line><line x1="14" y1="2" x2="14" y2="4"></line></svg>` },
            { key: "dessert", title: "Desertlar",   svg: `<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#ec4899" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"></path><path d="M8 6h8"></path><path d="M4 10h16v11a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V10z"></path></svg>` }
        ];

        const titles = [];

        // Har bir bo'lim uchun toza sarlavha yaratamiz
        groups.forEach((group) => {
            const groupCards = foodCards.filter((card) => card.dataset.category === group.key);
            if (groupCards.length > 0) {
                const title = document.createElement("h2");
                title.className = "category-title";
                title.dataset.category = group.key;
                title.innerHTML = `${group.svg} <span>${group.title}</span>`;

                foodList.appendChild(title);
                titles.push(title);

                groupCards.forEach((card) => foodList.appendChild(card));
            }
        });

        /* FEED UP STYLE CARD ENHANCER (IMAGE WRAPPER, ROUND FLOATING PLUS, DISCOUNT BADGE) */
        const discountRates = [30, 24, 18, 15, 20, 25];
        foodCards.forEach((card, index) => {
            const img = card.querySelector("img");

            // 1. Image wrapper yaratish (agar yo'q bo'lsa)
            let imgWrap = card.querySelector(".food-card-img-wrap");
            if (!imgWrap && img) {
                imgWrap = document.createElement("div");
                imgWrap.className = "food-card-img-wrap";
                img.parentNode.insertBefore(imgWrap, img);
                imgWrap.appendChild(img);
            }

            // 2. Ortiqcha floating tugma olib tashlandi, faqat kartaning asosiy Savatga tugmasi ishlatiladi

            // 3. Chegirma yorlig'i va eski narx (har 3-taomga rasmdegidek chiroyli chegirma qo'shish)
            if (index % 3 === 0 && imgWrap && !card.querySelector(".food-badge-discount")) {
                const rate = discountRates[(index / 3) % discountRates.length];
                const badge = document.createElement("span");
                badge.className = "food-badge-discount";
                badge.textContent = `-${rate}%`;
                imgWrap.appendChild(badge);

                // Eski narxni hisoblash va ko'rsatish
                const strong = card.querySelector("strong");
                if (strong && !card.querySelector(".food-old-price")) {
                    const priceText = strong.textContent.trim();
                    const cleanPrice = parseInt(priceText.replace(/\D/g, "")) || 0;
                    if (cleanPrice > 0) {
                        const oldPrice = Math.round((cleanPrice / (1 - rate / 100)) / 1000) * 1000;
                        const oldPriceEl = document.createElement("span");
                        oldPriceEl.className = "food-old-price";
                        oldPriceEl.textContent = oldPrice.toLocaleString("uz-UZ");
                        strong.parentNode.insertBefore(oldPriceEl, strong);
                    }
                }
            }
        });

        /* KATEGORIYA TANLASH */
        const activeCatHeading = document.querySelector("#active-category-display, #menu-active-category-title");
        categories.forEach((category) => {
            category.addEventListener("click", () => {
                const selected = category.dataset.category;
                categories.forEach((item) => {
                    if (item.dataset.category === selected) {
                        item.classList.add("active");
                    } else {
                        item.classList.remove("active");
                    }
                });

                if (activeCatHeading) {
                    const rawName = category.textContent.trim().replace(/^[^a-zA-Z0-9а-яА-ЯёЁ]+/, "").trim();
                    activeCatHeading.textContent = rawName ? rawName.toUpperCase() : "AKSIYALAR";
                }

                // Sarlavhalar
                titles.forEach((title) => {
                    const visible = selected === "all" || title.dataset.category === selected;
                    title.style.display = visible ? "" : "none";
                });

                // Kartalar
                foodCards.forEach((card) => {
                    const visible = selected === "all" || card.dataset.category === selected;
                    card.style.display = visible ? "" : "none";
                });

                if (menuDropdown) menuDropdown.classList.remove("show");
            });
        });

        /* REAL-TIME HEADER SEARCH FILTER */
        const searchInput = document.querySelector("#menu-search-input");
        if (searchInput) {
            searchInput.addEventListener("input", (e) => {
                const query = e.target.value.trim().toLowerCase();
                foodCards.forEach(card => {
                    const h3 = card.querySelector("h3") ? card.querySelector("h3").textContent.toLowerCase() : "";
                    const p = card.querySelector("p") ? card.querySelector("p").textContent.toLowerCase() : "";
                    const matched = !query || h3.includes(query) || p.includes(query);
                    card.style.display = matched ? "" : "none";
                });
                titles.forEach(title => {
                    if (query) {
                        const cat = title.dataset.category;
                        const hasCards = foodCards.some(c => c.dataset.category === cat && c.style.display !== "none");
                        title.style.display = hasCards ? "" : "none";
                    } else {
                        title.style.display = "";
                    }
                });
            });
        }
    }

    /* MENYU TUGMASI */
    if (menuBtn && menuDropdown) {
        menuBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            menuDropdown.classList.toggle("show");
        });

        document.addEventListener("click", (event) => {
            if (!menuDropdown.contains(event.target) && event.target !== menuBtn) {
                menuDropdown.classList.remove("show");
            }
        });
    }

    /* CARD PRODUCT EXTRACTOR (STABLE UNIQUE ID) */
    function extractCardProduct(card) {
        if (!card.dataset.id) {
            const h3 = card.querySelector("h3");
            const rawTitle = (h3 ? h3.textContent.trim() : "").toLowerCase().replace(/[^a-z0-9]+/g, "-");
            card.dataset.id = rawTitle || ("item-" + Math.random().toString(36).substring(2, 7));
        }
        const id = card.dataset.id;
        const title = card.querySelector("h3") ? card.querySelector("h3").textContent.trim() : "Taom";
        const strong = card.querySelector("strong");
        const cleanPrice = strong ? (parseInt(strong.textContent.replace(/\D/g, "")) || 0) : 0;
        const img = card.querySelector("img") ? card.querySelector("img").src : "";
        const category = card.dataset.category || "food";
        return { id: id, slug: id, name: title, price: cleanPrice, image: img, category: category };
    }

    /* CARD CONTROLS INITIALIZER (USER REQUEST: Savatga tugmasini bossa + va - paydo bo'lsin) */
    function initCardControls() {
        document.querySelectorAll(".food-card").forEach(card => {
            const plusBtn = card.querySelector(".food-controls .plus");
            const minusBtn = card.querySelector(".food-controls .minus");

            if (plusBtn && !plusBtn.dataset.listenerBound) {
                plusBtn.dataset.listenerBound = "true";
                plusBtn.addEventListener("click", (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const prod = extractCardProduct(card);
                    if (typeof AllonApp !== "undefined") {
                        AllonApp.addToCart(prod);
                        syncCardQuantities();
                        renderSidebarCart();
                    }
                });
            }

            if (minusBtn && !minusBtn.dataset.listenerBound) {
                minusBtn.dataset.listenerBound = "true";
                minusBtn.addEventListener("click", (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const prod = extractCardProduct(card);
                    if (typeof AllonApp !== "undefined") {
                        AllonApp.updateQuantity(prod.id, -1);
                        syncCardQuantities();
                        renderSidebarCart();
                    }
                });
            }
        });
    }

    function syncCardQuantities() {
        const cart = (typeof AllonApp !== "undefined" && AllonApp.getCart) ? AllonApp.getCart() : [];
        const allCards = document.querySelectorAll(".food-card");
        allCards.forEach(card => {
            const prod = extractCardProduct(card);
            const item = cart.find(i => i.id == prod.id || i.slug == prod.slug || i.name == prod.name);
            const qty = item ? (item.quantity || 0) : 0;

            const qtyElem = card.querySelector(".quantity");
            if (qtyElem) {
                qtyElem.textContent = qty;
            }

            const controls = card.querySelector(".food-controls");
            if (controls) {
                if (qty > 0) {
                    controls.classList.add("has-qty");
                } else {
                    controls.classList.remove("has-qty");
                }
            }
        });

        // Bottom dock savat badge ni ham yangilaymiz
        const count = typeof AllonApp !== "undefined" ? AllonApp.getCartCount() : 0;
        document.querySelectorAll(".dock-cart-badge, .cart-count-badge").forEach(badge => {
            badge.textContent = count;
        });
    }

    function renderSidebarCart() {
        const cartList = document.querySelector("#cart-list");
        const totalElem = document.querySelector("#total");
        const cartCountElem = document.querySelector("#cart-count");

        if (!cartList) return;

        const cart = typeof AllonApp !== "undefined" ? AllonApp.getCart() : [];
        const total = typeof AllonApp !== "undefined" ? AllonApp.getCartTotal() : 0;
        const count = typeof AllonApp !== "undefined" ? AllonApp.getCartCount() : 0;
        const isRu = (typeof AllonApp !== "undefined" && AllonApp.getCurrentLanguage() === 'ru');
        const curr = isRu ? 'сум' : "so‘m";

        if (totalElem) totalElem.textContent = total.toLocaleString("uz-UZ");
        if (cartCountElem) cartCountElem.textContent = count;
        updateMobileFloatCart(count, total, isRu);

        if (cart.length === 0) {
            cartList.innerHTML = `
                <div class="empty-cart">
                    <span>🛒</span>
                    <h3>${isRu ? 'Корзина пуста' : 'Savat bo‘sh'}</h3>
                    <p>${isRu ? 'Выберите блюда из меню' : 'Menyudan taom tanlang'}</p>
                </div>
            `;
            return;
        }

        let html = "";
        cart.forEach(item => {
            const displayName = (typeof AllonApp !== "undefined" && AllonApp.translateItemName) ? AllonApp.translateItemName(item.name) : item.name;
            const delTitle = isRu ? 'Удалить' : 'O‘chirish';
            html += `
                <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.08);">
                    <div style="flex-grow:1; padding-right:10px;">
                        <strong style="display:block; font-size:14px; margin-bottom:2px; color:var(--white);">${displayName}</strong>
                        <small style="color:var(--gold); font-size:12px;">${item.price.toLocaleString("uz-UZ")} ${curr} × ${item.quantity}</small>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <div style="display:flex; align-items:center; gap:6px; background:rgba(255,255,255,0.06); padding:2px 6px; border-radius:14px;">
                            <button onclick="changeCartItem('${item.id}', -1)" style="border:none; background:transparent; color:#fff; cursor:pointer; font-size:14px; padding:0 4px;">−</button>
                            <span style="font-size:12px; min-width:14px; text-align:center; color:#fff;">${item.quantity}</span>
                            <button onclick="changeCartItem('${item.id}', 1)" style="border:none; background:transparent; color:#fff; cursor:pointer; font-size:14px; padding:0 4px;">+</button>
                        </div>
                        <button onclick="removeCartItem('${item.id}')" style="border:none; background:rgba(228,91,91,0.15); color:#e45b5b; width:24px; height:24px; border-radius:50%; cursor:pointer; font-size:12px; display:grid; place-items:center;" title="${delTitle}">✕</button>
                    </div>
                </div>
            `;
        });
        cartList.innerHTML = html;
    }

    window.addEventListener('appLanguageChanged', () => {
        renderSidebarCart();
    });

    window.changeCartItem = function(id, delta) {
        if (typeof AllonApp !== "undefined") {
            AllonApp.updateQuantity(id, delta);
            syncCardQuantities();
            renderSidebarCart();
        }
    };

    window.removeCartItem = function(id) {
        if (typeof AllonApp !== "undefined") {
            AllonApp.removeFromCart(id);
            syncCardQuantities();
            renderSidebarCart();
        }
    };

    /* PLUS & MINUS GLOBAL DELEGATED CLICK HANDLERS (BULLETPROOF) */
    document.addEventListener("click", (e) => {
        const plusBtn = e.target.closest(".plus");
        if (plusBtn) {
            e.preventDefault();
            e.stopPropagation();
            const card = plusBtn.closest(".food-card");
            if (card) {
                const prod = extractCardProduct(card);
                if (typeof AllonApp !== "undefined") {
                    AllonApp.addToCart(prod);
                    syncCardQuantities();
                    renderSidebarCart();
                }
            }
            return;
        }

        const minusBtn = e.target.closest(".minus");
        if (minusBtn) {
            e.preventDefault();
            e.stopPropagation();
            const card = minusBtn.closest(".food-card");
            if (card) {
                const prod = extractCardProduct(card);
                if (typeof AllonApp !== "undefined") {
                    AllonApp.updateQuantity(prod.id, -1);
                    syncCardQuantities();
                    renderSidebarCart();
                }
            }
            return;
        }

        // Kartaga bosilganda (agar tugmaga emas, rasm/matnga bosilsa va hali savatda yo'q bo'lsa)
        const clickedCard = e.target.closest(".food-card");
        if (clickedCard && !e.target.closest(".food-controls, .food-float-plus")) {
            const controls = clickedCard.querySelector(".food-controls");
            if (controls && !controls.classList.contains("has-qty")) {
                const prod = extractCardProduct(clickedCard);
                if (typeof AllonApp !== "undefined") {
                    AllonApp.addToCart(prod);
                    syncCardQuantities();
                    renderSidebarCart();
                }
            }
        }
    });

    /* ORDER BUTTON CLICK -> CHECKOUT */
    const orderBtn = document.querySelector("#order-btn");
    if (orderBtn) {
        orderBtn.addEventListener("click", () => {
            const count = typeof AllonApp !== "undefined" ? AllonApp.getCartCount() : 0;
            if (count === 0) {
                const isRu = (typeof AllonApp !== "undefined" && AllonApp.getCurrentLanguage() === 'ru');
                alert(isRu ? "Корзина пуста! Пожалуйста, сначала выберите блюда из меню." : "Savat bo‘sh! Iltimos, avval biror taom tanlang.");
                return;
            }
            window.location.href = "/checkout/";
        });
    }

    // Initialize cart sync & controls
    initCardControls();
    syncCardQuantities();
    renderSidebarCart();

    /* CART DRAWER & BOTTOM DOCK INTEGRATION */
    const cartAside = document.querySelector("aside.cart");
    // Header cart button opens the quick slide drawer
    const openCartBtns = document.querySelectorAll("#open-cart-btn, #header-cart-btn, .header-cart-btn, .oqtepa-cart-btn");

    let cartBackdrop = document.querySelector(".cart-backdrop");
    if (!cartBackdrop && cartAside) {
        cartBackdrop = document.createElement("div");
        cartBackdrop.className = "cart-backdrop";
        document.body.appendChild(cartBackdrop);
        cartBackdrop.addEventListener("click", closeCartDrawer);
    }

    if (cartAside && !cartAside.querySelector(".cart-close-btn")) {
        const cartHeader = cartAside.querySelector(".cart-header");
        if (cartHeader) {
            const closeBtn = document.createElement("button");
            closeBtn.type = "button";
            closeBtn.className = "cart-close-btn";
            closeBtn.innerHTML = "✕";
            closeBtn.setAttribute("aria-label", "Yopish");
            closeBtn.addEventListener("click", closeCartDrawer);
            cartHeader.appendChild(closeBtn);
        }
    }

    function openCartDrawer() {
        if (cartAside) cartAside.classList.add("open");
        if (cartBackdrop) cartBackdrop.classList.add("open");
    }

    function closeCartDrawer() {
        if (cartAside) cartAside.classList.remove("open");
        if (cartBackdrop) cartBackdrop.classList.remove("open");
    }

    window.openCartDrawer = openCartDrawer;
    window.closeCartDrawer = closeCartDrawer;

    openCartBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            if (window.location.pathname === "/cart" || window.location.pathname === "/cart/") return;
            e.preventDefault();
            openCartDrawer();
        });
    });

    // USER REQUEST: Pastdagi savat tugmasi to'g'ridan-to'g'ri savat sahifasiga kirishni ta'minlaydi
    const dockCartBtn = document.querySelector("#dock-cart-btn");
    if (dockCartBtn) {
        dockCartBtn.addEventListener("click", (e) => {
            // Agar link bo'lsa href bo'yicha ketadi, baribir kafolat uchun:
            window.location.href = "/cart";
        });
    }

    /* ==========================================================================
       BOTTOM DOCK FULL INTERACTIVITY (ALL BUTTONS 100% FUNCTIONAL)
       ========================================================================== */
    const dockHomeBtn = document.querySelector("#dock-home-btn");
    if (dockHomeBtn) {
        dockHomeBtn.addEventListener("click", (e) => {
            if (window.location.pathname.includes("/menu")) {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: "smooth" });
                // Reset category to 'all'
                const allPill = document.querySelector('.cat-pill[data-category="all"], .category[data-category="all"]');
                if (allPill) allPill.click();
                // Clear search
                const searchInp = document.querySelector("#menu-search-input");
                if (searchInp && searchInp.value) {
                    searchInp.value = "";
                    searchInp.dispatchEvent(new Event("input"));
                }
            }
        });
    }

    const dockSearchBtn = document.querySelector("#dock-search-btn");
    if (dockSearchBtn) {
        dockSearchBtn.addEventListener("click", (e) => {
            e.preventDefault();
            const searchInput = document.querySelector("#menu-search-input");
            if (searchInput) {
                searchInput.focus();
                searchInput.scrollIntoView({ behavior: "smooth", block: "center" });
                searchInput.style.outline = "2px solid #e52d27";
                searchInput.style.boxShadow = "0 0 16px rgba(229, 45, 39, 0.35)";
                setTimeout(() => {
                    searchInput.style.outline = "";
                    searchInput.style.boxShadow = "";
                }, 2000);
            } else {
                window.location.href = "/menu#search";
            }
        });
    }

    // CLOCHE / QUICK CATEGORY MODAL HANDLER
    const dockCatBtn = document.querySelector("#dock-categories-btn");
    const catModal = document.querySelector("#category-quick-modal");
    const catBackdrop = document.querySelector("#category-modal-backdrop");
    const catCloseBtn = document.querySelector("#cat-modal-close-btn");

    function openCategoryModal() {
        if (catModal) catModal.classList.add("open");
        if (catBackdrop) catBackdrop.classList.add("open");
    }

    function closeCategoryModal() {
        if (catModal) catModal.classList.remove("open");
        if (catBackdrop) catBackdrop.classList.remove("open");
    }

    if (dockCatBtn) {
        dockCatBtn.addEventListener("click", (e) => {
            e.preventDefault();
            if (catModal && catModal.classList.contains("open")) {
                closeCategoryModal();
            } else {
                openCategoryModal();
            }
        });
    }

    if (catCloseBtn) catCloseBtn.addEventListener("click", closeCategoryModal);
    if (catBackdrop) catBackdrop.addEventListener("click", closeCategoryModal);

    // Category modal card selection
    document.querySelectorAll(".cat-modal-item").forEach(item => {
        item.addEventListener("click", () => {
            const catSlug = item.dataset.category;
            document.querySelectorAll(".cat-modal-item").forEach(i => i.classList.remove("active"));
            item.classList.add("active");

            // Trigger corresponding category pill
            const targetPill = document.querySelector(`.cat-pill[data-category="${catSlug}"], .category[data-category="${catSlug}"]`);
            if (targetPill) {
                targetPill.click();
            }

            closeCategoryModal();

            // Smooth scroll to food list
            const foodListElem = document.querySelector("#food-list") || document.querySelector(".menu-products-section");
            if (foodListElem) {
                foodListElem.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });

    /* ==========================================================================
       NAVBAR MORE OPTIONS DROPDOWN (AS REQUESTED)
       ========================================================================== */
    const moreBtns = document.querySelectorAll(".navbar-more-btn, #navbar-more-btn, #m-navbar-more-btn");
    const moreDropdown = document.querySelector("#navbar-more-dropdown");
    const moreBackdrop = document.querySelector("#navbar-more-backdrop");
    const moreCloseBtn = document.querySelector("#more-menu-close-btn");

    function openMoreMenu() {
        if (moreDropdown) moreDropdown.classList.add("open");
        if (moreBackdrop) moreBackdrop.classList.add("open");
    }

    function closeMoreMenu() {
        if (moreDropdown) moreDropdown.classList.remove("open");
        if (moreBackdrop) moreBackdrop.classList.remove("open");
    }

    moreBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (moreDropdown && moreDropdown.classList.contains("open")) {
                closeMoreMenu();
            } else {
                openMoreMenu();
            }
        });
    });

    if (moreCloseBtn) moreCloseBtn.addEventListener("click", closeMoreMenu);
    if (moreBackdrop) moreBackdrop.addEventListener("click", closeMoreMenu);

    // USER REQUEST: Mobil topbar, qo'shimcha menyu va desktopdagi barcha til tugmalarini sinxronlashtirish
    function syncLanguageUI(lang) {
        document.querySelectorAll(".m-lang-btn, .more-lang-btn, .lang-btn-item").forEach(b => {
            b.classList.toggle("active", b.dataset.lang === lang);
        });
    }

    

    // Delivery / pickup switch inside more menu
    const moreDelDelivery = document.querySelector("#more-del-delivery");
    const moreDelPickup = document.querySelector("#more-del-pickup");
    if (moreDelDelivery && moreDelPickup) {
        moreDelDelivery.addEventListener("click", () => {
            moreDelDelivery.classList.add("active");
            moreDelPickup.classList.remove("active");
            const curDelivery = document.querySelector("#current-delivery-type");
            if (curDelivery) curDelivery.textContent = "Yetkazib berish";
            if (typeof AllonApp !== "undefined" && AllonApp.showToast) {
                AllonApp.showToast("🛵 Yetkazib berish tanlandi");
            }
        });
        moreDelPickup.addEventListener("click", () => {
            moreDelPickup.classList.add("active");
            moreDelDelivery.classList.remove("active");
            const curDelivery = document.querySelector("#current-delivery-type");
            if (curDelivery) curDelivery.textContent = "Olib ketish";
            if (typeof AllonApp !== "undefined" && AllonApp.showToast) {
                AllonApp.showToast("🛍 Olib ketish tanlandi");
            }
        });
    }

    // Delivery / Pickup toggler (both desktop pill and mobile bar)
    let isTakeaway = false;
    document.querySelectorAll("#delivery-select-trigger, .delivery-pill").forEach(trigger => {
        trigger.style.cursor = "pointer";
        trigger.addEventListener("click", () => {
            isTakeaway = !isTakeaway;
            const textEls = document.querySelectorAll("#current-delivery-type, .delivery-pill strong");
            textEls.forEach(el => {
                el.textContent = isTakeaway ? "Olib ketish" : "Yetkazib berish";
            });
            if (moreDelDelivery && moreDelPickup) {
                moreDelDelivery.classList.toggle("active", !isTakeaway);
                moreDelPickup.classList.toggle("active", isTakeaway);
            }
            if (typeof AllonApp !== "undefined" && AllonApp.showToast) {
                AllonApp.showToast(isTakeaway ? "🛍 Olib ketish tanlandi" : "🛵 Yetkazib berish tanlandi");
            }
        });
    });

    // Region pill (Toshkent)
    document.querySelectorAll(".region-pill").forEach(pill => {
        pill.style.cursor = "pointer";
        pill.addEventListener("click", () => {
            if (typeof AllonApp !== "undefined" && AllonApp.showToast) {
                AllonApp.showToast("📍 Yetkazib berish hududi: Toshkent shahri bo‘ylab 24/7");
            }
        });
    });

    // Bell notification button
    const bellBtn = document.querySelector("#bell-notif-btn");
    if (bellBtn) {
        bellBtn.addEventListener("click", () => {
            if (typeof AllonApp !== "undefined" && AllonApp.showToast) {
                AllonApp.showToast("🔔 3 ta yangi aksiya: Burgerlar va pitsalarga 20% gacha chegirma!");
            }
        });
    }

    // Avatar button
    const avatarBtn = document.querySelector(".m-feedup-avatar");
    if (avatarBtn) {
        avatarBtn.addEventListener("click", () => {
            if (typeof AllonApp !== "undefined" && AllonApp.showToast) {
                AllonApp.showToast("👤 Al Ezoz mijoz kabineti faol!");
            }
        });
    }

    // Mobile floating cart widget (Dock bilan uyg'unlashtirilgan)
    let floatCartBar = document.querySelector(".mobile-float-cart");
    if (!floatCartBar) {
        floatCartBar = document.createElement("div");
        floatCartBar.className = "mobile-float-cart";
        floatCartBar.innerHTML = `
            <div class="m-cart-info">
                <span class="m-cart-badge">🛒 <b id="m-float-count">0</b></span>
                <span class="m-cart-total"><b id="m-float-total">0</b> so‘m</span>
            </div>
            <button type="button" class="m-cart-order-btn">Zakaz berish →</button>
        `;
        floatCartBar.addEventListener("click", (e) => {
            e.preventDefault();
            openCartDrawer();
        });
        document.body.appendChild(floatCartBar);
    }

    function updateMobileFloatCart(count, total, isRu) {
        if (!floatCartBar) return;
        const curCount = (count !== undefined) ? count : (typeof AllonApp !== "undefined" ? AllonApp.getCartCount() : 0);
        const curTotal = (total !== undefined) ? total : (typeof AllonApp !== "undefined" ? AllonApp.getCartTotal() : 0);
        const isRussian = (isRu !== undefined) ? isRu : (typeof AllonApp !== "undefined" && AllonApp.getCurrentLanguage() === 'ru');
        
        const countEl = document.querySelector("#m-float-count");
        const totalEl = document.querySelector("#m-float-total");
        const orderBtnEl = floatCartBar.querySelector(".m-cart-order-btn");
        
        if (countEl) countEl.textContent = curCount;
        if (totalEl) totalEl.textContent = curTotal.toLocaleString("uz-UZ");
        if (orderBtnEl) orderBtnEl.textContent = isRussian ? "Оформить заказ →" : "Zakaz berish →";
        
        if (curCount > 0) {
            floatCartBar.classList.add("visible");
        } else {
            floatCartBar.classList.remove("visible");
        }
    }
    window.updateMobileFloatCart = updateMobileFloatCart;
    updateMobileFloatCart();

    /* KATEGORIYA CHIPLARIDAN EMOJILARNI TOZALASH (FEED UP STYLE) */
    document.querySelectorAll(".cat-pill").forEach(pill => {
        pill.childNodes.forEach(node => {
            if (node.nodeType === Node.TEXT_NODE) {
                node.textContent = node.textContent.replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '').trim();
            }
        });
        const iconSpan = pill.querySelector("span:not(.cat-label)");
        if (iconSpan && iconSpan.textContent.trim() !== "%") {
            const txt = iconSpan.textContent.trim();
            if (/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u.test(txt)) {
                iconSpan.style.display = "none";
            }
        }
    });

    /* STICKY HEADER & LOGO ANIMATION ON SCROLL */
    const siteHeader = document.querySelector(".header") || document.querySelector("#main-header");
    if (siteHeader) {
        const handleHeaderScroll = () => {
            if (window.scrollY > 20) {
                siteHeader.classList.add("is-scrolled");
            } else {
                siteHeader.classList.remove("is-scrolled");
            }
        };
        window.addEventListener("scroll", handleHeaderScroll, { passive: true });
        handleHeaderScroll();
    }

    /* GLOBAL ESC KEY — CLOSE ANY OPEN OVERLAY */
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" || e.key === "Esc") {
            if (typeof closeMoreMenu === "function") closeMoreMenu();
            if (typeof closeCategoryModal === "function") closeCategoryModal();
            if (typeof closeCartDrawer === "function") closeCartDrawer();
        }
    });

    /* SAFETY: close all overlays on page load/show to avoid stale open state */
    window.addEventListener("pageshow", () => {
        [
            "#navbar-more-dropdown", "#navbar-more-backdrop",
            "#category-quick-modal", "#category-modal-backdrop",
            "aside.cart", ".cart-backdrop"
        ].forEach(sel => {
            const el = document.querySelector(sel);
            if (el) el.classList.remove("open");
        });
    });

} // END initMenuApp

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMenuApp);
} else {
    initMenuApp();
}