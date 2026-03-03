package main

import (
	"log"
	"net/http"
	"os"
)

// getEnv returns the value of an environment variable or a default value.
func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func main() {
	// Get configuration from environment variables
	port := getEnv("PORT", "8081")

	// Register HTTP handlers
	http.HandleFunc("/sort", HandleSort)
	http.HandleFunc("/health", HandleHealth)

	// Log server startup
	log.Printf("Starting sort module on port %s", port)
	log.Printf("Module: %s, Version: %s", moduleName, moduleVersion)

	// Start HTTP server
	addr := ":" + port
	if err := http.ListenAndServe(addr, nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
