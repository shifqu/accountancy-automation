"""Ida's HTTP API main functionality."""
from ida_py import bot, server, transformer
from ida_py.api.config import api_config
from ida_py.api.utils import assert_post, convert_to_json_dict

API_CONFIG = api_config()

app = server.Application()


@app.route("/ping")
def ping(_: server.Request) -> server.JSONResponse:
    """Return a heartbeat.

    Returns
    -------
    JSONResponse
        A successful response.
    """
    return server.JSONResponse({"ok": True, "ping": "pong!"})


@app.route(API_CONFIG.bot_route)
def telegram_webhook(request: server.Request) -> server.JSONResponse:
    """Run the telegram bot to register a response.

    This endpoint is called for each new message sent to the telegram bot.

    Parameters
    ----------
    request : Request
        The request as received by the endpoint.

    Returns
    -------
    JSONResponse
        A successful response

    Raises
    ------
    ApiException
        Whenever the request was invalid or when the bot failed to process the update.
    """
    assert_post(request.method)
    update_json = convert_to_json_dict(request.body)

    try:
        update = transformer.from_dict(bot.TelegramUpdate, update_json)
    except transformer.ValidationError as exc:
        raise server.ApiException({"ok": False, "error": str(exc)}, status_code=400)

    secret_token = request.headers.get("X-TELEGRAM-BOT-API-SECRET-TOKEN", "")

    try:
        bot.run(update, secret_token)
    except bot.ExecutionError as exc:
        raise server.ApiException({"ok": False, "error": str(exc)}, status_code=400)

    return server.JSONResponse({"ok": True})


@app.route("/.*")
def route_404(_: server.Request) -> server.JSONResponse:
    """Return a 404.

    This endpoint is a catch-all endpoint and should always be declared last.

    Raises
    ------
    ApiException
        An ApiException with a false "ok" flag and status-code 404.
    """
    raise server.ApiException({"ok": False}, status_code=404)


def run():
    """Serve Ida' API."""
    app.serve(API_CONFIG.host, API_CONFIG.port)


if __name__ == "__main__":
    run()
