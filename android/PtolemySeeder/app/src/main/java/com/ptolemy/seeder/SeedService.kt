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
import org.json.JSONArray
import java.io.File

data class CorpusState(
    val name:    String,
    val tag:     String = "",
    val idx:     Int    = 0,
    val total:   Int    = 0,
    val studied: Int    = 0,
    val skipped: Int    = 0,
    val status:  String = "WAITING",  // WAITING RUNNING PAUSED COMPLETE ERROR
    val color:   String = "gold",
    val error:   String = "",
)

object SeedLiveData {
    /** Map of corpus name → current state, observed by MainActivity. */
    val corpora = MutableLiveData<Map<String, CorpusState>>(emptyMap())
    val allDone = MutableLiveData(false)
    /** Ordered name list for stable card ordering in the UI. */
    val order   = MutableLiveData<List<String>>(emptyList())

    fun update(name: String, state: CorpusState) {
        val current = corpora.value ?: emptyMap()
        corpora.postValue(current + (name to state))
    }

    fun markDone(name: String) {
        val current = corpora.value ?: emptyMap()
        val prev    = current[name] ?: return
        corpora.postValue(current + (name to prev.copy(status = "COMPLETE")))
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
        if (intent?.action == ACTION_STOP) { stopSelf(); return START_NOT_STICKY }
        startForeground(NOTIF_ID, buildNotification("Starting…"))
        extractAssets()
        startSeedThread()
        return START_STICKY
    }

    // ── asset extraction ───────────────────────────────────────────────────

    private fun extDir(): String = getExternalFilesDir(null)?.absolutePath
        ?: filesDir.absolutePath

    private val assetFiles = listOf(
        "corpus_list.json",
        "foundations.txt",
        "meaning.txt",
        "war_corpus.txt",
        "python_corpus.txt",
        "c_corpus.txt",
    )

    private fun extractAssets() {
        val dir = extDir()
        for (name in assetFiles) {
            val dest = File(dir, name)
            // Always overwrite corpus_list.json (allows adb push to override)
            if (!dest.exists() || name == "corpus_list.json") {
                try {
                    assets.open(name).use { inp ->
                        dest.outputStream().use { out -> inp.copyTo(out) }
                    }
                } catch (_: Exception) {}
            }
        }
    }

    // ── read ordered corpus names from corpus_list.json ────────────────────

    private fun loadCorpusOrder(): List<Pair<String, String>> {
        val f = File(extDir(), "corpus_list.json")
        if (!f.exists()) return emptyList()
        return try {
            val arr = JSONArray(f.readText())
            (0 until arr.length()).map { i ->
                val obj = arr.getJSONObject(i)
                Pair(
                    obj.getString("name"),
                    obj.optString("color", "gold")
                )
            }
        } catch (_: Exception) { emptyList() }
    }

    // ── Python seeder thread ───────────────────────────────────────────────

    private fun startSeedThread() {
        // Seed initial WAITING states
        val corpusMeta = loadCorpusOrder()
        handler.post {
            SeedLiveData.order.value = corpusMeta.map { it.first }
            val initial = corpusMeta.associate { (name, color) ->
                name to CorpusState(name = name, color = color)
            }
            SeedLiveData.corpora.value = initial
        }

        Thread {
            if (!Python.isStarted()) Python.start(AndroidPlatform(this))
            val py      = Python.getInstance()
            val runner  = py.getModule("seed_runner")
            val extDir  = extDir()

            val callback = PyObject.fromJava(object : Any() {
                @Suppress("unused")
                fun __call__(
                    name: String, tag: String, @Suppress("UNUSED_PARAMETER") url: String,
                    idx: Int, total: Int, studied: Int, skipped: Int
                ) {
                    val color = corpusMeta.find { it.first == name }?.second ?: "gold"
                    val state = CorpusState(
                        name    = name,
                        tag     = tag,
                        idx     = idx + 1,
                        total   = total,
                        studied = studied,
                        skipped = skipped,
                        status  = "RUNNING",
                        color   = color,
                    )
                    handler.post {
                        SeedLiveData.update(name, state)
                        updateNotification()
                    }
                }
            })

            try {
                runner.callAttr("run_all", extDir, callback, 15)
                handler.post {
                    val names = SeedLiveData.order.value ?: emptyList()
                    names.forEach { SeedLiveData.markDone(it) }
                    SeedLiveData.allDone.value = true
                    updateNotification(done = true)
                }
            } catch (e: Exception) {
                handler.post { updateNotification(error = e.message ?: "error") }
            }
        }.also { it.isDaemon = true; it.name = "PtolemySeed" }.start()
    }

    // ── notifications ──────────────────────────────────────────────────────

    private fun createNotificationChannel() {
        val ch = NotificationChannel(
            CHANNEL_ID, "Ptolemy Seeder", NotificationManager.IMPORTANCE_LOW
        ).apply { description = "Corpus seeding" }
        getSystemService(NotificationManager::class.java).createNotificationChannel(ch)
    }

    private fun buildNotification(text: String, done: Boolean = false): Notification {
        val pi = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java),
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
        val states = SeedLiveData.corpora.value ?: emptyMap()
        val text = when {
            error.isNotEmpty() -> "Error: $error"
            done -> "All complete — pull .bin files to ~/.ptolemy/"
            else -> states.values
                .filter { it.status == "RUNNING" }
                .joinToString("  ") { "${it.name.take(4)}:${it.idx}/${it.total}" }
                .ifEmpty { "Running…" }
        }
        getSystemService(NotificationManager::class.java)
            .notify(NOTIF_ID, buildNotification(text, done))
    }
}
