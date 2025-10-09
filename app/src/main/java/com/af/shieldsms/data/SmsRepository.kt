package com.af.shieldsms.data

import android.content.Context
import androidx.room.Room
import com.af.shieldsms.data.db.AppDatabase
import com.af.shieldsms.data.db.MessageEntity
import com.af.shieldsms.data.remote.ApiService
import com.af.shieldsms.data.remote.ClassificationRequest
import kotlinx.coroutines.flow.Flow

class SmsRepository private constructor(context: Context) {
    private val db = Room.databaseBuilder(
        context.applicationContext, AppDatabase::class.java, "shieldsms.db"
    ).fallbackToDestructiveMigration().build()

    private var api: ApiService = ApiService.create("http://10.0.2.2:8000", null)

    fun setApi(baseUrl: String, token: String?) {
        api = ApiService.create(baseUrl, token)
    }

    suspend fun saveIncoming(address: String, body: String, ts: Long): Long =
        db.messageDao().insert(MessageEntity(address = address, body = body, timestamp = ts))

    fun observeMessages(): Flow<List<MessageEntity>> = db.messageDao().getAll()

    suspend fun classifyAndUpdate(id: Long, text: String) {
        runCatching {
            val r = api.classify(ClassificationRequest(text))
            db.messageDao().updateClassification(id, r.label, r.score, "SENT")
        }.onFailure {
            db.messageDao().updateClassification(id, null, null, "FAILED")
        }
    }

    companion object {
        @Volatile private var INSTANCE: SmsRepository? = null
        fun get(context: Context): SmsRepository =
            INSTANCE ?: synchronized(this) {
                INSTANCE ?: SmsRepository(context).also { INSTANCE = it }
            }
    }
}
