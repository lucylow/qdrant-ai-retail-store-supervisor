package ch.genaizurich2026.dynamicvector

import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application

fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "DynamicVector",
    ) {
        _root_ide_package_.dev.dynamicvector.App()
    }
}
