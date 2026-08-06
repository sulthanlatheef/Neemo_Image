<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);

header("Content-Type: application/json");

$action = $_GET['action'] ?? '';

$fastapiBaseUrl = "http://127.0.0.1:5000/figmaimport";

$devControllerBaseUrl = "http://127.0.0.1:3001";

/*
|--------------------------------------------------------------------------
| HELPER FUNCTION
|--------------------------------------------------------------------------
*/
function postMultipartRequest($url)
{
    $ch = curl_init();

    $postFields = [];

    foreach ($_FILES as $fieldName => $file) {

        $postFields[$fieldName] = new CURLFile(

            $file["tmp_name"],

            $file["type"],

            $file["name"]

        );

    }

    curl_setopt_array($ch, [

        CURLOPT_URL => $url,

        CURLOPT_POST => true,

        CURLOPT_RETURNTRANSFER => true,

        CURLOPT_POSTFIELDS => $postFields,

        CURLOPT_TIMEOUT => 0

    ]);

    $response = curl_exec($ch);

    if (curl_errno($ch)) {

        throw new Exception(

            curl_error($ch)

        );

    }

    curl_close($ch);

    return $response;
}

function sendGetRequest($url)
{
    $ch = curl_init();

    curl_setopt_array($ch, [

        CURLOPT_URL => $url,

        CURLOPT_RETURNTRANSFER => true

    ]);

    $response = curl_exec($ch);

    if (curl_errno($ch)) {

        return json_encode([
            "error" => curl_error($ch)
        ]);
    }

    return $response;
}

/*
|--------------------------------------------------------------------------
| START SERVER
|--------------------------------------------------------------------------
*/

if ($action === 'start_server') {

    echo sendGetRequest(
        $devControllerBaseUrl . "/start"
    );

    exit;
}

/*
|--------------------------------------------------------------------------
| STOP SERVER
|--------------------------------------------------------------------------
*/

if ($action === 'stop_server') {

    echo sendGetRequest(
        $devControllerBaseUrl . "/stop"
    );

    exit;
}

/*
|--------------------------------------------------------------------------
| RESTART SERVER
|--------------------------------------------------------------------------
*/

if ($action === 'restart_server') {

    echo sendGetRequest(
        $devControllerBaseUrl . "/restart"
    );

    exit;
}

/*
|--------------------------------------------------------------------------
| GET LOGS
|--------------------------------------------------------------------------
*/

if ($action === 'get_logs') {

    echo sendGetRequest(
        $devControllerBaseUrl . "/logs"
    );

    exit;
}

/*
|--------------------------------------------------------------------------
| GET SERVER STATUS
|--------------------------------------------------------------------------
*/

if ($action === 'get_status') {

    echo sendGetRequest(
        $devControllerBaseUrl . "/status"
    );

    exit;
}

/*
|--------------------------------------------------------------------------
| START NEMO CONTROLLER
|--------------------------------------------------------------------------
*/

if ($action === 'start_nemo') {

    try {

        $batFile = "C:\\wamp64\\www\\Neemo_image_beta\\Engine\\start_nemo.bat";

        $process = popen(
            'cmd /c start "" "' . $batFile . '"',
            'r'
        );

        if ($process === false) {
            throw new Exception("Failed to start Nemo.");
        }

        pclose($process);

        echo json_encode([
            "status" => "started"
        ]);

    } catch (Exception $e) {

        http_response_code(500);

        echo json_encode([
            "status" => "error",
            "message" => $e->getMessage()
        ]);
    }

    exit;
}
function postJsonRequest($url, $payload)
{
    $ch = curl_init();

    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => [
            "Content-Type: application/json"
        ],
        CURLOPT_POSTFIELDS => json_encode($payload),
        CURLOPT_TIMEOUT => 0
    ]);

    $response = curl_exec($ch);

    if (curl_errno($ch)) {
        throw new Exception(curl_error($ch));
    }

    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    curl_close($ch);

    if ($status >= 400) {
        throw new Exception($response);
    }

    return $response;
}
/*
|--------------------------------------------------------------------------
| HEALTH CHECK
|--------------------------------------------------------------------------
*/

if ($action === 'health') {

    echo sendGetRequest(
        "http://127.0.0.1:8000/health"
    );

    exit;
}
/*
|--------------------------------------------------------------------------
| LOAD FRAMES
|--------------------------------------------------------------------------
*/

if ($action === "upload_image") {

    echo postMultipartRequest(
        "http://127.0.0.1:3001/upload_image"
    );

    exit;
}

/*
|--------------------------------------------------------------------------
| HTML + CSS Upload
|--------------------------------------------------------------------------
*/

if ($action === "upload_html_css") {

    echo postMultipartRequest(

        "http://127.0.0.1:3001/upload_html_css"

    );

    exit;

}
/*
|--------------------------------------------------------------------------
| INVALID ACTION
|--------------------------------------------------------------------------
*/

echo json_encode([
    "error" => "Invalid action"
]);