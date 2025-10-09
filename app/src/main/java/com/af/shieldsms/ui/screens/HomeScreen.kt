package com.af.shieldsms.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.platform.LocalContext
import com.af.shieldsms.data.SmsRepository
import kotlinx.coroutines.flow.collectLatest

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(onOpenSettings: () -> Unit) {
    val ctx = LocalContext.current
    val repo = remember { SmsRepository.get(ctx) }
    var messages by remember { mutableStateOf(emptyList<com.af.shieldsms.data.db.MessageEntity>()) }

    LaunchedEffect(Unit) {
        repo.observeMessages().collectLatest { messages = it }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Shield-SMS") },
                actions = { TextButton(onClick = onOpenSettings) { Text("Settings") } }
            )
        }
    ) { p ->
        LazyColumn(Modifier.padding(p)) {
            items(messages) { msg ->
                ListItem(
                    headlineText = { Text(msg.address, fontWeight = FontWeight.SemiBold) },
                    supportingText = { Text(msg.body, maxLines = 2) },
                    trailingContent = {
                        val label = msg.label ?: "—"
                        AssistChip(onClick = { }, label = { Text(label) })
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { }
                        .padding(horizontal = 12.dp, vertical = 6.dp)
                )
                Divider()
            }
        }
    }
}
