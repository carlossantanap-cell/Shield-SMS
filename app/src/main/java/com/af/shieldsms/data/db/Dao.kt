package com.af.shieldsms.data.db

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Dao
interface MessageDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(msg: MessageEntity): Long

    @Query("SELECT * FROM messages ORDER BY timestamp DESC")
    fun getAll(): Flow<List<MessageEntity>>

    @Query("UPDATE messages SET label=:label, score=:score, status=:status WHERE id=:id")
    suspend fun updateClassification(id: Long, label: String?, score: Double?, status: String)
}
