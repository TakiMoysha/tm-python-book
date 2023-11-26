import pathlib

from robyn import Request, Response, Robyn, jsonify, SubRouter
from robyn.logger import Logger
from robyn.templating import JinjaTemplate
from robyn.ws import WebSocket

# setup
app = Robyn(__file__)
logger = Logger()

## Templates
current_file_path = pathlib.Path(__file__).parent.resolve()
jinja_templates = JinjaTemplate(current_file_path / "templates")

@app.get("/")
async def default(request):
    return f"Hello, {request.ip_addr}!"

@app.get("/dashboard")
async def index(request: Request):
    context = {
        "framework": "Robyn",
        "templating_engine": "Jinja2",
    }
    return jinja_templates.render_template("base.html", **context)

# request lifecycle
events_endpoint_name = "/lifecycle"

@app.get(events_endpoint_name)
async def lifecycle(request: Request):
    data = {
        "url": request.url,
        "query": request
    }
    return jsonify(data)

# before/after on particular request
@app.before_request(events_endpoint_name)
async def pre_log_lifecycle_req(request: Request):
    # logger.info(f"Received request: {request}")
    pass

@app.after_request(events_endpoint_name)
async def post_log_lifecycle_req(response: Response):
    # logger.info(f"Sending response {response}")
    pass


# # before/after on all requests
@app.before_request()
async def before_request(request: Request):
    return request

@app.after_request()
async def after_request(response: Response):
    return response

# websockets
notif_ws = WebSocket(app, "/notifications")

@notif_ws.on("connect")
async def notify_connect():
    return "Connected to notifications"

@notif_ws.on("message")
async def notify_message(message):
    return f"Received: {message}"

@notif_ws.on("close")
async def notify_disconnect():
    return "Disconnected from notifications"


# sub domain
## prefix not work?
spa_router = SubRouter(__name__, prefix="/spa")

@spa_router.get("/")
async def single_page_app(request: Request):
    return "Stub endpoint"

# view
@spa_router.view("/sync/view/:id")
def sync_decorator_view():
    def get(request: Request):
        return {
            "status_code": 200,
            "description": "OK",
            "body": {"id": request.path_params["id"]},
        }

    def post(request: Request):
        body = request.body
        return {"status_code": 201, "description": body, "body": {"num": 6}}

# error handler
@app.get("/error")
def error(request: Request):
    raise Exception("Error!")

# not work?
@app.exception
def handle_exception(error):
    return {
        "status_code": 501,
        "description": "Not Implemented",
        "body": {"error": error},
    }

# runner
app.include_router(spa_router)
app.start(port=8080)
