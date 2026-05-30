package com.ptolemy.seeder

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.Environment
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.ptolemy.seeder.databinding.ActivityMainBinding
import java.io.File

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        requestNotificationPermission()

        // Start the seeder service immediately — it handles re-entry gracefully
        ContextCompat.startForegroundService(
            this, Intent(this, SeedService::class.java))

        observeProgress()
    }

    private fun requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(
                this, Manifest.permission.POST_NOTIFICATIONS
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                1
            )
        }
    }

    private fun observeProgress() {
        SeedLiveData.foundations.observe(this) { s ->
            binding.foundationsProgress.max     = s.total.coerceAtLeast(1)
            binding.foundationsProgress.progress = s.idx
            binding.foundationsStatus.text       = statusLine(s)
            binding.foundationsChip.text         = s.status
        }
        SeedLiveData.meaning.observe(this) { s ->
            binding.meaningProgress.max      = s.total.coerceAtLeast(1)
            binding.meaningProgress.progress = s.idx
            binding.meaningStatus.text       = statusLine(s)
            binding.meaningChip.text         = s.status
        }
        SeedLiveData.fermat.observe(this) { s ->
            binding.fermatProgress.max      = s.total.coerceAtLeast(1)
            binding.fermatProgress.progress = s.idx
            binding.fermatStatus.text       = statusLine(s)
            binding.fermatChip.text         = s.status
        }
        SeedLiveData.allDone.observe(this) { done ->
            if (done) {
                val dir = getExternalFilesDir(null)?.absolutePath ?: filesDir.absolutePath
                binding.doneCard.visibility = android.view.View.VISIBLE
                binding.outputPath.text =
                    "Files ready at:\n$dir\n\n" +
                    "Copy to ~/.ptolemy/ on your Linux machine:\n" +
                    "  monad_foundations.bin\n" +
                    "  monad_meaning.bin\n" +
                    "  monad_war.bin"
            }
        }
    }

    private fun statusLine(s: CorpusState): String {
        if (s.total == 0) return "Waiting…"
        val url = if (s.tag.isNotEmpty()) "[${s.tag}]" else ""
        return "${s.idx}/${s.total}  studied:${s.studied}  skipped:${s.skipped}  $url"
    }
}
