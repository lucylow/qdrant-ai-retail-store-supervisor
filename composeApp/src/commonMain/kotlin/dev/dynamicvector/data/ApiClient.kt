package dev.dynamicvector.data

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.request.forms.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class TokenResponse(val access_token: String, val token_type: String)

@Serializable
data class UserInfo(val username: String, val full_name: String)

object ApiClient {

    private val client = HttpClient {
        install(ContentNegotiation) {
            json(Json { ignoreUnknownKeys = true })
        }
    }

    var token: String? = null
        private set

    var user: UserInfo? = null
        private set

    suspend fun login(username: String, password: String): Result<UserInfo> {
        return try {
            val tokenResp: TokenResponse = client.submitForm(
                url = "$BASE_URL/token",
                formParameters = parameters {
                    append("username", username)
                    append("password", password)
                },
            ).body()

            token = tokenResp.access_token

            val userInfo: UserInfo = client.get("$BASE_URL/users/me") {
                bearerAuth(tokenResp.access_token)
            }.body()

            user = userInfo
            Result.success(userInfo)
        } catch (e: Exception) {
            token = null
            user = null
            Result.failure(e)
        }
    }

    fun logout() {
        token = null
        user = null
    }
}