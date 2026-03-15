package ch.genaizurich2026.dynamicvector.data

import ch.genaizurich2026.dynamicvector.model.*

// ── Mock results ─────────────────────────────────────────────────────────────

val mockResults = listOf(
    ContextResultItem(
        id = "1",
        contextId = "ctx-retail",
        matchScore = 95,
        title = "Allbirds Tree Runners",
        subtitle = "Allbirds",
        price = 98.00,
        rating = 4.6,
        source = "allbirds.com",
        tags = listOf(
            ResultTag("Eco-Friendly", TagColor.GREEN),
            ResultTag("Your Style", TagColor.BLUE),
        ),
    ),
    ContextResultItem(
        id = "2",
        contextId = "ctx-retail",
        matchScore = 92,
        title = "Organic Cotton Tee",
        subtitle = "Patagonia",
        price = 45.00,
        rating = 4.8,
        source = "patagonia.com",
        tags = listOf(
            ResultTag("Sustainable", TagColor.GREEN),
            ResultTag("Fair Trade", TagColor.PURPLE),
        ),
    ),
    ContextResultItem(
        id = "3",
        contextId = "ctx-retail",
        matchScore = 88,
        title = "Bamboo Wireless Charger",
        subtitle = "Nimble",
        price = 35.99,
        rating = 4.3,
        source = "gonimble.com",
        tags = listOf(
            ResultTag("Eco-Friendly", TagColor.GREEN),
            ResultTag("Budget Pick", TagColor.BLUE),
        ),
    ),
    ContextResultItem(
        id = "4",
        contextId = "ctx-retail",
        matchScore = 85,
        title = "Recycled Canvas Backpack",
        subtitle = "Cotopaxi",
        price = 75.00,
        rating = 4.7,
        source = "cotopaxi.com",
        tags = listOf(
            ResultTag("B Corp", TagColor.PURPLE),
            ResultTag("Local Pickup", TagColor.BLUE),
        ),
    ),
    ContextResultItem(
        id = "5",
        contextId = "ctx-retail",
        matchScore = 82,
        title = "Fair Trade Coffee Beans",
        subtitle = "Counter Culture",
        price = 16.50,
        rating = 4.9,
        source = "counterculturecoffee.com",
        tags = listOf(
            ResultTag("Fair Trade", TagColor.PURPLE),
            ResultTag("Top Rated", TagColor.GREEN),
        ),
    ),
)

// ── Mock saved queries ───────────────────────────────────────────────────────

val mockSavedQueries = listOf(
    ContextQuery(
        id = "q1",
        name = "Weekly Groceries",
        contextIds = listOf("ctx-retail"),
        answers = listOf(
            ContextAnswer("q-category", "category", listOf("groceries"), "Groceries"),
            ContextAnswer("q-location", "location", listOf("local-5"), "Local"),
        ),
        naturalLanguage = "Best organic produce deals within 5 miles",
        createdAt = "2026-03-08",
        scheduled = true,
        scheduleInterval = "weekly",
        lastRun = "2026-03-10",
    ),
    ContextQuery(
        id = "q2",
        name = "Gift Ideas",
        contextIds = listOf("ctx-retail"),
        answers = listOf(
            ContextAnswer("q-price", "price", listOf("0-50"), "Under \$50"),
            ContextAnswer("q-sustainability", "sustainability", listOf("eco"), "Eco-Friendly"),
        ),
        naturalLanguage = "Unique eco-friendly gifts under \$50",
        createdAt = "2026-03-05",
    ),
    ContextQuery(
        id = "q3",
        name = "Running Gear",
        contextIds = listOf("ctx-retail"),
        answers = listOf(
            ContextAnswer("q-category", "category", listOf("clothing"), "Clothing"),
            ContextAnswer("q-rating", "rating", listOf("4+"), "4\u2605+"),
        ),
        naturalLanguage = "Best rated running shoes for flat feet",
        createdAt = "2026-03-01",
        scheduled = true,
        scheduleInterval = "daily",
        lastRun = "2026-03-11",
    ),
)

// ── Mock profile ─────────────────────────────────────────────────────────────

val mockProfile = UserProfile(
    name = "Alex Johnson",
    username = "alexj",
    email = "alex.johnson@example.com",
    phone = "+1 (503) 555-0142",
    location = "Portland, OR",
    memberSince = "January 2026",
    contextId = "ctx-profile",
)

// ── Mock history ─────────────────────────────────────────────────────────────

val mockHistory = listOf(
    HistoryEntry("h1", "Weekly Groceries", "2026-03-10 14:30", 12, listOf("Retail Products")),
    HistoryEntry("h2", "Running Gear", "2026-03-11 09:15", 8, listOf("Retail Products")),
    HistoryEntry("h3", "Gift Ideas", "2026-03-09 16:00", 5, listOf("Retail Products")),
)

// ── Shopping context questions ───────────────────────────────────────────────

val shoppingQuestions = listOf(
    ContextQuestion(
        id = "q-category",
        fieldKey = "category",
        question = "What are you shopping for?",
        options = listOf(
            ContextOption("cat-electronics", "Electronics", "electronics"),
            ContextOption("cat-groceries", "Groceries", "groceries"),
            ContextOption("cat-clothing", "Clothing", "clothing"),
            ContextOption("cat-home", "Home & Garden", "home"),
            ContextOption("cat-beauty", "Beauty", "beauty"),
            ContextOption("cat-sports", "Sports", "sports"),
        ),
    ),
    ContextQuestion(
        id = "q-price",
        fieldKey = "price",
        question = "What's your budget?",
        options = listOf(
            ContextOption("price-under25", "Under \$25", "0-25"),
            ContextOption("price-25-50", "\$25 \u2013 \$50", "25-50"),
            ContextOption("price-50-100", "\$50 \u2013 \$100", "50-100"),
            ContextOption("price-100-200", "\$100 \u2013 \$200", "100-200"),
            ContextOption("price-200plus", "\$200+", "200+"),
        ),
    ),
    ContextQuestion(
        id = "q-brand",
        fieldKey = "brand",
        question = "Any brand preferences?",
        options = listOf(
            ContextOption("brand-ethical", "Ethical Brands", "ethical"),
            ContextOption("brand-local", "Local Makers", "local-makers"),
            ContextOption("brand-premium", "Premium", "premium"),
            ContextOption("brand-budget", "Budget Brands", "budget"),
        ),
    ),
    ContextQuestion(
        id = "q-location",
        fieldKey = "location",
        question = "Where do you want to shop?",
        options = listOf(
            ContextOption("loc-local", "Local (5 mi)", "local-5"),
            ContextOption("loc-nearby", "Nearby (25 mi)", "nearby-25"),
            ContextOption("loc-online", "Online Only", "online"),
            ContextOption("loc-instore", "In-Store Pickup", "instore"),
        ),
    ),
    ContextQuestion(
        id = "q-sustainability",
        fieldKey = "sustainability",
        question = "Do sustainability features matter?",
        options = listOf(
            ContextOption("sus-eco", "Eco-Friendly", "eco"),
            ContextOption("sus-fairtrade", "Fair Trade", "fairtrade"),
            ContextOption("sus-recycled", "Recycled Materials", "recycled"),
            ContextOption("sus-bcorp", "B Corp", "bcorp"),
        ),
    ),
    ContextQuestion(
        id = "q-rating",
        fieldKey = "rating",
        question = "Minimum rating?",
        options = listOf(
            ContextOption("rate-4plus", "4\u2605 and up", "4+"),
            ContextOption("rate-45plus", "4.5\u2605 and up", "4.5+"),
        ),
    ),
    ContextQuestion(
        id = "q-custom",
        fieldKey = "custom",
        question = "Anything else to narrow it down?",
        options = listOf(
            ContextOption("cust-coupons", "Has Coupons", "coupons"),
            ContextOption("cust-new", "New Releases", "new-releases"),
            ContextOption("cust-sale", "On Sale", "on-sale"),
            ContextOption("cust-trending", "Trending", "trending"),
        ),
        multiSelect = true,
    ),
)

// ── Mock contexts ────────────────────────────────────────────────────────────

val mockContexts = listOf(
    Context(
        id = "ctx-retail",
        name = "Retail Products",
        description = "Product catalog with pricing, ratings, and availability",
        sourceType = ContextSourceType.VECTOR_COLLECTION,
        sourceConfig = ContextSourceConfig(
            collectionName = "products",
            embeddingModel = "sentence-transformers/all-mpnet-base-v2",
        ),
        questions = shoppingQuestions,
        resultSchema = listOf(
            ResultFieldSchema("title", "Name", FieldType.STRING),
            ResultFieldSchema("price", "Price", FieldType.PRICE, sortable = true, filterable = true),
            ResultFieldSchema("rating", "Rating", FieldType.RATING, sortable = true, filterable = true),
            ResultFieldSchema("brand", "Brand", FieldType.STRING, filterable = true),
            ResultFieldSchema("source", "Source", FieldType.URL),
        ),
        createdAt = "2026-02-15",
    ),
    Context(
        id = "ctx-services",
        name = "Local Services",
        description = "Local service providers with reviews and scheduling",
        sourceType = ContextSourceType.SCRAPING_AGENT,
        sourceConfig = ContextSourceConfig(
            endpoint = "https://api.example.com/services",
        ),
        questions = listOf(
            ContextQuestion(
                id = "svc-type",
                fieldKey = "service_type",
                question = "What type of service?",
                options = listOf(
                    ContextOption("svc-plumbing", "Plumbing", "plumbing"),
                    ContextOption("svc-electrical", "Electrical", "electrical"),
                    ContextOption("svc-cleaning", "Cleaning", "cleaning"),
                    ContextOption("svc-landscaping", "Landscaping", "landscaping"),
                ),
            ),
            ContextQuestion(
                id = "svc-location",
                fieldKey = "location",
                question = "Where do you need service?",
                options = listOf(
                    ContextOption("loc-local", "Local (5 mi)", "local-5"),
                    ContextOption("loc-nearby", "Nearby (25 mi)", "nearby-25"),
                ),
            ),
        ),
        resultSchema = listOf(
            ResultFieldSchema("title", "Provider", FieldType.STRING),
            ResultFieldSchema("rating", "Rating", FieldType.RATING, sortable = true),
            ResultFieldSchema("price", "Price", FieldType.PRICE, sortable = true),
        ),
        createdAt = "2026-03-01",
    ),
    Context(
        id = "ctx-research",
        name = "Research Papers",
        description = "Academic papers, citations, and abstracts",
        sourceType = ContextSourceType.DOCUMENT_STORE,
        sourceConfig = ContextSourceConfig(
            collectionName = "papers",
        ),
        questions = listOf(
            ContextQuestion(
                id = "res-topic",
                fieldKey = "topic",
                question = "What topic area?",
                options = listOf(
                    ContextOption("topic-ai", "AI / ML", "ai-ml"),
                    ContextOption("topic-sustainability", "Sustainability", "sustainability"),
                    ContextOption("topic-economics", "Economics", "economics"),
                ),
            ),
        ),
        resultSchema = listOf(
            ResultFieldSchema("title", "Title", FieldType.STRING),
            ResultFieldSchema("authors", "Authors", FieldType.STRING),
            ResultFieldSchema("year", "Year", FieldType.NUMBER, sortable = true),
        ),
        createdAt = "2026-03-10",
    ),
    Context(
        id = "ctx-profile",
        name = "My Profile",
        description = "Your preferences — automatically enriches other Contexts",
        sourceType = ContextSourceType.USER_PROFILE,
        sourceConfig = ContextSourceConfig(),
        questions = listOf(
            ContextQuestion(
                id = "prof-location",
                fieldKey = "location",
                question = "Your default location",
                options = listOf(
                    ContextOption("loc-portland", "Portland, OR", "portland"),
                    ContextOption("loc-zurich", "Zurich", "zurich"),
                    ContextOption("loc-berlin", "Berlin", "berlin"),
                ),
            ),
            ContextQuestion(
                id = "prof-budget",
                fieldKey = "price",
                question = "Your typical budget",
                options = listOf(
                    ContextOption("budget-low", "Under \$50", "0-50"),
                    ContextOption("budget-mid", "Under \$200", "0-200"),
                    ContextOption("budget-high", "No limit", "0+"),
                ),
            ),
            ContextQuestion(
                id = "prof-sustainability",
                fieldKey = "sustainability",
                question = "Sustainability preference",
                options = listOf(
                    ContextOption("sus-eco", "Eco-Friendly", "eco"),
                    ContextOption("sus-fairtrade", "Fair Trade", "fairtrade"),
                ),
                multiSelect = true,
            ),
        ),
        resultSchema = emptyList(),
        createdAt = "2026-01-15",
    ),
)

// ── Labels ───────────────────────────────────────────────────────────────────

val fieldLabels = mapOf(
    "category" to "Category",
    "brand" to "Brand",
    "price" to "Budget",
    "location" to "Location",
    "sustainability" to "Sustainability",
    "rating" to "Rating",
    "custom" to "Extras",
    "service_type" to "Service Type",
    "topic" to "Topic",
)

val intervalLabels = mapOf(
    "hourly" to "Every hour",
    "daily" to "Every day",
    "weekly" to "Every week",
)
