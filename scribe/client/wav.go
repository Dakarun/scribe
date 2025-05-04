package main

import (
	"encoding/binary"
)

// encodeWAV converts raw audio data to WAV format
func encodeWAV(rawData []byte) []byte {
	// WAV header parameters
	sampleRate := uint32(16000)      // 16kHz
	bitsPerSample := uint16(16)      // 16-bit
	channels := uint16(1)            // mono
	byteRate := sampleRate * uint32(bitsPerSample) * uint32(channels) / 8
	blockAlign := uint16(channels) * bitsPerSample / 8

	// Create WAV header
	header := make([]byte, 44)
	copy(header[0:4], []byte("RIFF"))                     // ChunkID
	binary.BigEndian.PutUint32(header[4:8], 36+uint32(len(rawData))) // ChunkSize
	copy(header[8:12], []byte("WAVE"))                    // Format
	copy(header[12:16], []byte("fmt "))                  // Subchunk1ID
	binary.BigEndian.PutUint32(header[16:20], 16)         // Subchunk1Size
	binary.BigEndian.PutUint16(header[20:22], 1)          // AudioFormat (PCM)
	binary.BigEndian.PutUint16(header[22:24], channels)   // NumChannels
	binary.BigEndian.PutUint32(header[24:28], sampleRate) // SampleRate
	binary.BigEndian.PutUint32(header[28:32], byteRate)   // ByteRate
	binary.BigEndian.PutUint16(header[32:34], blockAlign) // BlockAlign
	binary.BigEndian.PutUint16(header[34:36], bitsPerSample) // BitsPerSample
	copy(header[36:40], []byte("data"))                  // Subchunk2ID
	binary.BigEndian.PutUint32(header[40:44], uint32(len(rawData))) // Subchunk2Size

	// Combine header and raw data
	wavData := make([]byte, len(header)+len(rawData))
	copy(wavData[0:44], header)
	copy(wavData[44:], rawData)

	return wavData
}
