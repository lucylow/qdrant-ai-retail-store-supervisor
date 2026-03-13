package ch.genaizurich2026.dynamicvector

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform