package ch.genaizurich2026.dynamicvector.data

import ch.genaizurich2026.dynamicvector.model.*

val mockResults = listOf(
    ShoppingResult(
        id = "1",
        name = "Allbirds Tree Runners",
        brand = "Allbirds",
        price = 98.00,
        rating = 4.6,
        matchScore = 95,
        tags = listOf(
            ResultTag("Eco-Friendly", TagColor.GREEN),
            ResultTag("Your Style", TagColor.BLUE),
        ),
        source = "allbirds.com",
    ),
    ShoppingResult(
        id = "2",
        name = "Organic Cotton Tee",
        brand = "Patagonia",
        price = 45.00,
        rating = 4.8,
        matchScore = 92,
        tags = listOf(
            ResultTag("Sustainable", TagColor.GREEN),
            ResultTag("Fair Trade", TagColor.PURPLE),
        ),
        source = "patagonia.com",
    ),
    ShoppingResult(
        id = "3",
        name = "Bamboo Wireless Charger",
        brand = "Nimble",
        price = 35.99,
        rating = 4.3,
        matchScore = 88,
        tags = listOf(
            ResultTag("Eco-Friendly", TagColor.GREEN),
            ResultTag("Budget Pick", TagColor.BLUE),
        ),
        source = "gonimble.com",
    ),
    ShoppingResult(
        id = "4",
        name = "Recycled Canvas Backpack",
        brand = "Cotopaxi",
        price = 75.00,
        rating = 4.7,
        matchScore = 85,
        tags = listOf(
            ResultTag("B Corp", TagColor.PURPLE),
            ResultTag("Local Pickup", TagColor.BLUE),
        ),
        source = "cotopaxi.com",
    ),
    ShoppingResult(
        id = "5",
        name = "Fair Trade Coffee Beans",
        brand = "Counter Culture",
        price = 16.50,
        rating = 4.9,
        matchScore = 82,
        tags = listOf(
            ResultTag("Fair Trade", TagColor.PURPLE),
            ResultTag("Top Rated", TagColor.GREEN),
        ),
        source = "counterculturecoffee.com",
    ),
)

val mockSavedQueries = listOf(
    ShoppingQuery(
        id = "q1",
        name = "Weekly Groceries",
        filters = listOf(
            QueryFilter("1", FilterType.CATEGORY, "Groceries", "groceries", true),
            QueryFilter("2", FilterType.LOCATION, "Local", "local", true),
        ),
        naturalLanguage = "Best organic produce deals within 5 miles",
        createdAt = "2026-03-08",
        scheduled = true,
        scheduleInterval = "weekly",
        lastRun = "2026-03-10",
    ),
    ShoppingQuery(
        id = "q2",
        name = "Gift Ideas",
        filters = listOf(
            QueryFilter("1", FilterType.PRICE, "Under \$50", "0-50", true),
            QueryFilter("2", FilterType.SUSTAINABILITY, "Eco-Friendly", "eco", true),
        ),
        naturalLanguage = "Unique eco-friendly gifts under \$50",
        createdAt = "2026-03-05",
        scheduled = false,
    ),
    ShoppingQuery(
        id = "q3",
        name = "Running Gear",
        filters = listOf(
            QueryFilter("1", FilterType.CATEGORY, "Clothing", "clothing", true),
            QueryFilter("2", FilterType.RATING, "4\u2605+", "4+", true),
        ),
        naturalLanguage = "Best rated running shoes for flat feet",
        createdAt = "2026-03-01",
        scheduled = true,
        scheduleInterval = "daily",
        lastRun = "2026-03-11",
    ),
)

val mockProfile = UserProfile(
    name = "Alex Johnson",
    username = "alexj",
    email = "alex.johnson@example.com",
    phone = "+1 (503) 555-0142",
    location = "Portland, OR",
    memberSince = "January 2026",
)

val mockHistory = listOf(
    HistoryEntry("h1", "Weekly Groceries", "2026-03-10 14:30", 12),
    HistoryEntry("h2", "Running Gear", "2026-03-11 09:15", 8),
    HistoryEntry("h3", "Gift Ideas", "2026-03-09 16:00", 5),
)

val mockRepositories = listOf(
    Repository(
        id = "repo-1",
        name = "Retail Products",
        endpoint = "https://api.example.com/retail",
        description = "Product catalog with pricing, ratings, and availability",
        createdAt = "2026-02-15",
        preferences = RepositoryPreferences(
            goals = listOf("Find sustainable products", "Compare prices across brands"),
            preferredBrands = listOf("Patagonia", "Allbirds", "Cotopaxi"),
            sustainabilityPriority = "high",
            priceRange = Pair(0, 200),
            values = listOf("Eco-Friendly", "Fair Trade"),
            customNotes = "Prefer items with free shipping",
        ),
    ),
    Repository(
        id = "repo-2",
        name = "Local Services",
        endpoint = "https://api.example.com/services",
        description = "Local service providers with reviews and scheduling",
        createdAt = "2026-03-01",
        preferences = RepositoryPreferences(
            goals = listOf("Find reliable local providers"),
            preferredBrands = emptyList(),
            sustainabilityPriority = "medium",
            priceRange = Pair(0, 500),
            values = listOf("Local", "Verified"),
            customNotes = "",
        ),
    ),
    Repository(
        id = "repo-3",
        name = "Research Papers",
        endpoint = "https://api.example.com/research",
        description = "Academic papers, citations, and abstracts",
        createdAt = "2026-03-10",
    ),
)

val agentQuestions = listOf(
    AgentQuestion(
        id = "q-category",
        type = FilterType.CATEGORY,
        question = "What are you shopping for?",
        options = listOf(
            AgentOption("cat-electronics", "Electronics", "electronics"),
            AgentOption("cat-groceries", "Groceries", "groceries"),
            AgentOption("cat-clothing", "Clothing", "clothing"),
            AgentOption("cat-home", "Home & Garden", "home"),
            AgentOption("cat-beauty", "Beauty", "beauty"),
            AgentOption("cat-sports", "Sports", "sports"),
        ),
    ),
    AgentQuestion(
        id = "q-price",
        type = FilterType.PRICE,
        question = "What's your budget?",
        options = listOf(
            AgentOption("price-under25", "Under \$25", "0-25"),
            AgentOption("price-25-50", "\$25 \u2013 \$50", "25-50"),
            AgentOption("price-50-100", "\$50 \u2013 \$100", "50-100"),
            AgentOption("price-100-200", "\$100 \u2013 \$200", "100-200"),
            AgentOption("price-200plus", "\$200+", "200+"),
        ),
    ),
    AgentQuestion(
        id = "q-brand",
        type = FilterType.BRAND,
        question = "Any brand preferences?",
        options = listOf(
            AgentOption("brand-ethical", "Ethical Brands", "ethical"),
            AgentOption("brand-local", "Local Makers", "local-makers"),
            AgentOption("brand-premium", "Premium", "premium"),
            AgentOption("brand-budget", "Budget Brands", "budget"),
        ),
    ),
    AgentQuestion(
        id = "q-location",
        type = FilterType.LOCATION,
        question = "Where do you want to shop?",
        options = listOf(
            AgentOption("loc-local", "Local (5 mi)", "local-5"),
            AgentOption("loc-nearby", "Nearby (25 mi)", "nearby-25"),
            AgentOption("loc-online", "Online Only", "online"),
            AgentOption("loc-instore", "In-Store Pickup", "instore"),
        ),
    ),
    AgentQuestion(
        id = "q-sustainability",
        type = FilterType.SUSTAINABILITY,
        question = "Do sustainability features matter?",
        options = listOf(
            AgentOption("sus-eco", "Eco-Friendly", "eco"),
            AgentOption("sus-fairtrade", "Fair Trade", "fairtrade"),
            AgentOption("sus-recycled", "Recycled Materials", "recycled"),
            AgentOption("sus-bcorp", "B Corp", "bcorp"),
        ),
    ),
    AgentQuestion(
        id = "q-rating",
        type = FilterType.RATING,
        question = "Minimum rating?",
        options = listOf(
            AgentOption("rate-4plus", "4\u2605 and up", "4+"),
            AgentOption("rate-45plus", "4.5\u2605 and up", "4.5+"),
        ),
    ),
    AgentQuestion(
        id = "q-custom",
        type = FilterType.CUSTOM,
        question = "Anything else to narrow it down?",
        options = listOf(
            AgentOption("cust-coupons", "Has Coupons", "coupons"),
            AgentOption("cust-new", "New Releases", "new-releases"),
            AgentOption("cust-sale", "On Sale", "on-sale"),
            AgentOption("cust-trending", "Trending", "trending"),
        ),
        multiSelect = true,
    ),
)

val typeLabels = mapOf(
    FilterType.CATEGORY to "Category",
    FilterType.BRAND to "Brand",
    FilterType.PRICE to "Budget",
    FilterType.LOCATION to "Location",
    FilterType.SUSTAINABILITY to "Sustainability",
    FilterType.RATING to "Rating",
    FilterType.CUSTOM to "Extras",
)

val intervalLabels = mapOf(
    "hourly" to "Every hour",
    "daily" to "Every day",
    "weekly" to "Every week",
)
