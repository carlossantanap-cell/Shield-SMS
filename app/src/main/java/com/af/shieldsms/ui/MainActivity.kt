package com.af.shieldsms.ui

import android.Manifest
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.material3.Surface
import androidx.navigation.compose.rememberNavController
import com.af.shieldsms.ui.screens.NavGraph
import com.af.shieldsms.ui.theme.ShieldTheme

class MainActivity : ComponentActivity() {

    private val launcher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { /* UI reacciona por estado */ }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val perms = buildList {
            add(Manifest.permission.RECEIVE_SMS)
            if (Build.VERSION.SDK_INT >= 33) add(Manifest.permission.POST_NOTIFICATIONS)
        }.toTypedArray()
        launcher.launch(perms)

        setContent {
            ShieldTheme {
                Surface { NavGraph(rememberNavController()) }
            }
        }
    }
}
