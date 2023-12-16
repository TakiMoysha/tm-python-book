# import os
import pathlib

from robyn import Request, Response, Robyn, jsonify, SubRouter
from robyn.logger import Logger
from robyn.templating import JinjaTemplate, 
from robyn.ws import WebSocket

# settings
app = Robyn(__file__)
logger = Logger()

## Templates
current_file_path = pathlib.Path(__file__).parent.resolve()
jinja_templates = JinjaTemplate(current_file_path / "templates")

@app.get("/")
async def default(request):
    return "Hello, World!"

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
# @app.before_request()
# async def before_request(request: Request):
#     print("before_request")
    # return request
#
# @app.after_request()
# async def after_request(response: Response):
#     print("after_request")
    # return response

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

# spa router
spa_router = SubRouter(__name__, prefix="/spa")

@spa_router.get("/")
async def single_page_app(request: Request):
    return "Stub endpoint"

# view
def sync_decorator_view():
    def get():
        return "Sync decorator view"

    def post(request: Request):
        body = request.body
        return {"status_code": 201, "description": body}

# runner
app.include_router(spa_router)
app.add_view('/sync/view/decorator', sync_decorator_view)
app.start(port=8080)
