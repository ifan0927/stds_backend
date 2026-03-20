package main

import (
	"github.com/gin-gonic/gin"
	"github.com/ifan0927/stds-backend/internal/api"
	"github.com/ifan0927/stds-backend/internal/handler"
)

func main() {

	r := gin.New()

	// health endpoint
	r.GET("/healthz", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status": "ok",
		})
	})

	// all endpoint
	server := handler.NewServer()

	strictHandler := api.NewStrictHandler(server, nil)

	api.RegisterHandlers(r, strictHandler)

	err := r.Run(":8080")
	if err != nil {
		return
	}

}
