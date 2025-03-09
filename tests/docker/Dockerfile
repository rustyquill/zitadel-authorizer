FROM golang:latest as healthcheck
WORKDIR /app

ADD main.go /app
RUN go build -o /app/healthcheck /app/main.go

FROM ghcr.io/zitadel/zitadel:latest

COPY --from=healthcheck /app/healthcheck /healthcheck
