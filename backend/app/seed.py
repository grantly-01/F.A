"""
Funding Aggregator — Seed с казахстанскими грантами
python -m app.seed
"""
import asyncio
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from app.database import async_session, init_db, engine, Base
from app.models.grant import Grant, Category
from app.models.user import User
from app.core.security import hash_password


CATEGORIES = [
    {"name": "Наука и исследования", "slug": "science", "color": "#8b5cf6", "description": "Научные гранты и стипендии"},
    {"name": "IT и технологии", "slug": "it-tech", "color": "#3b82f6", "description": "Информационные технологии, AI, стартапы"},
    {"name": "Медицина и здоровье", "slug": "healthcare", "color": "#10b981", "description": "Медицинские исследования, здравоохранение"},
    {"name": "Образование", "slug": "education", "color": "#f59e0b", "description": "Стипендии, обучение, повышение квалификации"},
    {"name": "Экология и энергетика", "slug": "ecology", "color": "#06b6d4", "description": "Экология, зелёная энергетика, устойчивое развитие"},
    {"name": "Культура и искусство", "slug": "culture", "color": "#ec4899", "description": "Культурные проекты, искусство, история"},
    {"name": "Инженерия", "slug": "engineering", "color": "#f97316", "description": "Инженерные разработки, промышленность"},
    {"name": "Социальные науки", "slug": "social", "color": "#a855f7", "description": "Экономика, социология, право"},
    {"name": "Стартапы и инновации", "slug": "startup", "color": "#ef4444", "description": "Предпринимательство, инновации, бизнес"},
    {"name": "Международные", "slug": "international", "color": "#14b8a6", "description": "Международное сотрудничество, обмен"},
]

GRANTS = [
    {
        "title": "Программа «Болашак» — Международная стипендия Президента РК",
        "description": "Международная стипендия Президента Республики Казахстан «Болашақ» предоставляет возможность обучения в лучших университетах мира. Покрывает обучение, проживание, перелёт, медицинскую страховку. Обязательное условие — возвращение и работа в Казахстане не менее 5 лет.",
        "source_url": "https://www.bolashak.gov.kz/ru/o-stipendii",
        "source_name": "bolashak.gov.kz",
        "amount_min": Decimal("5000000"),
        "amount_max": Decimal("30000000"),
        "currency": "KZT",
        "deadline": date(2025, 9, 30),
        "posted_date": date(2025, 3, 1),
        "eligibility": "Граждане РК до 35 лет, знание иностранного языка (IELTS 6.5+)",
        "country": "Казахстан",
        "region": "Международный",
        "status": "active",
        "categories": ["education", "international"],
        "keywords": ["Болашак", "стипендия", "обучение за рубежом", "магистратура", "PhD"],
    },
    {
        "title": "Грант МОН РК — Научные исследования фундаментального характера",
        "description": "Министерство науки и высшего образования РК выделяет гранты на фундаментальные научные исследования. Финансирование до 100 млн тенге на 3 года. Приоритетные направления: информационные технологии, биотехнологии, новые материалы, энергетика.",
        "source_url": "https://www.gov.kz/memleket/entities/science",
        "source_name": "gov.kz",
        "amount_min": Decimal("30000000"),
        "amount_max": Decimal("100000000"),
        "currency": "KZT",
        "deadline": date(2025, 7, 15),
        "posted_date": date(2025, 2, 1),
        "eligibility": "Научные организации и вузы РК, наличие PhD/к.н.",
        "country": "Казахстан",
        "status": "active",
        "categories": ["science"],
        "keywords": ["МОН", "фундаментальные исследования", "наука", "PhD", "казахстан"],
    },
    {
        "title": "Грант КНТФ — Коммерциализация результатов научной деятельности",
        "description": "Комитет науки и технологий финансирует проекты по коммерциализации научных разработок. Гранты до 50 млн тенге. Требуется готовый прототип или технология на стадии TRL 5+. Поддерживаются проекты в области ИТ, агротехнологий, медицины.",
        "source_url": "https://www.gov.kz/memleket/entities/science/press/article",
        "source_name": "gov.kz",
        "amount_min": Decimal("10000000"),
        "amount_max": Decimal("50000000"),
        "currency": "KZT",
        "deadline": date(2025, 8, 1),
        "posted_date": date(2025, 3, 15),
        "eligibility": "Учёные и исследователи РК, наличие прототипа TRL 5+",
        "country": "Казахстан",
        "status": "active",
        "categories": ["science", "startup"],
        "keywords": ["коммерциализация", "КНТФ", "наука", "прототип", "TRL"],
    },
    {
        "title": "QazInnovations — Грант на инновационные стартапы",
        "description": "QazInnovations (ранее QazTech Ventures) предоставляет гранты до 25 млн тенге для инновационных стартапов Казахстана на стадии pre-seed и seed. Приоритеты: FinTech, EdTech, HealthTech, AgriTech, CleanTech. Менторская поддержка и доступ к инвесторам.",
        "source_url": "https://qazinnovations.gov.kz",
        "source_name": "qazinnovations.gov.kz",
        "amount_min": Decimal("5000000"),
        "amount_max": Decimal("25000000"),
        "currency": "KZT",
        "deadline": date(2025, 10, 15),
        "posted_date": date(2025, 4, 1),
        "eligibility": "Стартапы РК на стадии pre-seed/seed, ТОО зарегистрированное в РК",
        "country": "Казахстан",
        "status": "active",
        "categories": ["startup", "it-tech"],
        "keywords": ["стартап", "инновации", "QazInnovations", "pre-seed", "FinTech"],
    },
    {
        "title": "Astana Hub — Грант для IT-стартапов Tech Garden",
        "description": "Международный технопарк IT-стартапов Astana Hub предоставляет грантовое финансирование до 15 млн тенге. Резиденты получают налоговые льготы (освобождение от КПН и НДС), коворкинг, менторство. Фокус на экспортоориентированные IT-продукты.",
        "source_url": "https://astanahub.com/ru/programs/grants",
        "source_name": "astanahub.com",
        "amount_min": Decimal("3000000"),
        "amount_max": Decimal("15000000"),
        "currency": "KZT",
        "deadline": date(2025, 11, 1),
        "posted_date": date(2025, 5, 1),
        "eligibility": "IT-стартапы, резиденты или потенциальные резиденты Astana Hub",
        "country": "Казахстан",
        "status": "active",
        "categories": ["it-tech", "startup"],
        "keywords": ["Astana Hub", "IT", "стартап", "налоговые льготы", "технопарк"],
    },
    {
        "title": "Фонд «Даму» — Программа «Дорожная карта бизнеса 2025»",
        "description": "Фонд развития предпринимательства «Даму» субсидирует процентные ставки по кредитам и предоставляет гранты до 5 млн тенге для начинающих предпринимателей. Программа покрывает обучение, бизнес-планирование и сервисную поддержку.",
        "source_url": "https://damu.kz/programmy",
        "source_name": "damu.kz",
        "amount_min": Decimal("1000000"),
        "amount_max": Decimal("5000000"),
        "currency": "KZT",
        "deadline": date(2025, 12, 31),
        "posted_date": date(2025, 1, 15),
        "eligibility": "Начинающие предприниматели РК, ИП или ТОО",
        "country": "Казахстан",
        "status": "active",
        "categories": ["startup"],
        "keywords": ["Даму", "предпринимательство", "субсидии", "бизнес", "МСБ"],
    },
    {
        "title": "Назарбаев Университет — Исследовательский грант NURIS",
        "description": "Назарбаев Университет выделяет внутренние исследовательские гранты NURIS для преподавателей и исследователей. Финансирование до $100,000 на 2-3 года. Все области науки. Особый приоритет — междисциплинарные проекты.",
        "source_url": "https://nu.edu.kz/research/grants",
        "source_name": "nu.edu.kz",
        "amount_min": Decimal("20000000"),
        "amount_max": Decimal("50000000"),
        "currency": "KZT",
        "deadline": date(2025, 6, 30),
        "posted_date": date(2025, 2, 15),
        "eligibility": "Преподаватели и исследователи Назарбаев Университета",
        "country": "Казахстан",
        "status": "active",
        "categories": ["science", "education"],
        "keywords": ["Назарбаев Университет", "NURIS", "исследования", "наука"],
    },
    {
        "title": "ПРООН Казахстан — Гранты на устойчивое развитие и экологию",
        "description": "Программа развития ООН в Казахстане финансирует проекты в области устойчивого развития, изменения климата, управления водными ресурсами и биоразнообразия. Гранты от $10,000 до $100,000. Совместные проекты с государственными органами приветствуются.",
        "source_url": "https://www.undp.org/kazakhstan/grants",
        "source_name": "undp.org",
        "amount_min": Decimal("5000000"),
        "amount_max": Decimal("50000000"),
        "currency": "KZT",
        "deadline": date(2025, 9, 15),
        "posted_date": date(2025, 3, 1),
        "eligibility": "НПО, общественные организации, научные институты РК",
        "country": "Казахстан",
        "status": "active",
        "categories": ["ecology", "social"],
        "keywords": ["ПРООН", "ООН", "экология", "устойчивое развитие", "климат"],
    },
    {
        "title": "Грант акимата Астаны — Молодёжные инициативы",
        "description": "Акимат города Астаны предоставляет гранты до 3 млн тенге для молодёжных социальных проектов. Направления: волонтёрство, образование, культура, спорт, экология. Возраст участников: 14-29 лет.",
        "source_url": "https://www.gov.kz/memleket/entities/astana",
        "source_name": "gov.kz",
        "amount_min": Decimal("500000"),
        "amount_max": Decimal("3000000"),
        "currency": "KZT",
        "deadline": date(2025, 8, 15),
        "posted_date": date(2025, 4, 1),
        "eligibility": "Молодёжь РК 14-29 лет, НПО, молодёжные организации",
        "country": "Казахстан",
        "status": "active",
        "categories": ["social", "culture"],
        "keywords": ["молодёжь", "Астана", "социальные проекты", "волонтёрство"],
    },
    {
        "title": "USAID Казахстан — Грант на развитие гражданского общества",
        "description": "Агентство США по международному развитию выделяет гранты для НПО Казахстана. Направления: верховенство закона, медиа, гражданское участие, противодействие коррупции. Финансирование $20,000–$200,000 на 12-24 месяца.",
        "source_url": "https://www.usaid.gov/central-asia-regional",
        "source_name": "usaid.gov",
        "amount_min": Decimal("10000000"),
        "amount_max": Decimal("100000000"),
        "currency": "KZT",
        "deadline": date(2025, 7, 31),
        "posted_date": date(2025, 2, 1),
        "eligibility": "НПО и общественные организации Казахстана",
        "country": "Казахстан",
        "status": "active",
        "categories": ["social", "international"],
        "keywords": ["USAID", "гражданское общество", "НПО", "демократия"],
    },
    {
        "title": "Стипендия «Ел үміті» — Для талантливой молодёжи",
        "description": "Корпоративный фонд «Ел үміті» предоставляет стипендии для студентов из малообеспеченных семей, обучающихся в вузах Казахстана. Ежемесячная стипендия 100,000 тенге + оплата проживания. Отбор на основе успеваемости и социального статуса.",
        "source_url": "https://www.elumiti.kz",
        "source_name": "elumiti.kz",
        "amount_min": Decimal("1200000"),
        "amount_max": Decimal("2400000"),
        "currency": "KZT",
        "deadline": date(2025, 8, 31),
        "posted_date": date(2025, 5, 1),
        "eligibility": "Студенты казахстанских вузов из малообеспеченных семей, GPA 3.0+",
        "country": "Казахстан",
        "status": "active",
        "categories": ["education"],
        "keywords": ["стипендия", "студенты", "Ел үміті", "образование", "поддержка"],
    },
    {
        "title": "Zerde — Грант на цифровые технологии и Smart City",
        "description": "АО «Зерде» Национальный инфокоммуникационный холдинг финансирует проекты в области цифровизации, Smart City, кибербезопасности, Big Data и IoT. Гранты до 30 млн тенге. Приоритет — решения для государственных сервисов.",
        "source_url": "https://zerde.gov.kz",
        "source_name": "zerde.gov.kz",
        "amount_min": Decimal("10000000"),
        "amount_max": Decimal("30000000"),
        "currency": "KZT",
        "deadline": date(2025, 10, 1),
        "posted_date": date(2025, 4, 15),
        "eligibility": "IT-компании РК, разработчики, стартапы",
        "country": "Казахстан",
        "status": "active",
        "categories": ["it-tech"],
        "keywords": ["Зерде", "цифровизация", "Smart City", "кибербезопасность", "Big Data"],
    },
    {
        "title": "Фонд Сорос-Казахстан — Поддержка образовательных инициатив",
        "description": "Фонд Сорос-Казахстан поддерживает проекты в области образования, медиаграмотности и прав человека. Гранты от 1 до 15 млн тенге. Особый фокус на инклюзивное образование и критическое мышление.",
        "source_url": "https://www.soros.kz/grants",
        "source_name": "soros.kz",
        "amount_min": Decimal("1000000"),
        "amount_max": Decimal("15000000"),
        "currency": "KZT",
        "deadline": date(2025, 9, 1),
        "posted_date": date(2025, 3, 10),
        "eligibility": "НПО, образовательные учреждения, исследователи РК",
        "country": "Казахстан",
        "status": "active",
        "categories": ["education", "social"],
        "keywords": ["Сорос", "образование", "медиаграмотность", "права человека"],
    },
    {
        "title": "Самрук-Казына — Программа поддержки инноваций",
        "description": "Фонд национального благосостояния «Самрук-Қазына» финансирует инновационные проекты в нефтегазовой, горнодобывающей, транспортной и энергетической отраслях. Гранты до 200 млн тенге. Партнёрство с портфельными компаниями фонда.",
        "source_url": "https://sk.kz/innovation",
        "source_name": "sk.kz",
        "amount_min": Decimal("50000000"),
        "amount_max": Decimal("200000000"),
        "currency": "KZT",
        "deadline": date(2025, 11, 30),
        "posted_date": date(2025, 5, 15),
        "eligibility": "Казахстанские компании с инновационными решениями для промышленности",
        "country": "Казахстан",
        "status": "active",
        "categories": ["engineering", "startup"],
        "keywords": ["Самрук-Казына", "инновации", "промышленность", "нефтегаз", "энергетика"],
    },
    {
        "title": "Erasmus+ Казахстан — Международная мобильность студентов",
        "description": "Программа Европейского Союза Erasmus+ финансирует обмен студентами и преподавателями между вузами Казахстана и Европы. Стипендия покрывает проживание (€800-1100/мес), перелёт и страховку. Срок: 3-12 месяцев.",
        "source_url": "https://erasmusplus.kz",
        "source_name": "erasmusplus.kz",
        "amount_min": Decimal("2000000"),
        "amount_max": Decimal("8000000"),
        "currency": "KZT",
        "deadline": date(2025, 10, 30),
        "posted_date": date(2025, 4, 1),
        "eligibility": "Студенты и преподаватели казахстанских вузов-партнёров",
        "country": "Казахстан",
        "region": "Международный",
        "status": "active",
        "categories": ["education", "international"],
        "keywords": ["Erasmus+", "обмен", "Европа", "мобильность", "студенты"],
    },
    {
        "title": "ПРООН — Малые гранты ГЭФ для экологических проектов",
        "description": "Программа малых грантов Глобального экологического фонда (ГЭФ) через ПРООН поддерживает местные экологические инициативы. Гранты до $50,000 (≈24 млн тенге). Направления: биоразнообразие, деградация земель, водные ресурсы, возобновляемая энергия.",
        "source_url": "https://sgp.undp.org/kazakhstan",
        "source_name": "undp.org",
        "amount_min": Decimal("5000000"),
        "amount_max": Decimal("24000000"),
        "currency": "KZT",
        "deadline": date(2025, 12, 15),
        "posted_date": date(2025, 6, 1),
        "eligibility": "НПО, сообщества, фермерские хозяйства Казахстана",
        "country": "Казахстан",
        "status": "active",
        "categories": ["ecology"],
        "keywords": ["ГЭФ", "экология", "малые гранты", "биоразнообразие", "энергия"],
    },
    {
        "title": "British Council Kazakhstan — Newton-Al-Farabi Research Fund",
        "description": "Совместная программа Британского Совета и МОН РК финансирует исследовательское сотрудничество между учёными Казахстана и Великобритании. Гранты до £300,000 (≈180 млн тенге) на совместные проекты длительностью 2-3 года.",
        "source_url": "https://www.britishcouncil.kz/programmes",
        "source_name": "britishcouncil.kz",
        "amount_min": Decimal("50000000"),
        "amount_max": Decimal("180000000"),
        "currency": "KZT",
        "deadline": date(2025, 7, 1),
        "posted_date": date(2025, 1, 20),
        "eligibility": "Исследователи казахстанских и британских вузов/НИИ",
        "country": "Казахстан",
        "region": "Международный",
        "status": "active",
        "categories": ["science", "international"],
        "keywords": ["Newton", "Аль-Фараби", "Великобритания", "совместные исследования"],
    },
    {
        "title": "KazAID — Грант на развитие сельского хозяйства",
        "description": "Казахстанское агентство международного развития совместно с ФАО выделяет гранты для проектов в агросекторе. Поддержка фермеров, внедрение AgriTech, устойчивое земледелие. До 20 млн тенге на проект.",
        "source_url": "https://www.gov.kz/memleket/entities/moa",
        "source_name": "gov.kz",
        "amount_min": Decimal("5000000"),
        "amount_max": Decimal("20000000"),
        "currency": "KZT",
        "deadline": date(2025, 8, 20),
        "posted_date": date(2025, 3, 1),
        "eligibility": "Фермеры, аграрные НПО, AgriTech стартапы Казахстана",
        "country": "Казахстан",
        "status": "active",
        "categories": ["ecology", "startup"],
        "keywords": ["сельское хозяйство", "AgriTech", "фермеры", "ФАО", "KazAID"],
    },
]


async def seed():
    await init_db()
    # Drop and recreate tables for clean seed
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        cat_map = {}
        for cat_data in CATEGORIES:
            cat = Category(**cat_data)
            session.add(cat)
            cat_map[cat_data["slug"]] = cat
        await session.flush()
        print(f"✅ Создано {len(CATEGORIES)} категорий")

        for grant_data in GRANTS:
            cat_slugs = grant_data.pop("categories", [])
            keywords = grant_data.pop("keywords", [])
            grant_data["keywords_ai"] = {"keywords": keywords}
            grant_data["scraped_at"] = datetime.now(timezone.utc)
            grant_data["processed_at"] = datetime.now(timezone.utc)
            grant = Grant(**grant_data)
            grant.categories = [cat_map[s] for s in cat_slugs if s in cat_map]
            session.add(grant)
        await session.flush()
        print(f"✅ Создано {len(GRANTS)} грантов")

        demo = User(
            email="demo@fundingaggregator.kz",
            username="demo",
            hashed_password=hash_password("demo1234"),
            full_name="Демо Пользователь",
            is_active=True,
        )
        session.add(demo)
        await session.flush()
        print("✅ Создан демо пользователь (demo / demo1234)")

        await session.commit()
        print("\n🚀 База данных заполнена казахстанскими грантами!")


if __name__ == "__main__":
    asyncio.run(seed())
