package com.af.shieldsms.data.db

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "messages")
data class MessageEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val address: String,
    val body: String,
    val timestamp: Long,
    val label: String? = null,
    val score: Double? = null,
    val status: String = "PENDING" // PENDING | SENT | FAILED
)
