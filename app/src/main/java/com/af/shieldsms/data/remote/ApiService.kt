package com.af.shieldsms.data.remote

import com.squareup.moshi.Moshi
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import retrofit2.http.Body
import retrofit2.http.Headers
import retrofit2.http.POST

interface ApiService {
    @Headers("Content-Type: application/json")
    @POST("/classify")
    suspend fun classify(@Body req: ClassificationRequest): ClassificationResponse

    companion object {
        fun create(baseUrl: String, token: String? = null): ApiService {
            val logger = HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BODY }
            val auth = Interceptor { chain ->
                val req = chain.request().newBuilder().apply {
                    token?.let { header("Authorization", "Bearer $it") }
                }.build()
                chain.proceed(req)
            }
            val client = OkHttpClient.Builder()
                .addInterceptor(auth)
                .addInterceptor(logger)
                .build()
            val moshi = Moshi.Builder().build()
            return Retrofit.Builder()
                .baseUrl(baseUrl)
                .addConverterFactory(MoshiConverterFactory.create(moshi))
                .client(client)
                .build()
                .create(ApiService::class.java)
        }
    }
}
