package ch.genaizurich2026.dynamicvector.viewmodel

import androidx.lifecycle.ViewModel
import ch.genaizurich2026.dynamicvector.model.*
import ch.genaizurich2026.dynamicvector.navigation.Screen
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

/**
 * Snapshot of the query-builder wizard while the user steps through
 * a Context's questions.
 */
data class ActiveQueryState(
    val contextIds: List<String>,
    val composition: ContextComposition?,
    val questions: List<ContextQuestion>,
    val currentQuestionIndex: Int = 0,
    val answers: List<ContextAnswer> = emptyList(),
    val naturalLanguage: String = "",
    val exclusions: List<String> = emptyList(),
    val refinementNotes: List<String> = emptyList(),
) {
    val currentQuestion: ContextQuestion?
        get() = questions.getOrNull(currentQuestionIndex)

    val isComplete: Boolean
        get() = currentQuestionIndex >= questions.size
}

class DynamicVectorViewModel : ViewModel() {

    // ── Navigation ───────────────────────────────────────────────────────

    private val _currentScreen = MutableStateFlow<Screen>(Screen.Login)
    val currentScreen: StateFlow<Screen> = _currentScreen.asStateFlow()

    fun navigateTo(screen: Screen) {
        _currentScreen.value = screen
    }

    // ── Auth ─────────────────────────────────────────────────────────────

    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()

    fun login(username: String, password: String) {
        // TODO: real auth against backend
        _isLoggedIn.value = true
        _currentScreen.value = Screen.Home
    }

    fun logout() {
        _isLoggedIn.value = false
        _currentScreen.value = Screen.Login
    }

    // ── User profile ─────────────────────────────────────────────────────

    private val _profile = MutableStateFlow<UserProfile?>(null)
    val profile: StateFlow<UserProfile?> = _profile.asStateFlow()

    fun updateProfile(profile: UserProfile) {
        _profile.value = profile
    }

    /**
     * Returns default answers that the user-profile Context can provide
     * for another Context's questions. For example, if the profile has a
     * location and the target Context asks a location question, the
     * profile's value is returned as a pre-filled answer.
     */
    fun getProfileDefaults(targetContextId: String): List<ContextAnswer> {
        val profileCtx = _contexts.value.find { it.sourceType == ContextSourceType.USER_PROFILE }
            ?: return emptyList()
        val targetCtx = _contexts.value.find { it.id == targetContextId }
            ?: return emptyList()

        // Match profile answers to target questions by fieldKey
        val profileAnswers = _profileAnswers.value
        return targetCtx.questions.mapNotNull { question ->
            profileAnswers[question.fieldKey]?.let { values ->
                ContextAnswer(
                    questionId = question.id,
                    fieldKey = question.fieldKey,
                    selectedValues = values,
                    label = "From profile",
                )
            }
        }
    }

    // Stored answers from the user-profile Context, keyed by fieldKey
    private val _profileAnswers = MutableStateFlow<Map<String, List<String>>>(emptyMap())

    fun setProfileAnswer(fieldKey: String, values: List<String>) {
        _profileAnswers.update { it + (fieldKey to values) }
    }

    // ── Contexts ─────────────────────────────────────────────────────────

    private val _contexts = MutableStateFlow<List<Context>>(emptyList())
    val contexts: StateFlow<List<Context>> = _contexts.asStateFlow()

    fun addContext(context: Context) {
        _contexts.update { it + context }
    }

    fun updateContext(context: Context) {
        _contexts.update { list -> list.map { if (it.id == context.id) context else it } }
    }

    fun removeContext(id: String) {
        _contexts.update { list -> list.filter { it.id != id } }
        // Also remove from any compositions
        _compositions.update { list ->
            list.map { comp ->
                comp.copy(contextIds = comp.contextIds.filter { it != id })
            }.filter { it.contextIds.size >= 2 }
        }
    }

    fun toggleContext(id: String) {
        _contexts.update { list ->
            list.map { if (it.id == id) it.copy(active = !it.active) else it }
        }
    }

    // ── Context compositions ─────────────────────────────────────────────

    private val _compositions = MutableStateFlow<List<ContextComposition>>(emptyList())
    val compositions: StateFlow<List<ContextComposition>> = _compositions.asStateFlow()

    fun addComposition(composition: ContextComposition) {
        _compositions.update { it + composition }
    }

    fun removeComposition(id: String) {
        _compositions.update { list -> list.filter { it.id != id } }
    }

    // ── Query builder ────────────────────────────────────────────────────

    private val _activeQuery = MutableStateFlow<ActiveQueryState?>(null)
    val activeQuery: StateFlow<ActiveQueryState?> = _activeQuery.asStateFlow()

    /**
     * Start building a query against the given Contexts.
     * Merges all questions from selected Contexts (deduplicating by fieldKey),
     * and pre-fills any answers available from the user-profile Context.
     */
    fun startQuery(
        contextIds: List<String>,
        composition: ContextComposition? = null,
    ) {
        val selected = _contexts.value.filter { it.id in contextIds }
        val allQuestions = selected
            .flatMap { it.questions }
            .distinctBy { it.fieldKey }

        // Pre-fill from user profile
        val profileDefaults = contextIds.flatMap { getProfileDefaults(it) }
            .distinctBy { it.fieldKey }

        _activeQuery.value = ActiveQueryState(
            contextIds = contextIds,
            composition = composition,
            questions = allQuestions,
            answers = profileDefaults,
        )
        _resultSet.value = null
    }

    fun answerQuestion(answer: ContextAnswer) {
        _activeQuery.update { state ->
            state?.let {
                val updated = it.answers.filter { a -> a.questionId != answer.questionId } + answer
                it.copy(
                    answers = updated,
                    currentQuestionIndex = it.currentQuestionIndex + 1,
                )
            }
        }
    }

    fun skipQuestion() {
        _activeQuery.update { state ->
            state?.copy(currentQuestionIndex = (state.currentQuestionIndex + 1))
        }
    }

    fun previousQuestion() {
        _activeQuery.update { state ->
            state?.copy(
                currentQuestionIndex = (state.currentQuestionIndex - 1).coerceAtLeast(0),
            )
        }
    }

    fun setNaturalLanguage(text: String) {
        _activeQuery.update { it?.copy(naturalLanguage = text) }
    }

    fun addExclusion(resultId: String) {
        _activeQuery.update { state ->
            state?.copy(exclusions = state.exclusions + resultId)
        }
    }

    fun removeExclusion(resultId: String) {
        _activeQuery.update { state ->
            state?.copy(exclusions = state.exclusions.filter { it != resultId })
        }
    }

    fun resetQuery() {
        _activeQuery.value = null
        _resultSet.value = null
    }

    // ── Search execution ─────────────────────────────────────────────────

    private val _resultSet = MutableStateFlow<ContextResultSet?>(null)
    val resultSet: StateFlow<ContextResultSet?> = _resultSet.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    fun clearError() {
        _error.value = null
    }

    /**
     * Execute the active query against the backend.
     * Translates [ContextAnswer]s into Qdrant filters, runs vector search,
     * and generates suggested refinement questions from result distribution.
     */
    fun executeQuery() {
        val state = _activeQuery.value ?: return
        _isLoading.value = true
        _error.value = null

        // TODO: call backend POST /api/search with:
        //   - state.answers → structured filters (fieldKey → values)
        //   - state.naturalLanguage → vector search query text
        //   - state.exclusions → exclude IDs
        //   - state.contextIds → which collections to search
        //   - state.composition → how to combine results
        //
        // Backend returns ContextResultSet with items + suggestedRefinements.
        // For now this is a placeholder — wire up Ktor client here.

        _isLoading.value = false
    }

    /**
     * Answer a suggested refinement question to narrow the result set.
     * Adds the answer and re-executes the query.
     */
    fun refineQuery(refinementAnswer: ContextAnswer) {
        _activeQuery.update { state ->
            state?.copy(answers = state.answers + refinementAnswer)
        }
        executeQuery()
    }

    // ── Result sorting ───────────────────────────────────────────────────

    private val _sortOption = MutableStateFlow(SortOption.MATCH)
    val sortOption: StateFlow<SortOption> = _sortOption.asStateFlow()

    fun sortResults(by: SortOption) {
        _sortOption.value = by
        _resultSet.update { set ->
            set?.copy(items = when (by) {
                SortOption.MATCH -> set.items.sortedByDescending { it.matchScore }
                SortOption.PRICE_ASC -> set.items.sortedBy { it.price ?: Double.MAX_VALUE }
                SortOption.PRICE_DESC -> set.items.sortedByDescending { it.price ?: 0.0 }
                SortOption.RATING -> set.items.sortedByDescending { it.rating ?: 0.0 }
            })
        }
    }

    // ── Saved queries ────────────────────────────────────────────────────

    private val _savedQueries = MutableStateFlow<List<ContextQuery>>(emptyList())
    val savedQueries: StateFlow<List<ContextQuery>> = _savedQueries.asStateFlow()

    fun saveQuery(name: String) {
        val state = _activeQuery.value ?: return
        val query = ContextQuery(
            id = "q-${_savedQueries.value.size + 1}",
            name = name,
            contextIds = state.contextIds,
            composition = state.composition,
            answers = state.answers,
            naturalLanguage = state.naturalLanguage,
            exclusions = state.exclusions,
            createdAt = "", // TODO: format current date
        )
        _savedQueries.update { it + query }
    }

    fun deleteSavedQuery(queryId: String) {
        _savedQueries.update { list -> list.filter { it.id != queryId } }
    }

    fun runSavedQuery(queryId: String) {
        val query = _savedQueries.value.find { it.id == queryId } ?: return
        startQuery(query.contextIds, query.composition)
        _activeQuery.update {
            it?.copy(
                answers = query.answers,
                naturalLanguage = query.naturalLanguage,
                exclusions = query.exclusions,
                currentQuestionIndex = it.questions.size, // skip to end
            )
        }
        executeQuery()
    }

    fun scheduleQuery(queryId: String, interval: String?) {
        _savedQueries.update { list ->
            list.map {
                if (it.id == queryId) it.copy(
                    scheduled = interval != null,
                    scheduleInterval = interval,
                ) else it
            }
        }
    }

    // ── History ──────────────────────────────────────────────────────────

    private val _history = MutableStateFlow<List<HistoryEntry>>(emptyList())
    val history: StateFlow<List<HistoryEntry>> = _history.asStateFlow()

    fun clearHistory() {
        _history.value = emptyList()
    }
}
