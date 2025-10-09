package com.af.shieldsms.ui.screens

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable

@Composable
fun NavGraph(nav: NavHostController) {
    NavHost(navController = nav, startDestination = "home") {
        composable("home") { HomeScreen(onOpenSettings = { nav.navigate("settings") }) }
        composable("settings") { SettingsScreen(onBack = { nav.popBackStack() }) }
    }
}
