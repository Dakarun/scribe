package main

func loadConfig() *Config {
	return &Config{
		ServerURL:         "http://homelab-1:5000",
		EnergyThreshold:   1000,
		RecordTimeout:     2,
		PhraseTimeout:     3,
		DeviceName:        "default",
	}
}