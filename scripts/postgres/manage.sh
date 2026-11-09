#!/bin/sh
set -eu

action="${1:-help}"

case "$action" in
    up)
        docker compose up -d
        ;;
    status)
        docker compose ps
        ;;
    logs)
        docker compose logs
        ;;
    stop)
        docker compose stop
        ;;
    start)
        docker compose start
        ;;
    down)
        docker compose down
        ;;
    destroy-volume)
        if [ "${CONFIRM_DELETE_POSTGRES_VOLUME:-}" != "yes" ]; then
            echo "Set CONFIRM_DELETE_POSTGRES_VOLUME=yes to run docker compose down -v." >&2
            exit 2
        fi
        docker compose down -v
        ;;
    help|*)
        echo "Usage: sh scripts/postgres/manage.sh {up|status|logs|stop|start|down|destroy-volume}"
        ;;
esac
