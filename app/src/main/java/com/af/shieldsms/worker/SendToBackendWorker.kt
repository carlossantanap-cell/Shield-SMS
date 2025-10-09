package com.af.shieldsms.worker

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.af.shieldsms.data.SmsRepository

class SendToBackendWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        val id = inputData.getLong("messageId", -1L)
        val text = inputData.getString("text") ?: return Result.failure()
        if (id <= 0) return Result.failure()
        return try {
            SmsRepository.get(applicationContext).classifyAndUpdate(id, text)
            Result.success()
        } catch (e: Exception) { Result.retry() }
    }
}
