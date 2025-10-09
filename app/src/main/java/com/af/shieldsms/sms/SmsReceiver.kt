package com.af.shieldsms.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log

class SmsReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (Telephony.Sms.Intents.SMS_RECEIVED_ACTION != intent.action) return

        val msgs = Telephony.Sms.Intents.getMessagesFromIntent(intent)
        val body = msgs.joinToString("") { it.messageBody ?: "" }
        val address = msgs.firstOrNull()?.originatingAddress ?: "unknown"
        val ts = msgs.firstOrNull()?.timestampMillis ?: System.currentTimeMillis()

        Log.i("ShieldSMS", "SMS recibido de $address @ $ts: $body")

        // Próximo commit: aquí encolaremos un WorkManager para enviar al backend
        // y también guardaremos en Room. Por ahora, solo log seguro.
    }
}
