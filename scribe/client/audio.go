package main

import (
	"time"
	"github.com/ebitengine/portaudio"
)

func initAudioCapture(deviceName string) (interface{}, error) {
	// Initialize portaudio
	err := portaudio.Initialize()
	if err != nil {
		return nil, err
	}

	// Get default input device
	dev, err := portaudio.DefaultInputDevice()
	if err != nil {
		return nil, err
	}

	// Open stream with 44.1kHz sample rate, 2 channels, 1024 samples buffer
	stream, err := portaudio.OpenStream(dev, 44100, 2, 1024, nil)
	if err != nil {
		return nil, err
	}

	return stream, nil
}

func captureAudio(decoder interface{}, timeout float64) []byte {
	stream := decoder.(portaudio.Stream)
	
	// Start the audio stream
	err := stream.Start()
	if err != nil {
		return nil
	}
	
	// Create buffer for audio data
	buffer := make([]float32, 1024)
	startTime := time.Now()
	
	// Read audio data from the stream
	for {
		// Check timeout
		if time.Since(startTime) > time.Duration(timeout)*time.Second {
			break
		}
		
		// Read audio data from the stream
		n, err := stream.Read(buffer)
		if err != nil {
			break
		}
		
		// Process audio data if needed
	}
	
	// Stop the audio stream
	stream.Stop()
	
	// Convert float32 buffer to []byte (simplified example)
	result := make([]byte, len(buffer)*4)
	for i, v := range buffer {
		result[i*4] = byte(v * 128)
		result[i*4+1] = byte((v * 128) >> 8)
		result[i*4+2] = byte((v * 128) >> 16)
		result[i*4+3] = byte((v * 128) >> 24)
	}
	
	return result
}
