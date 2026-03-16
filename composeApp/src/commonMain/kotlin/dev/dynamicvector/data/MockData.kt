package dev.dynamicvector.data

import dev.dynamicvector.model.*
import dev.dynamicvector.theme.DVColors

object MockData {

    val events = listOf(
        QueryEvent("1", "Swiss watch deals", "Best automatic watches under CHF 500 near Zürich", "2 min ago", QueryStatus.LIVE,
            listOf(SourceType.QDRANT, SourceType.APIFY, SourceType.LIVEMAP), 24, 0.91f, true,
            listOf(
                QueryResult(1, "Automatic", "Tissot PRX Powermatic 80", "Swiss automatic, 80h power reserve, minimalist dial. Available at Bucherer Zürich Bahnhofstrasse.", listOf("CHF 445", "0.8 km", "In stock"), 0.94f, "Matches your preference for automatic movements with minimalist design. Strong value under CHF 500 budget. Closest physical store to your location."),
                QueryResult(2, "Automatic", "Hamilton Khaki Field Auto", "Swiss-made, 42mm case, date window, exhibition caseback. Dealer in Niederdorf.", listOf("CHF 395", "1.2 km", "In stock"), 0.89f, "Excellent Swiss automatic under budget. Field-style dial is slightly less minimalist but strong overall match."),
                QueryResult(3, "Quartz", "Mondaine Classic 40mm", "Iconic Swiss railway design. Clean dial, sapphire crystal. Available online with store pickup.", listOf("CHF 280", "2.1 km", "Online"), 0.82f, "Perfectly minimalist design and well under budget, but quartz movement doesn't match your automatic preference. Ranked highly on design and value."),
                QueryResult(4, "Automatic", "Certina DS-1 Powermatic 80", "Swiss automatic with 80h reserve. Sport-elegant design. Jelmoli Zürich.", listOf("CHF 475", "0.5 km", "In stock"), 0.78f, "Strong Swiss automatic within budget. Slightly sportier dial than your minimalist preference."),
            )),
        QueryEvent("2", "Competitor outdoor gear", "Track competitor pricing for outdoor gear in Bern region", "6h ago", QueryStatus.STALE,
            listOf(SourceType.QDRANT, SourceType.APIFY), 18, 0.72f, false,
            listOf(
                QueryResult(1, "Jacket", "Mammut Convey 3in1", "Versatile all-weather jacket. Gore-Tex. Multiple competitor prices tracked.", listOf("CHF 320–389", "Bern", "3 retailers"), 0.88f, "Top outdoor brand with significant price variance across competitors. Best deal at SportXX Bern."),
                QueryResult(2, "Backpack", "Deuter Aircontact Lite 50+10", "Large trekking pack. Competitor prices vary by CHF 40.", listOf("CHF 159–199", "Bern", "4 retailers"), 0.81f, "High demand item with notable price differences. Transa has the lowest current price."),
            )),
        QueryEvent("3", "Policy docs onboarding", "Surface relevant policy documents for new hires", "Yesterday", QueryStatus.DONE,
            listOf(SourceType.QDRANT, SourceType.LOCAL), 9, 0.85f, false,
            listOf(
                QueryResult(1, "Policy", "Employee Handbook v3.2", "Comprehensive onboarding guide covering benefits, PTO, and workplace policies.", listOf("PDF", "Local", "Updated Jan 2026"), 0.95f, "Direct match for onboarding queries. Most up-to-date version of the handbook."),
            )),
    )

    val savedQueries = listOf(
        SavedQuery("1", "Swiss watch deals", "Best automatic watches under CHF 500 near Zürich. Prefer minimalist dial, Swiss-made quality.", CompositionType.PIPELINE, listOf(SourceType.QDRANT, SourceType.APIFY, SourceType.LIVEMAP), 5, 24, "Every 6 hours · Next: 2:00 PM"),
        SavedQuery("2", "Competitor outdoor gear", "Track competitor pricing for outdoor gear and camping equipment in the Bern region.", CompositionType.PIPELINE, listOf(SourceType.QDRANT, SourceType.APIFY), 4, 18, "Daily at 7:00 AM"),
        SavedQuery("3", "Policy docs onboarding", "Surface relevant policy documents for employee onboarding questions.", CompositionType.UNION, listOf(SourceType.QDRANT, SourceType.LOCAL), 2, 9, null),
        SavedQuery("4", "Trending near me", "What's trending near my current location this week? Products, events, deals.", CompositionType.UNION, listOf(SourceType.QDRANT, SourceType.APIFY, SourceType.LIVEMAP), 3, 0, null),
    )

    val connectedRepos = listOf(
        Repository("Qdrant", SourceType.QDRANT, "collections", listOf(
            SavedSource("products", "12,847 pts · 768d · Synced 4m ago"),
            SavedSource("hm_ecommerce_products", "105,542 pts · 512d · via HuggingFace"),
            SavedSource("policy_docs", "2,341 pts · 1536d · Local upload"),
        )),
        Repository("Apify", SourceType.APIFY, "actors", listOf(
            SavedSource("price_tracker", "Last run 2h ago · 340 results"),
            SavedSource("google_maps_scraper", "Last run 1d ago · 128 results", isOnline = false),
        )),
        Repository("LiveMap", SourceType.LIVEMAP, "locations", listOf(
            SavedSource("Current GPS", "Zürich · 47.3769°N, 8.5417°E"),
        )),
    )

    val localSources = listOf(
        LocalSource("/Documents/HR", "12 files · 3.8 MB · Indexed 3d ago", true),
        LocalSource("supplier_contacts.csv", "128 KB · Indexed 1w ago", false),
        LocalSource("/Projects/SwissRetail", "47 files · 22.1 MB · Indexed 12h ago", true),
    )

    val exploreSources = listOf(
        ExploreSource("e1", "swiss_retail_products", SourceType.QDRANT, "Comprehensive Swiss retail catalog with 50k+ products across electronics, fashion, outdoor, and luxury goods.", "qdrant-cloud · public · updated 2h ago",
            listOf("Points" to "51,230", "Dimensions" to "768", "Updated" to "2h ago", "Size" to "1.2 GB"),
            schema = listOf(SchemaField("name","keyword"), SchemaField("brand","keyword"), SchemaField("category","keyword"), SchemaField("price","float"), SchemaField("currency","keyword"), SchemaField("rating","float"), SchemaField("location","geo"), SchemaField("sustainability_score","float"), SchemaField("description","text"), SchemaField("tags","keyword[]")),
            sampleRecord = listOf("name" to "\"Tissot PRX Powermatic 80\"", "brand" to "\"Tissot\"", "category" to "\"watches/automatic\"", "price" to "445.00", "rating" to "4.7", "sustainability_score" to "0.82"),
        ),
        ExploreSource("e2", "Qdrant/hm_ecommerce", SourceType.HUGGINGFACE, "H&M fashion product dataset with images, descriptions, and categories. Pre-embedded for Qdrant vector search.", "",
            listOf("Records" to "105,542", "Format" to "Parquet", "Downloads" to "2.4k"), isBookmarked = true, isAlreadySaved = true),
        ExploreSource("e3", "website-content-crawler", SourceType.APIFY, "Crawls any website and extracts structured content. Ideal for feeding product pages into Qdrant.", "",
            listOf("Runs" to "148k", "Rating" to "4.8 ★", "Author" to "Apify")),
        ExploreSource("e4", "Swiss POI database", SourceType.LIVEMAP, "Points of interest across Switzerland — stores, restaurants, transit hubs, landmarks. Real-time from livemap.ch.", "",
            listOf("Locations" to "320k", "Coverage" to "CH-wide", "Updates" to "Hourly")),
    )

    val templates = listOf(
        QueryTemplate("🏷️", "Deal finder", "Qdrant catalog → Apify price scrape → location filter → budget → suggest", listOf(SourceType.QDRANT, SourceType.APIFY, SourceType.LIVEMAP), DVColors.QdrantBg),
        QueryTemplate("📊", "Price monitor", "Schedule daily competitor price scans. Tracks trends and alerts on drops.", listOf(SourceType.APIFY, SourceType.QDRANT), DVColors.ApifyBg),
        QueryTemplate("📍", "Nearby discovery", "Find trending products, events, services near your GPS location.", listOf(SourceType.QDRANT, SourceType.LIVEMAP), DVColors.LiveMapBg),
        QueryTemplate("📚", "Knowledge base", "Semantic search over local documents. Great for onboarding, FAQs.", listOf(SourceType.QDRANT, SourceType.LOCAL), DVColors.LocalBg),
        QueryTemplate("🔄", "Cross-source pipeline", "Chain sources: search → scrape → filter → rank. The power template.", listOf(SourceType.QDRANT, SourceType.APIFY, SourceType.LIVEMAP), DVColors.GitBg),
        QueryTemplate("🌱", "Sustainability scan", "Find eco-certified products. Ranks by sustainability score.", listOf(SourceType.QDRANT, SourceType.APIFY), DVColors.AccentDim),
    )

    val pipelineSteps = listOf(
        PipelineStep(BlockType.SEARCH_QDRANT, listOf(StepSegment.TextPart("Search "), StepSegment.PillPart("products"), StepSegment.TextPart(" for "), StepSegment.PillPart("outdoor gear"), StepSegment.TextPart(" where category is "), StepSegment.PillPart("outdoor"))),
        PipelineStep(BlockType.SCRAPE_APIFY, listOf(StepSegment.TextPart("Scrape prices with "), StepSegment.PillPart("price_tracker"), StepSegment.TextPart(" for results above, limit "), StepSegment.PillPart("50"))),
        PipelineStep(BlockType.FILTER_LOCATION, listOf(StepSegment.TextPart("Filter by location within "), StepSegment.PillPart("30 km"), StepSegment.TextPart(" of "), StepSegment.PillPart("Bern"))),
        PipelineStep(BlockType.SET_BUDGET, listOf(StepSegment.TextPart("Set budget max "), StepSegment.PillPart("CHF 200"))),
        PipelineStep(BlockType.SUGGEST, listOf(StepSegment.TextPart("Suggest top "), StepSegment.PillPart("10"), StepSegment.TextPart(" results, prefer "), StepSegment.PillPart("sustainability, proximity"))),
    )

    val folderItems = listOf(
        FileItem("HR", true, "12 files", true), FileItem("Projects", true, "47 files"),
        FileItem("SwissRetail", true, "23 files", true), FileItem("Invoices", true, "89 files"),
        FileItem("Research", true, "31 files"), FileItem("supplier_contacts.csv", false, "128 KB"),
        FileItem("brand_guidelines.pdf", false, "4.2 MB"),
    )

    val goals = listOf(
        "I prefer sustainable and eco-friendly products",
        "I'm budget-conscious — prioritize value over premium",
        "Based in Zürich, rarely travel more than 30 km",
        "I care about Swiss-made quality",
    )
}
