package com.ptolemy.seeder

import android.app.*
import android.content.Context
import android.content.Intent
import android.os.*
import androidx.core.app.NotificationCompat
import androidx.lifecycle.LifecycleService
import androidx.lifecycle.MutableLiveData
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.io.File

data class CorpusState(
    val name:    String,
    val label:   String,
    val tag:     String  = "",
    val idx:     Int     = 0,
    val total:   Int     = 0,
    val studied: Int     = 0,
    val skipped: Int     = 0,
    val status:  String  = "WAITING",   // WAITING RUNNING PAUSED COMPLETE ERROR
    val error:   String  = "",
)

object SeedLiveData {
    val foundations = MutableLiveData(CorpusState("foundations", "Foundations"))
    val meaning     = MutableLiveData(CorpusState("meaning",     "Meaning"))
    val fermat      = MutableLiveData(CorpusState("fermat",      "Fermat / War"))
    val allDone     = MutableLiveData(false)

    fun forName(name: String) = when (name) {
        "foundations" -> foundations
        "meaning"     -> meaning
        else          -> fermat
    }
}

class SeedService : LifecycleService() {

    companion object {
        const val CHANNEL_ID  = "ptolemy_seed"
        const val NOTIF_ID    = 1701
        const val ACTION_STOP = "com.ptolemy.seeder.STOP"
    }

    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)

        if (intent?.action == ACTION_STOP) {
            stopSelf()
            return START_NOT_STICKY
        }

        startForeground(NOTIF_ID, buildNotification("Starting…"))
        extractAssets()
        startSeedThread()
        return START_STICKY
    }

    // ── asset extraction ───────────────────────────────────────────────────────

    private fun filesDir(): String = getExternalFilesDir(null)?.absolutePath
        ?: filesDir.absolutePath

    private fun extractAssets() {
        val dir = filesDir()
        for (name in listOf("foundations.txt", "meaning.txt")) {
            val dest = File(dir, name)
            if (!dest.exists()) {
                assets.open(name).use { inp ->
                    dest.outputStream().use { out -> inp.copyTo(out) }
                }
            }
        }
    }

    // ── Python seeder thread ───────────────────────────────────────────────────

    private fun startSeedThread() {
        Thread {
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(this))
            }
            val py      = Python.getInstance()
            val runner  = py.getModule("seed_runner")
            val filesDir = filesDir()

            // Progress callback — called from Python threads
            val callback = PyObject.fromJava(object : Any() {
                @Suppress("unused")
                fun __call__(name: String, tag: String, url: String,
                             idx: Int, total: Int, studied: Int, skipped: Int) {
                    val state = CorpusState(
                        name    = name,
                        label   = when (name) {
                            "foundations" -> "Foundations"
                            "meaning"     -> "Meaning"
                            else          -> "Fermat / War"
                        },
                        tag     = tag,
                        idx     = idx + 1,
                        total   = total,
                        studied = studied,
                        skipped = skipped,
                        status  = "RUNNING",
                    )
                    handler.post {
                        SeedLiveData.forName(name).value = state
                        updateNotification()
                    }
                }
            })

            try {
                runner.callAttr("run_all", filesDir, callback, 15)
                handler.post {
                    // Mark all complete
                    for (name in listOf("foundations", "meaning", "fermat")) {
                        val prev = SeedLiveData.forName(name).value ?: return@post
                        SeedLiveData.forName(name).value = prev.copy(status = "COMPLETE")
                    }
                    SeedLiveData.allDone.value = true
                    updateNotification(done = true)
                }
            } catch (e: Exception) {
                handler.post {
                    updateNotification(error = e.message ?: "error")
                }
            }
        }.also { it.isDaemon = true; it.name = "PtolemySeed" }.start()
    }

    // ── notifications ──────────────────────────────────────────────────────────

    private fun createNotificationChannel() {
        val ch = NotificationChannel(
            CHANNEL_ID,
            "Ptolemy Seeder",
            NotificationManager.IMPORTANCE_LOW
        ).apply { description = "Prime Directive corpus seeding" }
        getSystemService(NotificationManager::class.java).createNotificationChannel(ch)
    }

    private fun buildNotification(text: String, done: Boolean = false): Notification {
        val pi = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(if (done) "Ptolemy Seeder — Complete" else "Ptolemy Seeder")
            .setContentText(text)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentIntent(pi)
            .setOngoing(!done)
            .setSilent(true)
            .build()
    }

    private fun updateNotification(done: Boolean = false, error: String = "") {
        val f = SeedLiveData.foundations.value
        val m = SeedLiveData.meaning.value
        val w = SeedLiveData.fermat.value
        val text = when {
            error.isNotEmpty() -> "Error: $error"
            done -> "All three complete — copy .bin files to ~/.ptolemy/"
            else -> "F:${f?.idx ?: 0}/${f?.total ?: 0}  " +
                    "M:${m?.idx ?: 0}/${m?.total ?: 0}  " +
                    "W:${w?.idx ?: 0}/${w?.total ?: 0}"
        }
        getSystemService(NotificationManager::class.java)
            .notify(NOTIF_ID, buildNotification(text, done))
    }
}
