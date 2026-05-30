package com.ptolemy.seeder

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.Gravity
import android.view.ViewGroup.LayoutParams.MATCH_PARENT
import android.view.ViewGroup.LayoutParams.WRAP_CONTENT
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.cardview.widget.CardView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import org.json.JSONObject
import java.io.File

class MainActivity : AppCompatActivity() {

    private val progressBars = mutableMapOf<String, ProgressBar>()
    private val statusTexts  = mutableMapOf<String, TextView>()
    private val chipTexts    = mutableMapOf<String, TextView>()
    private lateinit var cardsContainer: LinearLayout
    private lateinit var doneCard:       CardView
    private lateinit var outputText:     TextView

    private val colorMap = mapOf(
        "gold"   to "#C9A84C",
        "blue"   to "#6EA8D4",
        "red"    to "#B05050",
        "green"  to "#6EAD7A",
        "purple" to "#9B7DC8",
        "cyan"   to "#4EC9C9",
        "orange" to "#D4915A",
    )

    private val pickPTorrent = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? -> uri?.let { importPTorrent(it) } }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(buildLayout())
        requestNotificationPermission()
        ContextCompat.startForegroundService(this, Intent(this, SeedService::class.java))

        // handle .ptorrent file opened via intent
        if (intent.action == Intent.ACTION_VIEW && intent.data != null) {
            importPTorrent(intent.data!!)
        }

        SeedLiveData.order.observe(this) { names ->
            val current = SeedLiveData.corpora.value ?: emptyMap()
            cardsContainer.removeAllViews()
            progressBars.clear(); statusTexts.clear(); chipTexts.clear()
            for (name in names) {
                val color = current[name]?.color ?: "gold"
                addCorpusCard(name, color)
            }
        }

        SeedLiveData.corpora.observe(this) { states ->
            for ((name, state) in states) {
                progressBars[name]?.apply {
                    max      = state.total.coerceAtLeast(1)
                    progress = state.idx
                }
                statusTexts[name]?.text = statusLine(state)
                chipTexts[name]?.text   = state.status
            }
        }

        SeedLiveData.allDone.observe(this) { done ->
            if (!done) return@observe
            val dir   = getExternalFilesDir(null)?.absolutePath ?: filesDir.absolutePath
            val names = SeedLiveData.order.value ?: emptyList()
            val bins  = names.joinToString("\n") { n ->
                val bin = SeedLiveData.corpora.value?.get(n)?.let {
                    binNameFromJson(n)
                } ?: "monad_${sanitize(n)}.bin"
                "  adb pull $dir/$bin"
            }
            outputText.text = "Files ready at:\n$dir\n\nPull to ~/.ptolemy/:\n$bins"
            doneCard.visibility = android.view.View.VISIBLE
        }
    }

    // ── layout ─────────────────────────────────────────────────────────────

    private fun buildLayout(): ScrollView {
        val bg = Color.parseColor("#0D0D14")

        val scroll = ScrollView(this).apply {
            setBackgroundColor(bg)
            layoutParams = LinearLayout.LayoutParams(MATCH_PARENT, MATCH_PARENT)
        }
        val outer = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(12), dp(16), dp(12), dp(24))
        }

        // Title
        outer.addView(TextView(this).apply {
            text = "Ptolemy Seeder"
            textSize = 20f
            setTextColor(Color.parseColor("#C9A84C"))
            setPadding(dp(4), 0, 0, dp(10))
            gravity = Gravity.CENTER_HORIZONTAL
        })

        // Transmission toolbar
        outer.addView(buildToolbar(), marginParams(bottom = 14))

        // Corpus cards
        cardsContainer = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        outer.addView(cardsContainer)

        // Done card
        doneCard = makeCard("#16161F").apply { visibility = android.view.View.GONE }
        outputText = TextView(this).apply {
            setTextColor(Color.parseColor("#E8E8E8"))
            textSize = 11f
            setPadding(dp(12), dp(12), dp(12), dp(12))
            setTextIsSelectable(true)
        }
        doneCard.addView(outputText)
        outer.addView(doneCard, marginParams(top = 12))

        scroll.addView(outer)
        return scroll
    }

    private fun buildToolbar(): LinearLayout {
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
        }
        row.addView(toolbarBtn("▶", "#6EAD7A") {
            startService(Intent(this, SeedService::class.java).apply {
                action = SeedService.ACTION_RESUME
            })
        })
        row.addView(toolbarBtn("⏸", "#C9A84C") {
            startService(Intent(this, SeedService::class.java).apply {
                action = SeedService.ACTION_PAUSE
            })
        })
        row.addView(toolbarBtn("✕ Done", "#7A7A8A") {
            clearDoneCards()
        })
        row.addView(toolbarBtn("＋ PTorrent", "#6EA8D4") {
            pickPTorrent.launch("*/*")
        })
        return row
    }

    private fun toolbarBtn(label: String, hexColor: String, action: () -> Unit): TextView =
        TextView(this).apply {
            text = label
            textSize = 12f
            setTextColor(Color.parseColor(hexColor))
            setPadding(dp(10), dp(7), dp(10), dp(7))
            setBackgroundColor(Color.parseColor("#1A1A26"))
            setOnClickListener { action() }
            layoutParams = LinearLayout.LayoutParams(WRAP_CONTENT, WRAP_CONTENT).also {
                it.marginEnd = dp(6)
            }
        }

    private fun clearDoneCards() {
        val order   = SeedLiveData.order.value?.toMutableList() ?: return
        val states  = SeedLiveData.corpora.value ?: return
        val active  = order.filter { states[it]?.status != "COMPLETE" }
        cardsContainer.removeAllViews()
        progressBars.clear(); statusTexts.clear(); chipTexts.clear()
        for (name in active) {
            val color = states[name]?.color ?: "gold"
            addCorpusCard(name, color)
        }
    }

    // ── corpus card ────────────────────────────────────────────────────────

    private fun addCorpusCard(name: String, colorKey: String) {
        val accent = Color.parseColor(colorMap[colorKey] ?: "#C9A84C")
        val card   = makeCard("#16161F")

        val col = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(12), dp(10), dp(12), dp(12))
        }

        // Name + chip + pause button row
        val nameRow = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        nameRow.addView(TextView(this).apply {
            text = name; textSize = 13f; setTextColor(accent)
            layoutParams = LinearLayout.LayoutParams(0, WRAP_CONTENT, 1f)
        })
        val chip = TextView(this).apply {
            text = "WAITING"; textSize = 10f; setTextColor(accent)
            setPadding(dp(6), dp(2), dp(6), dp(2))
            setBackgroundColor(Color.parseColor("#22222E"))
        }
        chipTexts[name] = chip
        nameRow.addView(chip)
        col.addView(nameRow)

        // Progress bar
        val bar = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply {
            max = 1; progress = 0
            progressTintList = android.content.res.ColorStateList.valueOf(accent)
            layoutParams = LinearLayout.LayoutParams(MATCH_PARENT, dp(6)).also {
                it.topMargin = dp(6)
            }
        }
        progressBars[name] = bar
        col.addView(bar)

        // Status line
        val statusTv = TextView(this).apply {
            text = "Waiting…"; textSize = 10f
            setTextColor(Color.parseColor("#7A7A8A"))
            setPadding(0, dp(4), 0, 0)
        }
        statusTexts[name] = statusTv
        col.addView(statusTv)

        card.addView(col)
        // tap → detail page
        card.setOnClickListener {
            startActivity(
                Intent(this, CorpusDetailActivity::class.java)
                    .putExtra(CorpusDetailActivity.EXTRA_CORPUS_NAME, name)
            )
        }
        cardsContainer.addView(card, marginParams(bottom = 10))
    }

    // ── PTorrent import ────────────────────────────────────────────────────

    private fun importPTorrent(uri: Uri) {
        try {
            val text = contentResolver.openInputStream(uri)?.bufferedReader()?.readText() ?: return
            val obj  = JSONObject(text)
            val name = obj.optString("name", "unknown")
            val dir  = getExternalFilesDir(null) ?: filesDir
            val inbox = File(dir, "inbox").also { it.mkdirs() }
            File(inbox, "import_${System.currentTimeMillis()}.ptorrent").writeText(text)
            Toast.makeText(this, "PTorrent queued: $name", Toast.LENGTH_SHORT).show()
            // ensure service is running to pick it up via FileObserver
            ContextCompat.startForegroundService(this, Intent(this, SeedService::class.java))
        } catch (_: Exception) {
            Toast.makeText(this, "Could not read PTorrent file", Toast.LENGTH_SHORT).show()
        }
    }

    // ── helpers ────────────────────────────────────────────────────────────

    private fun makeCard(bgHex: String): CardView = CardView(this).apply {
        setCardBackgroundColor(Color.parseColor(bgHex))
        radius = dp(8).toFloat(); cardElevation = dp(2).toFloat()
    }

    private fun marginParams(top: Int = 0, bottom: Int = 0) =
        LinearLayout.LayoutParams(MATCH_PARENT, WRAP_CONTENT).also {
            it.topMargin = dp(top); it.bottomMargin = dp(bottom)
        }

    private fun dp(n: Int) = (n * resources.displayMetrics.density).toInt()

    private fun statusLine(s: CorpusState): String {
        if (s.total == 0) return "Waiting…"
        val tag = if (s.tag.isNotEmpty()) "[${s.tag}]" else ""
        return "${s.idx}/${s.total}  ✓${s.studied}  ✗${s.skipped}  $tag"
    }

    private fun sanitize(name: String) = name.lowercase().replace(Regex("[^a-z0-9]"), "_")

    private fun binNameFromJson(name: String): String {
        val f = File(getExternalFilesDir(null) ?: filesDir, "corpus_list.json")
        if (!f.exists()) return "monad_${sanitize(name)}.bin"
        return try {
            val arr = org.json.JSONArray(f.readText())
            for (i in 0 until arr.length()) {
                val obj = arr.getJSONObject(i)
                if (obj.getString("name") == name) return obj.optString("bin", "monad_${sanitize(name)}.bin")
            }
            "monad_${sanitize(name)}.bin"
        } catch (_: Exception) { "monad_${sanitize(name)}.bin" }
    }

    private fun requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
            != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1
            )
        }
    }
}
