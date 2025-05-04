package main

import (
	"log"
	"time"
)

type Config struct {
	ServerURL         string  `yaml:"server_url"`
	EnergyThreshold   int     `yaml:"energy_threshold"`
	RecordTimeout     float64 `yaml:"record_timeout"`
	PhraseTimeout     float64 `yaml:"phrase_timeout"`
	DeviceName        string  `yaml:"device_name"`
}

func main() {
	// Load configuration
	config := loadConfig()
	
	// Initialize audio capture
	decoder, err := initAudioCapture(config.DeviceName)
	if err != nil {
		log.Fatalf("Failed to initialize audio capture: %v", err)
	}
	
	// Initialize HTTP client
	httpClient := NewHTTPClient(config.ServerURL)
	
	// Main processing loop
	for {
		// Capture audio
		audioData := captureAudio(decoder, config.RecordTimeout)
		
		// Encode to WAV
		wavData := encodeWAV(audioData)
		
		// Send to server
		err := httpClient.Upload(wavData)
		if err != nil {
			log.Printf("Upload failed: %v", err)
		}
		
		time.Sleep(time.Second)
	}
}