/**
 * Funding Aggregator — Internationalization (i18n)
 * Languages: Русский (ru), Қазақша (kz)
 */
const translations = {
  ru: {
    // Navbar
    "nav.home": "Главная",
    "nav.grants": "Гранты",
    "nav.ai_search": "AI Поиск",
    "nav.stats": "Статистика",
    "nav.signin": "Войти",
    "nav.signup": "Регистрация",
    "nav.logout": "Выйти",

    // Hero
    "hero.badge": "AI-поиск грантов",
    "hero.title1": "Найди ",
    "hero.title_highlight": "Гранты",
    "hero.title2": " и Стипендии в Казахстане",
    "hero.subtitle": "Агрегатор грантов, стипендий и конкурсов финансирования. Поиск с помощью искусственного интеллекта и умные рекомендации.",
    "hero.search_placeholder": "Поиск грантов... напр. 'гранты для IT стартапов до 5 млн тенге'",
    "hero.search_btn": "Найти",
    "hero.stat_total": "Всего грантов",
    "hero.stat_active": "Активных",
    "hero.stat_sources": "Источников",

    // Features
    "features.title1": "Почему ",
    "features.title_highlight": "Funding Aggregator",
    "features.title2": "?",
    "features.ai_title": "AI-Поиск",
    "features.ai_desc": "Поиск на естественном языке с помощью LLaMA 3. Просто опишите что ищете.",
    "features.realtime_title": "Автосбор данных",
    "features.realtime_desc": "Данные собираются с нескольких источников и обновляются автоматически каждые 6 часов.",
    "features.recommend_title": "Рекомендации",
    "features.recommend_desc": "Персональные рекомендации грантов на основе ваших интересов и избранного.",
    "features.filter_title": "Фильтрация",
    "features.filter_desc": "Фильтр по категории, стране, сумме, дедлайнам и другим параметрам.",
    "features.favorites_title": "Избранное",
    "features.favorites_desc": "Сохраняйте интересные гранты и создавайте свою персональную коллекцию.",
    "features.secure_title": "Безопасность",
    "features.secure_desc": "JWT-авторизация, Docker-контейнеризация, мониторинг Prometheus.",

    // Recent
    "recent.title1": "Последние ",
    "recent.title_highlight": "Возможности",
    "recent.view_all": "Смотреть все гранты →",

    // Grants page
    "grants.title1": "Каталог ",
    "grants.title_highlight": "Грантов",
    "grants.subtitle": "Поиск и фильтрация по всем агрегированным грантам",
    "grants.search_placeholder": "Поиск грантов...",
    "grants.all_sources": "Все источники",
    "grants.all_countries": "Все страны",
    "grants.active": "Активные",
    "grants.all": "Все",
    "grants.expired": "Истёкшие",
    "grants.newest": "Новые",
    "grants.oldest": "Старые",
    "grants.deadline_soon": "Ближайший дедлайн",
    "grants.amount_high": "Сумма (макс.)",
    "grants.apply_btn": "Применить",
    "grants.no_results": "Грантов не найдено. Попробуйте изменить фильтры.",
    "grants.no_data": "Грантов пока нет. Запустите сборщик данных.",
    "grants.api_error": "Не удалось загрузить гранты. Убедитесь что API работает.",

    // AI Search page
    "ai.title1": "🤖 AI ",
    "ai.title_highlight": "Поиск",
    "ai.subtitle": "Опишите что вы ищете на естественном языке",
    "ai.placeholder": "напр. Найди гранты для IT стартапов в Казахстане до 5 млн тенге с дедлайном в 2025...",
    "ai.search_btn": "✨ Найти с AI",
    "ai.try_label": "Попробуйте:",
    "ai.example1_label": "IT гранты <5М₸",
    "ai.example1_query": "гранты для IT стартапов в Казахстане до 5 миллионов тенге",
    "ai.example2_label": "Наука КЗ",
    "ai.example2_query": "научные гранты для молодых учёных в Казахстане",
    "ai.example3_label": "Стартапы 2025",
    "ai.example3_query": "инновационные гранты для стартапов с дедлайном в 2025",
    "ai.example4_label": "Стипендии",
    "ai.example4_query": "стипендии для магистрантов и докторантов Казахстана",
    "ai.signin_required": "Войдите чтобы использовать AI поиск",
    "ai.short_query": "Введите более длинный запрос",
    "ai.no_results": "Ничего не найдено. Попробуйте другой запрос.",
    "ai.error": "Ошибка AI поиска. Проверьте Groq API ключ.",
    "ai.found": "Найдено результатов:",

    // Stats page
    "stats.title1": "📊 ",
    "stats.title_highlight": "Статистика",
    "stats.subtitle": "Обзор агрегированных данных",
    "stats.total": "Всего грантов",
    "stats.active": "Активных",
    "stats.sources": "Источников",
    "stats.ai_engine": "AI движок",
    "stats.monitoring": "Мониторинг",

    // Auth modal
    "auth.signin_tab": "Вход",
    "auth.signup_tab": "Регистрация",
    "auth.username": "Имя пользователя",
    "auth.password": "Пароль",
    "auth.email": "Эл. почта",
    "auth.fullname": "ФИО",
    "auth.signin_btn": "Войти",
    "auth.signup_btn": "Создать аккаунт",
    "auth.welcome": "Добро пожаловать!",
    "auth.created": "Аккаунт создан! Входим...",
    "auth.logged_out": "Вы вышли",

    // Grant detail
    "detail.description": "Описание",
    "detail.eligibility": "Кто может подать",
    "detail.requirements": "Требования",
    "detail.keywords": "Ключевые слова",
    "detail.ai_summary": "AI Резюме",
    "detail.view_original": "Перейти к источнику →",
    "detail.favorite": "⭐ В избранное",
    "detail.added_fav": "Добавлено в избранное",
    "detail.removed_fav": "Удалено из избранного",

    // Footer
    "footer.built_with": "Сделано на FastAPI + Groq AI + PostgreSQL | 2025",

    // Countries
    "country.kz": "Казахстан",
    "country.us": "США",
    "country.eu": "Европа",
    "country.uk": "Великобритания",
    "country.de": "Германия",
    "country.international": "Международный",
  },

  kz: {
    // Navbar
    "nav.home": "Басты бет",
    "nav.grants": "Гранттар",
    "nav.ai_search": "AI Іздеу",
    "nav.stats": "Статистика",
    "nav.signin": "Кіру",
    "nav.signup": "Тіркелу",
    "nav.logout": "Шығу",

    // Hero
    "hero.badge": "AI грант іздеу",
    "hero.title1": "Қазақстандағы ",
    "hero.title_highlight": "Гранттар",
    "hero.title2": " мен Стипендияларды табыңыз",
    "hero.subtitle": "Гранттар, стипендиялар мен қаржыландыру конкурстарының агрегаторы. Жасанды интеллект арқылы іздеу.",
    "hero.search_placeholder": "Грант іздеу... мыс. 'IT стартаптар үшін гранттар 5 млн теңгеге дейін'",
    "hero.search_btn": "Іздеу",
    "hero.stat_total": "Барлық гранттар",
    "hero.stat_active": "Белсенді",
    "hero.stat_sources": "Дереккөздер",

    // Features
    "features.title1": "Неліктен ",
    "features.title_highlight": "Funding Aggregator",
    "features.title2": "?",
    "features.ai_title": "AI-Іздеу",
    "features.ai_desc": "LLaMA 3 арқылы табиғи тілде іздеу. Не іздеп жатқаныңызды сипаттаңыз.",
    "features.realtime_title": "Деректерді жинау",
    "features.realtime_desc": "Деректер бірнеше көздерден жиналып, автоматты түрде жаңартылады.",
    "features.recommend_title": "Ұсыныстар",
    "features.recommend_desc": "Қызығушылықтарыңызға негізделген жеке грант ұсыныстары.",
    "features.filter_title": "Сүзгілеу",
    "features.filter_desc": "Санат, ел, сома, мерзім бойынша сүзгілеу.",
    "features.favorites_title": "Таңдаулылар",
    "features.favorites_desc": "Қызықты гранттарды сақтаңыз.",
    "features.secure_title": "Қауіпсіздік",
    "features.secure_desc": "JWT авторизация, Docker контейнерлеу, Prometheus мониторинг.",

    // Recent
    "recent.title1": "Соңғы ",
    "recent.title_highlight": "Мүмкіндіктер",
    "recent.view_all": "Барлық гранттарды көру →",

    // Grants page
    "grants.title1": "Барлық ",
    "grants.title_highlight": "Гранттар",
    "grants.subtitle": "Барлық агрегатталған гранттар бойынша іздеу",
    "grants.search_placeholder": "Грант іздеу...",
    "grants.all_sources": "Барлық көздер",
    "grants.all_countries": "Барлық елдер",
    "grants.active": "Белсенді",
    "grants.all": "Барлығы",
    "grants.expired": "Мерзімі өткен",
    "grants.newest": "Жаңа",
    "grants.oldest": "Ескі",
    "grants.deadline_soon": "Жақын мерзім",
    "grants.amount_high": "Сома (макс.)",
    "grants.apply_btn": "Қолдану",
    "grants.no_results": "Грант табылмады.",
    "grants.no_data": "Гранттар жоқ.",
    "grants.api_error": "Гранттарды жүктеу мүмкін болмады.",

    // AI Search page
    "ai.title1": "🤖 AI ",
    "ai.title_highlight": "Іздеу",
    "ai.subtitle": "Не іздеп жатқаныңызды сипаттаңыз",
    "ai.placeholder": "мыс. Қазақстандағы IT стартаптар үшін 5 млн теңгеге дейінгі гранттарды тап...",
    "ai.search_btn": "✨ AI арқылы іздеу",
    "ai.try_label": "Көріңіз:",
    "ai.example1_label": "IT гранттар",
    "ai.example1_query": "Қазақстандағы IT стартаптар үшін гранттар",
    "ai.example2_label": "Ғылым",
    "ai.example2_query": "жас ғалымдар үшін ғылыми гранттар",
    "ai.example3_label": "Стартаптар",
    "ai.example3_query": "инновациялық гранттар стартаптар үшін",
    "ai.example4_label": "Стипендиялар",
    "ai.example4_query": "магистранттар мен докторанттар үшін стипендиялар",
    "ai.signin_required": "AI іздеу үшін кіріңіз",
    "ai.short_query": "Ұзынырақ сұрау енгізіңіз",
    "ai.no_results": "Ештеңе табылмады.",
    "ai.error": "AI іздеу қатесі.",
    "ai.found": "Табылған нәтижелер:",

    // Stats page
    "stats.title1": "📊 ",
    "stats.title_highlight": "Статистика",
    "stats.subtitle": "Деректерге шолу",
    "stats.total": "Барлық гранттар",
    "stats.active": "Белсенді",
    "stats.sources": "Дереккөздер",
    "stats.ai_engine": "AI қозғалтқыш",
    "stats.monitoring": "Мониторинг",

    // Auth modal
    "auth.signin_tab": "Кіру",
    "auth.signup_tab": "Тіркелу",
    "auth.username": "Пайдаланушы аты",
    "auth.password": "Құпия сөз",
    "auth.email": "Эл. пошта",
    "auth.fullname": "Аты-жөні",
    "auth.signin_btn": "Кіру",
    "auth.signup_btn": "Аккаунт жасау",
    "auth.welcome": "Қош келдіңіз!",
    "auth.created": "Аккаунт жасалды! Кіруде...",
    "auth.logged_out": "Сіз шықтыңыз",

    // Grant detail
    "detail.description": "Сипаттама",
    "detail.eligibility": "Кім бере алады",
    "detail.requirements": "Талаптар",
    "detail.keywords": "Кілт сөздер",
    "detail.ai_summary": "AI Түйіндеме",
    "detail.view_original": "Түпнұсқаға өту →",
    "detail.favorite": "⭐ Таңдаулыларға",
    "detail.added_fav": "Таңдаулыларға қосылды",
    "detail.removed_fav": "Таңдаулылардан алынды",

    // Footer
    "footer.built_with": "FastAPI + Groq AI + PostgreSQL негізінде жасалған | 2025",

    // Countries
    "country.kz": "Қазақстан",
    "country.us": "АҚШ",
    "country.eu": "Еуропа",
    "country.uk": "Ұлыбритания",
    "country.de": "Германия",
    "country.international": "Халықаралық",
  }
};

// i18n manager
const i18n = {
  currentLang: localStorage.getItem('lang') || 'ru',

  init() {
    this.applyLanguage(this.currentLang);
  },

  setLanguage(lang) {
    this.currentLang = lang;
    localStorage.setItem('lang', lang);
    this.applyLanguage(lang);
  },

  t(key) {
    const val = translations[this.currentLang]?.[key];
    if (val !== undefined && val !== null) return val;
    return translations['ru']?.[key] ?? key;
  },

  applyLanguage(lang) {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const text = this.t(key);
      if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
        el.placeholder = text;
      } else {
        el.textContent = text;
      }
    });

    // Update select options with data-i18n
    document.querySelectorAll('[data-i18n-option]').forEach(el => {
      const key = el.getAttribute('data-i18n-option');
      el.textContent = this.t(key);
    });

    // Update lang toggle button
    const toggleBtn = document.getElementById('lang-toggle');
    if (toggleBtn) {
      toggleBtn.textContent = lang === 'ru' ? 'ҚАЗ' : 'РУС';
    }

    // Update HTML lang
    document.documentElement.lang = lang === 'kz' ? 'kk' : 'ru';
  }
};
