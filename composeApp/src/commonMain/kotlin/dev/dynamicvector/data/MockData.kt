package dev.dynamicvector.data

import dev.dynamicvector.model.*

// ── Mock results ─────────────────────────────────────────────────────────────

val mockResults = listOf(
    _root_ide_package_.dev.dynamicvector.model.ContextResultItem(
        id = "1",
        contextId = "ctx-retail",
        matchScore = 95,
        title = "Allbirds Tree Runners",
        subtitle = "Allbirds",
        price = 98.00,
        rating = 4.6,
        source = "allbirds.com",
        tags = listOf(
            _root_ide_package_.dev.dynamicvector.model.ResultTag(
                "Eco-Friendly",
                _root_ide_package_.dev.dynamicvector.model.TagColor.GREEN
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultTag(
                "Your Style",
                _root_ide_package_.dev.dynamicvector.model.TagColor.BLUE
            ),
        ),
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextResultItem(
        id = "2",
        contextId = "ctx-retail",
        matchScore = 92,
        title = "Organic Cotton Tee",
        subtitle = "Patagonia",
        price = 45.00,
        rating = 4.8,
        source = "patagonia.com",
        tags = listOf(
            _root_ide_package_.dev.dynamicvector.model.ResultTag(
                "Sustainable",
                _root_ide_package_.dev.dynamicvector.model.TagColor.GREEN
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultTag(
                "Fair Trade",
                _root_ide_package_.dev.dynamicvector.model.TagColor.PURPLE
            ),
        ),
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextResultItem(
        id = "3",
        contextId = "ctx-retail",
        matchScore = 88,
        title = "Bamboo Wireless Charger",
        subtitle = "Nimble",
        price = 35.99,
        rating = 4.3,
        source = "gonimble.com",
        tags = listOf(
            _root_ide_package_.dev.dynamicvector.model.ResultTag(
                "Eco-Friendly",
                _root_ide_package_.dev.dynamicvector.model.TagColor.GREEN
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultTag(
                "Budget Pick",
                _root_ide_package_.dev.dynamicvector.model.TagColor.BLUE
            ),
        ),
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextResultItem(
        id = "4",
        contextId = "ctx-retail",
        matchScore = 85,
        title = "Recycled Canvas Backpack",
        subtitle = "Cotopaxi",
        price = 75.00,
        rating = 4.7,
        source = "cotopaxi.com",
        tags = listOf(
            _root_ide_package_.dev.dynamicvector.model.ResultTag(
                "B Corp",
                _root_ide_package_.dev.dynamicvector.model.TagColor.PURPLE
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultTag(
                "Local Pickup",
                _root_ide_package_.dev.dynamicvector.model.TagColor.BLUE
            ),
        ),
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextResultItem(
        id = "5",
        contextId = "ctx-retail",
        matchScore = 82,
        title = "Fair Trade Coffee Beans",
        subtitle = "Counter Culture",
        price = 16.50,
        rating = 4.9,
        source = "counterculturecoffee.com",
        tags = listOf(
            _root_ide_package_.dev.dynamicvector.model.ResultTag(
                "Fair Trade",
                _root_ide_package_.dev.dynamicvector.model.TagColor.PURPLE
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultTag(
                "Top Rated",
                _root_ide_package_.dev.dynamicvector.model.TagColor.GREEN
            ),
        ),
    ),
)

// ── Mock saved queries ───────────────────────────────────────────────────────

val mockSavedQueries = listOf(
    _root_ide_package_.dev.dynamicvector.model.ContextQuery(
        id = "q1",
        name = "Weekly Groceries",
        contextIds = listOf("ctx-retail"),
        answers = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextAnswer(
                "q-category",
                "category",
                listOf("groceries"),
                "Groceries"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextAnswer(
                "q-location",
                "location",
                listOf("local-5"),
                "Local"
            ),
        ),
        naturalLanguage = "Best organic produce deals within 5 miles",
        createdAt = "2026-03-08",
        scheduled = true,
        scheduleInterval = "weekly",
        lastRun = "2026-03-10",
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextQuery(
        id = "q2",
        name = "Gift Ideas",
        contextIds = listOf("ctx-retail"),
        answers = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextAnswer(
                "q-price",
                "price",
                listOf("0-50"),
                "Under \$50"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextAnswer(
                "q-sustainability",
                "sustainability",
                listOf("eco"),
                "Eco-Friendly"
            ),
        ),
        naturalLanguage = "Unique eco-friendly gifts under \$50",
        createdAt = "2026-03-05",
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextQuery(
        id = "q3",
        name = "Running Gear",
        contextIds = listOf("ctx-retail"),
        answers = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextAnswer(
                "q-category",
                "category",
                listOf("clothing"),
                "Clothing"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextAnswer(
                "q-rating",
                "rating",
                listOf("4+"),
                "4\u2605+"
            ),
        ),
        naturalLanguage = "Best rated running shoes for flat feet",
        createdAt = "2026-03-01",
        scheduled = true,
        scheduleInterval = "daily",
        lastRun = "2026-03-11",
    ),
)

// ── Mock profile ─────────────────────────────────────────────────────────────

val mockProfile = _root_ide_package_.dev.dynamicvector.model.UserProfile(
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
    _root_ide_package_.dev.dynamicvector.model.HistoryEntry(
        "h1",
        "Weekly Groceries",
        "2026-03-10 14:30",
        12,
        listOf("Retail Products")
    ),
    _root_ide_package_.dev.dynamicvector.model.HistoryEntry(
        "h2",
        "Running Gear",
        "2026-03-11 09:15",
        8,
        listOf("Retail Products")
    ),
    _root_ide_package_.dev.dynamicvector.model.HistoryEntry(
        "h3",
        "Gift Ideas",
        "2026-03-09 16:00",
        5,
        listOf("Retail Products")
    ),
)

// ── Shopping context questions ───────────────────────────────────────────────

val shoppingQuestions = listOf(
    _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
        id = "q-category",
        fieldKey = "category",
        question = "What are you shopping for?",
        options = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "cat-electronics",
                "Electronics",
                "electronics"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "cat-groceries",
                "Groceries",
                "groceries"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "cat-clothing",
                "Clothing",
                "clothing"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "cat-home",
                "Home & Garden",
                "home"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "cat-beauty",
                "Beauty",
                "beauty"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "cat-sports",
                "Sports",
                "sports"
            ),
        ),
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
        id = "q-price",
        fieldKey = "price",
        question = "What's your budget?",
        options = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "price-under25",
                "Under \$25",
                "0-25"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "price-25-50",
                "\$25 \u2013 \$50",
                "25-50"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "price-50-100",
                "\$50 \u2013 \$100",
                "50-100"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "price-100-200",
                "\$100 \u2013 \$200",
                "100-200"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "price-200plus",
                "\$200+",
                "200+"
            ),
        ),
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
        id = "q-brand",
        fieldKey = "brand",
        question = "Any brand preferences?",
        options = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "brand-ethical",
                "Ethical Brands",
                "ethical"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "brand-local",
                "Local Makers",
                "local-makers"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "brand-premium",
                "Premium",
                "premium"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "brand-budget",
                "Budget Brands",
                "budget"
            ),
        ),
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
        id = "q-location",
        fieldKey = "location",
        question = "Where do you want to shop?",
        options = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "loc-local",
                "Local (5 mi)",
                "local-5"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "loc-nearby",
                "Nearby (25 mi)",
                "nearby-25"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "loc-online",
                "Online Only",
                "online"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "loc-instore",
                "In-Store Pickup",
                "instore"
            ),
        ),
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
        id = "q-sustainability",
        fieldKey = "sustainability",
        question = "Do sustainability features matter?",
        options = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "sus-eco",
                "Eco-Friendly",
                "eco"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "sus-fairtrade",
                "Fair Trade",
                "fairtrade"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "sus-recycled",
                "Recycled Materials",
                "recycled"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "sus-bcorp",
                "B Corp",
                "bcorp"
            ),
        ),
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
        id = "q-rating",
        fieldKey = "rating",
        question = "Minimum rating?",
        options = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "rate-4plus",
                "4\u2605 and up",
                "4+"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "rate-45plus",
                "4.5\u2605 and up",
                "4.5+"
            ),
        ),
    ),
    _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
        id = "q-custom",
        fieldKey = "custom",
        question = "Anything else to narrow it down?",
        options = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "cust-coupons",
                "Has Coupons",
                "coupons"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "cust-new",
                "New Releases",
                "new-releases"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "cust-sale",
                "On Sale",
                "on-sale"
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextOption(
                "cust-trending",
                "Trending",
                "trending"
            ),
        ),
        multiSelect = true,
    ),
)

// ── Mock contexts ────────────────────────────────────────────────────────────

val mockContexts = listOf(
    _root_ide_package_.dev.dynamicvector.model.Context(
        id = "ctx-retail",
        name = "Retail Products",
        description = "Product catalog with pricing, ratings, and availability",
        sourceType = _root_ide_package_.dev.dynamicvector.model.ContextSourceType.VECTOR_COLLECTION,
        sourceConfig = _root_ide_package_.dev.dynamicvector.model.ContextSourceConfig(
            collectionName = "products",
            embeddingModel = "sentence-transformers/all-mpnet-base-v2",
        ),
        questions = _root_ide_package_.dev.dynamicvector.data.shoppingQuestions,
        resultSchema = listOf(
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "title",
                "Name",
                _root_ide_package_.dev.dynamicvector.model.FieldType.STRING
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "price",
                "Price",
                _root_ide_package_.dev.dynamicvector.model.FieldType.PRICE,
                sortable = true,
                filterable = true
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "rating",
                "Rating",
                _root_ide_package_.dev.dynamicvector.model.FieldType.RATING,
                sortable = true,
                filterable = true
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "brand",
                "Brand",
                _root_ide_package_.dev.dynamicvector.model.FieldType.STRING,
                filterable = true
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "source",
                "Source",
                _root_ide_package_.dev.dynamicvector.model.FieldType.URL
            ),
        ),
        createdAt = "2026-02-15",
    ),
    _root_ide_package_.dev.dynamicvector.model.Context(
        id = "ctx-services",
        name = "Local Services",
        description = "Local service providers with reviews and scheduling",
        sourceType = _root_ide_package_.dev.dynamicvector.model.ContextSourceType.SCRAPING_AGENT,
        sourceConfig = _root_ide_package_.dev.dynamicvector.model.ContextSourceConfig(
            endpoint = "https://api.example.com/services",
        ),
        questions = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
                id = "svc-type",
                fieldKey = "service_type",
                question = "What type of service?",
                options = listOf(
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "svc-plumbing",
                        "Plumbing",
                        "plumbing"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "svc-electrical",
                        "Electrical",
                        "electrical"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "svc-cleaning",
                        "Cleaning",
                        "cleaning"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "svc-landscaping",
                        "Landscaping",
                        "landscaping"
                    ),
                ),
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
                id = "svc-location",
                fieldKey = "location",
                question = "Where do you need service?",
                options = listOf(
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "loc-local",
                        "Local (5 mi)",
                        "local-5"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "loc-nearby",
                        "Nearby (25 mi)",
                        "nearby-25"
                    ),
                ),
            ),
        ),
        resultSchema = listOf(
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "title",
                "Provider",
                _root_ide_package_.dev.dynamicvector.model.FieldType.STRING
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "rating",
                "Rating",
                _root_ide_package_.dev.dynamicvector.model.FieldType.RATING,
                sortable = true
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "price",
                "Price",
                _root_ide_package_.dev.dynamicvector.model.FieldType.PRICE,
                sortable = true
            ),
        ),
        createdAt = "2026-03-01",
    ),
    _root_ide_package_.dev.dynamicvector.model.Context(
        id = "ctx-research",
        name = "Research Papers",
        description = "Academic papers, citations, and abstracts",
        sourceType = _root_ide_package_.dev.dynamicvector.model.ContextSourceType.DOCUMENT_STORE,
        sourceConfig = _root_ide_package_.dev.dynamicvector.model.ContextSourceConfig(
            collectionName = "papers",
        ),
        questions = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
                id = "res-topic",
                fieldKey = "topic",
                question = "What topic area?",
                options = listOf(
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "topic-ai",
                        "AI / ML",
                        "ai-ml"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "topic-sustainability",
                        "Sustainability",
                        "sustainability"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "topic-economics",
                        "Economics",
                        "economics"
                    ),
                ),
            ),
        ),
        resultSchema = listOf(
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "title",
                "Title",
                _root_ide_package_.dev.dynamicvector.model.FieldType.STRING
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "authors",
                "Authors",
                _root_ide_package_.dev.dynamicvector.model.FieldType.STRING
            ),
            _root_ide_package_.dev.dynamicvector.model.ResultFieldSchema(
                "year",
                "Year",
                _root_ide_package_.dev.dynamicvector.model.FieldType.NUMBER,
                sortable = true
            ),
        ),
        createdAt = "2026-03-10",
    ),
    _root_ide_package_.dev.dynamicvector.model.Context(
        id = "ctx-profile",
        name = "My Profile",
        description = "Your preferences — automatically enriches other Contexts",
        sourceType = _root_ide_package_.dev.dynamicvector.model.ContextSourceType.USER_PROFILE,
        sourceConfig = _root_ide_package_.dev.dynamicvector.model.ContextSourceConfig(),
        questions = listOf(
            _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
                id = "prof-location",
                fieldKey = "location",
                question = "Your default location",
                options = listOf(
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "loc-portland",
                        "Portland, OR",
                        "portland"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "loc-zurich",
                        "Zurich",
                        "zurich"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "loc-berlin",
                        "Berlin",
                        "berlin"
                    ),
                ),
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
                id = "prof-budget",
                fieldKey = "price",
                question = "Your typical budget",
                options = listOf(
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "budget-low",
                        "Under \$50",
                        "0-50"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "budget-mid",
                        "Under \$200",
                        "0-200"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "budget-high",
                        "No limit",
                        "0+"
                    ),
                ),
            ),
            _root_ide_package_.dev.dynamicvector.model.ContextQuestion(
                id = "prof-sustainability",
                fieldKey = "sustainability",
                question = "Sustainability preference",
                options = listOf(
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "sus-eco",
                        "Eco-Friendly",
                        "eco"
                    ),
                    _root_ide_package_.dev.dynamicvector.model.ContextOption(
                        "sus-fairtrade",
                        "Fair Trade",
                        "fairtrade"
                    ),
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
