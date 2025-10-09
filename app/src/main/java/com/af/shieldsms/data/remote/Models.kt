package com.af.shieldsms.data.remote

data class ClassificationRequest(val text: String)
data class ClassificationResponse(
    val label: String,
    val score: Double,
    val features_detected: List<String>? = null
)
