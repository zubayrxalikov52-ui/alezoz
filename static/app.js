/* ==========================================================================
   ALLON CAFE - SHARED CLIENT CORE (app.js)
   Version: 202610101241
   Synchronizes Cart, Theme, Mobile Navigation, Language, and Toasts
   ========================================================================== */

const AllonApp = (function() {
    // 1. CART MANAGEMENT (localStorage based)
    const CART_STORAGE_KEY = 'allon_cafe_cart_v1';

    function getCart() {
        try {
            return JSON.parse(localStorage.getItem(CART_STORAGE_KEY) || '[]');
        } catch (e) {
            return [];
        }
    }

    function saveCart(cart) {
        try {
            localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
        } catch (e) {}
        updateCartBadges();
    }

    function addToCart(product) {
        const cart = getCart();
        const existing = cart.find(item => item.id == product.id || item.slug == product.slug);
        if (existing) {
            existing.quantity = (existing.quantity || 1) + 1;
        } else {
            cart.push({
                id: product.id,
                slug: product.slug || ('prod-' + product.id),
                name: product.name,
                price: Number(product.price) || 0,
                image: product.image || '',
                quantity: 1
            });
        }
        saveCart(cart);
        showToast(`✅ "${product.name}" savatga qo‘shildi!`);
        return cart;
    }

    function updateQuantity(productId, change) {
        let cart = getCart();
        const item = cart.find(i => i.id == productId || i.slug == productId);
        if (item) {
            item.quantity += change;
            if (item.quantity <= 0) {
                cart = cart.filter(i => i !== item);
            }
        }
        saveCart(cart);
        return cart;
    }

    function removeFromCart(productId) {
        let cart = getCart();
        cart = cart.filter(i => i.id != productId && i.slug != productId);
        saveCart(cart);
        showToast('🗑 Mahsulot savatdan olib tashlandi');
        return cart;
    }

    function clearCart() {
        saveCart([]);
        updateCartBadges();
    }

    function getCartTotal() {
        const cart = getCart();
        return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    }

    function getCartCount() {
        const cart = getCart();
        return cart.reduce((count, item) => count + (item.quantity || 1), 0);
    }

    function updateCartBadges() {
        const count = getCartCount();
        document.querySelectorAll('.cart-count-badge, .cart-nav-badge, #cart-count').forEach(el => {
            el.textContent = count;
        });
    }

    // 2. PERMANENT WHITE (OQTEPA) THEME — Theme switcher removed
    function initTheme() {
        // Always use the clean white theme; clear any old saved theme
        document.body.removeAttribute("data-theme");
        try { localStorage.removeItem("cafe-theme"); } catch (e) {}
        // Remove any leftover theme-dropdown that may have been injected before
        const old = document.querySelector(".theme-dropdown");
        if (old) old.remove();
    }

    // 3. TOAST NOTIFICATIONS
    function showToast(message, duration = 3000) {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerHTML = `<span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = '0.3s';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    // 4. MOBILE DRAWER NAVIGATION
    function initMobileNav() {
        const toggles = document.querySelectorAll('.mobile-nav-toggle');
        const drawer = document.querySelector('.mobile-drawer');
        const backdrop = document.querySelector('.drawer-backdrop');
        const closeBtn = document.querySelector('.drawer-close');

        if (!drawer) return;

        function openDrawer() {
            drawer.classList.add('open');
            if (backdrop) backdrop.classList.add('open');
        }

        function closeDrawer() {
            drawer.classList.remove('open');
            if (backdrop) backdrop.classList.remove('open');
        }

        toggles.forEach(btn => btn.addEventListener('click', openDrawer));
        if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
        if (backdrop) backdrop.addEventListener('click', closeDrawer);
    }

    // 5. LANGUAGE SWITCHER (UZ / RU)
    const LANG_STORAGE_KEY = 'allon_cafe_lang_v1';

    const translations = {
        uz: {
            // Navigation
            "nav.home": "Bosh sahifa",
            "nav.menu": "Menyu",
            "nav.promos": "Aksiyalar",
            "nav.about": "Biz haqimizda",
            "nav.branches": "Filiallar",
            "nav.contact": "Kontaktlar",
            "nav.cart": "Savat",
            "header.deliveryType": "Yetkazib berish yoki olib ketish",
            "header.delivery": "Yetkazib berish",
            "header.region": "Hudud",
            "header.city": "Toshkent",
            "header.login": "Kirish",
            "header.searchPlaceholder": "Qidirish...",
            "menu.categoriesTitle": "Kategoriyalar",
            "table.welcome": "Xush kelibsiz!",
            "menu.heroTitle": "Mazali taomlar <br><span>yaxshi kayfiyat.</span>",
            "nav.admin": "🔐 Admin Panel",
            "nav.chef": "👨‍🍳 Oshpaz Paneli",

            // Footer
            "footer.desc": "Toshkent markazidagi eng mazali taomlar, yuqori darajadagi xizmat va shinam muhit maskani.",
            "footer.pages": "Sahifalar",
            "footer.hoursTitle": "Ish tartibi",
            "footer.hoursDays": "Dushanba – Yakshanba",
            "footer.kitchenClose": "Oshxona yopilishi: 22:30",
            "footer.contactTitle": "Bog‘lanish",
            "footer.address": "📍 Toshkent sh., Amir Temur shoh ko‘chasi, 42-uy",
            "footer.bot": "✈️ Telegram boti",
            "footer.copy": "© 2026 Al Ezoz. Barcha huquqlar himoyalangan.",
            "footer.slogan": "🍃 Yaxshi taom — yaxshi kayfiyat!",

            // Home Page
            "hero.badge": "⚡ PREMIYAL LAZZAT VA SHINAMLIK",
            "hero.title": "Mazali taomlar,",
            "hero.titleAccent": "unutilmas kayfiyat.",
            "hero.description": "Al Ezoz — eng saralangan tabiiy masalliqlar, mohir oshpazlar mahorati va o‘zgacha muhit uyg‘unligi. Biz bilan har bir daqiqangiz mazali xotiraga aylanadi.",
            "hero.viewMenu": "🍽 Menyuni ko‘rish",
            "hero.viewCart": "🛒 Savatni ko‘rish",
            "feat.fastDelivery": "Tezkor Yetkazib berish",
            "feat.fastDeliveryDesc": "Shahar bo‘ylab issiq holda 40 daqiqa ichida",
            "feat.halal": "100% Halol & Sof",
            "feat.halalDesc": "Faqat saralangan tabiiy masalliqlar",
            "feat.chefs": "Usta Oshpazlar",
            "feat.chefsDesc": "Har bir taom o‘zgacha mehr bilan tayyorlanadi",
            "section.categoriesLabel": "KATEGORIYALAR",
            "section.categoriesTitle": "Oshxonamiz",
            "section.categoriesTitleAccent": "yo‘nalishlari",
            "section.categoriesSubtitle": "O‘zingizga yoqqan taomlar bo‘limini tanlang va tezkor buyurtma bering",
            "section.popularLabel": "SARALANGAN TAOMLAR",
            "section.popularTitle": "Oshxonamiz durdonalari",
            "section.popularSubtitle": "Eng mashhur va sevimli taomlarimizni tatib ko‘ring",
            "btn.allDishes": "Barcha taomlarni ko‘rish",

            // About Page
            "about.teamSub": "Hikoyamiz & Jamoa",
            "about.welcome": "BIZNING HIKOYAMIZ",
            "about.heroTitle": "Mazali taom — bu shunchaki yegulik emas, <br><span style=\"color:var(--gold); font-family:Georgia, serif; font-style:italic;\">bu san’at asari.</span>",
            "about.p1": "Al Ezoz o‘z faoliyatini har bir mehmonga uy shinamligini va jahon andozalaridagi premium taomlar lazzatini tortiq etish maqsadi bilan boshlagan.",
            "about.p2": "Biz faqatgina saralangan, 100% tabiiy va yangi masalliqlardan foydalanamiz. Bizning oshxonamizda har bir sous qo‘lda tayyorlanadi, har bir go‘sht nozik did bilan tanlanadi va har bir taom mehr bilan taqdim etiladi.",
            "about.statYears": "Yillik tajriba",
            "about.statGuests": "Mamnun mehmonlar",
            "about.statHalal": "Halol masalliqlar",
            "about.valuesSmall": "QADRIYATLARIMIZ",
            "about.valuesTitle": "Biz nimaga <span>ishonamiz?</span>",
            "about.val1Title": "Sof & Yangi Go‘sht",
            "about.val1Desc": "Hech qanday muzlatilgan yoki sun’iy qo‘shimchalar yo‘q. Faqat kunlik yangi, sara mol va tovuq go‘shti.",
            "about.val2Title": "Tajribali Oshpazlar",
            "about.val2Desc": "Har bir taom o‘z sohasining ustalari tomonidan mualliflik retseptlari asosida tayyorlanadi.",
            "about.val3Title": "Tezkor & Issiq Yetkazish",
            "about.val3Desc": "Maxsus termobokslar orqali buyurtmangiz xuddi pechdan chiqqandek issiq va xushbo‘y yetib boradi.",

            // About Location & Map
            "about.locationBadge": "BIZNING MANZILIMIZ",
            "about.locationTitle": "Bizni xaritada <span>oson toping</span>",
            "about.locationSubtitle": "Toshkent markazida siz va yaqinlaringiz uchun shinam va mazali maskan",
            "about.addressLabel": "Aniq manzilimiz",
            "about.addressVal": "Toshkent shahri, Shayxontohur tumani, Qoratosh ko'chasi",
            "about.orientLabel": "Mo'ljal",
            "about.orientVal": "1-sonli shahar klinik shifoxonasi yaqinida",
            "about.hoursLabel": "Ish tartibi",
            "about.hoursVal": "Har kuni: 09:00 — 23:00 (Oshxona: 22:30 gacha)",
            "about.phoneLabel": "Telefon va Aloqa",
            "about.deliveryLabel": "Yetkazib berish xizmati",
            "about.deliveryVal": "Toshkent shahri bo'ylab issiq va tezkor yetkazib beramiz",
            "about.btnGoogleMaps": "Google Maps",
            "about.btnYandexMaps": "Yandex Xarita",
            "about.btnCall": "Qo'ng'iroq qilish",
            "about.btnRoute": "Yo'nalish olish (Marshrut)",
            "about.btnMenu": "Taomlar menyusi",
            "about.mapOpenNow": "Hozir ochiq • 09:00 - 23:00",

            "category.food": "Taomlar",
            "category.foodDesc": "Burgerlar va Issiq taomlar",
            "category.salad": "Salatlar",
            "category.saladDesc": "Yangi va Parhezbop",
            "category.snack": "Snacklar",
            "category.snackDesc": "Qarsildoq yeguliklar",
            "category.drink": "Ichimliklar",
            "category.drinkDesc": "Kokteyl va Qahvalar",
            "category.dessert": "Desertlar",
            "category.dessertDesc": "Shirinlik va Pirojniylar",

            // Contact Page
            "contact.welcome": "BIZ BILAN BOG‘LANING",
            "contact.title": "Savollaringiz bormi? <span style=\"color:var(--gold); font-family:Georgia,serif; font-style:italic;\">Biz doimo yordamga tayyormiz!</span>",
            "contact.infoTitle": "Aloqa ma’lumotlari",
            "contact.addrLabel": "Manzilimiz",
            "contact.landmark": "Mo‘ljal: Amir Temur xiyoboni",
            "contact.phoneLabel": "Telefon raqam",
            "contact.deliveryHours": "Yetkazib berish xizmati: 09:00 — 23:00",
            "contact.socialLabel": "Ijtimoiy tarmoqlar & Bot",
            "contact.formTitle": "Bizga xabar qoldiring",
            "contact.formSubtitle": "Taklif, mulohaza yoki stol band qilish bo‘yicha xabar yuboring, administratorimiz tezda siz bilan bog‘lanadi.",
            "form.nameLabel": "Ismingiz *",
            "form.namePlaceholder": "Masalan: Sardor Alimov",
            "form.phoneLabel": "Telefon raqamingiz *",
            "form.subjectLabel": "Mavzu",
            "form.subjectPlaceholder": "Stol band qilish, taklif yoki savol...",
            "form.messageLabel": "Xabaringiz *",
            "form.messagePlaceholder": "Xabaringiz matnini bu yerga yozing...",
            "form.submit": "Xabarni yuborish",

            // Menu Page
            "menu.title": "Mazali taomlar",
            "menu.titleAccent": "yaxshi kayfiyat.",
            "menu.desc": "Menyudan istagan taomingizni tanlang va buyurtmangizni savatga qo‘shing.",
            "search_placeholder": "Taomlarni qidirish...",

            // Cart Page & Sidebar
            "cart.title": "Savat",
            "cart.pageTitle": "Savatingiz",
            "cart.empty": "Savat bo‘sh",
            "cart.emptyDesc": "Menyudan taom tanlang",
            "cart.emptyPrompt": "Bizning mazali taomlarimiz bilan tanishib, o‘zingizga yoqqanini tanlang!",
            "cart.selectedItems": "Tanlangan taomlar",
            "cart.subtotal": "Oraliq summa:",
            "cart.delivery": "Yetkazib berish:",
            "cart.deliveryNotice": "admin bilan kelishiladi (100k dan yuqori)",
            "cart.total": "Jami:",
            "cart.totalPay": "Jami to‘lov:",
            "cart.checkout": "Zakaz berish",
            "cart.toCheckout": "Buyurtma berish",
            "cart.clear": "Savatni tozalash",
            "cart.continueShopping": "Menyuni ko‘rish",
            "cart.orderInfo": "◷ Buyurtma oshxonaga yuboriladi",

            "cart.badge": "XARIDLAR",
            "cart.yourCart": "Sizning",
            "cart.yourCartAccent": "Savatingiz",
            "cart.addMore": "Yana taom qo’shish",
            "cart.itemCount": "Mahsulotlar soni:",
            "checkout.badge": "RASMIYLASHTIRISH",
            "checkout.pageTitleAccent": "berish",
            "offer.badge": "MAXSUS TAKLIF",
            "offer.title": "Burger & Drink Combo Set",
            "offer.desc": "Classic Burger, Frantsuz fri kartoshkasi va muzdek ichimlik maxsus narxda. Har kuni soat 12:00 dan 16:00 gacha 20% chegirma!",
            "offer.btn": "Buyurtma berish",
            "hero.stat1": "Sara taomlar",
            "hero.stat2": "Halol & Yangi",
            "hero.stat3": "O’rtacha tayyorlash",
            "contact.headerSub": "Aloqa & Manzil",
            "contact.workHours": "Ish vaqti",
            "contact.workHoursLine": "Dushanba – Yakshanba: <strong>09:00 — 23:00</strong>",
            "status.badge": "BUYURTMA KUZATUVI",
            "status.trackingSub": "Kuzatuv tizimi",
            "status.itemsTitle": "Taomlar ro’yxati",
            "status.orderType": "Turi:",
            "status.backMenu": "Menyuga qaytish",
            "section.popularTitleAccent": "sevgan taomlar",

            
            // Checkout Page
            "checkout.pageTitle": "Buyurtma",
            "checkout.step1": "1. Buyurtma turi",
            "checkout.typeDelivery": "Yetkazib berish (Kuryer)",
            "checkout.typePickup": "Olib ketish (Restorandan)",
            "checkout.step2": "2. Mijoz ma’lumotlari",
            "checkout.telegramNotice": "Buyurtma yuborilgach, Telegram botimizga <b>/start</b> yuboring — 6 xonali tasdiqlash kodi keladi.",
            "checkout.nameLabel": "Ismingiz *",
            "checkout.namePlaceholder": "Masalan: Sardor Alimov",
            "checkout.phoneLabel": "Telefon raqamingiz *",
            "checkout.tgLabel": "Telegram username (ixtiyoriy)",
            "checkout.tgPlaceholder": "@username",
            "checkout.addrLabel": "Yetkazib berish manzili *",
            "checkout.addrPlaceholder": "Toshkent sh., Yunusobod tumani, 12-uy...",
            "checkout.mapLabel": "Xaritadan joyingizni tanlang (kuryer uchun)",
            "checkout.myLocation": "📍 Mening joylashuvim",
            "checkout.commentLabel": "Oshxona va kuryer uchun izoh (ixtiyoriy)",
            "checkout.commentPlaceholder": "Piyozsiz bo‘lsin, domofon kodi 45, eshik oldida qoldiring va h.k.",
            "checkout.tableCheckbox": "Men restoranning o‘zida stolda o‘tiribman",
            "checkout.tableLabel": "Stol raqami",
            "checkout.tablePlaceholder": "Masalan: Stol №7",
            "checkout.confirmBtn": "Buyurtmani tasdiqlash",
            "checkout.summaryTitle": "Buyurtma tarkibi",
            "checkout.subtotal": "Oraliq summa:",
            "checkout.deliveryService": "Yetkazib berish xizmati:",
            "checkout.deliveryFree": "admin bilan kelishiladi",
            "checkout.totalLabel": "Jami summa:",
            "checkout.guarantee": "🛡 Buyurtma yuborilgach, darhol administrator va oshxona KDS ekraniga uzatiladi hamda Telegram bot orqali bildirishnoma boradi.",

            // Order Status Page
            "status.pageTitle": "Buyurtma holati",
            "status.orderNum": "Buyurtma raqami",
            "status.trackingCode": "Kuzatuv kodi",
            "status.stepPending": "Qabul qilindi",
            "status.stepConfirmed": "Tasdiqlandi",
            "status.stepPreparing": "Tayyorlanmoqda",
            "status.stepReady": "Yetkazilmoqda",
            "status.stepDelivered": "Yetkazildi",
            "status.detailsTitle": "Buyurtma tafsilotlari",
            "status.custName": "Mijoz ismi:",
            "status.custPhone": "Telefon:",
            "status.custAddress": "Manzil / Stol:",
            "status.payMethod": "To'lov turi:",
            "status.callRest": "Restoranga qo'ng'iroq qilish",

            // Categories
            "group.food": "🍽 Taomlar",
            "group.salad": "🥗 Salatlar",
            "group.snack": "🍟 Snacklar",
            "group.drink": "🥤 Ichimliklar",
            "group.dessert": "🍰 Desertlar",

            "categories": {
                all: "Barchasi",
                food: "Taomlar",
                salad: "Salatlar",
                snack: "Snacklar",
                drink: "Ichimliklar",
                dessert: "Desertlar"
            }
        },
        ru: {
            // Navigation
            "nav.home": "Главная",
            "nav.menu": "Меню",
            "nav.promos": "Акции",
            "nav.about": "О нас",
            "nav.branches": "Филиалы",
            "nav.contact": "Контакты",
            "nav.cart": "Корзина",
            "header.deliveryType": "Доставка или еда навынос",
            "header.delivery": "Доставка",
            "header.region": "Регион",
            "header.city": "Ташкент",
            "header.login": "Войти",
            "header.searchPlaceholder": "Поиск...",
            "menu.categoriesTitle": "Категории",
            "table.welcome": "Добро пожаловать!",
            "menu.heroTitle": "Вкусные блюда <br><span>отличное настроение.</span>",
            "nav.admin": "🔐 Админ панель",
            "nav.chef": "👨‍🍳 Панель повара",

            // Footer
            "footer.desc": "Центр изысканных вкусов, первоклассного обслуживания и душевного уюта в сердце Ташкента.",
            "footer.pages": "Страницы",
            "footer.hoursTitle": "Режим работы",
            "footer.hoursDays": "Понедельник – Воскресенье",
            "footer.kitchenClose": "Кухня закрывается в 22:30",
            "footer.contactTitle": "Контакты",
            "footer.address": "📍 г. Ташкент, проспект Амира Темура, д. 42",
            "footer.bot": "✈️ Telegram бот",
            "footer.copy": "© 2026 Al Ezoz. Все права защищены.",
            "footer.slogan": "🍃 Вкусная еда — отличное настроение!",

            // Home Page
            "hero.badge": "⚡ ПРЕМИАЛЬНЫЕ ВКУСЫ И РОСКОШЬ",
            "hero.title": "Вкусные блюда,",
            "hero.titleAccent": "незабываемая атмосфера.",
            "hero.description": "Al Ezoz — это лучшие натуральные ингредиенты, мастерство опытных шеф-поваров и особая атмосфера, где каждый момент превращается в приятное воспоминание.",
            "hero.viewMenu": "🍽 Посмотреть меню",
            "hero.viewCart": "🛒 Посмотреть корзину",
            "feat.fastDelivery": "Быстрая доставка",
            "feat.fastDeliveryDesc": "По городу в горячем виде в течение 40 минут",
            "feat.halal": "100% Халяль и чистота",
            "feat.halalDesc": "Только отборные натуральные ингредиенты",
            "feat.chefs": "Шеф-мастера",
            "feat.chefsDesc": "Каждое блюдо готовится с особой заботой",
            "section.categoriesLabel": "КАТЕГОРИИ",
            "section.categoriesTitle": "Наши",
            "section.categoriesTitleAccent": "направления",
            "section.categoriesSubtitle": "Выберите раздел с любимыми блюдами и сделайте заказ быстро и удобно",
            "section.popularLabel": "ИЗБРАННЫЕ БЛЮДА",
            "section.popularTitle": "Шедевры нашей кухни",
            "section.popularSubtitle": "Попробуйте наши самые популярные и любимые блюда",
            "btn.allDishes": "Посмотреть все блюда",

            // About Page
            "about.teamSub": "Наша история & Команда",
            "about.welcome": "НАША ИСТОРИЯ",
            "about.heroTitle": "Вкусная еда — это не просто пища, <br><span style=\"color:var(--gold); font-family:Georgia, serif; font-style:italic;\">это произведение искусства.</span>",
            "about.p1": "Al Ezoz начал свою деятельность с целью подарить каждому гостю домашний уют и наслаждение блюдами мирового уровня.",
            "about.p2": "Мы используем исключительно отборные, 100% натуральные и свежие ингредиенты. На нашей кухне каждый соус готовится вручную, каждое мясо отбирается с особым вкусом, а каждое блюдо подается с любовью.",
            "about.statYears": "Лет опыта",
            "about.statGuests": "Довольных гостей",
            "about.statHalal": "Халяльные продукты",
            "about.valuesSmall": "НАШИ ЦЕННОСТИ",
            "about.valuesTitle": "Во что мы <span>верим?</span>",
            "about.val1Title": "Свежее и отборное мясо",
            "about.val1Desc": "Никаких замороженных продуктов или искусственных добавок. Только свежая говядина и куриное мясо высшего качества каждый день.",
            "about.val2Title": "Опытные шеф-повара",
            "about.val2Desc": "Каждое блюдо готовится мастерами своего дела по авторским рецептам.",
            "about.val3Title": "Быстрая & Горячая доставка",
            "about.val3Desc": "Блюда доставляются быстро и бережно в специальных термосумках, сохраняя идеальную температуру и свежесть.",

            // About Location & Map
            "about.locationBadge": "НАШЕ МЕСТОПОЛОЖЕНИЕ",
            "about.locationTitle": "Легко найдите нас <span>на карте</span>",
            "about.locationSubtitle": "Уютное и вкусное место для вас и ваших близких в центре Ташкента",
            "about.addressLabel": "Наш точный адрес",
            "about.addressVal": "г. Ташкент, Шайхантахурский район, ул. Караташ",
            "about.orientLabel": "Ориентир",
            "about.orientVal": "Рядом с городской клинической больницей №1",
            "about.hoursLabel": "Режим работы",
            "about.hoursVal": "Ежедневно: 09:00 — 23:00 (Кухня: до 22:30)",
            "about.phoneLabel": "Телефон и Связь",
            "about.deliveryLabel": "Служба доставки",
            "about.deliveryVal": "Быстро и бережно доставим горячие блюда по всему Ташкенту",
            "about.btnGoogleMaps": "Google Карты",
            "about.btnYandexMaps": "Яндекс Карты",
            "about.btnCall": "Позвонить",
            "about.btnRoute": "Построить маршрут",
            "about.btnMenu": "Меню блюд",
            "about.mapOpenNow": "Сейчас открыто • 09:00 - 23:00",

            // Home category cards
            "category.food": "Блюда",
            "category.foodDesc": "Бургеры & Горячие блюда",
            "category.salad": "Салаты",
            "category.saladDesc": "Свежие & Диетические",
            "category.snack": "Закуски",
            "category.snackDesc": "Хрустящие закуски",
            "category.drink": "Напитки",
            "category.drinkDesc": "Коктейли & Кофе",
            "category.dessert": "Десерты",
            "category.dessertDesc": "Сладости & Пирожные",

                        "category.food": "\u0411\u043b\u044e\u0434\u0430",
            "category.foodDesc": "\u0411\u0443\u0440\u0433\u0435\u0440\u044b \u0438 \u0413\u043e\u0440\u044f\u0447\u0438\u0435 \u0431\u043b\u044e\u0434\u0430",
            "category.salad": "\u0421\u0430\u043b\u0430\u0442\u044b",
            "category.saladDesc": "\u0421\u0432\u0435\u0436\u0438\u0435 \u0438 \u0414\u0438\u0435\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0435",
            "category.snack": "\u0417\u0430\u043a\u0443\u0441\u043a\u0438",
            "category.snackDesc": "\u0425\u0440\u0443\u0441\u0442\u044f\u0449\u0438\u0435 \u0437\u0430\u043a\u0443\u0441\u043a\u0438",
            "category.drink": "\u041d\u0430\u043f\u0438\u0442\u043a\u0438",
            "category.drinkDesc": "\u041a\u043e\u043a\u0442\u0435\u0439\u043b\u0438 \u0438 \u041a\u043e\u0444\u0435",
            "category.dessert": "\u0414\u0435\u0441\u0435\u0440\u0442\u044b",
            "category.dessertDesc": "\u0421\u043b\u0430\u0434\u043e\u0441\u0442\u0438 \u0438 \u041f\u0438\u0440\u043e\u0436\u043d\u044b\u0435",

            // Contact Page
            "contact.welcome": "СВЯЖИТЕСЬ С НАМИ",
            "contact.title": "Есть вопросы? <span style=\"color:var(--gold); font-family:Georgia,serif; font-style:italic;\">Мы всегда готовы помочь!</span>",
            "contact.infoTitle": "Контактная информация",
            "contact.addrLabel": "Наш адрес",
            "contact.landmark": "Ориентир: Сквер Амира Темура",
            "contact.phoneLabel": "Номера телефонов",
            "contact.deliveryHours": "Служба доставки: 09:00 — 23:00",
            "contact.socialLabel": "Социальные сети и бот",
            "contact.formTitle": "Оставьте нам сообщение",
            "contact.formSubtitle": "Отправьте пожелание, отзыв или заявку на бронь стола, и наш администратор свяжется с вами в кратчайшие сроки.",
            "form.nameLabel": "Ваше имя *",
            "form.namePlaceholder": "Например: Сардор Алимов",
            "form.phoneLabel": "Ваш номер телефона *",
            "form.subjectLabel": "Тема",
            "form.subjectPlaceholder": "Бронь стола, предложение или вопрос...",
            "form.messageLabel": "Ваше сообщение *",
            "form.messagePlaceholder": "Напишите текст вашего сообщения здесь...",
            "form.submit": "Отправить сообщение",

            // Menu Page
            "menu.title": "Вкусные блюда",
            "menu.titleAccent": "отличное настроение.",
            "menu.desc": "Выберите любые блюда из меню и добавьте ваш заказ в корзину.",
            "search_placeholder": "Поиск блюд...",

            // Cart Page & Sidebar
            "cart.title": "Корзина",
            "cart.pageTitle": "Ваша корзина",
            "cart.empty": "Корзина пуста",
            "cart.emptyDesc": "Выберите блюда из меню",
            "cart.emptyPrompt": "Ознакомьтесь с нашими вкусными блюдами и выберите то, что вам по душе!",
            "cart.selectedItems": "Выбранные блюда",
            "cart.subtotal": "Промежуточный итог:",
            "cart.delivery": "Доставка:",
            "cart.deliveryNotice": "уточняется у администратора",
            "cart.total": "Итого:",
            "cart.totalPay": "Итого к оплате:",
            "cart.checkout": "Оформить заказ",
            "cart.toCheckout": "Оформить заказ",
            "cart.clear": "Очистить корзину",
            "cart.continueShopping": "Перейти в меню",
            "cart.orderInfo": "◷ Заказ будет отправлен на кухню",

            "cart.badge": "ПОКУПКИ",
            "cart.yourCart": "Ваша",
            "cart.yourCartAccent": "Корзина",
            "cart.addMore": "Добавить ещё блюда",
            "cart.itemCount": "Количество товаров:",
            "checkout.badge": "ОФОРМЛЕНИЕ",
            "checkout.pageTitleAccent": "заказа",
            "offer.badge": "СПЕЦПРЕДЛОЖЕНИЕ",
            "offer.title": "Burger & Drink Combo Set",
            "offer.desc": "Classic Burger, картофель фри и холодный напиток по специальной цене. Каждый день с 12:00 до 16:00 скидка 20%!",
            "offer.btn": "Оформить заказ",
            "hero.stat1": "Избранных блюд",
            "hero.stat2": "Халяль & Свежее",
            "hero.stat3": "Ср. время приготовления",
            "contact.headerSub": "Контакты & Адрес",
            "contact.workHours": "Часы работы",
            "contact.workHoursLine": "Пнд – Вск: <strong>09:00 — 23:00</strong>",
            "status.badge": "ОТСЛЕЖИВАНИЕ ЗАКАЗА",
            "status.trackingSub": "Система отслеживания",
            "status.itemsTitle": "Список блюд",
            "status.orderType": "Тип:",
            "status.backMenu": "Вернуться в меню",
            "section.popularTitleAccent": "любимые блюда",

            
            // Checkout Page
            "checkout.pageTitle": "Оформление",
            "checkout.step1": "1. Тип заказа",
            "checkout.typeDelivery": "Доставка (Курьер)",
            "checkout.typePickup": "Самовывоз (Из ресторана)",
            "checkout.step2": "2. Данные клиента",
            "checkout.telegramNotice": "После отправки заказа отправьте команду <b>/start</b> в наш Telegram бот для получения 6-значного кода подтверждения.",
            "checkout.nameLabel": "Ваше имя *",
            "checkout.namePlaceholder": "Например: Сардор Алимов",
            "checkout.phoneLabel": "Ваш номер телефона *",
            "checkout.tgLabel": "Telegram username (необязательно)",
            "checkout.tgPlaceholder": "@username",
            "checkout.addrLabel": "Адрес доставки *",
            "checkout.addrPlaceholder": "г. Ташкент, Юнусабадский р-н, дом 12...",
            "checkout.mapLabel": "Выберите точку на карте (для курьера)",
            "checkout.myLocation": "📍 Моё местоположение",
            "checkout.commentLabel": "Примечание для кухни и курьера (необязательно)",
            "checkout.commentPlaceholder": "Без лука, код домофона 45, оставить у двери и т.д.",
            "checkout.tableCheckbox": "Я нахожусь в ресторане за столиком",
            "checkout.tableLabel": "Номер столика",
            "checkout.tablePlaceholder": "Например: Стол №7",
            "checkout.confirmBtn": "Подтвердить заказ",
            "checkout.summaryTitle": "Состав заказа",
            "checkout.subtotal": "Промежуточный итог:",
            "checkout.deliveryService": "Служба доставки:",
            "checkout.deliveryFree": "уточняется у администратора",
            "checkout.totalLabel": "Итоговая сумма:",
            "checkout.guarantee": "🛡 После отправки заказ мгновенно передается администратору и на кухонный экран KDS, а также отправляется уведомление в Telegram бот.",

            // Order Status Page
            "status.pageTitle": "Статус заказа",
            "status.orderNum": "Номер заказа",
            "status.trackingCode": "Код отслеживания",
            "status.stepPending": "Принят",
            "status.stepConfirmed": "Подтвержден",
            "status.stepPreparing": "Готовится",
            "status.stepReady": "Доставляется",
            "status.stepDelivered": "Доставлен",
            "status.detailsTitle": "Детали заказа",
            "status.custName": "Имя клиента:",
            "status.custPhone": "Телефон:",
            "status.custAddress": "Адрес / Столик:",
            "status.payMethod": "Способ оплаты:",
            "status.callRest": "Позвонить в ресторан",

            // Categories
            "group.food": "🍽 Блюда",
            "group.salad": "🥗 Салаты",
            "group.snack": "🍟 Закуски",
            "group.drink": "🥤 Напитки",
            "group.dessert": "🍰 Десерты",

            "categories": {
                all: "Все",
                food: "Блюда",
                salad: "Салаты",
                snack: "Закуски",
                drink: "Напитки",
                dessert: "Десерты"
            }
        }
    };

    const foodTranslations = {
        "apple juice": { uz: "Olma Sharbati", ru: "Яблочный Сок", uz_desc: "100% tabiiy olma sharbati", ru_desc: "Натуральный яблочный сок без сахара" },
        "avocado salad": { uz: "Avokado Salati", ru: "Салат с Авокадо", uz_desc: "Yangi avokado, pomidor va sara ko'katlar", ru_desc: "Полезный салат со спелым авокадо и томатами" },
        "beef steak": { uz: "Mol Go'shti Steyki", ru: "Стейк из Говядины", uz_desc: "Yumshoq va shira mol go'shti steyki", ru_desc: "Сочный стейк из отборной говядины" },
        "caesar salad": { uz: "Sezar Salati", ru: "Салат Цезарь", uz_desc: "Tovuq, parmesan, aysberg va maxsus sezar sousi", ru_desc: "Хрустящий айсберг, нежная курочка, пармезан и соус цезарь" },
        "carbonara": { uz: "Karbonara", ru: "Карбонара", uz_desc: "Klassik pasta, qaymoq va parmesan", ru_desc: "Итальянская паста карбонара со сливочным соусом и пармезаном" },
        "cheese burger": { uz: "Chizburger", ru: "Чизбургер", uz_desc: "Mol go'shti va erigan cheddar pishlog'i", ru_desc: "Классический чизбургер с сочным мясом и сыром чеддер" },
        "cheese fries": { uz: "Pishloqli Fri", ru: "Сырный Фри", uz_desc: "Qarsildoq fri va eritilgan cheddar pishlog'i", ru_desc: "Картофель фри с нежным расплавленным сыром чеддер" },
        "cheesecake": { uz: "Chizkeyk", ru: "Чизкейк", uz_desc: "Klassik nozik qaymoqli chizkeyk", ru_desc: "Нежнейший классический сливочный чизкейк" },
        "chicken burger": { uz: "Tovuqli Burger", ru: "Куриный Бургер", uz_desc: "Qarsildoq tovuq filesi va maxsus sous", ru_desc: "Хрустящее куриное филе со свежими овощами и соусом" },
        "chicken grill": { uz: "Tovuq Grill", ru: "Курица Гриль", uz_desc: "Qarsildoq terili shira tovuq va sabzavotlar", ru_desc: "Сочная запеченная курочка со свежими овощами" },
        "chicken nuggets": { uz: "Tovuqli Naggets", ru: "Куриные Наггетсы", uz_desc: "Qarsildoq tovuq naggetslari", ru_desc: "Хрустящие наггетсы из белого куриного мяса" },
        "chicken pasta": { uz: "Tovuqli Pasta", ru: "Паста с Курицей", uz_desc: "Tovuq va qaymoqli nozik pasta", ru_desc: "Паста с куриным филе в нежном сливочном соусе" },
        "chicken pizza": { uz: "Tovuqli Pitsa", ru: "Куриная Пицца", uz_desc: "Tovuq go'shti, mozzarella va qo'ziqorin", ru_desc: "Нежное куриное филе, грибы и тянущийся сыр моцарелла" },
        "chicken salad": { uz: "Tovuqli Salat", ru: "Куриный Салат", uz_desc: "Tovuq go'shti va yangi sabzavotlar", ru_desc: "Легкий салат с куриной грудкой и овощами" },
        "chicken steak": { uz: "Tovuqli Steyk", ru: "Куриный Стейк", uz_desc: "Grilda pishirilgan nozik tovuq filesi", ru_desc: "Нежный куриный стейк, приготовленный на гриле" },
        "chicken wings": { uz: "Tovuq Qanotchalari", ru: "Куриные Крылышки", uz_desc: "Achchiq va xushbo'y tovuq qanotlari", ru_desc: "Аппетитные куриные крылышки в пикантном соусе" },
        "chocolate brownie": { uz: "Brauni", ru: "Брауни", uz_desc: "Issiq shokoladli yong'oqli brauni", ru_desc: "Теплый шоколадный брауни с грецкими орехами" },
        "chocolate cake": { uz: "Shokoladli Tort", ru: "Шоколадный Торт", uz_desc: "To'yingan shokoladli yumshoq biskvit", ru_desc: "Воздушный бисквитный торт с бельгийским шоколадом" },
        "chocolate fondant": { uz: "Shokoladli Fondan", ru: "Шоколадный Фондан", uz_desc: "Ichidan oqib chiquvchi issiq shokoladli keks", ru_desc: "Изысканный десерт с жидким шоколадным центром" },
        "classic burger": { uz: "Klassik Burger", ru: "Классический Бургер", uz_desc: "Mol go'shti, cheddar pishlog'i va maxsus sous", ru_desc: "Сочная говяжья котлета, сыр чеддер и фирменный соус" },
        "cola": { uz: "Coca-Cola", ru: "Coca-Cola", uz_desc: "Muzdek sovutilgan Coca-Cola", ru_desc: "Освежающая ледяная Coca-Cola" },
        "donut": { uz: "Ponchik (Donut)", ru: "Пончик (Донат)", uz_desc: "Shokoladli va qulupnayli glazur bilan", ru_desc: "Мягкий донат в шоколадной и ягодной глазури" },
        "double burger": { uz: "Dabl Burger", ru: "Двойной Бургер", uz_desc: "Ikki qavatli mol go'shti va cheddar pishlog'i", ru_desc: "Двойная говяжья котлета с двойным сыром чеддер" },
        "fanta": { uz: "Fanta", ru: "Fanta", uz_desc: "Apelsinli xushbo'y sovutilgan ichimlik", ru_desc: "Яркая апельсиновая Fanta со льдом" },
        "four cheese pizza": { uz: "4 Xil Pishloqli Pitsa", ru: "Пицца Четыре Сыра", uz_desc: "To'rt xil sara pishloqlar uyg'unligi", ru_desc: "Ароматная пицца с четырьмя благородными сырами" },
        "french fries": { uz: "Kartoshka Fri", ru: "Картофель Фри", uz_desc: "Oltinrang qarsildoq kartoshka fri", ru_desc: "Золотистый и хрустящий картофель фри" },
        "fresh salad": { uz: "Bahoriy Salat", ru: "Свежий Салат", uz_desc: "Yangi uzilgan bodring, pomidor va ko'katlar", ru_desc: "Хрустящие огурцы, сладкие помидоры и свежая зелень" },
        "fruit cake": { uz: "Mevali Tort", ru: "Фруктовый Торт", uz_desc: "Yangi rezavor mevalar bilan bezatilgan", ru_desc: "Легкий торт со свежими сочными фруктами" },
        "greek salad": { uz: "Grekcha Salat", ru: "Греческий Салат", uz_desc: "Pomidor, bodring, feta pishlog'i va zaytun", ru_desc: "Свежие овощи, сыр фета, маслины и оливковое масло" },
        "ice cream": { uz: "Muzqaymoq", ru: "Мороженое", uz_desc: "Vanilli, shokoladli va mevali to'plar", ru_desc: "Сливочные шарики ванильного и шоколадного мороженого" },
        "iced tea": { uz: "Muzli Choy", ru: "Холодный Чай", uz_desc: "Sovutilgan mevali va limonli choy", ru_desc: "Освежающий холодный чай с лимоном" },
        "lag": { uz: "Lag'mon", ru: "Лагман", uz_desc: "Uy lag'moni, go'sht va yangi sabzavotlar", ru_desc: "Домашний лагман с сочным мясом и овощами" },
        "limonade": { uz: "Limonad", ru: "Лимонад", uz_desc: "Tabiiy limon va yalpizli tetiklashtiruvchi ichimlik", ru_desc: "Домашний лимонад из свежих лимонов и мяты" },
        "manti": { uz: "Manti", ru: "Манты", uz_desc: "Go'shtli bug'da pishirilgan manti", ru_desc: "Сочные домашние манты с рубленым мясом на пару" },
        "margherita pizza": { uz: "Margarita Pitsa", ru: "Пицца Маргарита", uz_desc: "Pomidor, mozzarella pishlog'i va rayhon", ru_desc: "Классическая пицца с томатами, моцареллой и базиликом" },
        "meat pizza": { uz: "Go'shtli Pitsa", ru: "Мясная Пицца", uz_desc: "Sara go'sht, kolbasa va mozzarella", ru_desc: "Сытная пицца с миксом отборного мяса и сыра" },
        "milkshake": { uz: "Milksheyk", ru: "Милкшейк", uz_desc: "Qaymoqli shokolad va sutli kokteyl", ru_desc: "Густой сливочный коктейль с шоколадом" },
        "mineral water": { uz: "Mineral Suv", ru: "Минеральная Вода", uz_desc: "Gazlangan va gazlanmagan toza suv", ru_desc: "Чистая минеральная вода" },
        "mojito": { uz: "Moxito", ru: "Мохито", uz_desc: "Yalpiz, laym va muz bilan tayyorlangan", ru_desc: "Освежающий мохито со свежей мятой и лаймом" },
        "onion rings": { uz: "Piyoz Halqalari", ru: "Луковые Кольца", uz_desc: "Qarsildoq non bo'lakchalarida qovurilgan", ru_desc: "Хрустящие луковые кольца в золотистой панировке" },
        "orange juice": { uz: "Apelsin Sharbati", ru: "Апельсиновый Сок", uz_desc: "100% tabiiy apelsin sharbati", ru_desc: "100% натуральный сок из спелых апельсинов" },
        "osh": { uz: "Osh (Palov)", ru: "Традиционный Плов", uz_desc: "An'anaviy o'zbek palovi, saralangan go'sht va mayiz bilan", ru_desc: "Традиционный узбекский плов из отборного мяса и жёлтой моркови" },
        "pancake": { uz: "Pankeyk", ru: "Панкейки", uz_desc: "Asal, rezavor mevalar va shokolad bilan", ru_desc: "Пышные американские панкейки с ягодами и сиропом" },
        "pepperoni pizza": { uz: "Pepperoni Pitsa", ru: "Пицца Пепперони", uz_desc: "Pepperoni, mozzarella va maxsus sous", ru_desc: "Острая пицца с колбасками пепперони и моцареллой" },
        "qozon kabob": { uz: "Qozon Kabob", ru: "Казан Кебаб", uz_desc: "Qarsildoq kartoshka va yumshoq go'sht", ru_desc: "Сочное мясо с золотистым картофелем по-казански" },
        "shashlik": { uz: "Shashlik", ru: "Шашлык", uz_desc: "Ko'mirda pishirilgan yumshoq go'sht", ru_desc: "Нежный шашлык, приготовленный на углях" },
        "spicy burger": { uz: "Achchiq Burger", ru: "Острый Бургер", uz_desc: "Achchiq sous, jalapeno va mol go'shti", ru_desc: "Пикантный бургер с перцем халапеньо и острым соусом" },
        "sprite": { uz: "Sprite", ru: "Sprite", uz_desc: "Limonli va yalpizli sovutilgan ichimlik", ru_desc: "Освежающий Sprite с легким цитрусовым вкусом" },
        "tiramisu": { uz: "Tiramisu", ru: "Тирамису", uz_desc: "Italyancha klassik qahvali desert", ru_desc: "Классический итальянский десерт с маскарпоне и кофе" },
        "waffle": { uz: "Vafli", ru: "Бельгийские Вафли", uz_desc: "Meva va shokoladli qarsildoq vafli", ru_desc: "Хрустящие вафли с ягодами и шоколадным топингом" }
    };

    function getCurrentLanguage() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const urlLang = urlParams.get('lang');
            if (urlLang === 'ru' || urlLang === 'uz') {
                localStorage.setItem(LANG_STORAGE_KEY, urlLang);
                return urlLang;
            }
            return localStorage.getItem(LANG_STORAGE_KEY) || 'uz';
        } catch (e) {
            return 'uz';
        }
    }

    function setLanguage(lang) {
        const cleanLang = (lang === 'ru') ? 'ru' : 'uz';
        try {
            localStorage.setItem(LANG_STORAGE_KEY, cleanLang);
            document.documentElement.lang = cleanLang;
        } catch (e) {}

        const dict = translations[cleanLang];

        // 1. Language buttons active state update (Segmented 2-button control)
        document.querySelectorAll('.lang-btn-item, .m-lang-btn, .more-lang-btn').forEach(btn => {
            if (btn.dataset.lang === cleanLang) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Single button fallback update
        document.querySelectorAll('.language-btn, #lang-btn').forEach(btn => {
            const flag = cleanLang === 'ru' ? '🇷🇺' : '🇺🇿';
            const code = cleanLang.toUpperCase();
            btn.innerHTML = `<span class="lang-flag">${flag}</span> <span class="lang-code">${code}</span> <span class="lang-arrow">▾</span>`;
        });

        // 2. Global static text via data-i18n attributes (textContent)
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            if (dict[key]) {
                el.textContent = dict[key];
            }
        });

        // 3. Global static text via data-i18n-html attributes (innerHTML)
        document.querySelectorAll('[data-i18n-html]').forEach(el => {
            const key = el.dataset.i18nHtml;
            if (dict[key]) {
                el.innerHTML = dict[key];
            }
        });

        // 4. Placeholders via data-i18n-placeholder
        document.querySelectorAll('[data-i18n-placeholder]').forEach(inp => {
            const key = inp.dataset.i18nPlaceholder;
            if (dict[key]) {
                inp.placeholder = dict[key];
            }
        });

        // 5. Navigation items
        document.querySelectorAll('.nav-link, .drawer-links a, .footer-links a').forEach(link => {
            const key = link.dataset.i18nKey;
            if (key && dict[key]) {
                link.textContent = dict[key];
                return;
            }

            const text = link.textContent.trim();
            if (text.includes('Bosh sahifa') || text.includes('Главная')) {
                link.textContent = dict['nav.home'];
            } else if (text.includes('Biz haqimizda') || text.includes('О нас')) {
                link.textContent = dict['nav.about'];
            } else if (text.includes('Menyu') || text.includes('Меню')) {
                if (!link.href.includes('secure-admin') && !link.href.includes('chef-panel')) {
                    link.textContent = dict['nav.menu'];
                }
            } else if (text.includes('Aloqa') || text.includes('Контакты')) {
                link.textContent = dict['nav.contact'];
            } else if (text.includes('Savat') || text.includes('Корзина')) {
                link.textContent = dict['nav.cart'];
            }
        });

        // 6. Search inputs
        document.querySelectorAll('.search-input, #search-input, .menu-search input').forEach(inp => {
            inp.placeholder = dict.search_placeholder;
        });

        // 7. Category buttons filter
        document.querySelectorAll('.category[data-category]').forEach(catBtn => {
            const catKey = catBtn.dataset.category;
            if (dict.categories && dict.categories[catKey]) {
                const iconSpan = catBtn.querySelector('span') ? catBtn.querySelector('span').outerHTML : '';
                catBtn.innerHTML = iconSpan + ' ' + dict.categories[catKey];
            }
        });

        // 8. Menu group titles (rendered by script.js)
        document.querySelectorAll('.category-title[data-category]').forEach(titleElem => {
            const groupKey = titleElem.dataset.category;
            if (dict[`group.${groupKey}`]) {
                titleElem.textContent = dict[`group.${groupKey}`];
            }
        });

        // 9. Food cards title & description translation
        document.querySelectorAll('.food-card').forEach(card => {
            const h3 = card.querySelector('h3');
            const p = card.querySelector('p');
            if (h3) {
                if (!card.dataset.nameOriginal) {
                    card.dataset.nameOriginal = h3.textContent.trim();
                }
                const rawName = card.dataset.nameOriginal.toLowerCase();
                for (const [key, t] of Object.entries(foodTranslations)) {
                    if (rawName.includes(key)) {
                        h3.textContent = (cleanLang === 'ru') ? t.ru : t.uz;
                        if (p) p.textContent = (cleanLang === 'ru') ? t.ru_desc : t.uz_desc;
                        break;
                    }
                }
            }
        });

        // 10. Cart sidebar
        document.querySelectorAll('.empty-cart h3').forEach(el => { el.textContent = dict['cart.empty']; });
        document.querySelectorAll('.empty-cart p').forEach(el => { el.textContent = dict['cart.emptyDesc']; });
        document.querySelectorAll('#order-btn, .order-btn').forEach(btn => {
            btn.innerHTML = `${dict['cart.checkout']} <span>→</span>`;
        });

        // 11. Direct element replacements for menu title and header descriptions
        document.querySelectorAll('.menu-title h1, .header-text h1, .menu-hero h1').forEach(h1 => {
            if (cleanLang === 'ru') {
                h1.innerHTML = `Вкусные блюда <br><span>отличное настроение.</span>`;
            } else {
                h1.innerHTML = `Mazali taomlar <br><span>yaxshi kayfiyat.</span>`;
            }
        });
        document.querySelectorAll('.menu-hero p, .header-text p').forEach(p => {
            if (p.textContent.includes('Menyudan istagan') || p.textContent.includes('Выберите любые')) {
                p.textContent = dict['menu.desc'];
            }
        });

                // 12. Currency translation (so'm / so‘m <-> сум)
        document.querySelectorAll('.food-card strong, .cart-item-row strong, .cart-item-row span, #det-total, #ch-subtotal, #ch-total, #summary-subtotal, #summary-total, #total').forEach(el => {
            if (cleanLang === 'ru') {
                el.textContent = el.textContent.replace(/so[‘']m/gi, 'сум');
            } else {
                el.textContent = el.textContent.replace(/сум/gi, "so‘m");
            }
        });

        // 13. Dynamic page title update
        const path = window.location.pathname;
        if (path.includes('menu')) document.title = (cleanLang === 'ru') ? 'Al Ezoz — Меню' : 'Al Ezoz — Menyu';
        else if (path.includes('about')) document.title = (cleanLang === 'ru') ? 'Al Ezoz — О нас' : 'Al Ezoz — Biz haqimizda';
        else if (path.includes('cart')) document.title = (cleanLang === 'ru') ? 'Al Ezoz — Корзина' : 'Al Ezoz — Savat';
        else if (path.includes('checkout')) document.title = (cleanLang === 'ru') ? 'Al Ezoz — Оформление заказа' : 'Al Ezoz — Buyurtma berish';
        else if (path.includes('contact')) document.title = (cleanLang === 'ru') ? 'Al Ezoz — Контакты' : 'Al Ezoz — Aloqa';
        else if (path.includes('order-status') || path.includes('status')) document.title = (cleanLang === 'ru') ? 'Al Ezoz — Статус заказа' : 'Al Ezoz — Buyurtma holati';
        else if (path === '/' || path === '') document.title = (cleanLang === 'ru') ? 'Al Ezoz — Главная' : 'Al Ezoz — Bosh sahifa';

        window.dispatchEvent(new CustomEvent('appLanguageChanged', { detail: { lang: cleanLang, dict: dict } }));
    }

    function toggleLanguage(e) {
        if (e && e.preventDefault) {
            e.preventDefault();
            e.stopPropagation();
        }
        const active = getCurrentLanguage();
        const nextLang = (active === 'uz') ? 'ru' : 'uz';
        setLanguage(nextLang);
        showToast(nextLang === 'ru' ? '🇷🇺 Язык изменен на Русский' : "🇺🇿 Til O'zbekchaga o'zgartirildi");
    }

    function initLanguageSwitcher() {
        const currentLang = getCurrentLanguage();

        document.querySelectorAll('.lang-btn-item, .m-lang-btn, .more-lang-btn').forEach(btn => {
            btn.onclick = function(e) {
                if (e) { e.preventDefault(); e.stopPropagation(); }
                const targetLang = this.dataset.lang;
                setLanguage(targetLang);
                showToast(targetLang === 'ru' ? '🇷🇺 Язык изменен на Русский' : "🇺🇿 Til O'zbekchaga o'zgartirildi");
            };
        });

        document.querySelectorAll('.language-btn, #lang-btn').forEach(btn => {
            btn.removeAttribute('onclick');
            btn.onclick = function(e) {
                toggleLanguage(e);
            };
        });

        setLanguage(currentLang);
    }

    // Attach global click event delegation as fallback
    document.addEventListener('click', (e) => {
        const item = e.target.closest('.lang-btn-item, .m-lang-btn, .more-lang-btn');
        if (item && item.dataset.lang) {
            if (e) { e.preventDefault(); e.stopPropagation(); }
            const targetLang = item.dataset.lang;
            setLanguage(targetLang);
            showToast(targetLang === 'ru' ? '🇷🇺 Язык изменен на Русский' : "🇺🇿 Til O'zbekchaga o'zgartirildi");
            return;
        }

        const btn = e.target.closest('.language-btn, #lang-btn');
        if (btn) {
            toggleLanguage(e);
        }
    });

    // On Load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initTheme();
            updateCartBadges();
            initMobileNav();
            initLanguageSwitcher();

            // Cart button: navigate to /cart page
            const openCartBtn = document.getElementById('open-cart-btn');
            if (openCartBtn) {
                openCartBtn.addEventListener('click', function() {
                    window.location.href = '/cart';
                });
            }
        });
    } else {
        initTheme();
        updateCartBadges();
        initMobileNav();
        initLanguageSwitcher();

        // Cart button: navigate to /cart page
        const openCartBtn = document.getElementById('open-cart-btn');
        if (openCartBtn) {
            openCartBtn.addEventListener('click', function() {
                window.location.href = '/cart';
            });
        }
    }

    return {
        getCart,
        saveCart,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        getCartTotal,
        getCartCount,
        updateCartBadges,
        applyTheme: initTheme,
        showToast,
        getCurrentLanguage,
        setLanguage,
        toggleLanguage,
        t: function(key) {
            const lang = getCurrentLanguage();
            return (translations[lang] && translations[lang][key]) || key;
        },
        translateItemName: function(name, targetLang) {
            if (!name) return "";
            const lang = targetLang || getCurrentLanguage();
            const lower = name.toLowerCase().trim();
            for (const [key, t] of Object.entries(foodTranslations)) {
                if (lower.includes(key)) {
                    return lang === 'ru' ? t.ru : t.uz;
                }
            }
            return name;
        },
        translateItemDesc: function(name, targetLang) {
            if (!name) return "";
            const lang = targetLang || getCurrentLanguage();
            const lower = name.toLowerCase().trim();
            for (const [key, t] of Object.entries(foodTranslations)) {
                if (lower.includes(key)) {
                    return lang === 'ru' ? t.ru_desc : t.uz_desc;
                }
            }
            return "";
        },
        getCurrencyText: function() {
            return getCurrentLanguage() === 'ru' ? 'сум' : "so‘m";
        },
        getFoodTranslations: function() {
            return foodTranslations;
        },
    };
})();

// ==========================================================================
// AL EZOZ - PREMIUM SPLASH & LOGO ENTRANCE ANIMATION
// ==========================================================================
(function initSiteSplashIntro() {
    function createSplashDOM() {
        let preloader = document.getElementById('site-preloader');
        if (!preloader && document.body) {
            preloader = document.createElement('div');
            preloader.id = 'site-preloader';
            preloader.className = 'site-preloader';
            preloader.setAttribute('role', 'status');
            preloader.setAttribute('aria-label', 'Yuklanmoqda...');
            preloader.innerHTML = `
                <div class="preloader-content">
                    <div class="preloader-logo-ring">
                        <div class="preloader-spinner-ring"></div>
                        <img src="/static/alezoz-logo.jpg" alt="Al Ezoz Logo" class="preloader-logo-img">
                    </div>
                    <div class="preloader-brand">
                        <span class="preloader-title">Al Ezoz</span>
                        <span class="preloader-sub">MILLIY TAOMLAR</span>
                    </div>
                    <div class="preloader-bar-wrap">
                        <div class="preloader-bar-line"></div>
                    </div>
                </div>
            `;
            document.body.prepend(preloader);
        }

        if (preloader) {
            preloader.addEventListener('click', () => {
                preloader.classList.add('hide-preloader');
                setTimeout(() => preloader.remove(), 500);
            });

            setTimeout(() => {
                preloader.classList.add('hide-preloader');
                setTimeout(() => {
                    if (preloader && preloader.parentNode) {
                        preloader.remove();
                    }
                }, 550);
            }, 1400);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createSplashDOM);
    } else {
        createSplashDOM();
    }
})();

