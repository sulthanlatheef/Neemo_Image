from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
import subprocess
import threading
import logging
import psutil
import time
import sys
import requests
import os
from websocket_client import (
    upload_image,
    upload_html_css
)
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)
from Config.config import DOCKER_PROJECT_PATH



# ------------------------------------------------------------------
# DISABLE FLASK REQUEST LOGS
# ------------------------------------------------------------------

#log = logging.getLogger('werkzeug')

#log.disabled = True

# ------------------------------------------------------------------
# APP
# ------------------------------------------------------------------

app = Flask(__name__)

CORS(app)

# Global environment
environment = "local"

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------

PROJECT_PATH = DOCKER_PROJECT_PATH

# ------------------------------------------------------------------
# GLOBAL STATE
# ------------------------------------------------------------------

server_process = None

server_logs = []

server_running = False
# ------------------------------------------------------------------
# NETWORK TRACKING
# ------------------------------------------------------------------

last_net = psutil.net_io_counters()

last_time = time.time()

@app.route("/set-environment", methods=["POST"])
def set_environment():
    global environment

    data = request.get_json()

    env = data.get("environment")

    if env not in ["local", "dev"]:
        return jsonify({
            "success": False,
            "message": "Invalid environment."
        }), 400

    environment = env

    print(f"Environment changed to: {environment}")

    return jsonify({
        "success": True,
        "environment": environment
    })

@app.route("/get-environment", methods=["GET"])
def get_environment():
    return jsonify({
        "environment": environment
    })
# ------------------------------------------------------------------
# LOG READER
# ------------------------------------------------------------------

def read_logs(process):

    global server_logs
    global server_running

    try:

        for line in iter(process.stdout.readline, ''):

            if line:

                clean_line = line.strip()

                print(clean_line)

                server_logs.append(clean_line)

                

    except Exception as e:

        server_logs.append(
            f"LOG ERROR: {str(e)}"
        )

    finally:

        server_running = False

# ------------------------------------------------------------------
# START SERVER
# ------------------------------------------------------------------

@app.route('/start')

def start_server():

    global server_process
    global server_running

    if server_running:

        return jsonify({
            "status": "already_running"
        })

    server_logs.clear()

    server_process = subprocess.Popen(

        ["docker", "compose", "up", "--build"],

        cwd=PROJECT_PATH,

        stdout=subprocess.PIPE,

        stderr=subprocess.STDOUT,

        text=True,

        bufsize=1,

        creationflags=subprocess.CREATE_NO_WINDOW
    )

    server_running = True

    # BACKGROUND LOG THREAD

    thread = threading.Thread(

        target=read_logs,

        args=(server_process,)
    )

    thread.daemon = True

    thread.start()

    return jsonify({
        "status": "started"
    })

# ------------------------------------------------------------------
# STOP SERVER
# ------------------------------------------------------------------

@app.route('/stop')

def stop_server():

    global server_running

    subprocess.run(

        ["docker", "compose", "down"],

        cwd=PROJECT_PATH,

        creationflags=subprocess.CREATE_NO_WINDOW
    )

    server_running = False
    server_logs.clear()

    server_logs.append(
        "SERVER STOPPED NEEMO"
    )

    return jsonify({
        "status": "stopped"
    })

# ------------------------------------------------------------------
# RESTART SERVER
# ------------------------------------------------------------------

@app.route('/restart')

def restart_server():

    stop_server()

    start_server()
    return jsonify({
        "status": "Restarted"
    })

# ------------------------------------------------------------------
# GET LOGS
# ------------------------------------------------------------------

@app.route('/logs')

def get_logs():

    return jsonify({

        "logs": server_logs,

        "running": server_running
    })

# ------------------------------------------------------------------
# STATUS
# ------------------------------------------------------------------

@app.route('/status')

def status():

    return jsonify({
        "running": server_running
    })
# ------------------------------------------------------------------
# LIVE PERFORMANCE METRICS
# ------------------------------------------------------------------

@app.route('/metrics')

def metrics():

    global last_net
    global last_time

    try:

        # ----------------------------------------------------------
        # CPU
        # ----------------------------------------------------------

        cpu_usage = psutil.cpu_percent(interval=0.8)

        # ----------------------------------------------------------
        # RAM
        # ----------------------------------------------------------

        ram_usage = psutil.virtual_memory().percent

        # ----------------------------------------------------------
        # NETWORK SPEED
        # ----------------------------------------------------------

        current_net = psutil.net_io_counters()

        current_time = time.time()

        time_diff = current_time - last_time

        bytes_sent = (
            current_net.bytes_sent -
            last_net.bytes_sent
        )

        bytes_recv = (
            current_net.bytes_recv -
            last_net.bytes_recv
        )

        upload_speed = (
            bytes_sent / time_diff
        ) / 1024

        download_speed = (
            bytes_recv / time_diff
        ) / 1024

        # ----------------------------------------------------------
        # UPDATE PREVIOUS VALUES
        # ----------------------------------------------------------

        last_net = current_net

        last_time = current_time

        # ----------------------------------------------------------
        # RETURN
        # ----------------------------------------------------------

        return jsonify({

            "cpu": round(cpu_usage),

            "ram": round(ram_usage),

            "network": round(download_speed, 1),

            "server_running": server_running
        })

    except Exception as e:

        return jsonify({

            "error": str(e)

        }), 500

# ------------------------------------------------------------------
# SHUTDOWN NEMO
# ------------------------------------------------------------------

@app.route('/shutdown')

def shutdown():
    #stop_server()

    subprocess.Popen(

        [
            "taskkill",
            "/F",
            "/IM",
            "pythonw.exe"
        ],

        creationflags=
            subprocess.CREATE_NO_WINDOW
    )

    return jsonify({
        "status": "shutdown"
    })
    
# ------------------------------------------------------------
# Upload Image
# ------------------------------------------------------------

@app.post("/upload_image")
def upload_image_endpoint():

    try:

        image = request.files.get("image")

        if image is None:

            return jsonify({

                "status": "error",

                "message": "Image file is required."

            }), 400

        temp_path = os.path.join(
            os.getcwd(),
            image.filename
        )

        image.save(temp_path)

        try:

            result = asyncio.run(

                upload_image(
                    temp_path,
                    environment
                )

            )

        finally:

            if os.path.exists(temp_path):
                os.remove(temp_path)

        return jsonify(result.get("result", {}))

    except requests.HTTPError as e:

        if e.response is not None:
            try:
                error = e.response.json()

                return jsonify({
                "status": "error",
                "message": error.get("detail", str(e))
            }), e.response.status_code

            except Exception:
                pass

        return jsonify({
        "status": "error",
        "message": str(e)
    }), 500

# ------------------------------------------------------------
# Upload HTML + CSS
# ------------------------------------------------------------

@app.post("/upload_html_css")
def upload_html_css_endpoint():

    try:

        html_file = request.files.get("html")

        if html_file is None:

            return jsonify({

                "status": "error",

                "message": "HTML file is required."

            }), 400

        css_file = request.files.get("css")

        html_path = os.path.join(
            os.getcwd(),
            html_file.filename
        )

        html_file.save(html_path)

        css_path = None

        if css_file:

            css_path = os.path.join(
                os.getcwd(),
                css_file.filename
            )

            css_file.save(css_path)

        try:

            result = asyncio.run(

                upload_html_css(

                    html_path,

                    css_path,

                    environment

                )

            )

        finally:

            if os.path.exists(html_path):
                os.remove(html_path)

            if css_path and os.path.exists(css_path):
                os.remove(css_path)

        return jsonify(result.get("result", {}))

    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------

if __name__ == '__main__':

    app.run(

        host='0.0.0.0',

        port=3001,

        debug=False
    )