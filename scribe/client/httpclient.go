package main

import (
	"bytes"
	"fmt"
	"net/http"
)

type HTTPClient struct {
	serverURL string
}

func NewHTTPClient(serverURL string) *HTTPClient {
	return &HTTPClient{serverURL: serverURL}
}

func (c *HTTPClient) Upload(wavData []byte) error {
	url := fmt.Sprintf("%s/upload", c.serverURL)
	resp, err := http.Post(url, "audio/wav", bytes.NewBuffer(wavData))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("server returned non-200 status: %d", resp.StatusCode)
	}
	return nil
}